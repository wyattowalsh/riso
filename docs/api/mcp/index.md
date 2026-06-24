# MCP Server API

The Model Context Protocol (MCP) server provides tools for project scaffolding and template management.

## Overview

The Riso MCP server exposes the Copier templating system as AI-accessible tools, enabling:

- Interactive project generation through guided wizards
- Programmatic template rendering via direct Copier API calls
- Template validation and answer management
- Session persistence for multi-step workflows

## Architecture

The MCP server is organized into several key modules:

- **Server**: Core MCP server implementation and initialization
- **Tools**: AI-accessible tool definitions (Copier API, Wizard)
- **Resources**: Template metadata, sample variants, and catalogs
- **Session**: Session state management for wizard workflows
- **Config**: Server configuration and settings
- **Errors**: Custom exception types

```{toctree}
:maxdepth: 2

server
tools
resources
session
config
errors
prompts
```

## Quick Start

Start the MCP server:

```bash
uv run python -m riso.mcp
```

Or use it as an MCP server in supported AI tools (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "riso": {
      "command": "uv",
      "args": ["run", "python", "-m", "riso.mcp"]
    }
  }
}
```

## Tools Reference

- {py:func}`~riso.mcp.tools.copier_api.copier_copy` - Generate new projects
- {py:func}`~riso.mcp.tools.copier_api.copier_update` - Update existing projects
- {py:func}`~riso.mcp.tools.copier_api.copier_recopy` - Regenerate projects
- {py:func}`~riso.mcp.tools.wizard.wizard_start` - Start interactive wizard
- {py:func}`~riso.mcp.tools.wizard.wizard_step` - Submit wizard step answers

## Resources Reference

- `sample://variants` - List available sample project variants
- `template://prompts` - Get template prompt schemas
- `catalog://modules` - Browse module catalog
