"""Canonical removed Copier answer keys (SSOT for hooks, CLI, and web)."""

from __future__ import annotations

REMOVED_ANSWER_KEYS: dict[str, str] = {
    "api_tracks": "`api_module` plus `api_languages`",
    "api_language": "`api_languages`",
    "docs_site": "`docs_module` plus `docs_framework`",
    "mcp_language": "`mcp_languages`",
    "saas_starter_module": "`saas_infra_module`",
    "saas_auth": "`saas_auth_module` plus `saas_auth_provider`",
    "saas_billing": "`saas_billing_module` plus `saas_billing_provider`",
}

__all__ = ["REMOVED_ANSWER_KEYS"]
