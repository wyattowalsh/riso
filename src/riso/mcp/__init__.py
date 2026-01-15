"""Riso MCP Server package.

Exposes Riso template operations as MCP tools, resources, and prompts.
"""

from .config import ServerConfig, get_config, load_config
from .errors import (
    CopierOperationError,
    MCPError,
    MCPErrorCode,
    PathNotFoundError,
    PermissionDeniedError,
    SessionExpiredError,
    SessionNotFoundError,
    TemplateNotFoundError,
    ValidationFailedError,
)
from .server import __version__, create_server, mcp, run_server, session_manager
from .session import SessionManager, WizardSession, WizardStep

__all__ = [
    # Server
    "__version__",
    "mcp",
    "run_server",
    "create_server",
    "session_manager",
    # Config
    "ServerConfig",
    "get_config",
    "load_config",
    # Session
    "SessionManager",
    "WizardSession",
    "WizardStep",
    # Errors
    "MCPError",
    "MCPErrorCode",
    "CopierOperationError",
    "PathNotFoundError",
    "PermissionDeniedError",
    "SessionExpiredError",
    "SessionNotFoundError",
    "TemplateNotFoundError",
    "ValidationFailedError",
]
