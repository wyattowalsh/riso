"""Unit tests for agent_smoke_agents_md.py."""

from __future__ import annotations

import pytest

from agent_smoke_agents_md import evaluate

pytestmark = [pytest.mark.unit, pytest.mark.usefixtures("ci_scripts_path")]

MINIMAL_AGENTS = """# AGENTS.md

> Human docs: [README.md](./README.md)

- **Package**: `riso_example`

| Task | Command |
| ---- | ------- |
| Install | `uv sync` |

## Boundaries

### Never Touch
- secrets
"""


class TestAgentSmokeEvaluate:
    """Tests for AGENTS.md smoke evaluation."""

    def test_all_checks_pass(self):
        """Complete AGENTS.md passes all smoke questions."""
        result = evaluate(MINIMAL_AGENTS)
        assert result["overall_passed"] is True
        assert result["passed"] == result["total"]

    def test_missing_boundaries_fails(self):
        """Missing Boundaries section fails smoke."""
        text = "# AGENTS.md\n\nREADME.md\n\n| Task | Command |\n"
        result = evaluate(text)
        assert result["overall_passed"] is False
        boundaries = next(
            c for c in result["checks"] if c["id"] == "boundaries_section"
        )
        assert boundaries["passed"] is False

    def test_merged_table_rows_fail(self):
        """Merged quick-reference rows fail smoke."""
        text = MINIMAL_AGENTS.replace(
            "| Install | `uv sync` |",
            "| ---- | ------- || Install | `uv sync` |",
        )
        result = evaluate(text)
        merged = next(c for c in result["checks"] if c["id"] == "table_rows_not_merged")
        assert merged["passed"] is False
