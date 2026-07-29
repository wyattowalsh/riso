"""Ensure hooks.workflow_validator imports when only scripts/ is on sys.path.

post_gen_project.py appends ``<repo>/scripts`` then imports
``hooks.workflow_validator``. A brittle logger import previously raised
ModuleNotFoundError and disabled all hook tooling for sample renders.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "scripts"


@pytest.mark.unit
def test_workflow_validator_imports_with_scripts_on_path_only() -> None:
    """Import succeeds with scripts/ on path (no repo root required)."""
    # Drop repo-root entries so we exercise the post_gen layout.
    cleaned = [
        p
        for p in sys.path
        if Path(p).resolve() not in {REPO.resolve(), (REPO / "src").resolve()}
    ]
    scripts_s = str(SCRIPTS.resolve())
    if scripts_s not in cleaned:
        cleaned.append(scripts_s)

    # Remove cached modules that may have been imported under a different layout.
    for name in list(sys.modules):
        if (
            name == "hooks"
            or name.startswith("hooks.")
            or name
            in {
                "logger",
                "lib",
                "lib.logger",
                "scripts.lib.logger",
                "scripts.lib",
                "scripts",
            }
        ):
            del sys.modules[name]

    old_path = sys.path[:]
    try:
        sys.path[:] = cleaned
        mod = importlib.import_module("hooks.workflow_validator")
        assert hasattr(mod, "validate_workflows_directory")
        assert hasattr(mod, "logger")
    finally:
        sys.path[:] = old_path
