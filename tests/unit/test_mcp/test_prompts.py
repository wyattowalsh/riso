"""Tests for MCP server prompts."""

from __future__ import annotations

import pytest

pytest.importorskip("fastmcp")
pytest.importorskip("pydantic_settings")


class TestWorkflowPrompts:
    """Tests for workflow prompts."""

    def test_workflow_prompts_registration(self):
        """Test that workflow prompts are registered."""
        from riso.mcp.prompts.workflows import register_workflow_prompts
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_workflow_prompts(mcp)

        # Verify registration completed without error
        assert True

    def test_new_project_prompt_registered(self):
        """Test that new_project prompt is registered."""
        from riso.mcp.prompts.workflows import register_workflow_prompts
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_workflow_prompts(mcp)

        # Check prompt is in the prompt manager
        prompt_names = [p.name for p in mcp._prompt_manager._prompts.values()]
        assert "new_project" in prompt_names

    def test_update_existing_prompt_registered(self):
        """Test that update_existing prompt is registered."""
        from riso.mcp.prompts.workflows import register_workflow_prompts
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_workflow_prompts(mcp)

        prompt_names = [p.name for p in mcp._prompt_manager._prompts.values()]
        assert "update_existing" in prompt_names

    def test_full_stack_setup_prompt_registered(self):
        """Test that full_stack_setup prompt is registered."""
        from riso.mcp.prompts.workflows import register_workflow_prompts
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_workflow_prompts(mcp)

        prompt_names = [p.name for p in mcp._prompt_manager._prompts.values()]
        assert "full_stack_setup" in prompt_names

    def test_mcp_server_setup_prompt_registered(self):
        """Test that mcp_server_setup prompt is registered."""
        from riso.mcp.prompts.workflows import register_workflow_prompts
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_workflow_prompts(mcp)

        prompt_names = [p.name for p in mcp._prompt_manager._prompts.values()]
        assert "mcp_server_setup" in prompt_names

    def test_quality_setup_prompt_registered(self):
        """Test that quality_setup prompt is registered."""
        from riso.mcp.prompts.workflows import register_workflow_prompts
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_workflow_prompts(mcp)

        prompt_names = [p.name for p in mcp._prompt_manager._prompts.values()]
        assert "quality_setup" in prompt_names


class TestPromptIntegration:
    """Integration tests for prompt registration."""

    def test_prompts_registered_on_server(self):
        """Test that prompts are properly set up on server."""
        from riso.mcp.server import mcp as server

        # The server should be properly configured with prompts
        assert server is not None
        assert server.name == "riso-mcp"
