"""Tests for validate command (shipped run_validate entrypoint)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path

import pytest

from riso.cli.commands.validate import run_validate
from riso.cli.config import CliConfig
from riso.core.errors import ValidationFailedError
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit


def test_validate_requires_answers_file_or_data() -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    with pytest.raises(ValueError, match="answers-file"):
        run_validate(config, answers_file=None, data_pairs=None)


def test_validate_accepts_data_pairs_for_minimal_project() -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    result = run_validate(
        config,
        answers_file=None,
        data_pairs=["project_name=Demo App"],
        strict=False,
    )
    assert "valid" in result
    assert isinstance(result.get("errors"), list)
    assert isinstance(result.get("warnings"), list)


def test_validate_rejects_removed_answer_keys(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    answers = tmp_path / "answers.yml"
    answers.write_text("project_name: Demo\napi_tracks: python\n", encoding="utf-8")

    with pytest.raises(ValidationFailedError):
        run_validate(config, answers_file=answers, data_pairs=None, strict=True)


def test_validate_strict_false_returns_invalid_payload_without_raise(
    tmp_path: Path,
) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    answers = tmp_path / "answers.yml"
    answers.write_text("project_name: \n", encoding="utf-8")

    result = run_validate(
        config,
        answers_file=answers,
        data_pairs=None,
        strict=False,
    )
    assert "valid" in result
