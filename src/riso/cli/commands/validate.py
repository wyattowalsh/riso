"""Validate command — check template answers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.cli.helpers import resolve_answers
from riso.core.errors import ValidationFailedError
from riso.core.generation_gates import validate_answers_for_generation
from riso.template import validate_answers

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_validate(
    config: CliConfig,
    *,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    strict: bool = True,
    schema_only: bool = False,
) -> dict:
    """Validate answers after remaps.

    Default runs Copier prompt-schema validation and generation combo
    gates. Pass ``schema_only=True`` to skip generation gates.
    """
    if answers_file or data_pairs:
        answers = resolve_answers(
            answers_file=answers_file,
            data_pairs=data_pairs,
            template_path=config.template_path,
        )
    elif answers_file is None and not data_pairs:
        raise ValueError("Provide --answers-file and/or --data key=value")

    schema = validate_answers(answers, config.template_path)
    if schema_only:
        if strict and not schema.valid:
            raise ValidationFailedError(schema.errors)
        return schema.to_dict()

    gate = validate_answers_for_generation(answers)
    errors = list(schema.errors) + list(gate.errors)
    warnings = list(schema.warnings) + list(gate.warnings)
    valid = schema.valid and gate.ok
    payload = {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
    }
    if strict and not valid:
        raise ValidationFailedError(errors)
    return payload
