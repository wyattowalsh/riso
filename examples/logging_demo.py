#!/usr/bin/env python3
"""Demo script showing structured logging in action.

Run with: uv run --group mcp python examples/logging_demo.py
"""

import json
import sys

# Add src to path for demo
sys.path.insert(0, "src")

# Import directly to avoid package initialization issues
import importlib.util

spec = importlib.util.spec_from_file_location(
    "logging_module", "src/riso/mcp/logging.py"
)
if spec is None or spec.loader is None:
    raise ImportError("Could not load logging module")
logging_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logging_module)

setup_logging = logging_module.setup_logging
log_event = logging_module.log_event
log_tool_call = logging_module.log_tool_call


def demo_json_logging():
    """Demonstrate JSON structured logging."""
    print("=== JSON Structured Logging Demo ===\n")

    logger = setup_logging(level="INFO", json_output=True)

    # Server startup event
    log_event(
        logger,
        "server_started",
        level="info",
        server="riso-mcp",
        version="1.0.0",
        transport="stdio",
        log_format="json",
    )

    # Session creation event
    log_event(
        logger,
        "session_created",
        level="info",
        session_id="abc123",
        project_name="my-project",
        template_variant="default",
        total_sessions=5,
    )

    # Tool execution event
    log_event(
        logger,
        "tool_called",
        level="info",
        tool_name="copier_copy",
        duration_ms=1234.56,
        status="success",
    )

    # Error event
    log_event(
        logger,
        "error_occurred",
        level="error",
        error_type="ValidationError",
        error_message="Invalid project name",
    )

    print()


def demo_human_logging():
    """Demonstrate human-readable logging."""
    print("=== Human-Readable Logging Demo ===\n")

    logger = setup_logging(level="INFO", json_output=False)

    # Server startup event
    log_event(
        logger,
        "server_started",
        level="info",
        server="riso-mcp",
        version="1.0.0",
    )

    # Session creation event
    log_event(
        logger,
        "session_created",
        level="info",
        session_id="abc123",
        project_name="my-project",
    )

    print()


def demo_tool_decorator():
    """Demonstrate automatic tool call logging."""
    print("=== Tool Call Decorator Demo ===\n")

    logger = setup_logging(level="INFO", json_output=True)

    @log_tool_call(logger=logger)
    def create_project(name: str, template: str) -> dict:
        """Simulate a project creation tool."""
        import time

        time.sleep(0.1)  # Simulate some work
        return {"success": True, "name": name, "template": template}

    @log_tool_call(logger=logger)
    def failing_tool():
        """Simulate a tool that fails."""
        raise ValueError("Something went wrong")

    # Call successful tool
    result = create_project("my-app", "python")
    print(f"\nTool result: {result}")

    # Call failing tool
    print("\nTrying to call failing tool...")
    try:
        failing_tool()
    except ValueError as e:
        print(f"Caught error: {e}")

    print()


def demo_session_events():
    """Demonstrate session-related events."""
    print("=== Session Events Demo ===\n")

    logger = setup_logging(level="INFO", json_output=True)

    # Session created
    log_event(
        logger,
        "session_created",
        level="info",
        session_id="sess_001",
        project_name="web-app",
        template_variant="full-stack",
        total_sessions=3,
    )

    # Session expired
    log_event(
        logger,
        "session_expired",
        level="warning",
        session_id="sess_old",
        age_minutes=65.5,
    )

    # Sessions cleaned up
    log_event(
        logger,
        "sessions_cleaned",
        level="info",
        expired_count=5,
        remaining_sessions=10,
    )

    print()


if __name__ == "__main__":
    demo_json_logging()
    demo_human_logging()
    demo_tool_decorator()
    demo_session_events()

    print("=== Demo Complete ===")
    print(
        "\nKey Features Demonstrated:"
        "\n1. Structured JSON logging with rich context"
        "\n2. Human-readable fallback format"
        "\n3. Automatic tool call timing and error logging"
        "\n4. Session lifecycle event tracking"
    )
