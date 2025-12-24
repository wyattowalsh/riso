"""Module catalog resources for MCP.

Exposes the template module catalog with feature descriptions.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..config import get_config

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_catalog_resources(mcp: FastMCP) -> None:
    """Register catalog resources with the MCP server.

    Resources registered:
    - riso://catalog/modules - Complete module catalog
    - riso://catalog/dependencies - Module dependency map

    Parameters
    ----------
    mcp
        FastMCP server instance
    """
    config = get_config()

    @mcp.resource("riso://catalog/modules")
    def get_modules_catalog() -> str:
        """Get the complete module catalog.

        Returns detailed information about all available template
        modules including features, dependencies, and compatibility.
        """
        from riso.template import get_module_catalog, get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        catalog = get_module_catalog(template_path)

        # Format as readable markdown
        lines = ["# Riso Template Module Catalog\n"]

        if "modules" in catalog:
            for module in catalog["modules"]:
                name = module.get("name", "unknown")
                desc = module.get("description", "No description")
                lines.append(f"## {name}")
                lines.append(f"\n{desc}\n")

                if "features" in module:
                    lines.append("### Features")
                    for feature in module["features"]:
                        lines.append(f"- {feature}")
                    lines.append("")

                if "dependencies" in module:
                    lines.append("### Dependencies")
                    for dep in module["dependencies"]:
                        lines.append(f"- `{dep}`")
                    lines.append("")

        return "\n".join(lines)

    @mcp.resource("riso://catalog/modules.json")
    def get_modules_catalog_json() -> str:
        """Get the module catalog as raw JSON.

        Returns the module catalog in its raw JSON format
        for programmatic processing.
        """
        from riso.template import get_module_catalog, get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        catalog = get_module_catalog(template_path)
        return json.dumps(catalog, indent=2)

    @mcp.resource("riso://catalog/prompts")
    def get_prompts_catalog() -> str:
        """Get a catalog of all template prompts.

        Returns detailed information about each prompt including
        type, choices, defaults, and conditions.
        """
        from riso.template import get_defaults, get_prompts, get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        prompts = get_prompts(template_path)
        defaults = get_defaults(template_path)

        lines = ["# Riso Template Prompts\n"]

        for name, prompt in prompts.items():
            lines.append(f"## {name}")

            prompt_type = prompt.get("type", "str")
            lines.append(f"- **Type:** {prompt_type}")

            help_text = prompt.get("help", "")
            if help_text:
                lines.append(f"- **Description:** {help_text}")

            default = defaults.get(name)
            if default is not None:
                lines.append(f"- **Default:** `{default}`")

            choices = prompt.get("choices")
            if choices:
                lines.append("- **Choices:**")
                choice_list = list(choices.keys()) if isinstance(choices, dict) else choices
                for choice in choice_list:
                    lines.append(f"  - `{choice}`")

            when = prompt.get("when")
            if when:
                lines.append(f"- **Condition:** `{when}`")

            lines.append("")

        return "\n".join(lines)

    @mcp.resource("riso://catalog/dependencies")
    def get_dependencies_map() -> str:
        """Get the module dependency map.

        Shows which modules depend on each other and what
        external dependencies they bring.
        """
        lines = [
            "# Module Dependencies\n",
            "## Core Dependencies (always included)",
            "- `pytest>=7.0` - Testing framework",
            "- `pytest-cov>=4.0` - Coverage plugin",
            "- `ruff>=0.8.0` - Linter and formatter",
            "- `ty>=0.0.6` - Type checker",
            "- `pylint>=3.0` - Static analysis",
            "",
            "## CLI Module (`cli_module=enabled`)",
            "- `typer>=0.12.0` - CLI framework",
            "- `rich>=13.0` - Rich terminal output",
            "",
            "## Python API (`api_tracks` includes `python`)",
            "- `fastapi>=0.115.0` - Web framework",
            "- `uvicorn>=0.32.0` - ASGI server",
            "- `pydantic>=2.0` - Data validation",
            "- `httpx>=0.27.0` - HTTP client",
            "",
            "## Node API (`api_tracks` includes `node`)",
            "- `fastify@^5.0.0` - Web framework",
            "- `typescript@^5.6.0` - Type checking",
            "- `vitest@^2.0.0` - Testing framework",
            "",
            "## MCP Module (`mcp_module=enabled`)",
            "- `fastmcp>=2.13.0` - MCP server framework",
            "- `httpx>=0.27.0` - HTTP client",
            "",
            "## WebSocket Module (`websocket_module=enabled`)",
            "- `websockets>=14.0` - WebSocket library",
            "- Requires: `api_tracks` includes `python`",
            "",
            "## GraphQL Module (`graphql_api_module=enabled`)",
            "- `strawberry-graphql>=0.250.0` - GraphQL framework",
            "- Requires: `api_tracks` includes `python`",
            "",
            "## Documentation Sites",
            "### Fumadocs (`docs_site=fumadocs`)",
            "- Next.js 15 + Fumadocs",
            "- pnpm workspace integration",
            "",
            "### Sphinx Shibuya (`docs_site=sphinx-shibuya`)",
            "- `sphinx>=8.0` - Documentation generator",
            "- `shibuya>=2024.12` - Theme",
            "",
            "### Docusaurus (`docs_site=docusaurus`)",
            "- `@docusaurus/core@^3.0` - Documentation platform",
        ]

        return "\n".join(lines)
