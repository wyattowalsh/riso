"""Riso MCP Server - FastMCP v2 implementation.

Exposes Riso template scaffolding as MCP tools, resources, and prompts
with support for stdio, SSE, and HTTP streaming transports.
"""

from __future__ import annotations

import logging
import os

from fastmcp import FastMCP

from .config import ServerConfig, load_config
from .logging import log_event, setup_logging
from .session import SessionManager

__version__ = "1.0.0"
SERVER_NAME = "riso-mcp"


def create_server(config: ServerConfig | None = None) -> tuple[FastMCP, SessionManager]:
    """Create and register a configured MCP server instance."""
    server_config = config or load_config()

    mcp = FastMCP(
        name=server_config.name,
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

    # Initialize persistence backend
    store = None
    if server_config.wizard.persistence_backend != "memory":
        from .persistence import JSONFileStore, SQLiteStore

        persistence_path = server_config.wizard.persistence_path
        if server_config.wizard.persistence_backend == "json":
            store = JSONFileStore(base_path=persistence_path)
        elif server_config.wizard.persistence_backend == "sqlite":
            if persistence_path is not None:
                db_path = persistence_path / "sessions.db"
            else:
                db_path = None
            store = SQLiteStore(db_path=db_path)

    session_manager = SessionManager(
        ttl_minutes=server_config.wizard.session_ttl_minutes,
        max_sessions=server_config.wizard.max_sessions,
        rate_config=server_config.wizard.rate_limit,
        auto_cleanup_interval=server_config.wizard.auto_cleanup_interval,
        store=store,
    )

    # Load persisted sessions if available
    if store is not None:
        loaded = session_manager.load_persisted_sessions()
        logger = logging.getLogger("riso.mcp.server")
        if loaded > 0:
            log_event(
                logger,
                "persisted_sessions_restored",
                level="info",
                count=loaded,
                backend=server_config.wizard.persistence_backend,
            )

    from .tools import register_tools
    from .resources import register_resources
    from .prompts import register_prompts

    register_tools(mcp, session_manager)
    register_resources(mcp)
    register_prompts(mcp)

    return mcp, session_manager


def _setup_logging(config: ServerConfig) -> logging.Logger:
    """Configure logging for MCP server.

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    return setup_logging(
        level=config.log_level,
        json_output=config.json_logs,
        server_name=SERVER_NAME,
    )


# Create server instance on import for entry points/tests.
# Skip initialization during Sphinx autodoc build to avoid import errors.
if not os.environ.get("SPHINX_BUILD"):
    _CONFIG = load_config()
    mcp, session_manager = create_server(_CONFIG)

    # ASGI app for HTTP deployments (Vercel, Railway, etc.)
    # Usage: uvicorn riso.mcp.server:app --host 0.0.0.0 --port 8000
    app = mcp.http_app()
else:
    # Provide stub values for documentation build
    _CONFIG = None
    mcp = None
    session_manager = None
    app = None


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

    logger = _setup_logging(server_config)

    actual_transport = transport or server_config.transport
    actual_host = host or server_config.host
    actual_port = port or server_config.port
    runtime_mcp, _runtime_session_manager = create_server(server_config)

    # Log server startup event
    log_event(
        logger,
        "server_started",
        level="info",
        server=SERVER_NAME,
        version=__version__,
        transport=actual_transport,
        host=actual_host if actual_transport != "stdio" else None,
        port=actual_port if actual_transport != "stdio" else None,
        log_format="json" if server_config.json_logs else "human",
    )

    try:
        if actual_transport == "stdio":
            runtime_mcp.run()
        elif actual_transport == "sse":
            runtime_mcp.run(transport="sse", host=actual_host, port=actual_port)
        elif actual_transport == "http":
            runtime_mcp.run(
                transport="streamable-http", host=actual_host, port=actual_port
            )
        else:
            raise ValueError(f"Unknown transport: {actual_transport}")
    except KeyboardInterrupt:
        log_event(logger, "server_stopped", level="info", reason="user_interrupt")
    except Exception as exc:
        log_event(
            logger,
            "error_occurred",
            level="error",
            error_type=type(exc).__name__,
            error_message=str(exc),
        )
        raise


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
