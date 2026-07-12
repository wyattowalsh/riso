"""Canonical removed Copier answer keys (SSOT for hooks, CLI, and web).

Prefer the packaged SSOT under ``riso.core.removed_answer_keys`` when the
``riso`` package is importable (installed wheel / editable install). Fall back
to an identical local dict so template hooks that only put ``scripts/`` on
``sys.path`` keep working.
"""

from __future__ import annotations

try:
    from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS
except ImportError:  # pragma: no cover - hooks without installed package
    REMOVED_ANSWER_KEYS = {
        "api_tracks": "`api_module` plus `api_languages`",
        "api_language": "`api_languages`",
        "docs_site": "`docs_module` plus `docs_framework`",
        "mcp_language": "`mcp_languages`",
        "saas_starter_module": "`saas_infra_module`",
        "saas_auth": "`saas_auth_module` plus `saas_auth_provider`",
        "saas_billing": "`saas_billing_module` plus `saas_billing_provider`",
        "include_admin": "`saas_admin_dashboard`",
    }

__all__ = ["REMOVED_ANSWER_KEYS"]
