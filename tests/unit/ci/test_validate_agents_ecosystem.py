"""Unit tests for validate_agents_ecosystem.py."""

from __future__ import annotations

from pathlib import Path

import pytest
from validate_agents_ecosystem import (
    _enables_agents_plugin,
    check_copier_exclude,
    check_render_tree,
    check_required_files,
)

pytestmark = [pytest.mark.unit, pytest.mark.usefixtures("ci_scripts_path")]


class TestCopierExcludePatterns:
    """Ensure copier.yml excludes harness files when ai_tools is disabled."""

    def test_copier_yml_has_ai_tools_excludes(self):
        """copier.yml must gate harness paths on ai_tools_module."""
        copier_yml = Path(__file__).resolve().parents[3] / "template" / "copier.yml"
        text = copier_yml.read_text(encoding="utf-8")
        required = [
            "{% if ai_tools_module != 'enabled' %}CLAUDE.md{% endif %}",
            "{% if ai_tools_module != 'enabled' %}.cursor/{% endif %}",
            "{% if ai_tools_module != 'enabled' %}.github/copilot/{% endif %}",
            "{% if ai_tools_module != 'enabled' %}docs/ai-tools.md{% endif %}",
        ]
        for snippet in required:
            assert snippet in text

    def test_check_copier_exclude_passes_on_repo(self):
        """Live copier.yml satisfies the ecosystem exclude check."""
        assert check_copier_exclude() == 0


class TestAgentsPluginDetection:
    """Detect Cursor and Claude/Copilot plugin enablement shapes."""

    def test_detects_claude_marketplace_keys(self):
        """Claude/Copilot settings use agents@agents plus the GitHub repo."""
        text = '{"enabledPlugins":{"agents@agents":true},"repo":"wyattowalsh/agents"}'
        assert _enables_agents_plugin(text) is True

    def test_detects_cursor_plugins_map(self):
        """Cursor settings enable plugins.agents without marketplace keys."""
        text = '{"plugins":{"agents":{"enabled":true}}}'
        assert _enables_agents_plugin(text) is True

    def test_rejects_unrelated_settings(self):
        """Unrelated JSON is not treated as Agents plugin enablement."""
        assert _enables_agents_plugin('{"permissions":{"defaultMode":"ask"}}') is False


class TestRequiredPluginTemplates:
    """Template payload includes Agents plugin settings files."""

    def test_check_required_files_passes_on_repo(self):
        """Live template files satisfy the ecosystem required-file check."""
        assert check_required_files() == 0


def _write_agents_md(render_dir: Path) -> None:
    """Write a long-enough AGENTS.md for render-tree checks."""
    lines = ["# AGENTS.md", ""]
    lines.extend(f"- item {index}" for index in range(20))
    (render_dir / "AGENTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestRenderTreePluginSettings:
    """Rendered trees must include or omit plugin settings with ai_tools."""

    def test_enabled_render_requires_plugin_settings(self, tmp_path: Path):
        """ai_tools enabled requires Cursor, Claude, and Copilot plugin settings."""
        _write_agents_md(tmp_path)
        (tmp_path / "CLAUDE.md").write_text("See AGENTS.md\n", encoding="utf-8")
        (tmp_path / ".warp").mkdir()
        (tmp_path / ".warp" / "WARP.md").write_text("See AGENTS.md\n", encoding="utf-8")
        (tmp_path / ".cursor").mkdir()
        (tmp_path / ".cursor" / "rules").write_text("See AGENTS.md\n", encoding="utf-8")
        (tmp_path / ".cursor" / "settings.json").write_text(
            '{"plugins":{"agents":{"enabled":true}}}\n', encoding="utf-8"
        )
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text(
            '{"enabledPlugins":{"agents@agents":true},'
            '"extraKnownMarketplaces":{"agents":{"source":'
            '{"source":"github","repo":"wyattowalsh/agents"}}}}\n',
            encoding="utf-8",
        )
        (tmp_path / ".github" / "copilot").mkdir(parents=True)
        (tmp_path / ".github" / "copilot" / "settings.json").write_text(
            '{"enabledPlugins":{"agents@agents":true},'
            '"extraKnownMarketplaces":{"agents":{"source":'
            '{"source":"github","repo":"wyattowalsh/agents"}}}}\n',
            encoding="utf-8",
        )
        assert check_render_tree(tmp_path, ai_tools_enabled=True) == 0

    def test_enabled_render_fails_without_plugin_settings(self, tmp_path: Path):
        """Missing plugin settings fail when ai_tools is enabled."""
        _write_agents_md(tmp_path)
        (tmp_path / "CLAUDE.md").write_text("See AGENTS.md\n", encoding="utf-8")
        (tmp_path / ".warp").mkdir()
        (tmp_path / ".warp" / "WARP.md").write_text("See AGENTS.md\n", encoding="utf-8")
        (tmp_path / ".cursor").mkdir()
        (tmp_path / ".cursor" / "rules").write_text("See AGENTS.md\n", encoding="utf-8")
        errors = check_render_tree(tmp_path, ai_tools_enabled=True)
        assert errors >= 3

    def test_disabled_render_rejects_plugin_settings(self, tmp_path: Path):
        """ai_tools disabled must not emit plugin settings files."""
        _write_agents_md(tmp_path)
        (tmp_path / ".cursor").mkdir()
        (tmp_path / ".cursor" / "settings.json").write_text("{}\n", encoding="utf-8")
        errors = check_render_tree(tmp_path, ai_tools_enabled=False)
        assert errors >= 1
