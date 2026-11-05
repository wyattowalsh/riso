"""Tests for recopy command (shipped run_recopy entrypoint)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from riso.cli.commands.recopy import run_recopy
from riso.cli.config import CliConfig
from riso.core.errors import (
    CopierOperationError,
    PathNotFoundError,
    ValidationFailedError,
)
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit


def test_recopy_missing_destination_raises_path_not_found(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    missing = tmp_path / "does-not-exist"

    with pytest.raises(PathNotFoundError):
        run_recopy(
            config,
            destination=str(missing),
            answers_file=None,
            data_pairs=None,
        )


def test_recopy_dry_run_returns_diff_dict_without_live_worker(
    tmp_path: Path,
) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: Demo\ncli_module: enabled\ncli_languages: [python]\n",
        encoding="utf-8",
    )

    with patch("riso.cli.commands.recopy.template_run_recopy") as worker:
        result = run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Demo"],
            dry_run=True,
        )

    worker.assert_not_called()
    assert result["operation"] == "recopy"
    assert result["dry_run"] is True
    assert result["preview_engine"] == "answers"
    assert result["answers"].get("project_name") == "Demo"
    assert "summary" in result


def test_recopy_remaps_removed_answer_keys_before_worker(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    with patch(
        "riso.cli.commands.recopy.template_run_recopy",
        return_value=fake_result,
    ) as worker:
        run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["api_tracks=python"],
        )

    worker.assert_called_once()
    data = worker.call_args.kwargs["data"]
    assert data["api_module"] == "enabled"
    assert data["api_languages"] == ["python"]
    assert "api_tracks" not in data


def test_recopy_rejects_removed_answer_keys(tmp_path: Path) -> None:
    """Fail-closed leftover (unmapped saas_auth), not remappable api_tracks."""
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()

    with pytest.raises(ValidationFailedError) as exc:
        run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["saas_auth=firebase"],
        )
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_recopy_dry_run_remaps_existing_answers(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: Demo\napi_language: python\n",
        encoding="utf-8",
    )
    with patch("riso.cli.commands.recopy.template_run_recopy") as worker:
        result = run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Demo"],
            dry_run=True,
        )

    worker.assert_not_called()
    answers = result["answers"]
    assert answers["api_languages"] == ["python"]
    assert "api_language" not in answers
    assert result["preview_engine"] == "answers"


def test_recopy_live_writes_remapped_dest_answers(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()
    answers = dest / ".copier-answers.yml"
    answers.write_text("project_name: Demo\napi_language: python\n", encoding="utf-8")
    original = answers.read_bytes()
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    def succeed(**kwargs):
        assert answers.read_bytes() == original
        assert kwargs["data"]["project_name"] == "Renamed"
        answers.write_text(
            "_commit: new-commit\n_src_path: new-source\n", encoding="utf-8"
        )
        return fake_result

    with patch("riso.cli.commands.recopy.template_run_recopy", side_effect=succeed):
        run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Renamed"],
            dry_run=False,
        )

    written = yaml.safe_load(answers.read_text(encoding="utf-8"))
    assert written["api_languages"] == ["python"]
    assert "api_language" not in written
    assert written["project_name"] == "Renamed"
    assert written["_commit"] == "new-commit"
    assert written["_src_path"] == "new-source"


@pytest.mark.parametrize("failure", ["gate", "worker"])
def test_recopy_failure_does_not_persist_remaps(tmp_path: Path, failure: str) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()
    answers = dest / ".copier-answers.yml"
    answers.write_text("project_name: Demo\napi_language: python\n", encoding="utf-8")
    original = answers.read_bytes()
    pairs = ["api_module=enabled", "api_languages=[]"] if failure == "gate" else None
    error = ValidationFailedError if failure == "gate" else CopierOperationError
    with patch(
        "riso.cli.commands.recopy.template_run_recopy",
        side_effect=CopierOperationError("recopy", "worker rejected source"),
    ) as worker:
        with pytest.raises(error):
            run_recopy(
                config,
                destination=str(dest),
                answers_file=None,
                data_pairs=pairs,
            )
    if failure == "gate":
        worker.assert_not_called()
    assert answers.read_bytes() == original


def test_recopy_passes_skip_post_gen_to_template_runner(tmp_path: Path) -> None:
    config = CliConfig.from_options(
        template_path=resolve_template_path(),
        skip_post_gen=True,
    )
    dest = tmp_path / "proj"
    dest.mkdir()

    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    with patch(
        "riso.cli.commands.recopy.template_run_recopy",
        return_value=fake_result,
    ) as worker:
        result = run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=None,
            dry_run=False,
        )

    worker.assert_called_once()
    assert worker.call_args.kwargs["skip_post_gen"] is True
    assert result["success"] is True
