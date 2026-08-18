"""Answer validation helpers for CLI and template operations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from riso.core.errors import ValidationFailedError
from riso.core.generation_gates import normalize_api_features
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
    "normalize_api_feature_modules",
    "persist_remapped_answers",
    "prepare_copier_data",
    "reject_removed_answer_keys",
    "remap_answers_file",
    "serialize_remap_ops",
    "strip_empty_lists_for_copier",
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


def normalize_api_feature_modules(context: Mapping[str, Any]) -> dict[str, Any]:
    """Derive graphql/websocket flags and token-list api_features.

    Explicit ``graphql_api_module`` / ``websocket_module`` answers win when set
    to ``enabled``; otherwise ``api_features`` drives the derived state.
    Rewrites ``api_features`` to a sorted token list so Jinja membership tests
    are token-safe.
    """
    tokens = sorted(normalize_api_features(context.get("api_features")))
    graphql = context.get("graphql_api_module", "disabled")
    websocket = context.get("websocket_module", "disabled")

    if graphql != "enabled" and "graphql" in tokens:
        graphql = "enabled"
    if websocket != "enabled" and "websocket" in tokens:
        websocket = "enabled"

    return {
        "api_features": tokens,
        "graphql_api_module": graphql,
        "websocket_module": websocket,
    }


def prepare_copier_data(answers: dict[str, Any]) -> dict[str, Any]:
    """Normalize API feature flags; keep empty lists for generation gates.

    Call :func:`strip_empty_lists_for_copier` only when sending the mapping
    to Copier.
    """
    prepared = dict(answers)
    if any(
        key in prepared
        for key in ("api_features", "graphql_api_module", "websocket_module")
    ):
        prepared.update(normalize_api_feature_modules(prepared))
    return prepared


def strip_empty_lists_for_copier(answers: Mapping[str, Any]) -> dict[str, Any]:
    """Drop empty list values Copier cannot consume as ``data=`` overrides."""
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


def persist_remapped_answers(path: Path, remapped: Mapping[str, Any]) -> None:
    """Write remaps into dest answers after Copier succeeds.

    Merges *remapped* over the dest file (preserving Copier-managed keys
    such as ``_src_path``) and drops :data:`REMOVED_ANSWER_KEYS`.
    """
    existing: dict[str, Any] = {}
    if path.is_file():
        try:
            existing = load_answers_file(path)
        except ValidationFailedError:
            existing = {}
    merged = {**existing, **dict(remapped)}
    for key in REMOVED_ANSWER_KEYS:
        merged.pop(key, None)
    dump_answers_file(path, merged)
