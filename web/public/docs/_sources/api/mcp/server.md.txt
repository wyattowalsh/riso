# Server Module

Core MCP server implementation providing the main server loop and tool/resource registration.

```{eval-rst}
.. automodule:: riso.mcp.server
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Key Components

The server module implements the main MCP server class and provides:

- Server initialization and startup
- Tool registration (Copier API, Wizard, Validation)
- Resource registration (Samples, Templates, Catalog)
- Request handling and routing
- Error handling and logging

## Usage

The server can be started directly or embedded in other applications:

```python
from riso.mcp.server import create_server

# Create and run the server
server = create_server()
# Server runs via MCP protocol (stdio, sse, or other transports)
```

## Configuration

Server behavior can be customized through environment variables and configuration files.
See {doc}`config` for details.
