"""Tests for update command remap-then-Copier behavior."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from riso.cli.commands.update import run_update
from riso.cli.config import CliConfig
from riso.core.errors import (
    CopierOperationError,
    PathNotFoundError,
    ValidationFailedError,
)
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "remap"


def _config() -> CliConfig:
    return CliConfig.from_options(template_path=resolve_template_path())


def _write_fixture(dest: Path, name: str) -> Path:
    dest.mkdir()
    answers = dest / ".copier-answers.yml"
    answers.write_text((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    return answers


def test_update_missing_destination_raises(tmp_path: Path) -> None:
    with pytest.raises(PathNotFoundError):
        run_update(_config(), destination=str(tmp_path / "missing"))


def test_update_dry_run_remaps_without_writing(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    answers = _write_fixture(dest, "api_language.yml")
    original = answers.read_text(encoding="utf-8")
    with patch("riso.cli.commands.update.template_run_update") as worker:
        result = run_update(_config(), destination=str(dest), dry_run=True)

    worker.assert_not_called()
    remapped = result["answers"]
    assert remapped["api_languages"] == ["python"]
    assert "api_language" not in remapped
    assert answers.read_text(encoding="utf-8") == original
    assert result["preview_engine"] == "answers"
    assert result["dry_run"] is True
    assert result["remap"]["changed"] is True
    assert result["remap"]["written"] is False
    assert any(op["old"] == "api_language" for op in result["remap"]["ops"])


def test_update_dry_run_runs_generation_gates_without_writing(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: Demo\n"
        "saas_infra_module: enabled\n"
        "saas_database: neon\n"
        "saas_storage: supabase-storage\n",
        encoding="utf-8",
    )
    original = (dest / ".copier-answers.yml").read_text(encoding="utf-8")

    with patch("riso.cli.commands.update.template_run_update") as worker:
        with pytest.raises(ValidationFailedError) as exc:
            run_update(_config(), destination=str(dest), dry_run=True)

    worker.assert_not_called()
    assert (dest / ".copier-answers.yml").read_text(encoding="utf-8") == original
    assert exc.value.data is not None
    assert any("Neon" in err or "neon" in err for err in exc.value.data["errors"])


def test_update_live_writes_remapped_answers_after_copier(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    answers = _write_fixture(dest, "api_language.yml")
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    def fake_update(**kwargs: object) -> SimpleNamespace:
        current = yaml.safe_load(answers.read_text(encoding="utf-8"))
        assert "api_language" in current
        assert kwargs["answers"]["api_languages"] == ["python"]
        return fake_result

    with patch(
        "riso.cli.commands.update.template_run_update",
        side_effect=fake_update,
    ) as worker:
        result = run_update(_config(), destination=str(dest), dry_run=False)

    worker.assert_called_once()
    written = yaml.safe_load(answers.read_text(encoding="utf-8"))
    assert written["api_languages"] == ["python"]
    assert "api_language" not in written
    assert result["remap"]["written"] is True
    assert result["success"] is True


def test_update_copier_failure_leaves_answers_unchanged(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    answers = _write_fixture(dest, "api_language.yml")
    original = answers.read_text(encoding="utf-8")

    with patch(
        "riso.cli.commands.update.template_run_update",
        side_effect=CopierOperationError("update", "boom"),
    ):
        with pytest.raises(CopierOperationError):
            run_update(_config(), destination=str(dest), dry_run=False)

    assert answers.read_text(encoding="utf-8") == original


def test_update_does_not_wrap_validation_failed_as_copier_error(
    tmp_path: Path,
) -> None:
    dest = tmp_path / "proj"
    _write_fixture(dest, "already_canonical.yml")

    with patch(
        "riso.cli.commands.update.template_run_update",
        side_effect=ValidationFailedError(["blocked"]),
    ):
        with pytest.raises(ValidationFailedError) as exc:
            run_update(_config(), destination=str(dest), dry_run=False)

    assert exc.value.data is not None
    assert "blocked" in exc.value.data["errors"]


def test_update_leftover_fails_closed_without_write(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    answers = _write_fixture(dest, "leftover.yml")
    original = answers.read_text(encoding="utf-8")

    with patch("riso.cli.commands.update.template_run_update") as worker:
        with pytest.raises(ValidationFailedError) as exc:
            run_update(_config(), destination=str(dest), dry_run=True)

    worker.assert_not_called()
    assert answers.read_text(encoding="utf-8") == original
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_update_idempotent_canonical_is_noop_write(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    answers = _write_fixture(dest, "already_canonical.yml")
    original = answers.read_text(encoding="utf-8")
    with patch("riso.cli.commands.update.template_run_update") as worker:
        result = run_update(_config(), destination=str(dest), dry_run=True)

    worker.assert_not_called()
    assert result["preview_engine"] == "answers"
    assert result["remap"]["changed"] is False
    assert result["remap"]["ops"] == []
    assert answers.read_text(encoding="utf-8") == original


def test_update_passes_skip_post_gen(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    _write_fixture(dest, "already_canonical.yml")
    config = CliConfig.from_options(
        template_path=resolve_template_path(),
        skip_post_gen=True,
    )
    fake_result = SimpleNamespace(to_dict=lambda: {"success": True})

    with patch(
        "riso.cli.commands.update.template_run_update",
        return_value=fake_result,
    ) as worker:
        run_update(config, destination=str(dest), dry_run=False)

    assert worker.call_args.kwargs["skip_post_gen"] is True
