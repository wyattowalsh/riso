"""Structured logging utilities for Riso MCP server."""

from __future__ import annotations

import functools
import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields from LogRecord
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            for key, value in record.extra.items():
                log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    json_output: bool = True,
    server_name: str = "riso-mcp",
) -> logging.Logger:
    """Configure structured logging for the MCP server.

    Parameters
    ----------
    level
        Log level (DEBUG, INFO, WARNING, ERROR)
    json_output
        Use JSON format (True) or human-readable (False)
    server_name
        Name to include in log entries (for informational purposes)

    Returns
    -------
    logging.Logger
        Configured logger instance

    Warnings
    --------
    This function modifies the global logger state. In multi-threaded
    environments, ensure this is called during initialization before
    creating worker threads to avoid race conditions.
    """
    # Store server_name as a module-level variable for use in log events
    globals()["_server_name"] = server_name
    logger = logging.getLogger("riso.mcp")
    logger.setLevel(getattr(logging, level.upper()))

    # Clear handlers in a thread-safe manner
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    handler = logging.StreamHandler(sys.stderr)

    if json_output:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    logger.addHandler(handler)
    logger.propagate = False  # Prevent duplicate logs

    return logger


def log_event(
    logger: logging.Logger,
    event: str,
    level: str = "info",
    **kwargs: Any,
) -> None:
    """Log a structured event with additional context.

    Parameters
    ----------
    logger
        Logger instance
    event
        Event name (e.g., "server_started", "tool_called")
    level
        Log level
    **kwargs
        Additional context fields
    """
    extra_data = {"event": event, **kwargs}

    # Create a log record with the extra data
    log_level = getattr(logging, level.upper())
    record = logger.makeRecord(
        logger.name,
        log_level,
        "",
        0,
        event,
        (),
        None,
    )
    record.extra = extra_data
    logger.handle(record)


T = TypeVar("T", bound=Callable[..., Any])


def log_tool_call(logger: logging.Logger | None = None) -> Callable[[T], T]:
    """Decorator to log MCP tool calls with timing and status.

    Parameters
    ----------
    logger
        Optional logger instance. If not provided, uses default riso.mcp logger.

    Returns
    -------
    Callable
        Decorator function

    Example
    -------
    >>> @log_tool_call()
    ... def my_tool(arg1: str) -> dict:
    ...     return {"result": "success"}
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal logger
            if logger is None:
                logger = logging.getLogger("riso.mcp.tools")

            tool_name = func.__name__
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                log_event(
                    logger,
                    "tool_called",
                    level="info",
                    tool_name=tool_name,
                    duration_ms=round(duration * 1000, 2),
                    status="success",
                )

                return result

            except Exception as exc:
                duration = time.time() - start_time

                log_event(
                    logger,
                    "tool_called",
                    level="error",
                    tool_name=tool_name,
                    duration_ms=round(duration * 1000, 2),
                    status="error",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )

                raise

        return wrapper  # type: ignore

    return decorator
