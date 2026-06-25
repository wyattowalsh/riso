"""Shared helpers for CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from riso.core.answers import prepare_copier_data, reject_removed_answer_keys
from riso.core.errors import ValidationFailedError
from riso.template import (
    get_defaults,
    load_copier_config,
    merge_answers_with_defaults,
    validate_answers,
)


def load_answers_file(path: Path) -> dict[str, Any]:
    """Load answers from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Answers file must be a mapping: {path}")
    return data


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
    """Coerce string values to bool/int/float when obvious."""
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
    reject_removed_answer_keys(provided)

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
    return prepare_copier_data(merged)


def validate_and_raise(
    answers: dict[str, Any],
    template_path: Path,
) -> dict[str, Any]:
    """Validate answers and return result dict; raise on failure."""
    reject_removed_answer_keys(answers)
    result = validate_answers(answers, template_path)
    if not result.valid:
        raise ValidationFailedError(result.errors)
    return result.to_dict()
