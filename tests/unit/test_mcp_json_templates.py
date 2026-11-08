"""Tests for dest-root MCP JSON family command gating."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

jinja2 = pytest.importorskip("jinja2")

pytestmark = pytest.mark.unit

TEMPLATE_FILES = Path(__file__).parents[2] / "template" / "files"

MCP_JSON_TEMPLATES = (
    "mcp.json.jinja",
    "opencode.json.jinja",
    ".mcp.json.jinja",
    ".copilot/mcp-config.json.jinja",
    ".amazonq/mcp.json.jinja",
    ".warp/mcp.json.jinja",
    ".gemini/settings.json.jinja",
)


def _render(relative: str, **context: object) -> str:
    """Render one harness projection with the selected language answers."""
    path = TEMPLATE_FILES / relative
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(path.parent)))
    return env.get_template(path.name).render(**context)


def _servers(rendered: str) -> dict[str, object]:
    """Read the server map used by this harness projection."""
    payload = json.loads(rendered)
    if "mcpServers" in payload:
        servers = payload["mcpServers"]
    else:
        servers = payload["mcp"]
    assert isinstance(servers, dict)
    return servers


class TestMcpJsonFamily:
    """Project MCP command follows mcp_languages; no unpinned github: specs."""

    @pytest.mark.parametrize("relative", MCP_JSON_TEMPLATES)
    def test_go_only_does_not_emit_python_command(self, relative: str) -> None:
        """Go MCP must not spawn the Python launcher."""
        rendered = _render(
            relative,
            mcp_module="enabled",
            mcp_languages=["go"],
            project_slug="demo",
            package_name="demo",
            ai_tools_mcp_thinking=False,
            ai_tools_mcp_web=False,
            ai_tools_mcp_documents=False,
            ai_tools_mcp_utilities=False,
            ai_tools_mcp_search=False,
        )
        servers = _servers(rendered)
        dumped = json.dumps(servers)
        assert "python" not in dumped
        assert "uv" not in dumped
        assert "./go/mcp/cmd/server" in dumped
        assert "github:aaronsb/think-strategies" not in dumped

    @pytest.mark.parametrize("relative", MCP_JSON_TEMPLATES)
    def test_python_uses_project_mcp_package(self, relative: str) -> None:
        """Every Python launcher selects the MCP group and project package."""
        rendered = _render(
            relative,
            mcp_module="enabled",
            mcp_languages=["python"],
            project_slug="demo",
            package_name="demo_pkg",
            ai_tools_mcp_thinking=False,
            ai_tools_mcp_web=False,
            ai_tools_mcp_documents=False,
            ai_tools_mcp_utilities=False,
            ai_tools_mcp_search=False,
        )
        server = _servers(rendered)["demo"]
        assert isinstance(server, dict) and server["command"] == "uv"
        assert server["args"] == [
            "run",
            "--directory",
            "python",
            "--group",
            "mcp",
            "python",
            "-m",
            "demo_pkg.mcp",
        ]

    @pytest.mark.parametrize("relative", MCP_JSON_TEMPLATES)
    def test_typescript_uses_node_mcp_dist(self, relative: str) -> None:
        """TypeScript MCP launches node/mcp/dist/index.js."""
        rendered = _render(
            relative,
            mcp_module="enabled",
            mcp_languages=["typescript"],
            project_slug="demo",
            package_name="demo",
            ai_tools_mcp_thinking=False,
            ai_tools_mcp_web=False,
            ai_tools_mcp_documents=False,
            ai_tools_mcp_utilities=False,
            ai_tools_mcp_search=False,
        )
        dumped = json.dumps(_servers(rendered))
        assert "node/mcp/dist/index.js" in dumped
        assert "python" not in dumped

    @pytest.mark.parametrize("relative", MCP_JSON_TEMPLATES)
    def test_rust_uses_cargo_run(self, relative: str) -> None:
        """Rust MCP uses cargo --manifest-path rust/mcp/Cargo.toml."""
        rendered = _render(
            relative,
            mcp_module="enabled",
            mcp_languages=["rust"],
            project_slug="demo",
            package_name="demo",
            ai_tools_mcp_thinking=False,
            ai_tools_mcp_web=False,
            ai_tools_mcp_documents=False,
            ai_tools_mcp_utilities=False,
            ai_tools_mcp_search=False,
        )
        dumped = json.dumps(_servers(rendered))
        assert "rust/mcp/Cargo.toml" in dumped
        assert "python" not in dumped

    @pytest.mark.parametrize("relative", MCP_JSON_TEMPLATES)
    def test_think_strategies_unpinned_github_absent(self, relative: str) -> None:
        """Unpinned github:aaronsb/think-strategies must not appear."""
        rendered = _render(
            relative,
            mcp_module="disabled",
            mcp_languages=[],
            project_slug="demo",
            package_name="demo",
        )
        assert "github:aaronsb/think-strategies" not in rendered
        assert "think-strategies" not in rendered
