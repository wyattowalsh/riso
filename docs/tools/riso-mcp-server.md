---
name: Riso MCP Server
type: mcp
category: project-tools
description: MCP server exposing Riso template scaffolding to AI assistants
icon: tabler:template
popularity: 80
tags: [mcp, copier, template, ai, wizard]
install_command: uv sync --group mcp
provided_by: riso
brand_colors: false
---

# Riso MCP Server

The Riso MCP server exposes Copier template scaffolding as MCP tools, resources, and prompts. This enables AI assistants like Claude to create and manage Riso projects.

## Quick Start

```bash
# Install MCP dependencies
uv sync --group mcp

# Run the server (stdio mode)
uv run python -m riso.mcp

# Run with MCP Inspector
npx @modelcontextprotocol/inspector uv run python -m riso.mcp
```

## Configuration

### Environment Variables

| Variable             | Default     | Description                                    |
| -------------------- | ----------- | ---------------------------------------------- |
| `RISO_MCP_TRANSPORT` | `stdio`     | Transport: `stdio`, `sse`, `http`              |
| `RISO_MCP_HOST`      | `127.0.0.1` | Bind address for HTTP/SSE                      |
| `RISO_MCP_PORT`      | `3000`      | Port for HTTP/SSE                              |
| `RISO_MCP_LOG_LEVEL` | `INFO`      | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Adding to Claude Desktop

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "riso": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--group", "mcp", "python", "-m", "riso.mcp"],
      "timeout": 120000
    }
  }
}
```

## Tools

### Copier API Tools

| Tool                        | Description                                   |
| --------------------------- | --------------------------------------------- |
| `copier_copy`               | Create new project from template with answers |
| `copier_update`             | Update existing project with template changes |
| `copier_recopy`             | Regenerate project from scratch               |
| `list_template_variants`    | List all available sample configurations      |
| `validate_template_answers` | Validate answers against schema               |
| `get_prompts`               | Get all template prompts with schemas         |

### Wizard Tools

Interactive multi-step project generation:

| Tool                   | Description                                                |
| ---------------------- | ---------------------------------------------------------- |
| `wizard_start`         | Start new wizard session                                   |
| `wizard_step`          | Submit answers for current step                            |
| `wizard_back`          | Go back to previous step                                   |
| `wizard_status`        | Get current session state                                  |
| `wizard_generate`      | Generate project from completed session (supports `force`) |
| `wizard_cancel`        | Cancel and cleanup session                                 |
| `wizard_list_sessions` | List all active sessions                                   |

### Wizard Workflow Example

```python
# Start a wizard session
result = wizard_start(project_name="my-app", destination="~/projects/my-app")
session_id = result["session_id"]

# Complete each step
wizard_step(session_id, {"project_name": "my-app", "project_layout": "single-package", "project_language": "python"})
wizard_step(session_id, {"quality_profile": "strict", "python_versions": ["3.11", "3.12"]})
wizard_step(session_id, {"cli_module": "enabled", "api_tracks": "python"})

# Generate the project
wizard_generate(session_id)

# Overwrite an existing destination
wizard_generate(session_id, force=True)
```

## Resources

The server exposes the following resources:

| URI                                                      | Description                        |
| -------------------------------------------------------- | ---------------------------------- |
| `riso://template/copier.yml`                             | Main template configuration        |
| `riso://template/files/python/pyproject.toml.jinja`      | Python pyproject template          |
| `riso://template/files/shared/module_catalog.json.jinja` | Module catalog template            |
| `riso://template/hooks/pre_gen_project.py`               | Pre-generation hook                |
| `riso://template/hooks/post_gen_project.py`              | Post-generation hook               |
| `riso://template/structure`                              | Template file tree (depth-limited) |
| `riso://samples`                                         | List of sample variants            |
| `riso://samples/default/answers`                         | Default sample answers             |
| `riso://samples/full-stack/answers`                      | Full-stack sample answers          |
| `riso://samples/monorepo/answers`                        | Monorepo sample answers            |
| `riso://samples/metadata/render_matrix.json`             | Render matrix metadata             |
| `riso://samples/metadata/module_success.json`            | Module success rates               |
| `riso://catalog/modules`                                 | Full module catalog (markdown)     |
| `riso://catalog/modules.json`                            | Full module catalog (JSON)         |
| `riso://catalog/prompts`                                 | Prompt catalog (markdown)          |
| `riso://catalog/dependencies`                            | Dependency map                     |

## Prompts

Pre-built workflow prompts:

| Prompt             | Description                 |
| ------------------ | --------------------------- |
| `new_project`      | Guided new project creation |
| `update_existing`  | Update project workflow     |
| `full_stack_setup` | Full-stack configuration    |
| `mcp_server_setup` | New MCP server project      |
| `quality_setup`    | Quality tools configuration |

## Error Codes

MCP-compliant error codes:

| Code   | Name                 | Description                |
| ------ | -------------------- | -------------------------- |
| -32001 | `TEMPLATE_NOT_FOUND` | Template or file not found |
| -32002 | `VALIDATION_FAILED`  | Answer validation failed   |
| -32003 | `SESSION_NOT_FOUND`  | Wizard session not found   |
| -32004 | `SESSION_EXPIRED`    | Session has expired        |
| -32005 | `COPIER_ERROR`       | Copier operation failed    |
| -32006 | `PATH_NOT_FOUND`     | Path does not exist        |
| -32007 | `PERMISSION_DENIED`  | Operation not permitted    |

## Architecture

```
src/riso/mcp/
├── __init__.py              # Package exports
├── __main__.py              # Module entry point
├── server.py                # FastMCP server
├── config.py                # Pydantic configuration
├── session.py               # Wizard session management
├── errors.py                # MCP error types
├── tools/
│   ├── __init__.py          # Tool registration
│   ├── copier_api.py        # Copier API tools
│   └── wizard.py            # Wizard tools
├── resources/
│   ├── __init__.py
│   ├── templates.py         # Template resources
│   ├── samples.py           # Sample resources
│   └── catalog.py           # Catalog resources
└── prompts/
    ├── __init__.py
    └── workflows.py         # Workflow prompts
```

## Development

### Running Tests

```bash
# Run MCP unit tests
uv run pytest tests/unit/test_mcp/ -v

# With coverage
uv run pytest tests/unit/test_mcp/ --cov=src/riso/mcp
```

### Adding New Tools

```python
# In src/riso/mcp/tools/my_tool.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_my_tools(mcp: "FastMCP") -> None:
    @mcp.tool()
    def my_tool(param: str) -> dict:
        """My tool description."""
        return {"result": param}
```

### Transport Options

```bash
# stdio (default)
uv run python -m riso.mcp

# SSE (Server-Sent Events)
uv run python -m riso.mcp --transport sse --port 3000

# HTTP (streamable)
uv run python -m riso.mcp --transport http --port 3000
```
