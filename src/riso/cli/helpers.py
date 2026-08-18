"""Shared helpers for CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from riso.core.answers import (
    apply_then_reject_removed_keys,
    load_answers_file,
    prepare_copier_data,
)
from riso.core.errors import ValidationFailedError
from riso.core.generation_gates import validate_answers_for_generation
from riso.template import (
    get_defaults,
    load_copier_config,
    merge_answers_with_defaults,
    validate_answers,
)

# Re-export SSOT loader for CLI callers/tests.
__all__ = [
    "load_answers_file",
    "parse_data_pairs",
    "resolve_answers",
    "validate_and_raise",
]


def parse_data_pairs(data: list[str] | None) -> dict[str, Any]:
    """Parse key=value pairs from CLI --data flags."""
    result: dict[str, Any] = {}
    if not data:
        return result
    for pair in data:
        if "=" not in pair:
            raise ValueError(f"Invalid --data pair (expected key=value): {pair}")
        key, _, value = pair.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid --data pair (empty key): {pair}")
        result[key] = _coerce_value(value)
    return result


def _coerce_value(value: str) -> Any:
    """Coerce string values to list/dict (YAML) or bool/int/float when obvious."""
    try:
        parsed = yaml.safe_load(value)
    except yaml.YAMLError:
        parsed = None
    else:
        if isinstance(parsed, (list, dict)):
            return parsed
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


def resolve_answers(
    *,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    template_path: Path,
) -> dict[str, Any]:
    """Merge answers file and --data pairs with template defaults."""
    provided: dict[str, Any] = {}
    if answers_file:
        provided.update(load_answers_file(answers_file))
    provided.update(parse_data_pairs(data_pairs))
    provided = apply_then_reject_removed_keys(provided).answers

    copier_config = load_copier_config(template_path)
    defaults = get_defaults(template_path)
    project_name = provided.get(
        "project_name", defaults.get("project_name", "riso-project")
    )
    merged = merge_answers_with_defaults(
        project_name=str(project_name),
        config=copier_config,
        provided_answers=provided,
    )
    # Defaults can reintroduce removed keys after the provided-only remap.
    remapped = apply_then_reject_removed_keys(merged).answers
    return prepare_copier_data(remapped)


def validate_and_raise(
    answers: dict[str, Any],
    template_path: Path,
) -> dict[str, Any]:
    """Validate answers and return result dict; raise on failure."""
    remapped = apply_then_reject_removed_keys(answers).answers
    answers.clear()
    answers.update(remapped)
    result = validate_answers(answers, template_path)
    gate = validate_answers_for_generation(answers)
    errors = list(result.errors) + list(gate.errors)
    if errors:
        raise ValidationFailedError(errors)
    payload = result.to_dict()
    payload["errors"] = errors
    payload["warnings"] = list(result.warnings) + list(gate.warnings)
    payload["valid"] = True
    return payload
