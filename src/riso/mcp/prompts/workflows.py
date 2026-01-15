"""Pre-built workflow prompts for MCP.

Provides guided workflows for common project setup scenarios.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_workflow_prompts(mcp: FastMCP) -> None:
    """Register workflow prompts with the MCP server.

    Prompts registered:
    - new_project - Guided new project creation
    - update_existing - Update project workflow
    - full_stack_setup - Full-stack configuration
    - mcp_server_setup - New MCP server project

    Parameters
    ----------
    mcp
        FastMCP server instance
    """

    @mcp.prompt()
    def new_project(
        name: str = "",
        layout: str = "single-package",
    ) -> str:
        """Guide through creating a new Riso project.

        Parameters
        ----------
        name
            Project name to use (leave empty for interactive selection)
        layout
            Project layout: "single-package" or "monorepo"

        Returns
        -------
        str
            Guided workflow instructions
        """
        intro = f"""# Create a New Riso Project

Let's set up your new project{"" if not name else f" called '{name}'"}.

## Step 1: Project Basics

{"You've chosen: " + name if name else "First, let's decide on a project name."}
Layout: {layout}

## Step 2: Choose Your Stack

What features do you need?

### API Options
- **Python API**: FastAPI with async support, OpenAPI docs
- **Node API**: Fastify with TypeScript
- **Both**: Full-stack with shared types

### Additional Modules
- **CLI**: Typer-based command line interface
- **MCP**: Model Context Protocol server
- **WebSocket**: Real-time communication
- **GraphQL**: Strawberry GraphQL layer

## Step 3: Documentation

Choose your docs platform:
- **Fumadocs**: Next.js 15 with MDX, best for interactive docs
- **Sphinx Shibuya**: Python-native with API autodocs
- **Docusaurus**: React-based with versioning

## Step 4: Quality Profile

- **Standard**: Balanced lint rules, essential checks
- **Strict**: Maximum strictness, all optional checks enabled

---

To proceed, use the `wizard_start` tool:
```
wizard_start(project_name="{name or "my-project"}", destination="~/projects/{name or "my-project"}")
```

Or use `copier_copy` for a quick start with defaults:
```
copier_copy(destination="~/projects/{name or "my-project"}", answers={{"project_name": "{name or "my-project"}"}})
```
"""
        return intro

    @mcp.prompt()
    def update_existing(project_path: str = "") -> str:
        """Guide through updating an existing project.

        Parameters
        ----------
        project_path
            Path to existing project

        Returns
        -------
        str
            Update workflow instructions
        """
        return f"""# Update Existing Riso Project

{"Path: " + project_path if project_path else "Specify the path to your existing Riso project."}

## What Gets Updated

When you update a project, Copier will:
1. Apply new template features and fixes
2. Update configuration files with new options
3. Preserve your custom code and settings

## Before You Update

1. **Commit your changes**: Ensure your working directory is clean
2. **Check the changelog**: Review what's new in the template
3. **Backup important files**: Just in case

## Update Options

### Standard Update (recommended)
Applies changes while keeping your existing answers:
```
copier_update(destination="{project_path or "/path/to/project"}")
```

### Re-prompt Update
Re-asks questions even if they have answers:
```
copier_update(destination="{project_path or "/path/to/project"}", skip_answered=False)
```

### Full Recopy
Regenerates everything (for major version updates):
```
copier_recopy(destination="{project_path or "/path/to/project"}")
```

## After Updating

1. Run `uv sync` to update dependencies
2. Run `make quality` to verify everything works
3. Review git diff for any conflicts
"""

    @mcp.prompt()
    def full_stack_setup() -> str:
        """Configure a full-stack Python + Node.js project.

        Returns
        -------
        str
            Full-stack setup instructions
        """
        return """# Full-Stack Project Setup

Create a production-ready full-stack application with Python backend
and modern frontend.

## Architecture Overview

```
project/
├── packages/
│   ├── api-python/      # FastAPI backend
│   │   ├── src/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── api-node/        # Fastify services (optional)
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   ├── web/             # Frontend (optional)
│   │   ├── src/
│   │   └── package.json
│   └── shared/          # Shared logic
│       └── logic/
├── docs/                # Documentation site
├── docker-compose.yml
└── turbo.json          # Monorepo orchestration
```

## Recommended Configuration

```python
answers = {
    "project_name": "my-fullstack-app",
    "project_layout": "monorepo",
    "quality_profile": "strict",
    "cli_module": "enabled",
    "api_tracks": "python+node",
    "mcp_module": "enabled",
    "websocket_module": "enabled",
    "docs_site": "fumadocs",
    "shared_logic": "enabled",
    "ci_platform": "github-actions",
    "include_databases": "yes",
}
```

## Quick Start

```
copier_copy(
    destination="~/projects/my-fullstack-app",
    answers=answers
)
```

## After Generation

1. `cd my-fullstack-app && uv sync`
2. `pnpm install` (for Node packages)
3. `docker-compose up -d` (start databases)
4. `make dev` (run all services)

## Key Files

- `turbo.json` - Monorepo task orchestration
- `docker-compose.yml` - Local development services
- `.github/workflows/` - CI/CD pipelines
- `packages/shared/` - Cross-package utilities
"""

    @mcp.prompt()
    def mcp_server_setup(language: str = "python") -> str:
        """Configure a new MCP server project.

        Parameters
        ----------
        language
            Implementation language: "python", "typescript", or "rust"

        Returns
        -------
        str
            MCP server setup instructions
        """
        lang_specific = {
            "python": """
