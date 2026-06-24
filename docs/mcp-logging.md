# Structured Logging in Riso MCP Server

The Riso MCP server includes comprehensive structured logging support for better observability and debugging.

## Overview

The logging system provides:

- **Structured JSON logging** for machine parsing and log aggregation
- **Human-readable fallback** for development and debugging
- **Automatic tool call tracking** with timing and error details
- **Session lifecycle events** for monitoring user activity
- **Configurable log levels** and output formats

## Configuration

Configure logging through environment variables or config file:

```bash
# Environment variables
export RISO_MCP_LOG_LEVEL=INFO      # DEBUG, INFO, WARNING, ERROR
export RISO_MCP_JSON_LOGS=true      # true for JSON, false for human-readable
```

Or in `riso-mcp.toml`:

```toml
log_level = "INFO"
json_logs = true
```

## Log Event Types

### Server Events

**server_started** - Server initialization
```json
{
  "timestamp": "2026-01-18T17:10:35.676433+00:00",
  "level": "INFO",
  "logger": "riso.mcp",
  "message": "server_started",
  "event": "server_started",
  "server": "riso-mcp",
  "version": "1.0.0",
  "transport": "stdio",
  "host": null,
  "port": null,
  "log_format": "json"
}
```

**server_stopped** - Server shutdown
```json
{
  "event": "server_stopped",
  "level": "INFO",
  "reason": "user_interrupt"
}
```

### Tool Events

**tool_called** - Tool execution (success)
```json
{
  "timestamp": "2026-01-18T17:10:35.676876+00:00",
  "level": "INFO",
  "event": "tool_called",
  "tool_name": "copier_copy",
  "duration_ms": 123.45,
  "status": "success"
}
```

**tool_called** - Tool execution (error)
```json
{
  "timestamp": "2026-01-18T17:10:35.676929+00:00",
  "level": "ERROR",
  "event": "tool_called",
  "tool_name": "copier_copy",
  "duration_ms": 45.67,
  "status": "error",
  "error_type": "ValidationError",
  "error_message": "Invalid project name"
}
```

### Session Events

**session_created** - New wizard session
```json
{
  "event": "session_created",
  "level": "INFO",
  "session_id": "abc123",
  "project_name": "my-project",
  "template_variant": "default",
  "total_sessions": 5
}
```

**session_expired** - Session timeout
```json
{
  "event": "session_expired",
  "level": "WARNING",
  "session_id": "old_session",
  "age_minutes": 65.5
}
```

**sessions_cleaned** - Cleanup operation
```json
{
  "event": "sessions_cleaned",
  "level": "INFO",
  "expired_count": 3,
  "remaining_sessions": 7
}
```

### Error Events

**error_occurred** - General errors
```json
{
  "event": "error_occurred",
  "level": "ERROR",
  "error_type": "CopierOperationError",
  "error_message": "Failed to generate project"
}
```

## Using the Logging API

### Basic Setup

```python
from riso.mcp.logging import setup_logging, log_event

# Initialize logger
logger = setup_logging(
    level="INFO",
    json_output=True,
    server_name="riso-mcp"
)

# Log an event
log_event(
    logger,
    "custom_event",
    level="info",
    user_id="123",
    action="created"
)
```

### Tool Call Decorator

Automatically log tool calls with timing:

```python
from riso.mcp.logging import log_tool_call

@log_tool_call()
def my_tool(arg: str) -> dict:
    """Your tool implementation."""
    return {"result": arg}

# Automatically logs:
# - Tool name
# - Execution duration
# - Success/failure status
# - Error details (if failed)
```

### Custom Events

```python
from riso.mcp.logging import log_event

log_event(
    logger,
    "project_generated",
    level="info",
    project_name="my-app",
    template="python",
    modules=["cli", "api"],
    duration_seconds=2.5
)
```

## Output Formats

### JSON Format (json_logs=true)

```json
{
  "timestamp": "2026-01-18T17:10:35.676433+00:00",
  "level": "INFO",
  "logger": "riso.mcp",
  "message": "server_started",
  "event": "server_started",
  "server": "riso-mcp",
  "version": "1.0.0"
}
```

**Benefits:**
- Machine-parsable for log aggregation
- Works with tools like Elasticsearch, Splunk
- Easy to filter and analyze
- Structured context fields

### Human-Readable Format (json_logs=false)

```
2026-01-18 12:10:35,676 - riso.mcp - INFO - server_started
```

**Benefits:**
- Easy to read during development
- Good for local debugging
- No JSON parsing required
- Familiar format

## Best Practices

1. **Use appropriate log levels:**
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Warning messages (e.g., session expired)
   - ERROR: Error conditions

2. **Include relevant context:**
   ```python
   log_event(
       logger,
       "operation_completed",
       level="info",
       operation="copy",
       duration_ms=1234,
       files_created=42,
       destination="/path/to/project"
   )
   ```

3. **Use the decorator for tools:**
   ```python
   @log_tool_call()  # Automatic timing and error logging
   def my_tool():
       pass
   ```

4. **Enable JSON in production:**
   - Set `json_logs=true` for production environments
   - Use human-readable format for local development

5. **Monitor key events:**
   - Server startup/shutdown
   - Session creation/expiration
   - Tool execution times
   - Error rates

## Integration Examples

### Log Aggregation (ELK Stack)

```python
# Configure for Elasticsearch
logger = setup_logging(
    level="INFO",
    json_output=True  # JSON format for Logstash
)
```

Ship logs to Logstash:
```bash
riso-mcp 2>&1 | logstash -f logstash.conf
```

### Monitoring (Prometheus)

Parse JSON logs to expose metrics:
```python
# Count tool calls by status
tool_calls_total{status="success"} 150
tool_calls_total{status="error"} 5

# Track session metrics
sessions_active 10
sessions_created_total 50
```

### Debugging

```bash
# Show only errors
riso-mcp 2>&1 | jq 'select(.level == "ERROR")'

# Show tool execution times
riso-mcp 2>&1 | jq 'select(.event == "tool_called") | {tool: .tool_name, ms: .duration_ms}'

# Monitor session activity
riso-mcp 2>&1 | jq 'select(.event | startswith("session_"))'
```

## Testing

Run the logging tests:

```bash
uv run pytest tests/unit/test_mcp/test_logging.py -v
```

Run the demo:

```bash
uv run --group mcp python examples/logging_demo.py
```

## See Also

- [MCP Server Configuration](api/mcp/config.md)
- [Error Handling](api/mcp/errors.md)
- [Session Management](api/mcp/session.md)
