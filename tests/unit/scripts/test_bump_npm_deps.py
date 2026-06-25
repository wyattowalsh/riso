"""Tests for template npm dependency bump automation."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BUMP_SCRIPT = REPO_ROOT / "scripts" / "ci" / "bump_template_npm_deps.py"
SURFACES_CONFIG = REPO_ROOT / "scripts" / "ci" / "npm_surfaces.json"


def _load_bump_module():
    spec = importlib.util.spec_from_file_location("bump_template_npm_deps", BUMP_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_npm_surfaces_config_loads() -> None:
    data = json.loads(SURFACES_CONFIG.read_text(encoding="utf-8"))
    names = {surface["name"] for surface in data["surfaces"]}
    assert "docs-fumadocs" in names
    assert "node-saas" in names
    assert "node-mcp-ts" in names
    assert "eslint" in data["ncu_reject"]


def test_bump_script_imports_surfaces() -> None:
    module = _load_bump_module()
    assert len(module.SURFACES) >= 7
    saas = next(surface for surface in module.SURFACES if surface.name == "node-saas")
    assert saas.sample_variant == "rag-enabled"
    assert saas.package_relpath == "node/saas/package.json"


@pytest.mark.parametrize(
    "output",
    [
        "All dependencies match the latest package versions :)",
        "No package versions to upgrade",
    ],
)
def test_ncu_up_to_date_detection(output: str, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_bump_module()

    class _Surface:
        name = "test"
        sample_variant = "default"
        package_relpath = "package.json"
        template_jinja = "template/files/package.json.jinja"

    def fake_run_ncu(_package_dir: Path, *, apply: bool) -> tuple[int, str]:
        return 0, output

    monkeypatch.setattr(module, "run_ncu", fake_run_ncu)

    _name, ok, _err = module.process_surface(_Surface(), apply=False, skip_render=True)
    assert ok is True
