---
name: FastMCP
type: mcp
category: optional-modules
description: Model Context Protocol server framework for Python
icon: tabler:robot
popularity: 85
homepage: https://github.com/jlowin/fastmcp
repository: https://github.com/jlowin/fastmcp
tags: [python, mcp, llm, tools, ai]
install_command: uv add fastmcp
provided_by: external
brand_colors: false
---

# FastMCP

FastMCP is a Python framework for building Model Context Protocol (MCP) servers. MCP enables AI assistants like Claude to interact with external tools and services.

## Features

- **Decorator-based**: Simple `@mcp.tool()` decorators for tool definitions
- **Type-safe**: Automatic Pydantic validation for inputs and outputs
- **Resources**: Expose data resources with URIs to LLMs
- **Prompts**: Define reusable prompts with parameters
- **Multi-transport**: stdio, SSE, and HTTP streaming support
- **Schema generation**: Automatic JSON Schema from type hints

## Usage in Riso

### Enable MCP Module

When generating a project with Copier:

```yaml
mcp_module: enabled
mcp_languages:
  - python  # python, typescript, or rust
mcp_transport: stdio  # stdio, sse, or http
mcp_example_tools: true
```

### Generated Structure

```
src/{package_name}/mcp/
├── __init__.py          # Package exports
├── __main__.py          # Module entry point
├── server.py            # FastMCP server initialization
├── config.py            # Pydantic configuration
├── errors.py            # MCP error types
├── tools/
│   ├── __init__.py      # Tool registration
│   ├── echo.py          # Example: message echoing
│   ├── timestamp.py     # Example: time utilities
│   └── http_fetch.py    # Example: web content retrieval
├── resources/           # Resource providers
└── prompts/             # Prompt templates
```

### Running the Server

```bash
# stdio mode (default, for Claude Desktop)
uv run python -m {package_name}.mcp

# SSE mode (for web clients)
uv run python -m {package_name}.mcp --transport sse --port 3000

# HTTP streaming mode
uv run python -m {package_name}.mcp --transport http --port 3000

# With MCP Inspector
npx @modelcontextprotocol/inspector uv run python -m {package_name}.mcp
```

## Example Tool

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def search(query: str, limit: int = 10) -> list[dict]:
    """Search for information.

    Parameters
    ----------
    query
        Search query string
    limit
        Maximum results to return

    Returns
    -------
    list[dict]
        Search results with title and url
    """
    # Implementation...
    return [{"title": "Result", "url": "https://..."}]

@mcp.tool()
async def fetch_url(url: str) -> dict:
    """Fetch content from a URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return {"status": response.status_code, "content": response.text[:1000]}
```

## Example Resource

```python
@mcp.resource("app://config/{section}")
def get_config(section: str) -> str:
    """Return configuration for a section."""
    config = load_config()
    return json.dumps(config.get(section, {}))
```

## Example Prompt

```python
@mcp.prompt()
def code_review(language: str = "python", focus: str = "quality") -> str:
    """Guide through a code review."""
    return f"""Please review the following {language} code.

Focus areas:
- {focus}
- Security considerations
- Performance implications

Provide specific, actionable feedback.
"""
```

## Configuration

```python
from pydantic_settings import BaseSettings

class MCPConfig(BaseSettings):
    model_config = {"env_prefix": "MY_MCP_"}

    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 3000
    log_level: str = "INFO"
```

## Claude Desktop Integration

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "my_package.mcp"],
      "timeout": 60000
    }
  }
}
```

## Related

- [Riso MCP Server](riso-mcp-server.md) - Riso's project-level MCP server
- [MCP Specification](https://modelcontextprotocol.io/) - Official protocol documentation
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - Framework documentation

## Template Languages

Riso supports MCP server generation in multiple languages:

| Language   | Framework  | When to Use                               |
| ---------- | ---------- | ----------------------------------------- |
| Python     | FastMCP v2 | Python projects, AI/ML integration        |
| TypeScript | FastMCP    | Node.js projects, web services            |
| Rust       | rmcp SDK   | Systems programming, performance-critical |
