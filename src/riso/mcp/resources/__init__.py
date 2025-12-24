"""MCP resources registration.

Exposes template files, sample configurations, and module catalog.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_resources(mcp: FastMCP) -> None:
    """Register all MCP resources with the server.

    Parameters
    ----------
    mcp
        FastMCP server instance
    """
    from .catalog import register_catalog_resources
    from .samples import register_sample_resources
    from .templates import register_template_resources

    register_template_resources(mcp)
    register_sample_resources(mcp)
    register_catalog_resources(mcp)


__all__ = ["register_resources"]
