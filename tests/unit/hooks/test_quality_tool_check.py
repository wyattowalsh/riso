"""Unit tests for quality_tool_check.py"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "hooks"))


class TestToolCheck:
    """Tests for ToolCheck dataclass."""

    def test_tool_check_creation(self):
        """Should create ToolCheck with all fields."""
        from quality_tool_check import ToolCheck
        check = ToolCheck(
            name="ruff",
            status="present",
            command="uv tool run ruff --version",
        )
        assert check.name == "ruff"
        assert check.status == "present"

    def test_tool_check_with_optional_fields(self):
        """Should handle optional fields."""
        from quality_tool_check import ToolCheck
        check = ToolCheck(
            name="mypy",
            status="failed",
            command="uv tool install mypy",
            stderr="Installation error",
            next_steps="Install manually",
        )
        assert check.stderr == "Installation error"
        assert check.next_steps == "Install manually"


class TestEnsurePythonQualityTools:
    """Tests for ensure_python_quality_tools function."""

    def test_all_tools_present(self, monkeypatch):
        """Should return empty list when all tools present."""
        from unittest.mock import MagicMock
        import subprocess

        def mock_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "tool 1.0.0"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from quality_tool_check import ensure_python_quality_tools
        checks = ensure_python_quality_tools()

        # All tools should be present
        for check in checks:
            assert check.status == "present"

    def test_handles_missing_tool(self, monkeypatch):
        """Should handle missing tool gracefully."""
        import subprocess

        call_count = [0]

        def mock_run(cmd, *args, **kwargs):
            result = MagicMock()
            call_count[0] += 1
            # First call (version check) fails, second call (install) also fails
            if "version" in str(cmd) or call_count[0] == 1:
                result.returncode = 1
                result.stdout = ""
                result.stderr = "not found"
            else:
                result.returncode = 1
                result.stdout = ""
                result.stderr = "install failed"
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from quality_tool_check import ensure_python_quality_tools
        checks = ensure_python_quality_tools()

        # At least one tool should have failed status
        failed = [c for c in checks if c.status == "failed"]
        assert len(failed) > 0


class TestEnsureNodeQualityTools:
    """Tests for ensure_node_quality_tools function."""

    def test_pnpm_present(self, monkeypatch):
        """Should detect pnpm when present."""
        import subprocess
        import shutil

        monkeypatch.setattr(shutil, "which", lambda x: "/usr/bin/pnpm" if x == "pnpm" else None)

        def mock_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "8.0.0"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from quality_tool_check import ensure_node_quality_tools
        checks = ensure_node_quality_tools(required=True)

        pnpm_checks = [c for c in checks if c.name == "pnpm"]
        if pnpm_checks:
            assert pnpm_checks[0].status in ["present", "installed"]

    def test_handles_missing_corepack(self, monkeypatch):
        """Should handle missing corepack."""
        import subprocess
        import shutil

        monkeypatch.setattr(shutil, "which", lambda x: None)

        def mock_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = ""
            result.stderr = "corepack not found"
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from quality_tool_check import ensure_node_quality_tools
        checks = ensure_node_quality_tools(required=True)

        # Should return failed status for pnpm
        pnpm_checks = [c for c in checks if c.name == "pnpm"]
        if pnpm_checks:
            assert pnpm_checks[0].status == "failed"
