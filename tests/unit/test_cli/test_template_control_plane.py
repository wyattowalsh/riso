"""Control-plane tests for generation gates, update kwargs, skip_tasks, post_gen."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from riso.core.errors import (
    CopierOperationError,
    OperationTimeoutError,
    ValidationFailedError,
)
from riso.template import run_generator, run_recopy, run_update


@pytest.mark.parametrize(
    ("module", "languages"),
    [
        ("api_module", "api_languages"),
        ("cli_module", "cli_languages"),
        ("mcp_module", "mcp_languages"),
    ],
)
def test_generator_rejects_explicit_empty_languages_before_worker(
    tmp_path: Path, module: str, languages: str
) -> None:
    """An enabled module's empty language list fails before Copier starts."""
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError) as exc_info:
            run_generator(
                destination=tmp_path / "out",
                data={module: "enabled", languages: []},
                template_path=tmp_path,
            )
    worker.assert_not_called()
    assert exc_info.value.data is not None
    assert any(languages in error for error in exc_info.value.data["errors"])


def test_recopy_validates_empty_override_before_worker(tmp_path: Path) -> None:
    """An invalid recopy override leaves saved answers byte-for-byte intact."""
    dest = tmp_path / "proj"
    dest.mkdir()
    answers = dest / ".copier-answers.yml"
    answers.write_text("api_module: enabled\napi_languages: [python]\n")
    original = answers.read_bytes()
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError) as exc_info:
            run_recopy(
                destination=dest,
                data={"api_languages": []},
                template_path=tmp_path,
            )
    worker.assert_not_called()
    assert exc_info.value.data is not None
    assert any("api_languages" in error for error in exc_info.value.data["errors"])
    assert answers.read_bytes() == original


@pytest.mark.parametrize("operation", ["copy", "update", "recopy"])
def test_external_templates_never_run_managed_post_gen(
    tmp_path: Path, operation: str
) -> None:
    """No template operation gives an external source a managed hook."""
    external = tmp_path / "external"
    (external / "hooks").mkdir(parents=True)
    (external / "hooks" / "post_gen_project.py").write_text(
        "raise RuntimeError('untrusted')\n"
    )
    dest = tmp_path / "project"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        f"_src_path: {external}\nproject_name: Demo\n"
    )
    with (
        patch("riso.template._run_copier_worker"),
        patch("riso.template.run_post_gen") as post,
    ):
        if operation == "copy":
            run_generator(destination=dest, data={}, template_path=external, force=True)
        elif operation == "update":
            run_update(destination=dest, template_path=external)
        else:
            run_recopy(destination=dest, data=None, template_path=external)
    post.assert_not_called()


def test_run_generator_blocks_removed_keys_before_copier(tmp_path: Path) -> None:
    """Unmapped removed answers prevent all Copier worker execution."""
    dest = tmp_path / "out"
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError):
            run_generator(
                destination=dest,
                data={"saas_auth": "firebase", "project_name": "x"},
                template_path=tmp_path,
            )
        worker.assert_not_called()


def test_run_generator_remaps_old_keys_before_copier(tmp_path: Path) -> None:
    """Only canonical remapped API selections cross the Copier boundary."""
    dest = tmp_path / "out"
    captured: dict[str, Any] = {}

    def fake_worker(_op: str, payload: dict[str, Any], _timeout: int | None) -> None:
        captured["payload"] = payload
        dest.mkdir()

    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_generator(
            destination=dest,
            data={"api_tracks": "python", "project_name": "x"},
            template_path=tmp_path,
            skip_post_gen=True,
        )

    data = captured["payload"]["data"]
    assert data["api_module"] == "enabled"
    assert data["api_languages"] == ["python"]
    assert "api_tracks" not in data


def test_run_generator_calls_worker_with_skip_tasks_true(
    tmp_path: Path,
) -> None:
    """Copy operations disable Copier tasks and retain post-gen coordination."""
    dest = tmp_path / "out"
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
        captured["op"] = op
        captured["payload"] = payload
        captured["timeout"] = timeout
        dest.mkdir()

    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen") as post,
    ):
        result = run_generator(
            destination=dest,
            data={"cli_module": "enabled", "cli_languages": ["python"]},
            template_path=tmp_path,
            skip_post_gen=True,
        )
    assert result.success is True
    assert captured["op"] == "copy"
    assert captured["payload"]["skip_tasks"] is True
    post.assert_called_once()


def test_run_update_validates_saved_source_without_overriding_worker_data(
    tmp_path: Path,
) -> None:
    """Updates validate source metadata without pretending data can replace it."""
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        f"_src_path: {tmp_path / 'template'}\n"
        "cli_module: enabled\ncli_languages: [python]\n",
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], _timeout: int | None) -> None:
        captured["op"] = op
        captured["payload"] = payload

    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_update(
            destination=dest,
            template_path=tmp_path / "template",
            skip_post_gen=True,
        )
    assert captured["op"] == "update"
    assert captured["payload"]["skip_tasks"] is True
    assert captured["payload"]["data"] == {
        "cli_module": "enabled",
        "cli_languages": ["python"],
    }
    assert "defaults" not in captured["payload"] or isinstance(
        captured["payload"].get("defaults"), (bool, type(None))
    )


def test_run_update_rejects_corrupt_answers_file(tmp_path: Path) -> None:
    """Corrupt saved YAML fails closed before any update worker starts."""
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: [unterminated\n",
        encoding="utf-8",
    )
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError):
            run_update(destination=dest, template_path=tmp_path, skip_post_gen=True)
        worker.assert_not_called()


def test_run_update_blocks_bad_saas(tmp_path: Path) -> None:
    """Invalid SaaS provider combinations cannot reach the update worker."""
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "saas_infra_module: enabled\n"
        "saas_database: neon\n"
        "saas_storage: supabase-storage\n",
        encoding="utf-8",
    )
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError):
            run_update(destination=dest, template_path=tmp_path)
        worker.assert_not_called()


def test_timeout_raises_operation_timeout(tmp_path: Path) -> None:
    """Copier worker timeouts become a domain-specific operation timeout."""
    dest = tmp_path / "out"
    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        side_effect=__import__("subprocess").TimeoutExpired(cmd="x", timeout=1),
    ):
        with pytest.raises(OperationTimeoutError):
            run_generator(
                destination=dest,
                data={"cli_module": "enabled", "cli_languages": ["python"]},
                template_path=tmp_path,
                timeout=1,
                skip_post_gen=True,
            )


def test_worker_nonzero_raises_copier_operation_error(tmp_path: Path) -> None:
    """Worker stderr survives conversion into a Copier operation failure."""
    dest = tmp_path / "out"
    completed = __import__("subprocess").CompletedProcess(
        args=["x"],
        returncode=1,
        stdout="",
        stderr="boom",
    )
    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        return_value=completed,
    ):
        with pytest.raises(CopierOperationError) as exc_info:
            run_generator(
                destination=dest,
                data={"cli_module": "enabled", "cli_languages": ["python"]},
                template_path=tmp_path,
                skip_post_gen=True,
            )
    assert "boom" in str(exc_info.value)


def test_post_gen_skipped_when_flag_set(tmp_path: Path) -> None:
    """An explicit skip flag suppresses the managed post-generation hook."""
    dest = tmp_path / "out"

    def fake_worker(_op: str, _payload: dict[str, Any], _timeout: int | None) -> None:
        dest.mkdir()

    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template.run_post_gen") as post,
    ):
        run_generator(
            destination=dest,
            data={"cli_module": "enabled", "cli_languages": ["python"]},
            template_path=tmp_path,
            skip_post_gen=True,
        )
    post.assert_not_called()
