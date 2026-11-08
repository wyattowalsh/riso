"""Verify desktop payload contracts that must survive Copier generation."""

from __future__ import annotations

import json
import struct
import tomllib
from pathlib import Path

import pytest
import yaml

copier_main = pytest.importorskip("copier._main")

ROOT = Path(__file__).parents[2]
FILES = ROOT / "template" / "files"
DESKTOP = {
    "desktop_module": "enabled",
    "desktop_framework": "tauri",
    "desktop_features": [],
    "desktop_platforms": ["mac", "windows", "linux"],
    "ci_platform": "github-actions",
    "project_name": "Desktop Runtime Test",
    "project_slug": "desktop-runtime-test",
}


@pytest.fixture(name="copier_env")
def _copier_env(tmp_path):
    """Use the same Jinja settings as Copier's installed renderer."""
    with copier_main.Worker(
        src_path=str(ROOT / "template"),
        dst_path=tmp_path / "copier-environment",
        defaults=True,
        quiet=True,
    ) as worker:
        yield worker.jinja_env


@pytest.fixture(name="workflow_source")
def _workflow_source() -> Path:
    """Locate the emitted root workflow rather than a nested desktop copy."""
    matches = list((FILES / ".github" / "workflows").glob("*riso-tauri.yml*.jinja"))
    assert len(matches) == 1
    return matches[0]


def _render(environment, relative_path: str, context: dict) -> str:
    """Render one desktop source using the configured Copier environment."""
    template = environment.from_string((FILES / relative_path).read_text())
    return template.render(context)


@pytest.mark.parametrize(
    ("override", "filename"),
    [
        ({}, "riso-tauri.yml"),
        ({"desktop_module": "disabled"}, ""),
        ({"desktop_framework": "electron-vite"}, ""),
        ({"ci_platform": "gitlab-ci"}, ""),
    ],
)
def test_tauri_workflow_filename_emits_only_for_selected_root_ci(
    copier_env, workflow_source, override, filename
):
    """Unselected projects do not receive an empty or inert workflow file."""
    context = {**DESKTOP, **override}
    emitted = copier_env.from_string(workflow_source.stem).render(context)
    assert emitted == filename
    assert not (FILES / "tauri/.github/workflows/ci.yml.jinja").exists()


def test_tauri_workflow_checks_workspace_and_builds_assets_before_native_code(
    copier_env, workflow_source
):
    """Workflow jobs execute from their actual generated package and crate roots."""
    workflow = yaml.safe_load(
        copier_env.from_string(workflow_source.read_text()).render(DESKTOP)
    )
    jobs = workflow["jobs"]
    frontend_runs = [step["run"] for step in jobs["frontend"]["steps"] if "run" in step]
    assert frontend_runs == [
        "pnpm install --frozen-lockfile",
        *[
            f"pnpm --filter ./tauri --fail-if-no-match run {check}"
            for check in ("typecheck", "lint", "test", "build:frontend")
        ],
    ]
    native = jobs["native"]
    assert native["needs"] == "frontend"
    assert {item["target"] for item in native["strategy"]["matrix"]["include"]} == {
        "x86_64-apple-darwin",
        "aarch64-apple-darwin",
        "x86_64-pc-windows-msvc",
        "x86_64-unknown-linux-gnu",
    }
    runs = [step for step in native["steps"] if "run" in step]
    assert "libwebkit2gtk-4.1-dev" in runs[0]["run"]
    assert "build:frontend" in runs[2]["run"]
    assert all(step["working-directory"] == "tauri/src-tauri" for step in runs[3:])
    assert all(
        not any(word in step["run"] for word in ("tauri build", "--publish"))
        for step in runs
    )


@pytest.mark.parametrize(
    "features",
    [[], ["auto_updater"], ["deep_linking"], ["auto_updater", "deep_linking"]],
)
def test_tauri_config_and_cargo_features_align(copier_env, features):
    """Asset and optional link configuration match the native plugin declarations."""
    context = {**DESKTOP, "desktop_features": features}
    config = json.loads(
        _render(copier_env, "tauri/src-tauri/tauri.conf.json.jinja", context)
    )
    cargo = tomllib.loads(
        _render(copier_env, "tauri/src-tauri/Cargo.toml.jinja", context)
    )
    assert config["app"]["security"]["assetProtocol"]["enable"] is True
    assert "protocol-asset" in cargo["dependencies"]["tauri"]["features"]
    assert cargo["package"]["rust-version"] == "1.90"
    assert "infoString" not in config["bundle"]["macOS"]
    plugins = config.get("plugins", {})
    assert ("updater" in plugins) == ("auto_updater" in features)
    assert ("deep-link" in plugins) == ("deep_linking" in features)
    assert ("tauri-plugin-deep-link" in cargo["dependencies"]) == (
        "deep_linking" in features
    )
    if "deep_linking" in features:
        assert plugins["deep-link"]["desktop"]["schemes"] == [DESKTOP["project_slug"]]


def test_tauri_codegen_icons_have_the_required_rgba_encoding():
    """Reject source icon derivatives that make generate_context panic."""
    icons = FILES / "tauri" / "src-tauri" / "icons"
    for filename, size in (
        ("32x32.png", 32),
        ("128x128.png", 128),
        ("128x128@2x.png", 256),
    ):
        header = (icons / filename).read_bytes()[:26]
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">IIBB", header[16:26]) == (size, size, 8, 6)


@pytest.mark.parametrize(
    ("directory", "framework"), [("electron", "electron-vite"), ("tauri", "tauri")]
)
def test_desktop_test_and_coverage_scripts_ship_their_runner(
    copier_env, directory, framework
):
    """Both app templates emit actual suites and a matching coverage provider."""
    context = {**DESKTOP, "desktop_framework": framework}
    manifest = json.loads(
        _render(copier_env, f"{directory}/package.json.jinja", context)
    )
    assert manifest["scripts"]["test"] == "vitest run"
    assert manifest["scripts"]["test:coverage"] == "vitest run --coverage"
    dependencies = manifest["devDependencies"]
    assert dependencies["vitest"] == dependencies["@vitest/coverage-v8"]
    suites = sorted((FILES / directory / "tests").glob("*.test.ts*.jinja"))
    assert len(suites) >= 2
    assert all(
        copier_env.from_string(path.read_text()).render(context).strip()
        for path in suites
    )
