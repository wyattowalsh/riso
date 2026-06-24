"""Tests for MCP server tools."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("fastmcp")
pytest.importorskip("pydantic_settings")

from riso.mcp.errors import ValidationFailedError


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_copier_run():
    """Mock copier.run_copy for testing."""
    with patch("copier.run_copy") as mock:
        mock.return_value = MagicMock()
        yield mock


class TestCopierAPITools:
    """Tests for Copier API tools."""

    def test_get_prompts_tool_registered(self):
        """Test that get_prompts tool is registered."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        # Verify tool was registered
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "get_prompts" in tool_names

    def test_list_template_variants_tool_registered(self):
        """Test that list_template_variants tool is registered."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "list_template_variants" in tool_names

    def test_validate_template_answers_tool_registered(self):
        """Test that validate_template_answers tool is registered."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "validate_template_answers" in tool_names

    def test_copier_copy_tool_registered(self):
        """Test that copier_copy tool is registered."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "copier_copy" in tool_names

    def test_copier_update_tool_registered(self):
        """Test that copier_update tool is registered."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "copier_update" in tool_names

    def test_copier_recopy_tool_registered(self):
        """Test that copier_recopy tool is registered."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "copier_recopy" in tool_names

    def test_validate_template_answers_rejects_removed_answer_keys(self):
        """Removed answer keys are hard errors, not compatibility aliases."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        validate_template_answers = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "validate_template_answers":
                validate_template_answers = tool.fn
                break

        assert validate_template_answers is not None
        with pytest.raises(ValidationFailedError) as exc_info:
            validate_template_answers({"docs_site": "fumadocs"})
        assert "docs_site" in exc_info.value.data["errors"][0]


class TestWizardTools:
    """Tests for wizard tools."""

    def test_wizard_tools_registration(self):
        """Test that all wizard tools are registered."""
        from riso.mcp.tools.wizard import register_wizard_tools
        from riso.mcp.session import SessionManager
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        session_manager = SessionManager()
        register_wizard_tools(mcp, session_manager)

        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        expected_tools = [
            "wizard_start",
            "wizard_step",
            "wizard_back",
            "wizard_status",
            "wizard_generate",
            "wizard_cancel",
            "wizard_list_sessions",
        ]
        for tool in expected_tools:
            assert tool in tool_names, f"Missing wizard tool: {tool}"

    def test_session_manager_creation(self):
        """Test SessionManager initialization."""
        from riso.mcp.session import SessionManager

        manager = SessionManager(ttl_minutes=30)
        assert manager._ttl_minutes == 30
        assert manager.active_session_count == 0

    def test_session_manager_create_session(self):
        """Test creating a new session."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        session = manager.create_session(
            project_name="test",
            destination="/tmp/test",
        )

        assert session.session_id is not None
        assert session.project_name == "test"
        assert session.current_step == 0
        assert len(session.steps) > 0

    def test_session_manager_get_session(self):
        """Test retrieving an existing session."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        created = manager.create_session()

        retrieved = manager.get_session(created.session_id)
        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    def test_session_manager_delete_session(self):
        """Test deleting a session."""
        from riso.mcp.session import SessionManager
        from riso.mcp.errors import SessionNotFoundError

        manager = SessionManager()
        session = manager.create_session()
        session_id = session.session_id

        result = manager.delete_session(session_id)
        assert result is True

        with pytest.raises(SessionNotFoundError):
            manager.get_session(session_id)


class TestToolIntegration:
    """Integration tests for tool registration."""

    def test_all_tools_registered_on_server(self):
        """Test that all tools are registered on the MCP server."""
        from riso.mcp.server import mcp

        # Get tool names directly from the tool manager
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        # Copier API tools
        assert "copier_copy" in tool_names
        assert "copier_update" in tool_names
        assert "copier_recopy" in tool_names
        assert "get_prompts" in tool_names
        assert "list_template_variants" in tool_names
        assert "validate_template_answers" in tool_names

        # Wizard tools
        assert "wizard_start" in tool_names
        assert "wizard_step" in tool_names
        assert "wizard_back" in tool_names
        assert "wizard_status" in tool_names
        assert "wizard_generate" in tool_names
        assert "wizard_cancel" in tool_names
        assert "wizard_list_sessions" in tool_names

    def test_server_name(self):
        """Test that server has correct name."""
        from riso.mcp.server import mcp
        from riso.mcp.config import load_config

        assert mcp.name == load_config().name
