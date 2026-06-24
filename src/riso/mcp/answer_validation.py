"""Answer validation helpers for MCP entrypoints."""

from __future__ import annotations

from typing import Any

from .errors import ValidationFailedError


REMOVED_ANSWER_KEYS: dict[str, str] = {
    "api_tracks": "`api_module` plus `api_languages`",
    "api_language": "`api_languages`",
    "docs_site": "`docs_module` plus `docs_framework`",
    "mcp_language": "`mcp_languages`",
    "saas_starter_module": "`saas_infra_module`",
}


def reject_removed_answer_keys(answers: dict[str, Any]) -> None:
    """Reject answer keys removed from the public MCP/template surface."""
    errors = [
        f"{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}"
        for key in sorted(set(answers) & set(REMOVED_ANSWER_KEYS))
    ]
    if errors:
        raise ValidationFailedError(errors)
