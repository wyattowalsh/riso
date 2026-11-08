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


_PHANTOM_FRONTEND_VARIANTS = frozenset({"react-vite", "sveltekit", "vue-vite"})


def test_npm_surfaces_config_loads() -> None:
    data = json.loads(SURFACES_CONFIG.read_text(encoding="utf-8"))
    names = {surface["name"] for surface in data["surfaces"]}
    variants = {surface["sample_variant"] for surface in data["surfaces"]}
    assert "docs-fumadocs" in names
    assert "node-saas" in names
    assert "node-mcp-ts" in names
    assert "api-node" in names
    assert names.isdisjoint(_PHANTOM_FRONTEND_VARIANTS)
    assert variants.isdisjoint(_PHANTOM_FRONTEND_VARIANTS)
    assert "eslint" in data["ncu_reject"]


def test_npm_surfaces_have_real_samples_and_jinja() -> None:
    data = json.loads(SURFACES_CONFIG.read_text(encoding="utf-8"))
    samples_root = REPO_ROOT / "samples"
    for surface in data["surfaces"]:
        variant = surface["sample_variant"]
        answers = samples_root / variant / "copier-answers.yml"
        if not answers.exists():
            nested = list(samples_root.glob(f"**/{variant}/copier-answers.yml"))
            answers = nested[0] if nested else answers
        name = surface["name"]
        assert answers.exists(), f"missing sample answers for {name}: {variant}"
        jinja = REPO_ROOT / surface["template_jinja"]
        assert jinja.is_file(), f"missing template jinja for {name}: {jinja}"
        assert "frontend/" not in surface["package_relpath"]
        assert "template/files/frontend/" not in surface["template_jinja"]


def test_frontend_template_tree_removed() -> None:
    assert not (REPO_ROOT / "template" / "files" / "frontend").exists()


def test_bump_script_imports_surfaces() -> None:
    module = _load_bump_module()
    assert len(module.SURFACES) >= 7
    names = {surface.name for surface in module.SURFACES}
    assert "api-node" in names
    assert names.isdisjoint(_PHANTOM_FRONTEND_VARIANTS)
    saas = next(surface for surface in module.SURFACES if surface.name == "node-saas")
    assert saas.sample_variant == "rag-enabled"
    assert saas.package_relpath == "node/saas/package.json"
    api_node = next(
        surface for surface in module.SURFACES if surface.name == "api-node"
    )
    assert api_node.sample_variant == "circleci-node"
    assert api_node.package_relpath == "node/apps/api-node/package.json"
    assert api_node.template_jinja == (
        "template/files/node/apps/api-node/package.json.jinja"
    )


@pytest.mark.parametrize(
    "output",
    [
        "All dependencies match the latest package versions :)",
        "No package versions to upgrade",
    ],
)
def test_ncu_up_to_date_detection(
    output: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_bump_module()
    sample_dir = tmp_path / "samples" / "default"
    sample_dir.mkdir(parents=True)
    (sample_dir / "copier-answers.yml").write_text(
        "project_name: test\n", encoding="utf-8"
    )
    render_dir = sample_dir / "render"
    render_dir.mkdir(parents=True)
    (render_dir / "package.json").write_text(
        '{"name":"test","dependencies":{"lodash":"1.0.0"}}',
        encoding="utf-8",
    )
    template_jinja = tmp_path / "template" / "files" / "package.json.jinja"
    template_jinja.parent.mkdir(parents=True, exist_ok=True)
    template_jinja.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

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
