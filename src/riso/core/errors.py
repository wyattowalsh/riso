"""Riso error types for CLI and template operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class ExitCode(IntEnum):
    """CLI exit codes."""

    SUCCESS = 0
    OPERATIONAL_FAILURE = 1
    USAGE_OR_VALIDATION = 2
    INTERRUPTED = 130


@dataclass
class RisoError(Exception):
    """Base Riso error with structured data."""

    message: str
    exit_code: ExitCode = ExitCode.OPERATIONAL_FAILURE
    data: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


class TemplateNotFoundError(RisoError):
    """Raised when template or template file is not found."""

    def __init__(self, path: str) -> None:
        super().__init__(
            message=f"Template not found: {path}",
            exit_code=ExitCode.USAGE_OR_VALIDATION,
            data={"path": path},
        )


class ValidationFailedError(RisoError):
    """Raised when answer validation fails."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__(
            message=f"Validation failed with {len(errors)} error(s)",
            exit_code=ExitCode.USAGE_OR_VALIDATION,
            data={"errors": errors},
        )


class CopierOperationError(RisoError):
    """Raised when a Copier operation fails."""

    def __init__(self, operation: str, details: str) -> None:
        super().__init__(
            message=f"Copier {operation} failed: {details}",
            exit_code=ExitCode.OPERATIONAL_FAILURE,
            data={"operation": operation, "details": details},
        )


class PathNotFoundError(RisoError):
    """Raised when a path is not found."""

    def __init__(self, path: str) -> None:
        super().__init__(
            message=f"Path not found: {path}",
            exit_code=ExitCode.USAGE_OR_VALIDATION,
            data={"path": path},
        )


class PermissionDeniedError(RisoError):
    """Raised when an operation is not permitted."""

    def __init__(self, operation: str, reason: str) -> None:
        super().__init__(
            message=f"Permission denied for {operation}: {reason}",
            exit_code=ExitCode.USAGE_OR_VALIDATION,
            data={"operation": operation, "reason": reason},
        )


class OperationTimeoutError(RisoError):
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
            exit_code=ExitCode.OPERATIONAL_FAILURE,
            data={
                "operation": operation,
                "timeout_seconds": timeout_seconds,
                "details": details,
            },
        )


class OperationCancelled(RisoError):
    """Raised when an operation is cancelled."""

    def __init__(self, reason: str = "Operation cancelled") -> None:
        super().__init__(
            message=reason,
            exit_code=ExitCode.INTERRUPTED,
            data={"reason": reason},
        )
