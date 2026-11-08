"""Canonical removed Copier answer keys (package SSOT for CLI/wheel installs)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

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

_TOKEN_SPLIT = re.compile(r"[\s,+/|]+")

_API_LANGUAGES = frozenset({"python", "node", "rust", "go"})
_MCP_LANGUAGES = frozenset({"python", "typescript", "rust", "go"})
_MCP_ALIASES = {"node": "typescript", "js": "typescript"}
_API_TRACK_ALIASES = {
    "python": "python",
    "node": "node",
    "rust": "rust",
    "go": "go",
    "fastapi": "python",
    "fastify": "node",
    "actix": "rust",
}
_API_TRACKS_OFF = frozenset({"", "none", "disabled", "[]"})
_DOCS_SITE_OFF = frozenset({"none", "false", "disabled", "off"})
_DOCS_SITE_FRAMEWORKS = {
    "sphinx": "sphinx-shibuya",
    "sphinx-shibuya": "sphinx-shibuya",
    "docusaurus": "docusaurus",
    "fumadocs": "fumadocs",
}
_SPLIT_OFF = frozenset({"none", "disabled", "false", "off"})
_SAAS_AUTH_PROVIDERS = frozenset({"clerk", "authjs"})
_SAAS_BILLING_PROVIDERS = frozenset({"stripe", "paddle", "lemonsqueezy"})
_MODULE_ON = frozenset({"enabled", "true", "yes", "on", "1"})
_MODULE_OFF = frozenset({"disabled", "false", "no", "off", "0", "none"})
_BOOL_TRUE = frozenset({"true", "yes", "on", "1", "enabled"})
_BOOL_FALSE = frozenset({"false", "no", "off", "0", "disabled", "none", ""})


@dataclass(frozen=True)
class RemapOp:
    """One remap-table row, or one applied operation when before/after are set."""

    old: str
    new_keys: tuple[str, ...]
    action: str
    before: Any = None
    after: Any = None


@dataclass(frozen=True)
class RemapResult:
    """Outcome of applying known removed-key remaps."""

    answers: dict[str, Any]
    ops: tuple[RemapOp, ...]


ANSWER_KEY_REMAPS: dict[str, RemapOp] = {
    "api_tracks": RemapOp(
        old="api_tracks",
        new_keys=("api_module", "api_languages"),
        action="derive",
    ),
    "api_language": RemapOp(
        old="api_language",
        new_keys=("api_languages",),
        action="wrap-list",
    ),
    "docs_site": RemapOp(
        old="docs_site",
        new_keys=("docs_module", "docs_framework"),
        action="derive",
    ),
    "mcp_language": RemapOp(
        old="mcp_language",
        new_keys=("mcp_languages",),
        action="wrap-list",
    ),
    "saas_starter_module": RemapOp(
        old="saas_starter_module",
        new_keys=("saas_infra_module",),
        action="rename",
    ),
    "saas_auth": RemapOp(
        old="saas_auth",
        new_keys=("saas_auth_module", "saas_auth_provider"),
        action="split",
    ),
    "saas_billing": RemapOp(
        old="saas_billing",
        new_keys=("saas_billing_module", "saas_billing_provider"),
        action="split",
    ),
    "include_admin": RemapOp(
        old="include_admin",
        new_keys=("saas_admin_dashboard",),
        action="rename-bool",
    ),
}


def _norm_token(value: Any) -> str:
    return str(value).strip().lower()


def _is_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, frozenset))


def _tokens(value: Any) -> list[str]:
    if value is None:
        return []
    if _is_sequence(value):
        return [_norm_token(item) for item in value if _norm_token(item)]
    text = str(value).strip()
    if not text:
        return []
    return [part for part in _TOKEN_SPLIT.split(text.lower()) if part]


def _wrap_list(
    value: Any,
    allowed: frozenset[str],
    aliases: Mapping[str, str] | None = None,
) -> list[str] | None:
    alias_map = dict(aliases or {})
    if _is_sequence(value):
        out: list[str] = []
        seen: set[str] = set()
        for item in value:
            raw = str(item).strip()
            if not raw:
                continue
            mapped = alias_map.get(raw.lower(), raw.lower())
            if mapped not in allowed:
                return None
            if mapped in seen:
                continue
            seen.add(mapped)
            out.append(mapped)
        return out
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        mapped = alias_map.get(raw.lower(), raw.lower())
        if mapped not in allowed:
            return None
        return [mapped]
    return None


def _module_toggle(value: Any) -> str | None:
    if isinstance(value, bool):
        return "enabled" if value else "disabled"
    if (
        isinstance(value, (int, float))
        and value in {0, 1}
        and not isinstance(value, bool)
    ):
        return "enabled" if value == 1 else "disabled"
    text = _norm_token(value)
    if text in _MODULE_ON:
        return "enabled"
    if text in _MODULE_OFF:
        return "disabled"
    return None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in _BOOL_TRUE:
            return True
        if text in _BOOL_FALSE:
            return False
    return None


def _is_off(value: Any, off_tokens: frozenset[str]) -> bool:
    if value is None:
        return True
    if _is_sequence(value) and len(value) == 0:
        return True
    if isinstance(value, bool):
        return (not value) and "false" in off_tokens
    return _norm_token(value) in off_tokens


def _map_api_language(value: Any) -> dict[str, Any] | None:
    wrapped = _wrap_list(value, _API_LANGUAGES)
    if wrapped is None:
        return None
    return {"api_languages": wrapped}


def _map_mcp_language(value: Any) -> dict[str, Any] | None:
    wrapped = _wrap_list(value, _MCP_LANGUAGES, _MCP_ALIASES)
    if wrapped is None:
        return None
    return {"mcp_languages": wrapped}


def _map_api_tracks(value: Any) -> dict[str, Any] | None:
    if _is_off(value, _API_TRACKS_OFF):
        return {"api_module": "disabled"}
    langs: list[str] = []
    seen: set[str] = set()
    for token in _tokens(value):
        mapped = _API_TRACK_ALIASES.get(token)
        if mapped is None or mapped in seen:
            continue
        seen.add(mapped)
        langs.append(mapped)
    if not langs:
        return None
    return {"api_module": "enabled", "api_languages": langs}


def _map_docs_site(value: Any) -> dict[str, Any] | None:
    if _is_off(value, _DOCS_SITE_OFF):
        return {"docs_module": "disabled"}
    if _is_sequence(value):
        return None
    framework = _DOCS_SITE_FRAMEWORKS.get(_norm_token(value))
    if framework is None:
        return None
    return {"docs_module": "enabled", "docs_framework": framework}


def _map_saas_starter_module(value: Any) -> dict[str, Any] | None:
    toggle = _module_toggle(value)
    if toggle is None:
        return None
    return {"saas_infra_module": toggle}


def _map_split(
    value: Any,
    *,
    module_key: str,
    provider_key: str,
    providers: frozenset[str],
) -> dict[str, Any] | None:
    if _is_off(value, _SPLIT_OFF):
        return {module_key: "disabled"}
    if _is_sequence(value):
        return None
    provider = _norm_token(value)
    if provider not in providers:
        return None
    return {module_key: "enabled", provider_key: provider}


def _map_saas_auth(value: Any) -> dict[str, Any] | None:
    return _map_split(
        value,
        module_key="saas_auth_module",
        provider_key="saas_auth_provider",
        providers=_SAAS_AUTH_PROVIDERS,
    )


def _map_saas_billing(value: Any) -> dict[str, Any] | None:
    return _map_split(
        value,
        module_key="saas_billing_module",
        provider_key="saas_billing_provider",
        providers=_SAAS_BILLING_PROVIDERS,
    )


def _map_include_admin(value: Any) -> dict[str, Any] | None:
    flag = _as_bool(value)
    if flag is None:
        return None
    return {"saas_admin_dashboard": flag}


_DEST_MAPPERS = {
    "api_tracks": _map_api_tracks,
    "api_language": _map_api_language,
    "docs_site": _map_docs_site,
    "mcp_language": _map_mcp_language,
    "saas_starter_module": _map_saas_starter_module,
    "saas_auth": _map_saas_auth,
    "saas_billing": _map_saas_billing,
    "include_admin": _map_include_admin,
}


def _write_dests(out: dict[str, Any], dests: Mapping[str, Any]) -> dict[str, Any]:
    after: dict[str, Any] = {}
    for key, value in dests.items():
        if key not in out:
            out[key] = value
        after[key] = out[key]
    return after


def apply_removed_key_remaps(answers: Mapping[str, Any]) -> RemapResult:
    """Apply known removed-key remaps. Leave unmapped leftovers for reject."""
    out = dict(answers)
    ops: list[RemapOp] = []
    for old, spec in ANSWER_KEY_REMAPS.items():
        if old not in out:
            continue
        before = out[old]
        dests = _DEST_MAPPERS[old](before)
        if dests is None:
            continue
        after = _write_dests(out, dests)
        del out[old]
        ops.append(
            RemapOp(
                old=old,
                new_keys=spec.new_keys,
                action=spec.action,
                before=before,
                after=after,
            )
        )
    return RemapResult(answers=out, ops=tuple(ops))


__all__ = [
    "ANSWER_KEY_REMAPS",
    "REMOVED_ANSWER_KEYS",
    "RemapOp",
    "RemapResult",
    "apply_removed_key_remaps",
]
