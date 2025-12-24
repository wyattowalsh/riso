"""Riso MCP Server - FastMCP v2 implementation.

Exposes Riso template scaffolding as MCP tools, resources, and prompts
with support for stdio, SSE, and HTTP streaming transports.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from fastmcp import FastMCP

from .config import ServerConfig, get_config, load_config
from .session import SessionManager

if TYPE_CHECKING:
    pass

__version__ = "1.0.0"
SERVER_NAME = "riso-mcp"

# Create server instance
config = get_config()

mcp = FastMCP(
    name=config.name,
    version=__version__,
    instructions=(
        "Riso MCP Server - Scaffolds Python, Node.js, and full-stack projects "
        "using the Riso Copier template. Supports interactive wizard workflows "
        "and direct Copier API access.\n\n"
        "Available capabilities:\n"
        "- Tools: Template operations (copy, update, recopy) and wizard workflow\n"
        "- Resources: Template files, sample configurations, module catalog\n"
        "- Prompts: Pre-built workflows for common project setups"
    ),
)

# Session manager for wizard state
session_manager = SessionManager(
    ttl_minutes=config.wizard.session_ttl_minutes,
    max_sessions=config.wizard.max_sessions,
)


def _register_tools() -> None:
    """Register all MCP tools."""
    from .tools import register_tools

    register_tools(mcp, session_manager)


def _register_resources() -> None:
    """Register all MCP resources."""
    from .resources import register_resources

    register_resources(mcp)


def _register_prompts() -> None:
    """Register all MCP prompts."""
    from .prompts import register_prompts

    register_prompts(mcp)


def _setup_logging() -> None:
    """Configure logging for MCP server."""
    try:
        from loguru import logger

        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <cyan>MCP</cyan> | <level>{level: <8}</level> | <level>{message}</level>",
            level=config.log_level,
            colorize=True,
        )
    except ImportError:
        import logging

        logging.basicConfig(
            level=getattr(logging, config.log_level, logging.INFO),
            format="%(asctime)s | MCP | %(levelname)-8s | %(message)s",
        )


# Register all capabilities on import
_setup_logging()
_register_tools()
_register_resources()
_register_prompts()


def run_server(
    transport: str | None = None,
    host: str | None = None,
    port: int | None = None,
) -> None:
    """Run the MCP server with specified transport.

    Parameters
    ----------
    transport
        Transport type: "stdio", "sse", or "http". Defaults to config value.
    host
        Bind address for HTTP/SSE transports. Defaults to config value.
    port
        Port for HTTP/SSE transports. Defaults to config value.
    """
    server_config = load_config()

    actual_transport = transport or server_config.transport
    actual_host = host or server_config.host
    actual_port = port or server_config.port

    try:
        from loguru import logger

        logger.info(
            f"Starting {SERVER_NAME} v{__version__} with {actual_transport} transport"
        )
    except ImportError:
        print(
            f"Starting {SERVER_NAME} v{__version__} with {actual_transport} transport",
            file=sys.stderr,
        )

    if actual_transport == "stdio":
        mcp.run()
    elif actual_transport == "sse":
        mcp.run(transport="sse", host=actual_host, port=actual_port)
    elif actual_transport == "http":
        mcp.run(transport="streamable-http", host=actual_host, port=actual_port)
    else:
        raise ValueError(f"Unknown transport: {actual_transport}")


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Riso MCP Server")
    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "sse", "http"],
        default=None,
        help="Transport type (default: from config or stdio)",
    )
    parser.add_argument(
        "--host",
        "-H",
        default=None,
        help="Host for HTTP/SSE (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=None,
        help="Port for HTTP/SSE (default: 3000)",
    )

    args = parser.parse_args()
    run_server(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
