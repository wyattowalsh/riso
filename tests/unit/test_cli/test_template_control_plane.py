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
from riso.template import _evaluate_when, run_generator, run_recopy, run_update


def test_run_generator_blocks_removed_keys_before_copier(tmp_path: Path) -> None:
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
    dest = tmp_path / "out"
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
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


def test_run_generator_keeps_empty_lists_for_gates(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError):
            run_generator(
                destination=dest,
                data={"cli_module": "enabled", "cli_languages": []},
                template_path=tmp_path,
            )
        worker.assert_not_called()


def test_run_update_passes_src_path_in_data(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "cli_module: enabled\ncli_languages: [python]\n",
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
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
    assert captured["payload"]["overwrite"] is True
    assert captured["payload"]["unsafe"] is False
    data = captured["payload"]["data"]
    assert data["_src_path"] == str(tmp_path / "template")
    assert data["cli_module"] == "enabled"
    assert data["cli_languages"] == ["python"]
    assert "defaults" not in captured["payload"] or isinstance(
        captured["payload"].get("defaults"), (bool, type(None))
    )


def test_run_update_bundled_template_sets_unsafe_true(tmp_path: Path) -> None:
    from riso.core.paths import resolve_template_path

    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "cli_module: enabled\ncli_languages: [python]\n",
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
        captured["payload"] = payload

    bundled = resolve_template_path()
    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_update(destination=dest, template_path=bundled, skip_post_gen=True)
    assert captured["payload"]["unsafe"] is True
    assert captured["payload"]["skip_tasks"] is True
    assert captured["payload"]["overwrite"] is True


def test_run_update_rejects_corrupt_answers_file(tmp_path: Path) -> None:
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
    dest = tmp_path / "out"

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
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


def test_evaluate_when_bool_literals_before_falsy_check() -> None:
    assert _evaluate_when(False, {}) is False
    assert _evaluate_when(True, {}) is True
    assert _evaluate_when(None, {}) is True
    assert _evaluate_when("", {}) is True


def test_run_recopy_payload_overwrite_defaults_skip_answered(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
        captured["op"] = op
        captured["payload"] = payload

    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_recopy(
            destination=dest,
            data={"project_name": "Demo"},
            template_path=tmp_path / "template",
            skip_post_gen=True,
        )
    assert captured["op"] == "recopy"
    payload = captured["payload"]
    assert payload["skip_tasks"] is True
    assert payload["overwrite"] is True
    assert payload["defaults"] is True
    assert payload["skip_answered"] is True
    assert payload["unsafe"] is False
    assert payload["data"]["_src_path"] == str(tmp_path / "template")
