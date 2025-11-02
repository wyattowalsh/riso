# Python MCP API Contract

**Feature**: 013-mcp-servers | **Language**: Python | **Date**: 2025-11-02

## Overview

This document defines the API contract for Python MCP servers using FastMCP. It specifies the expected interfaces, method signatures, and behavior for all MCP protocol operations.

## Server Interface

### Server Initialization

```python
from fastmcp import FastMCP
from typing import Optional

# Create server instance
mcp = FastMCP(
    name: str,                    # Server identifier (required)
    version: str = "1.0.0",       # Semantic version (optional, default: "1.0.0")
    description: Optional[str] = None  # Server description (optional)
)
```

**Contract**:
- Server name must match `^[a-z0-9-]+$`
- Version must follow semver format `^\d+\.\d+\.\d+$`
- Server instance is singleton per process

---

## Tool Registration

### Tool Decorator

```python
from pydantic import BaseModel, Field
from typing import Annotated

@mcp.tool()
async def tool_name(
    param1: Annotated[str, Field(description="Parameter description")],
    param2: Annotated[int, Field(ge=0, le=100)]
) -> str:
    """
    Tool description that appears in MCP protocol.
    
    This docstring becomes the tool's description field.
    """
    # Implementation
    return "result"
```

**Contract**:
- Decorator: `@mcp.tool()`
- Function name becomes tool name (must match `^[a-z][a-z0-9_]*$`)
- Parameters must have type hints (Pydantic types recommended)
- Function must be async (`async def`)
- Docstring becomes tool description (first line summary, rest is details)
- Return type hint optional but recommended
- Raises `McpError` for business logic errors
- Raises `ValidationError` for input validation failures (handled automatically)

### Tool with Complex Input

```python
class ToolInput(BaseModel):
    """Input schema for complex tool"""
    required_field: str = Field(..., description="Required string field")
    optional_field: int | None = Field(None, ge=0, description="Optional int ≥ 0")
    nested: dict[str, any] = Field(default_factory=dict)

@mcp.tool()
async def complex_tool(input: ToolInput) -> dict:
    """Process complex input and return structured output."""
    return {
        "processed": input.required_field,
        "count": input.optional_field or 0
    }
```

**Contract**:
- Pydantic models generate JSON Schema automatically
- Field descriptions become schema descriptions
- Constraints (ge, le, max_length, etc.) enforced automatically
- Return type can be dict, list, BaseModel, or primitive

---

## Resource Registration

### Resource Decorator

```python
@mcp.resource("resource://resource_name")
async def resource_name() -> str:
    """Resource description."""
    return "resource content"
```

**Contract**:
- Decorator: `@mcp.resource(uri: str)`
- URI must be valid (e.g., `resource://name`, `file:///{path}`)
- Function must be async
- Return type: `str`, `bytes`, or Pydantic model (serialized to JSON)
- Docstring becomes resource description

### Dynamic Resource with Parameters

```python
@mcp.resource("file:///{path}")
async def file_browser(path: str) -> dict:
    """Browse files at the specified path."""
    # Extract {path} parameter from URI
    import os
    return {
        "path": path,
        "contents": os.listdir(path)
    }
```

**Contract**:
- URI parameters in `{brackets}` become function parameters
- Parameter extraction handled by FastMCP automatically
- Must validate parameters (check path exists, authorized, etc.)
- Return mime type inferred from content (override with `@mcp.resource(uri, mime_type="...")`)

---

## Prompt Registration

### Prompt Decorator

```python
from fastmcp import Message

@mcp.prompt()
async def prompt_name(
    required_param: str,
    optional_param: str = "default"
) -> list[Message]:
    """Prompt description."""
    return [
        Message(role="system", content="System message"),
        Message(role="user", content=f"User message with {required_param}")
    ]
```

**Contract**:
- Decorator: `@mcp.prompt()`
- Function must be async
- Return type: `list[Message]` where `Message` has `role` and `content` fields
- Roles: `"system"`, `"user"`, or `"assistant"`
- Parameters can have defaults (making them optional in prompt invocation)

---

## Error Handling

### Raising MCP Errors

```python
from fastmcp import McpError

@mcp.tool()
async def may_fail(param: str) -> str:
    if not param:
        raise McpError(
            code=-32602,  # Invalid params
            message="Parameter cannot be empty",
            data={"param": "param"}
        )
    
    try:
        # Operation that may fail
        result = await risky_operation(param)
    except Exception as e:
        # Log full error server-side
        logger.error(f"Tool failed", exc_info=e)
        # Return sanitized error to client
        raise McpError(
            code=-32603,  # Internal error
            message="Operation failed",
            data={"hint": "Check server logs"}
        )
    
    return result
```

**Contract**:
- Use `McpError` for expected/business logic errors
- Error codes:
  - `-32700`: Parse error
  - `-32600`: Invalid request
  - `-32601`: Method not found
  - `-32602`: Invalid params
  - `-32603`: Internal error
  - `-32000` to `-32099`: Custom MCP errors
- Uncaught exceptions converted to Internal error (-32603) automatically
- Production mode: stack traces never sent to client (only logged)

---

## Configuration

### Loading Configuration

```python
from pathlib import Path
import tomli

def load_config(config_path: Path = Path("config.toml")) -> dict:
    """Load TOML configuration with environment overrides."""
    with open(config_path, "rb") as f:
        config = tomli.load(f)
    
    # Override with environment variables
    import os
    if log_level := os.getenv("MCP_LOG_LEVEL"):
        config["server"]["log_level"] = log_level
    
    return config
```

**Contract**:
- Configuration file: `config.toml` (TOML format)
- Environment variables override file settings
- Prefix: `MCP_SERVER_*` or `MCP_*`
- Validation: Pydantic model recommended for type safety

