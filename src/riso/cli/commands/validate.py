"""Validate command — check template answers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.cli.helpers import resolve_answers
from riso.core.errors import ValidationFailedError
from riso.template import validate_answers

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_validate(
    config: CliConfig,
    *,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    strict: bool = True,
) -> dict:
    """Validate answers against template schema."""
    if answers_file or data_pairs:
        answers = resolve_answers(
            answers_file=answers_file,
            data_pairs=data_pairs,
            template_path=config.template_path,
        )
    elif answers_file is None and not data_pairs:
        raise ValueError("Provide --answers-file and/or --data key=value")

    result = validate_answers(answers, config.template_path)
    if strict and not result.valid:
        raise ValidationFailedError(result.errors)
    return result.to_dict()
