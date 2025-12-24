"""MCP tools registration.

Provides both Copier API tools and interactive wizard tools.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from ..session import SessionManager


def register_tools(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all MCP tools with the server.

    Parameters
    ----------
    mcp
        FastMCP server instance
    session_manager
        Session manager for wizard workflows
    """
    from .copier_api import register_copier_tools
    from .wizard import register_wizard_tools

    register_copier_tools(mcp)
    register_wizard_tools(mcp, session_manager)


__all__ = ["register_tools"]
