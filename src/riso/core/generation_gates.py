"""Shared pre-generation answer gates for CLI and hooks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS


@dataclass(frozen=True)
class GateResult:
    """Outcome of generation answer validation."""

    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


_MODULE_LANGUAGE_PAIRS: tuple[tuple[str, str], ...] = (
    ("cli_module", "cli_languages"),
    ("api_module", "api_languages"),
    ("mcp_module", "mcp_languages"),
    ("docs_module", "docs_languages"),
)


def normalize_api_features(raw: Any) -> frozenset[str]:
    """Normalize api_features to a token set (``none`` / empty → empty set)."""
    if raw is None:
        return frozenset()
    if isinstance(raw, (list, tuple, set, frozenset)):
        tokens = {str(item).strip().lower() for item in raw if str(item).strip()}
    else:
        text = str(raw).strip().lower()
        if not text or text in {"none", "[]"}:
            return frozenset()
        # Support comma-separated or single token; avoid substring false positives
        # by splitting on commas first, else treat whole string as one token.
        if "," in text:
            tokens = {part.strip() for part in text.split(",") if part.strip()}
        else:
            tokens = {text}
    tokens.discard("none")
    return frozenset(tokens)


def _as_enabled(value: Any) -> bool:
    return str(value or "").strip().lower() == "enabled"


def _collect_saas_selected(answers: Mapping[str, Any]) -> list[str]:
    selected: list[str] = []
    for key in (
        "saas_runtime",
        "saas_hosting",
        "saas_database",
        "saas_orm",
        "saas_auth",
        "saas_storage",
        "saas_cicd",
        "saas_auth_provider",
        "saas_billing_provider",
    ):
        value = answers.get(key)
        if value is not None and str(value).strip():
            selected.append(str(value).strip())
    return selected


def _saas_errors(answers: Mapping[str, Any]) -> list[str]:
    if not _as_enabled(answers.get("saas_infra_module")):
        return []

    errors: list[str] = []
    selected = _collect_saas_selected(answers)

    if "neon" in selected and "supabase-storage" in selected:
        errors.append(
            "Cannot use Neon database with Supabase Storage. "
            "Choose full Supabase (database + storage) or Neon + Cloudflare R2."
        )

    if (
        answers.get("saas_realtime") == "supabase-realtime"
        and answers.get("saas_database") != "supabase"
    ):
        errors.append(
            "Supabase Realtime requires saas_database='supabase' "
            "(or choose another realtime provider)."
        )

    return errors


def _language_errors(answers: Mapping[str, Any]) -> list[str]:
    """Error only when languages are explicitly empty/invalid.

    Missing language keys are warnings (defaults may still apply later).
    """
    errors: list[str] = []
    for module_key, languages_key in _MODULE_LANGUAGE_PAIRS:
        if not _as_enabled(answers.get(module_key)):
            continue
        if languages_key not in answers:
            # Absent key: non-blocking (caller may merge defaults).
            continue
        langs = answers.get(languages_key)
        if isinstance(langs, str):
            if not langs.strip() or langs.strip().lower() == "none":
                errors.append(f"{module_key} is enabled but {languages_key} is empty.")
            continue
        if not isinstance(langs, (list, tuple, set)):
            errors.append(
                f"{languages_key} must be a list when {module_key} is enabled."
            )
            continue
        if len(langs) == 0:
            errors.append(
                f"{module_key} is enabled but {languages_key} is empty "
                "(select at least one language)."
            )
    return errors


def _removed_key_errors(answers: Mapping[str, Any]) -> list[str]:
    return [
        f"{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}"
        for key in sorted(set(answers) & set(REMOVED_ANSWER_KEYS))
    ]


def validate_answers_for_generation(answers: Mapping[str, Any]) -> GateResult:
    """Validate answers before project generation / update.

    Returns errors for blocking issues and warnings for non-blocking notices.
    """
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(_removed_key_errors(answers))
    errors.extend(_saas_errors(answers))
    errors.extend(_language_errors(answers))

    # api_features normalize is available for callers; warn on bare substring traps
    # is handled by normalize_api_features used elsewhere.
    _ = normalize_api_features(answers.get("api_features"))

    return GateResult(
        ok=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


__all__ = [
    "GateResult",
    "normalize_api_features",
    "validate_answers_for_generation",
]