## Python MCP Server (FastMCP v2)

### Dependencies
- `fastmcp>=2.13.0` - Server framework
- `httpx>=0.27.0` - HTTP client for tools
- `pydantic>=2.0` - Schema validation

### Structure
```
src/your_project/mcp/
├── __init__.py
├── server.py      # FastMCP server
├── config.py      # Pydantic settings
├── errors.py      # MCP error types
├── tools/         # Tool implementations
│   ├── __init__.py
│   └── example.py
├── resources/     # Resource providers
└── prompts/       # Prompt templates
```

### Example Tool
```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def hello(name: str) -> str:
    \"\"\"Say hello to someone.\"\"\"
    return f"Hello, {name}!"
```
""",
            "typescript": """
## TypeScript MCP Server (FastMCP + Bun)

### Dependencies
- `fastmcp` - Server framework
- `zod` - Schema validation
- `dotenv` - Configuration

### Structure
```
src/
├── index.ts       # Entry point
├── config.ts      # Configuration
├── errors.ts      # Error types
└── tools/
    ├── index.ts
    └── example.ts
```

### Example Tool
```typescript
import { FastMCP } from "fastmcp";
import { z } from "zod";

const mcp = new FastMCP("my-server");

mcp.addTool({
  name: "hello",
  description: "Say hello to someone",
  parameters: z.object({ name: z.string() }),
  execute: async ({ name }) => `Hello, ${name}!`,
});
```
""",
            "rust": """
## Rust MCP Server (rmcp SDK)

### Dependencies
- `rmcp = "0.11"` - MCP SDK
- `tokio` - Async runtime
- `axum` - HTTP framework (for SSE/HTTP)
- `serde` - Serialization

### Structure
```
src/
├── lib.rs         # Library root
├── main.rs        # Entry point
├── config.rs      # Configuration
├── error.rs       # Error types
└── tools/
    ├── mod.rs
    └── example.rs
```

### Example Tool
```rust
use rmcp::{Tool, tool};

#[tool]
async fn hello(name: String) -> String {
    format!("Hello, {}!", name)
}
```
""",
        }

        lang_content = lang_specific.get(language.lower(), lang_specific["python"])

        return f"""# MCP Server Project Setup

Create a Model Context Protocol server in {language.capitalize()}.

{lang_content}

## Configuration

```python
answers = {{
    "project_name": "my-mcp-server",
    "mcp_module": "enabled",
    "mcp_language": "{language}",
    "mcp_transport": "stdio",  # or "sse", "http"
    "mcp_example_tools": True,
}}
```

## Generate the Project

```
copier_copy(
    destination="~/projects/my-mcp-server",
    answers=answers
)
```

## Testing Your Server

After generation:
1. Build the project
2. Run with MCP Inspector:
   ```
   npx @modelcontextprotocol/inspector <your-server-command>
   ```

## Transport Options

- **stdio**: Direct process communication (default)
- **SSE**: Server-Sent Events over HTTP
- **HTTP**: Streamable HTTP transport

Add to Claude Desktop `mcp.json`:
```json
{{
  "mcpServers": {{
    "my-server": {{
      "command": "uv",
      "args": ["run", "python", "-m", "my_project.mcp"]
    }}
  }}
}}
```
"""

    @mcp.prompt()
    def quality_setup(profile: str = "standard") -> str:
        """Configure quality tools and CI.

        Parameters
        ----------
        profile
            Quality profile: "standard" or "strict"

        Returns
        -------
        str
            Quality setup instructions
        """
        return f"""# Quality Suite Configuration

Set up comprehensive code quality for your project.

## Profile: {profile.capitalize()}

{"### Standard Profile" if profile == "standard" else "### Strict Profile"}

{
            "Balanced configuration suitable for most projects:"
            if profile == "standard"
            else "Maximum strictness for high-reliability code:"
        }

| Tool | {profile.capitalize()} Setting |
|------|-----------|
| Ruff | {"Base rules + imports" if profile == "standard" else "All rules enabled"} |
| ty | {
            "Standard type checking"
            if profile == "standard"
            else "Strict mode + inference"
        } |
| Pylint | {"Core checks" if profile == "standard" else "All categories enabled"} |
| pytest | {
            "Standard coverage" if profile == "standard" else "100% coverage required"
        } |

## Running Quality Checks

```bash
# Full suite
make quality

# Or with uv tasks
QUALITY_PROFILE={profile} uv run task quality

# Individual tools
uv run ruff check .
uv run ty check
uv run pylint src/
uv run pytest --cov
```

## CI Integration

The generated `.github/workflows/riso-quality.yml` runs:

1. **Lint Job**: Ruff check and format
2. **Type Job**: ty type checking
3. **Static Job**: Pylint analysis
4. **Test Job**: pytest with coverage

All jobs must pass for PR merge.

## Pre-commit Hooks

Enable automatic checks on commit:

```bash
uv run pre-commit install
```

Hooks included:
- ruff (format + lint)
- ty (type check)
- trailing whitespace
- end-of-file fixer
- yaml validation
"""
