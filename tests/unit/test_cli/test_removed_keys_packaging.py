"""Packaging tests: removed keys must work without checkout scripts/ on path."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def test_core_removed_keys_import_without_scripts_on_path() -> None:
    """Wheel-style import must not require repo scripts/ on sys.path."""
    from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS as core_keys
    from riso.core.answers import REMOVED_ANSWER_KEYS as answers_keys

    assert len(core_keys) == 8
    assert answers_keys == core_keys
    assert "api_tracks" in core_keys


def test_scripts_lib_reexport_matches_core() -> None:
    """scripts/lib re-export must match package SSOT when riso is importable."""
    from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS as core_keys

    scripts = Path(__file__).resolve().parents[3] / "scripts"
    inserted = False
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
        inserted = True
    # Snapshot modules we may touch so we can restore cleanly.
    saved = {
        name: sys.modules.get(name)
        for name in ("lib", "lib.removed_answer_keys", "lib.smoke_schema")
    }
    try:
        for name in list(saved):
            sys.modules.pop(name, None)
        mod = importlib.import_module("lib.removed_answer_keys")
        assert dict(mod.REMOVED_ANSWER_KEYS) == dict(core_keys)
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
        if inserted and str(scripts) in sys.path:
            sys.path.remove(str(scripts))