### Configuration Schema

```toml
[server]
name = "my-mcp-server"
version = "1.0.0"
log_level = "INFO"  # DEBUG|INFO|WARNING|ERROR|CRITICAL

[transport]
type = "stdio"  # or "http"
host = "0.0.0.0"  # HTTP only
port = 8000      # HTTP only

[timeouts]
tool = 30      # seconds
resource = 10
prompt = 5

[limits]
max_response_size_mb = 100
rate_limit_per_minute = 100  # HTTP only
rate_limit_burst = 20        # HTTP only
```

**Contract**:
- All sections optional (defaults provided)
- TOML syntax: valid TOML file required
- Validation: Server fails fast on startup if invalid

---

## Transport

### STDIO Transport (Default)

```python
import asyncio
from fastmcp import FastMCP

mcp = FastMCP("my-server")

# Register capabilities...

if __name__ == "__main__":
    # Run server with STDIO transport
    mcp.run()  # Reads from stdin, writes to stdout
```

**Contract**:
- Stdin: newline-delimited JSON-RPC messages
- Stdout: newline-delimited JSON-RPC responses
- Stderr: Logs (not part of protocol)
- EOF on stdin triggers graceful shutdown

### HTTP Transport

```python
from fastmcp import FastMCP
from fastmcp.transports import HTTPTransport

mcp = FastMCP("my-server")

# Register capabilities...

if __name__ == "__main__":
    transport = HTTPTransport(host="0.0.0.0", port=8000)
    mcp.run(transport=transport)
```

**Contract**:
- HTTP endpoints:
  - `POST /mcp/tools/call` - Invoke tool
  - `POST /mcp/resources/read` - Fetch resource
  - `POST /mcp/prompts/get` - Get prompt
  - `GET /mcp/sse` - Server-Sent Events stream
- Request body: JSON-RPC 2.0 message
- Response: JSON-RPC 2.0 response
- CORS: Configurable via `cors_enabled=True`
- Auth: Middleware hook for Bearer tokens/API keys

---

## Logging

### Structured Logging with Loguru

```python
from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

# Usage in tool
@mcp.tool()
async def logged_tool(param: str) -> str:
    logger.info("Tool invoked", extra={"tool": "logged_tool", "param": param})
    result = await process(param)
    logger.info("Tool completed", extra={"result": result})
    return result
```

**Contract**:
- Use Loguru for all logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structured logs: Use `extra={}` for context
- Production: INFO level, JSON format
- Development: DEBUG level, human-readable format
- Required fields: timestamp, level, message, correlation_id (if applicable)

---

## Testing

### Unit Test Example

```python
import pytest
from fastmcp import FastMCP

@pytest.fixture
def mcp_server():
    mcp = FastMCP("test-server")
    
    @mcp.tool()
    async def echo(message: str) -> str:
        """Echo the message."""
        return message
    
    return mcp

@pytest.mark.asyncio
async def test_tool_invocation(mcp_server):
    """Test tool can be invoked and returns expected result."""
    result = await mcp_server.call_tool("echo", {"message": "hello"})
    assert result == "hello"
```

**Contract**:
- Use pytest with pytest-asyncio
- Mock external dependencies (APIs, file systems)
- Test tool logic in isolation (no transport layer)
- Integration tests use real STDIO pipes or HTTP requests

---

## Lifecycle Hooks

### Server Lifecycle

```python
@mcp.on_startup
async def startup():
    """Called when server starts."""
    logger.info("Server starting")
    # Initialize connections, load resources, etc.

@mcp.on_shutdown
async def shutdown():
    """Called when server shuts down."""
    logger.info("Server shutting down")
    # Close connections, save state, etc.
```

**Contract**:
- `@mcp.on_startup`: Called once after server initialization, before accepting requests
- `@mcp.on_shutdown`: Called once during graceful shutdown
- Both must be async functions
- Exceptions in startup prevent server from starting
- Exceptions in shutdown are logged but don't prevent shutdown

---

## Performance Requirements

From specification and clarifications:

**Timeouts**:
- Tool operations: 30 seconds default (configurable)
- Resource fetches: 10 seconds default
- Prompt rendering: 5 seconds default

**Size Limits**:
- Response size: 100MB maximum (configurable via `MAX_RESPONSE_SIZE_MB`)
- Memory: <100MB per in-flight request

**Concurrency**:
- Handle 100 concurrent requests without errors (SC-007)
- Rate limiting (HTTP only): 100 requests/minute, burst of 20

**Startup**:
- Server ready within 5 seconds of launch

---

## Example Complete Server

```python
from fastmcp import FastMCP, Message, McpError
from pydantic import BaseModel, Field
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

# Create server
mcp = FastMCP("example-server", version="1.0.0")

# Tool example
class EchoInput(BaseModel):
    message: str = Field(..., description="Message to echo back")

@mcp.tool()
async def echo(input: EchoInput) -> str:
    """Echo the input message back to the caller."""
    logger.info("Echo tool invoked", extra={"message": input.message})
    return input.message

# Resource example
@mcp.resource("resource://about")
async def about() -> dict:
    """Server information."""
    return {
        "name": "example-server",
        "version": "1.0.0",
        "capabilities": ["tools", "resources", "prompts"]
    }

# Prompt example
@mcp.prompt()
async def greeting(name: str = "friend") -> list[Message]:
    """Generate a friendly greeting."""
    return [
        Message(role="system", content="You are a friendly assistant."),
        Message(role="user", content=f"Greet {name} warmly.")
    ]

if __name__ == "__main__":
    logger.info("Starting MCP server")
    mcp.run()
```

This contract defines all required interfaces for Python MCP servers and ensures consistency across implementations.
