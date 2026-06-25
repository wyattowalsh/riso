"""Unit tests for AGENTS.md template rendering."""

from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

pytestmark = pytest.mark.unit

TEMPLATE_ROOT = Path(__file__).resolve().parents[3] / "template" / "files"
AGENTS_TEMPLATE = TEMPLATE_ROOT / "AGENTS.md.jinja"


def _render_agents(context: dict[str, object]) -> str:
    """Render AGENTS.md.jinja with the given Copier-like context."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    template = env.get_template("AGENTS.md.jinja")
    return template.render(**context)


@pytest.fixture
def base_context() -> dict[str, object]:
    """Minimal context shared by rendered variants."""
    return {
        "project_name": "Test Project",
        "project_slug": "test-project",
        "package_name": "test_project",
        "project_layout": "single-package",
        "quality_profile": "standard",
        "task_runner": "just",
        "ci_platform": "github-actions",
        "cli_module": "disabled",
        "cli_languages": [],
        "api_module": "disabled",
        "api_languages": [],
        "mcp_module": "disabled",
        "mcp_languages": [],
        "docs_module": "enabled",
        "docs_framework": "fumadocs",
        "shared_logic": "disabled",
        "changelog_module": "disabled",
        "saas_infra_module": "disabled",
        "desktop_module": "disabled",
        "ai_tools_module": "enabled",
    }


class TestAgentsMdTemplate:
    """Tests for AGENTS.md.jinja content."""

    def test_template_file_exists(self):
        """AGENTS.md.jinja must exist in template payload."""
        assert AGENTS_TEMPLATE.exists()

    def test_renders_project_identity(self, base_context: dict[str, object]):
        """Rendered AGENTS.md includes project and package names."""
        output = _render_agents(base_context)
        assert "# AGENTS.md" in output
        assert "Test Project" in output
        assert "test_project" in output

    def test_fumadocs_only_has_no_python_quickstart_commands(
        self, base_context: dict[str, object]
    ):
        """Docs-only fumadocs variant should not document Python pytest commands."""
        output = _render_agents(base_context)
        assert "pnpm --filter docs-fumadocs" in output
        assert "uv run pytest" not in output

    def test_quick_reference_table_rows_are_separate(
        self, base_context: dict[str, object]
    ):
        """Table header separator must not merge with the first data row."""
        output = _render_agents(base_context)
        assert "| ------- ||" not in output
        assert "| Install workspace | `pnpm install` |" in output

    def test_python_and_node_rows_do_not_merge(self, base_context: dict[str, object]):
        """Python and Node quick-reference rows stay on separate lines."""
        base_context["cli_module"] = "enabled"
        base_context["cli_languages"] = ["python"]
        base_context["shared_logic"] = "enabled"
        output = _render_agents(base_context)
        assert "| ------- ||" not in output
        assert "all-files` ||" not in output
        assert "| Install workspace | `pnpm install` |" in output

    def test_cli_section_when_enabled(self, base_context: dict[str, object]):
        """CLI commands appear only when cli_module is enabled."""
        base_context["cli_module"] = "enabled"
        base_context["cli_languages"] = ["python"]
        output = _render_agents(base_context)
        assert "python -m test_project.cli" in output

    def test_cli_absent_when_disabled(self, base_context: dict[str, object]):
        """CLI commands must not appear when cli_module is disabled."""
        output = _render_agents(base_context)
        assert "python -m test_project.cli" not in output

    def test_ai_tools_reference_when_enabled(self, base_context: dict[str, object]):
        """AI tools docs linked when harness module enabled."""
        output = _render_agents(base_context)
        assert "docs/ai-tools.md" in output

    def test_ai_tools_section_hidden_when_disabled(
        self, base_context: dict[str, object]
    ):
        """AI tools references hidden when ai_tools_module disabled."""
        base_context["ai_tools_module"] = "disabled"
        output = _render_agents(base_context)
        assert "docs/ai-tools.md" not in output

    def test_uv_run_execution_rule_when_python_enabled(
        self, base_context: dict[str, object]
    ):
        """Python surface documents uv run convention."""
        base_context["cli_module"] = "enabled"
        base_context["cli_languages"] = ["python"]
        output = _render_agents(base_context)
        assert "uv run" in output
        assert "never bare `python`" in output
