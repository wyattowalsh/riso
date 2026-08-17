"""Answer validation helpers for CLI and template operations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from riso.core.errors import ValidationFailedError
from riso.core.removed_answer_keys import (
    REMOVED_ANSWER_KEYS,
    RemapOp,
    RemapResult,
    apply_removed_key_remaps,
)

__all__ = [
    "REMOVED_ANSWER_KEYS",
    "apply_then_reject_removed_keys",
    "dump_answers_file",
    "load_answers_file",
    "prepare_copier_data",
    "reject_removed_answer_keys",
    "remap_answers_file",
    "serialize_remap_ops",
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


def reject_removed_answer_keys(answers: Mapping[str, Any]) -> None:
    """Reject leftover removed keys after remaps have been applied."""
    errors = [
        f"{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}"
        for key in sorted(set(answers) & set(REMOVED_ANSWER_KEYS))
    ]
    if errors:
        raise ValidationFailedError(errors)


def apply_then_reject_removed_keys(answers: Mapping[str, Any]) -> RemapResult:
    """Apply known remaps, then fail closed on leftover removed keys."""
    result = apply_removed_key_remaps(answers)
    reject_removed_answer_keys(result.answers)
    return result


def serialize_remap_ops(ops: Sequence[RemapOp]) -> list[dict[str, Any]]:
    """JSON-safe preview rows for remap operations."""
    return [
        {
            "old": op.old,
            "new_keys": list(op.new_keys),
            "action": op.action,
            "before": op.before,
            "after": op.after,
        }
        for op in ops
    ]


def dump_answers_file(path: Path, answers: Mapping[str, Any]) -> None:
    """Write a Copier answers mapping as YAML."""
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ValidationFailedError(
            ["PyYAML is required to write answers files"]
        ) from exc

    text = yaml.safe_dump(
        dict(answers),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise ValidationFailedError([f"Cannot write answers file: {exc}"]) from exc


def remap_answers_file(path: Path, *, write: bool) -> RemapResult:
    """Load, apply remaps, reject leftovers, and optionally rewrite the file."""
    result = apply_then_reject_removed_keys(load_answers_file(path))
    if write and result.ops:
        dump_answers_file(path, result.answers)
    return result
