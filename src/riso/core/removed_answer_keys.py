"""Canonical removed Copier answer keys (package SSOT for CLI/wheel installs)."""

from __future__ import annotations

REMOVED_ANSWER_KEYS: dict[str, str] = {
    "api_tracks": "`api_module` plus `api_languages`",
    "api_language": "`api_languages`",
    "docs_site": "`docs_module` plus `docs_framework`",
    "mcp_language": "`mcp_languages`",
    "saas_starter_module": "`saas_infra_module`",
    "saas_auth": "`saas_auth_module` plus `saas_auth_provider`",
    "saas_billing": "`saas_billing_module` plus `saas_billing_provider`",
    "include_admin": "`saas_admin_dashboard`",
    # Note: graphql_api_module / websocket_module remain as *derived* Jinja flags
    # produced by pre_gen normalize_api_feature_modules — not user prompts, but
    # still written into answers context for template excludes. Do not list them
    # as removed user keys or pre_gen self-fails after normalization.
}

__all__ = ["REMOVED_ANSWER_KEYS"]
