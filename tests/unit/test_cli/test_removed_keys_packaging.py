"""Packaging tests: removed keys must work without checkout scripts/ on path."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from riso.core.removed_answer_keys import (
    ANSWER_KEY_REMAPS as CORE_REMAPS,
)
from riso.core.removed_answer_keys import (
    REMOVED_ANSWER_KEYS as CORE_KEYS,
)
from riso.core.removed_answer_keys import (
    apply_removed_key_remaps as core_apply,
)

# TS three-way key+op parity is WEB-T01 / PL-T10 — this file covers core ↔ scripts.lib.

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS = _REPO_ROOT / "scripts"
_LIB_FILE = _SCRIPTS / "lib" / "removed_answer_keys.py"
_LIB_MODULE_NAMES = ("lib", "lib.removed_answer_keys", "lib.smoke_schema")

_PARITY_CASES: list[dict[str, Any]] = [
    {"api_language": "python"},
    {"api_language": ["node", "go"]},
    {"mcp_language": "node"},
    {"mcp_language": "js"},
    {"mcp_language": ["node", "go"]},
    {"api_tracks": "none"},
    {"api_tracks": "python+node"},
    {"api_tracks": "fastapi"},
    {"api_tracks": []},
    {"docs_site": "off"},
    {"docs_site": "sphinx"},
    {"docs_site": "docusaurus"},
    {"saas_starter_module": "enabled"},
    {"saas_starter_module": False},
    {"saas_auth": "none"},
    {"saas_auth": "clerk"},
    {"saas_auth": "firebase"},
    {"saas_billing": "stripe"},
    {"saas_billing": "off"},
    {"include_admin": True},
    {"include_admin": "false"},
    {"include_admin": 1},
    {"api_language": "python", "api_languages": ["go"]},
    {
        "saas_auth": "authjs",
        "saas_auth_module": "disabled",
        "saas_auth_provider": "clerk",
    },
    {
        "api_tracks": "node",
        "api_module": "disabled",
        "api_languages": ["rust"],
    },
    {
        "api_tracks": "python+go",
        "mcp_language": "js",
        "docs_site": "docusaurus",
        "saas_starter_module": "enabled",
        "saas_auth": "authjs",
        "saas_billing": "lemonsqueezy",
        "include_admin": False,
    },
]


def _ops_payload(ops: Any) -> list[dict[str, Any]]:
    return [
        {
            "old": op.old,
            "new_keys": tuple(op.new_keys),
            "action": op.action,
            "before": op.before,
            "after": op.after,
        }
        for op in ops
    ]


def _remap_table_payload(table: Any) -> dict[str, tuple[str, tuple[str, ...], str]]:
    return {
        key: (spec.old, tuple(spec.new_keys), spec.action)
        for key, spec in table.items()
    }


@contextmanager
def _scripts_on_path() -> Iterator[None]:
    inserted = False
    if str(_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_SCRIPTS))
        inserted = True
    saved = {name: sys.modules.get(name) for name in _LIB_MODULE_NAMES}
    try:
        for name in list(saved):
            sys.modules.pop(name, None)
        yield
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
        if inserted and str(_SCRIPTS) in sys.path:
            sys.path.remove(str(_SCRIPTS))


def _import_scripts_lib() -> ModuleType:
    with _scripts_on_path():
        return importlib.import_module("lib.removed_answer_keys")


def _import_scripts_lib_fallback() -> ModuleType:
    """Load scripts/lib twin as if ``riso.core.removed_answer_keys`` is missing."""
    blocked = "riso.core.removed_answer_keys"
    saved = sys.modules.get(blocked)
    sys.modules[blocked] = None  # type: ignore[assignment]
    module_name = "lib.removed_answer_keys_fallback_probe"
    sys.modules.pop(module_name, None)
    try:
        spec = importlib.util.spec_from_file_location(module_name, _LIB_FILE)
        assert spec is not None
        assert spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.modules.pop(module_name, None)
        if saved is None:
            sys.modules.pop(blocked, None)
        else:
            sys.modules[blocked] = saved


def test_core_removed_keys_import_without_scripts_on_path() -> None:
    """Wheel-style import must not require repo scripts/ on sys.path."""
    from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS as core_keys
    from riso.core.answers import REMOVED_ANSWER_KEYS as answers_keys

    assert len(core_keys) == 8
    assert answers_keys == core_keys
    assert "api_tracks" in core_keys


def test_scripts_lib_reexport_matches_core() -> None:
    """scripts/lib re-export must match package SSOT when riso is importable."""
    mod = _import_scripts_lib()
    assert dict(mod.REMOVED_ANSWER_KEYS) == dict(CORE_KEYS)
    assert _remap_table_payload(mod.ANSWER_KEY_REMAPS) == _remap_table_payload(
        CORE_REMAPS
    )


def test_scripts_lib_prefers_packaged_import() -> None:
    """When riso is importable, public names are the packaged objects."""
    from riso.core import removed_answer_keys as core

    mod = _import_scripts_lib()
    assert mod.REMOVED_ANSWER_KEYS is core.REMOVED_ANSWER_KEYS
    assert mod.ANSWER_KEY_REMAPS is core.ANSWER_KEY_REMAPS
    assert mod.apply_removed_key_remaps is core.apply_removed_key_remaps
    assert mod.RemapOp is core.RemapOp
    assert mod.RemapResult is core.RemapResult
    assert mod.apply_removed_key_remaps is not mod._fallback_apply_removed_key_remaps


def test_fallback_keys_match_core() -> None:
    mod = _import_scripts_lib()
    assert dict(mod._FALLBACK_REMOVED_ANSWER_KEYS) == dict(CORE_KEYS)
    assert set(mod._FALLBACK_REMOVED_ANSWER_KEYS) == set(CORE_KEYS)
    assert len(mod._FALLBACK_REMOVED_ANSWER_KEYS) == 8


def test_fallback_remap_table_matches_core() -> None:
    mod = _import_scripts_lib()
    assert _remap_table_payload(
        mod._FALLBACK_ANSWER_KEY_REMAPS
    ) == _remap_table_payload(CORE_REMAPS)
    assert set(mod._FALLBACK_ANSWER_KEY_REMAPS) == set(CORE_KEYS)


def _case_id(case: dict[str, Any]) -> str:
    return "|".join(f"{key}={case[key]!r}" for key in sorted(case))


@pytest.mark.parametrize("answers", _PARITY_CASES, ids=_case_id)
def test_fallback_apply_matches_core(answers: dict[str, Any]) -> None:
    mod = _import_scripts_lib()
    original = dict(answers)
    core = core_apply(answers)
    fallback = mod._fallback_apply_removed_key_remaps(answers)
    assert answers == original
    assert fallback.answers == core.answers
    assert _ops_payload(fallback.ops) == _ops_payload(core.ops)


def test_fallback_apply_idempotent_matches_core() -> None:
    mod = _import_scripts_lib()
    first_core = core_apply({"api_language": "python", "mcp_language": "node"})
    first_fb = mod._fallback_apply_removed_key_remaps(
        {"api_language": "python", "mcp_language": "node"}
    )
    assert first_fb.answers == first_core.answers
    second_core = core_apply(first_core.answers)
    second_fb = mod._fallback_apply_removed_key_remaps(first_fb.answers)
    assert second_core.ops == ()
    assert second_fb.ops == ()
    assert second_fb.answers == second_core.answers == first_core.answers


def test_importerror_fallback_binds_local_twin() -> None:
    """Hooks without the wheel bind the local remaps + apply."""
    mod = _import_scripts_lib_fallback()
    assert dict(mod.REMOVED_ANSWER_KEYS) == dict(CORE_KEYS)
    assert _remap_table_payload(mod.ANSWER_KEY_REMAPS) == _remap_table_payload(
        CORE_REMAPS
    )
    assert mod.REMOVED_ANSWER_KEYS is mod._FALLBACK_REMOVED_ANSWER_KEYS
    assert mod.ANSWER_KEY_REMAPS is mod._FALLBACK_ANSWER_KEY_REMAPS
    assert mod.apply_removed_key_remaps is mod._fallback_apply_removed_key_remaps
    assert mod.RemapOp is mod._FallbackRemapOp
    assert mod.RemapResult is mod._FallbackRemapResult
    leftover = {"saas_auth": "firebase"}
    result = mod.apply_removed_key_remaps(leftover)
    assert result.answers == leftover
    assert result.ops == ()
