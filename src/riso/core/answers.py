"""Answer validation helpers for CLI and template operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from riso.core.errors import ValidationFailedError
from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS

__all__ = [
    "REMOVED_ANSWER_KEYS",
    "load_answers_file",
    "prepare_copier_data",
    "reject_removed_answer_keys",
]


def load_answers_file(path: Path) -> dict[str, Any]:
    """Load a YAML mapping of Copier answers (fail-closed on corruption).

    Raises:
        FileNotFoundError: if path does not exist.
        ValidationFailedError: on I/O, encoding, YAML parse, or non-mapping roots.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ValidationFailedError(
            ["PyYAML is required to load answers files"]
        ) from exc

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except (OSError, UnicodeError) as exc:
        raise ValidationFailedError([f"Cannot read answers file: {exc}"]) from exc
    except yaml.YAMLError as exc:
        raise ValidationFailedError([f"Invalid answers YAML: {exc}"]) from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationFailedError([f"Answers file must be a mapping: {path}"])
    return data


def prepare_copier_data(answers: dict[str, Any]) -> dict[str, Any]:
    """Strip values Copier cannot consume (e.g. empty list defaults)."""
    return {
        key: value
        for key, value in answers.items()
        if not (isinstance(value, list) and len(value) == 0)
    }


def reject_removed_answer_keys(answers: dict[str, Any]) -> None:
    """Reject answer keys removed from the public template surface."""
    errors = [
        f"{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}"
        for key in sorted(set(answers) & set(REMOVED_ANSWER_KEYS))
    ]
    if errors:
        raise ValidationFailedError(errors)
