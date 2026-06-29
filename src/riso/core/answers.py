"""Answer validation helpers for CLI and template operations."""

from __future__ import annotations

from typing import Any

from riso.core.errors import ValidationFailedError


def _load_removed_answer_keys() -> dict[str, str]:
    import sys
    from pathlib import Path

    scripts_parent = Path(__file__).resolve().parents[3] / "scripts"
    if str(scripts_parent) not in sys.path:
        sys.path.insert(0, str(scripts_parent))
    from lib.removed_answer_keys import REMOVED_ANSWER_KEYS as keys

    return dict(keys)


REMOVED_ANSWER_KEYS: dict[str, str] = _load_removed_answer_keys()


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
