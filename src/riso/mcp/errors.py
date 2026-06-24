"""MCP error types with proper error codes.

Maps Riso-specific errors to MCP protocol error codes per JSON-RPC spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class MCPErrorCode(IntEnum):
    """MCP error codes per JSON-RPC 2.0 specification."""

    # Standard JSON-RPC errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Riso custom codes (-32000 to -32099)
    TEMPLATE_NOT_FOUND = -32001
    VALIDATION_FAILED = -32002
    SESSION_NOT_FOUND = -32003
    SESSION_EXPIRED = -32004
    COPIER_ERROR = -32005
    PATH_NOT_FOUND = -32006
    PERMISSION_DENIED = -32007
    OPERATION_TIMEOUT = -32008
    TOO_MANY_REQUESTS = -32009


@dataclass
class MCPError(Exception):
    """Base MCP error with code and structured data."""

    message: str
    code: MCPErrorCode = MCPErrorCode.INTERNAL_ERROR
    data: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP error response format."""
        result: dict[str, Any] = {
            "code": int(self.code),
            "message": self.message,
        }
        if self.data:
            result["data"] = self.data
        return result


class TemplateNotFoundError(MCPError):
    """Raised when template or template file is not found."""

    def __init__(self, path: str) -> None:
        super().__init__(
            message=f"Template not found: {path}",
            code=MCPErrorCode.TEMPLATE_NOT_FOUND,
            data={"path": path},
        )


class ValidationFailedError(MCPError):
    """Raised when answer validation fails."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__(
            message=f"Validation failed with {len(errors)} error(s)",
            code=MCPErrorCode.VALIDATION_FAILED,
            data={"errors": errors},
        )


class SessionNotFoundError(MCPError):
    """Raised when wizard session is not found."""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"Session not found: {session_id}",
            code=MCPErrorCode.SESSION_NOT_FOUND,
            data={"session_id": session_id},
        )


class SessionExpiredError(MCPError):
    """Raised when wizard session has expired."""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"Session expired: {session_id}",
            code=MCPErrorCode.SESSION_EXPIRED,
            data={"session_id": session_id},
        )


class CopierOperationError(MCPError):
    """Raised when a Copier operation fails."""

    def __init__(self, operation: str, details: str) -> None:
        super().__init__(
            message=f"Copier {operation} failed: {details}",
            code=MCPErrorCode.COPIER_ERROR,
            data={"operation": operation, "details": details},
        )


class PathNotFoundError(MCPError):
    """Raised when a path is not found."""

    def __init__(self, path: str) -> None:
        super().__init__(
            message=f"Path not found: {path}",
            code=MCPErrorCode.PATH_NOT_FOUND,
            data={"path": path},
        )


class PermissionDeniedError(MCPError):
    """Raised when an operation is not permitted."""

    def __init__(self, operation: str, reason: str) -> None:
        super().__init__(
            message=f"Permission denied for {operation}: {reason}",
            code=MCPErrorCode.PERMISSION_DENIED,
            data={"operation": operation, "reason": reason},
        )


class TooManyRequestsError(MCPError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        data = {"retry_after": retry_after} if retry_after else None
        super().__init__(
            message=message,
            code=MCPErrorCode.TOO_MANY_REQUESTS,
            data=data,
        )


class OperationTimeoutError(MCPError):
    """Raised when an operation exceeds its timeout."""

    def __init__(
        self,
        operation: str,
        timeout_seconds: int,
        details: str | None = None,
    ) -> None:
        message = f"Operation '{operation}' timed out after {timeout_seconds}s"
        if details:
            message = f"{message}: {details}"

        super().__init__(
            message=message,
            code=MCPErrorCode.OPERATION_TIMEOUT,
            data={
                "operation": operation,
                "timeout_seconds": timeout_seconds,
                "details": details,
            },
        )


class OperationCancelled(MCPError):
    """Raised when an operation is cancelled by user request."""

    def __init__(self, reason: str = "Operation cancelled") -> None:
        super().__init__(
            message=reason,
            code=MCPErrorCode.INTERNAL_ERROR,
            data={"reason": reason},
        )
