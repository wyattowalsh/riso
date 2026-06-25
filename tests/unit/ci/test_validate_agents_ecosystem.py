"""Unit tests for validate_agents_ecosystem.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestCopierExcludePatterns:
    """Ensure copier.yml excludes harness files when ai_tools is disabled."""

    def test_copier_yml_has_ai_tools_excludes(self):
        """copier.yml must gate harness paths on ai_tools_module."""
        copier_yml = (
            pytest.importorskip("pathlib").Path(__file__).resolve().parents[3]
            / "template"
            / "copier.yml"
        )
        text = copier_yml.read_text(encoding="utf-8")
        required = [
            "{% if ai_tools_module != 'enabled' %}CLAUDE.md{% endif %}",
            "{% if ai_tools_module != 'enabled' %}.cursor/{% endif %}",
            "{% if ai_tools_module != 'enabled' %}docs/ai-tools.md{% endif %}",
        ]
        for snippet in required:
            assert snippet in text
