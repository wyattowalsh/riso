"""Tests for structured logging utilities."""

from __future__ import annotations

import json
import logging
from io import StringIO
from typing import Any

import pytest

from riso.mcp.logging import (
    StructuredFormatter,
    log_event,
    log_tool_call,
    setup_logging,
)


class TestStructuredFormatter:
    """Test JSON log formatter."""

    def test_format_basic_log(self) -> None:
        """Test basic log formatting."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "test message"
        assert "timestamp" in data

    def test_format_with_extra(self) -> None:
        """Test formatting with extra fields."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.extra = {"user_id": "123", "action": "create"}

        output = formatter.format(record)
        data = json.loads(output)

        assert data["user_id"] == "123"
        assert data["action"] == "create"


class TestSetupLogging:
    """Test logger setup."""

    def test_setup_json_logging(self) -> None:
        """Test JSON logging setup."""
        logger = setup_logging(level="DEBUG", json_output=True)

        assert logger.name == "riso.mcp"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, StructuredFormatter)

    def test_setup_human_logging(self) -> None:
        """Test human-readable logging setup."""
        logger = setup_logging(level="INFO", json_output=False)

        assert logger.name == "riso.mcp"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert not isinstance(logger.handlers[0].formatter, StructuredFormatter)

    def test_multiple_setup_no_duplicate_handlers(self) -> None:
        """Test that multiple setups don't create duplicate handlers."""
        logger1 = setup_logging()
        logger2 = setup_logging()

        assert logger1 is logger2
        assert len(logger1.handlers) == 1


class TestLogEvent:
    """Test structured event logging."""

    def test_log_event_basic(self) -> None:
        """Test basic event logging."""
        logger = logging.getLogger("test_events")
        logger.handlers = []
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

        log_event(logger, "test_event", level="info", user_id="123")

        output = stream.getvalue()
        data = json.loads(output)

        assert data["event"] == "test_event"
        assert data["user_id"] == "123"
        assert data["level"] == "INFO"

    def test_log_event_with_kwargs(self) -> None:
        """Test event logging with multiple kwargs."""
        logger = logging.getLogger("test_events_kwargs")
        logger.handlers = []
        logger.setLevel(logging.DEBUG)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

        log_event(
            logger,
            "server_started",
            level="info",
            server="test-server",
            version="1.0.0",
            transport="stdio",
        )

        output = stream.getvalue()
        data = json.loads(output)

        assert data["event"] == "server_started"
        assert data["server"] == "test-server"
        assert data["version"] == "1.0.0"
        assert data["transport"] == "stdio"


class TestLogToolCall:
    """Test tool call logging decorator."""

    def test_log_tool_call_success(self) -> None:
        """Test successful tool call logging."""
        logger = logging.getLogger("test_tools")
        logger.handlers = []
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

        @log_tool_call(logger=logger)
        def test_tool(arg: str) -> dict[str, Any]:
            return {"result": arg}

        result = test_tool("test")

        assert result == {"result": "test"}

        output = stream.getvalue()
        data = json.loads(output)

        assert data["event"] == "tool_called"
        assert data["tool_name"] == "test_tool"
        assert data["status"] == "success"
        assert "duration_ms" in data
        assert data["duration_ms"] >= 0

    def test_log_tool_call_error(self) -> None:
        """Test tool call logging on error."""
        logger = logging.getLogger("test_tools_error")
        logger.handlers = []
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

        @log_tool_call(logger=logger)
        def failing_tool() -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            failing_tool()

        output = stream.getvalue()
        data = json.loads(output)

        assert data["event"] == "tool_called"
        assert data["tool_name"] == "failing_tool"
        assert data["status"] == "error"
        assert data["error_type"] == "ValueError"
        assert data["error_message"] == "test error"
        assert "duration_ms" in data

    def test_log_tool_call_default_logger(self) -> None:
        """Test tool call decorator with default logger."""

        @log_tool_call()
        def tool_with_default_logger() -> str:
            return "success"

        result = tool_with_default_logger()
        assert result == "success"
