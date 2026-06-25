# Logging Quick Reference

## Configuration

```bash
# Environment variables
export RISO_MCP_LOG_LEVEL=INFO      # DEBUG, INFO, WARNING, ERROR
export RISO_MCP_JSON_LOGS=true      # true for JSON, false for human-readable
```

## Basic Usage

```python
from riso.mcp.logging import setup_logging, log_event, log_tool_call

# Setup
logger = setup_logging(level="INFO", json_output=True)

# Log events
log_event(logger, "event_name", level="info", key="value")

# Tool decorator
@log_tool_call()
def my_tool():
    pass
```

## Event Types

| Event | Level | Use Case |
|-------|-------|----------|
| `server_started` | INFO | Server initialization |
| `server_stopped` | INFO | Server shutdown |
| `tool_called` | INFO/ERROR | Tool execution |
| `session_created` | INFO | New wizard session |
| `session_expired` | WARNING | Session timeout |
| `sessions_cleaned` | INFO | Cleanup operation |
| `error_occurred` | ERROR | General errors |

## Output Formats

**JSON (production):**
```json
{"timestamp": "2026-01-18T17:10:35.676+00:00", "level": "INFO", "event": "server_started"}
```

**Human (development):**
```
2026-01-18 12:10:35,676 - riso.mcp - INFO - server_started
```

## Common Queries

```bash
# Show errors only
riso-mcp 2>&1 | jq 'select(.level == "ERROR")'

# Show tool timings
riso-mcp 2>&1 | jq 'select(.event == "tool_called") | {tool: .tool_name, ms: .duration_ms}'

# Monitor sessions
riso-mcp 2>&1 | jq 'select(.event | startswith("session_"))'

# Count events
riso-mcp 2>&1 | jq -s 'group_by(.event) | map({event: .[0].event, count: length})'
```

## Testing

```bash
# Run tests
uv run --group mcp --group test pytest tests/unit/test_mcp/test_logging.py -v

# Run demo
uv run python examples/logging_demo.py
```
