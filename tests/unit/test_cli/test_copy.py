"""Tests for copy command remap-then-Copier behavior."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from riso.cli.commands.copy import run_copy
from riso.cli.config import CliConfig
from riso.core.errors import ValidationFailedError
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "remap"


def _config() -> CliConfig:
    return CliConfig.from_options(template_path=resolve_template_path())


def test_copy_remaps_data_pairs_before_worker(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    with patch(
        "riso.cli.commands.copy.run_generator",
        return_value=fake_result,
    ) as worker:
        run_copy(
            _config(),
            destination=str(dest),
            answers_file=None,
            data_pairs=["project_name=Demo", "api_tracks=python"],
        )

    worker.assert_called_once()
    data = worker.call_args.kwargs["data"]
    assert data["api_module"] == "enabled"
    assert data["api_languages"] == ["python"]
    assert "api_tracks" not in data


def test_copy_remaps_answers_file_before_worker(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    answers = tmp_path / "answers.yml"
    answers.write_text((FIXTURE_DIR / "api_tracks.yml").read_text(encoding="utf-8"))
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    with patch(
        "riso.cli.commands.copy.run_generator",
        return_value=fake_result,
    ) as worker:
        run_copy(
            _config(),
            destination=str(dest),
            answers_file=answers,
            data_pairs=None,
        )

    worker.assert_called_once()
    data = worker.call_args.kwargs["data"]
    assert data["api_module"] == "enabled"
    assert data["api_languages"] == ["python", "node"]
    assert "api_tracks" not in data


def test_copy_rejects_leftover_saas_auth_without_worker(tmp_path: Path) -> None:
    """Fail-closed leftover (unmapped saas_auth), not remappable api_tracks."""
    dest = tmp_path / "out"

    with patch("riso.cli.commands.copy.run_generator") as worker:
        with pytest.raises(ValidationFailedError) as exc:
            run_copy(
                _config(),
                destination=str(dest),
                answers_file=None,
                data_pairs=["saas_auth=firebase"],
            )

    worker.assert_not_called()
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_copy_does_not_overwrite_dest_already_set(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    fake_result = SimpleNamespace(
        to_dict=lambda: {"success": True, "destination": str(dest)}
    )

    with patch(
        "riso.cli.commands.copy.run_generator",
        return_value=fake_result,
    ) as worker:
        run_copy(
            _config(),
            destination=str(dest),
            answers_file=None,
            data_pairs=[
                "project_name=Demo",
                "api_language=python",
                "api_languages=[go]",
            ],
        )

    worker.assert_called_once()
    data = worker.call_args.kwargs["data"]
    assert data["api_languages"] == ["go"]
    assert "api_language" not in data
