"""Copier emission contracts for the TypeScript MCP runtime and shipped tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

copier_main = pytest.importorskip("copier._main")

ROOT = Path(__file__).parents[2]
MCP_SOURCE = ROOT / "template" / "files" / "node" / "mcp"
CONTEXT = {
    "mcp_module": "enabled",
    "mcp_languages": ["typescript"],
    "mcp_example_tools": True,
    "mcp_transport": "stdio",
    "project_name": "MCP Runtime Test",
    "package_name": "mcp_runtime_test",
}


@pytest.fixture(name="copier_env")
def _copier_env(tmp_path):
    """Use Copier's real whitespace and extension settings for emitted files."""
    with copier_main.Worker(
        src_path=str(ROOT / "template"),
        dst_path=tmp_path / "copier-environment",
        defaults=True,
        quiet=True,
    ) as worker:
        yield worker.jinja_env


def _render_package(environment, context):
    """Render owned payload files and conditional filenames without invoking hooks."""
    rendered = {}
    for source in MCP_SOURCE.rglob("*.jinja"):
        parts = [
            environment.from_string(part.removesuffix(".jinja")).render(context)
            for part in source.relative_to(MCP_SOURCE).parts
        ]
        if not parts[-1]:
            continue
        rendered["/".join(parts)] = environment.from_string(source.read_text()).render(
            context
        )
    return rendered


@pytest.mark.parametrize("transport", ["stdio", "sse", "http"])
@pytest.mark.parametrize("examples", [False, True])
def test_runtime_ships_runnable_tests_for_every_public_choice(
    copier_env, transport, examples
):
    """Example-free packages retain tests without emitting an empty example test."""
    files = _render_package(
        copier_env,
        {**CONTEXT, "mcp_transport": transport, "mcp_example_tools": examples},
    )
    manifest = json.loads(files["package.json"])
    assert manifest["engines"]["node"] == "^22.19.0 || >=24.0.0"
    assert manifest["scripts"]["test"] == "vitest run"
    assert files["tests/transport.test.ts"].strip()
    assert files["src/transport.ts"].strip()
    assert ("tests/http-fetch.test.ts" in files) == examples
    assert ("tests/deadline.test.ts" in files) == examples
    if examples:
        assert files["tests/http-fetch.test.ts"].strip()
        assert files["src/tools/http-fetch.ts"].strip()
    else:
        for path in (
            "src/tools/http-fetch.ts",
            "src/tools/echo.ts",
            "src/tools/timestamp.ts",
            "src/resources/system.ts",
            "src/prompts/review.ts",
        ):
            assert files[path] == ""


def test_network_policy_dependencies_are_shipped_at_runtime(copier_env):
    """Production installs include the actual socket dispatcher and IP parser."""
    files = _render_package(copier_env, CONTEXT)
    manifest = json.loads(files["package.json"])
    for dependency in ("ipaddr.js", "undici"):
        assert dependency in manifest["dependencies"]
        assert dependency not in manifest["devDependencies"]
        assert f'from "{dependency}"' in files["src/tools/http-fetch.ts"]


@pytest.mark.parametrize(
    "override",
    [{"mcp_module": "disabled"}, {"mcp_languages": ["python"]}],
)
def test_disabled_track_has_no_runtime_or_tests(copier_env, override):
    """Disabled TypeScript MCP content remains empty before Copier exclusions."""
    files = _render_package(copier_env, {**CONTEXT, **override})
    assert all(not content.strip() for content in files.values())
