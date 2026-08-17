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
from riso.core.errors import PathNotFoundError, ValidationFailedError
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

    fake_diff = SimpleNamespace(
        to_dict=lambda: {
            "operation": "recopy",
            "files": [],
            "summary": {"added": 0, "modified": 0, "deleted": 0},
        }
    )

    with (
        patch(
            "riso.cli.commands.recopy.compute_diff",
            return_value=fake_diff,
        ) as compute,
        patch("riso.cli.commands.recopy.template_run_recopy") as worker,
    ):
        result = run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Demo"],
            dry_run=True,
        )

    worker.assert_not_called()
    compute.assert_called_once()
    kwargs = compute.call_args.kwargs
    assert kwargs["operation"] == "recopy"
    assert Path(kwargs["destination"]).resolve() == dest.resolve()
    assert isinstance(kwargs["answers"], dict)
    assert kwargs["answers"].get("project_name") == "Demo"
    assert result["operation"] == "recopy"
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
    fake_diff = SimpleNamespace(
        to_dict=lambda: {"operation": "recopy", "files": [], "summary": {}}
    )

    with (
        patch(
            "riso.cli.commands.recopy.compute_diff", return_value=fake_diff
        ) as compute,
        patch("riso.cli.commands.recopy.template_run_recopy") as worker,
    ):
        run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Demo"],
            dry_run=True,
        )

    worker.assert_not_called()
    answers = compute.call_args.kwargs["answers"]
    assert answers["api_languages"] == ["python"]
    assert "api_language" not in answers


def test_recopy_live_writes_remapped_dest_answers(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    dest = tmp_path / "proj"
    dest.mkdir()
    answers = dest / ".copier-answers.yml"
    answers.write_text("project_name: Demo\napi_language: python\n", encoding="utf-8")
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    with patch(
        "riso.cli.commands.recopy.template_run_recopy",
        return_value=fake_result,
    ):
        run_recopy(
            config,
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Demo"],
            dry_run=False,
        )

    written = yaml.safe_load(answers.read_text(encoding="utf-8"))
    assert written["api_languages"] == ["python"]
    assert "api_language" not in written


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
