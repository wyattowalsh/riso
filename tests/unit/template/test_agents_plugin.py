"""Unit tests for wyattowalsh/agents plugin enablement."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_ROOT = REPO_ROOT / "template" / "files"


def _render_jinja(relative: str) -> str:
    """Render a template file that has no Copier variables."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    return env.get_template(relative).render()


class TestMaintainerPluginSettings:
    """Maintainer repo project settings enable the Agents plugin."""

    def test_cursor_settings_enables_agents_plugin(self):
        """Cursor settings enable the agents plugin."""
        payload = json.loads((REPO_ROOT / ".cursor" / "settings.json").read_text())
        assert payload["plugins"]["agents"]["enabled"] is True

    def test_claude_settings_registers_github_marketplace(self):
        """Claude Code settings register and enable agents@agents."""
        payload = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text())
        assert payload["enabledPlugins"]["agents@agents"] is True
        source = payload["extraKnownMarketplaces"]["agents"]["source"]
        assert source["source"] == "github"
        assert source["repo"] == "wyattowalsh/agents"

    def test_copilot_settings_recommend_agents_plugin(self):
        """GitHub Copilot workspace settings recommend the Agents plugin."""
        payload = json.loads(
            (REPO_ROOT / ".github" / "copilot" / "settings.json").read_text()
        )
        assert payload["enabledPlugins"]["agents@agents"] is True
        source = payload["extraKnownMarketplaces"]["agents"]["source"]
        assert source["repo"] == "wyattowalsh/agents"


class TestTemplatePluginSettings:
    """Generated projects receive the same plugin enablement."""

    @pytest.mark.parametrize(
        "relative",
        [
            ".cursor/settings.json.jinja",
            ".claude/settings.json.jinja",
            ".github/copilot/settings.json.jinja",
        ],
    )
    def test_plugin_settings_templates_render_valid_json(self, relative: str):
        """Plugin settings templates render as JSON."""
        payload = json.loads(_render_jinja(relative))
        assert isinstance(payload, dict)

    def test_cursor_template_enables_agents_plugin(self):
        """Rendered Cursor settings enable the agents plugin."""
        payload = json.loads(_render_jinja(".cursor/settings.json.jinja"))
        assert payload["plugins"]["agents"]["enabled"] is True

    def test_claude_template_registers_github_marketplace(self):
        """Rendered Claude settings register wyattowalsh/agents."""
        payload = json.loads(_render_jinja(".claude/settings.json.jinja"))
        assert payload["enabledPlugins"]["agents@agents"] is True
        assert payload["permissions"]["defaultMode"] == "ask"
        source = payload["extraKnownMarketplaces"]["agents"]["source"]
        assert source["repo"] == "wyattowalsh/agents"

    def test_copilot_template_recommends_agents_plugin(self):
        """Rendered Copilot settings recommend agents@agents."""
        payload = json.loads(_render_jinja(".github/copilot/settings.json.jinja"))
        assert payload["enabledPlugins"]["agents@agents"] is True
        source = payload["extraKnownMarketplaces"]["agents"]["source"]
        assert source["source"] == "github"
        assert source["repo"] == "wyattowalsh/agents"

    def test_ai_tools_docs_describe_add_plugin(self):
        """AI tools docs document /add-plugin and the skills CLI fallback."""
        text = (TEMPLATE_ROOT / "docs" / "ai-tools.md.jinja").read_text()
        assert "/add-plugin github.com/wyattowalsh/agents" in text
        assert "npx skills add github:wyattowalsh/agents --all -y" in text
        assert "claude plugin install agents@agents" in text
