"""Answer validation helpers for CLI and template operations."""

from __future__ import annotations

from typing import Any

from riso.core.errors import ValidationFailedError

REMOVED_ANSWER_KEYS: dict[str, str] = {
    "api_tracks": "`api_module` plus `api_languages`",
    "api_language": "`api_languages`",
    "docs_site": "`docs_module` plus `docs_framework`",
    "mcp_language": "`mcp_languages`",
    "saas_starter_module": "`saas_infra_module`",
    "saas_auth": "`saas_auth_module` plus `saas_auth_provider`",
    "saas_billing": "`saas_billing_module` plus `saas_billing_provider`",
}


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
