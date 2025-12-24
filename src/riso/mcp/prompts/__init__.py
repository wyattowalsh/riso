"""MCP prompts registration.

Pre-built prompts for common Riso workflows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts with the server.

    Parameters
    ----------
    mcp
        FastMCP server instance
    """
    from .workflows import register_workflow_prompts

    register_workflow_prompts(mcp)


__all__ = ["register_prompts"]
