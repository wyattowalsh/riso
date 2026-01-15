"""Template file resources for MCP.

Exposes template configuration and file contents as MCP resources.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..config import get_config

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_template_resources(mcp: FastMCP) -> None:
    """Register template resources with the MCP server.

    Resources registered:
    - riso://template/copier.yml - Main template configuration
    - riso://template/files/{path} - Template file contents

    Parameters
    ----------
    mcp
        FastMCP server instance
    """
    config = get_config()
    max_bytes = config.max_response_size_mb * 1024 * 1024

    def _read_with_limit(path: Path) -> str:
        if not path.exists():
            return f"# {path.name} not found"
        try:
            if path.stat().st_size > max_bytes:
                return f"# {path.name} exceeds {config.max_response_size_mb}MB limit"
        except OSError:
            return f"# {path.name} could not be accessed"
        return path.read_text(encoding="utf-8")

    @mcp.resource("riso://template/copier.yml")
    def get_copier_yml() -> str:
        """Get the main copier.yml template configuration.

        Returns the complete Copier template configuration including
        prompts, defaults, metadata, and tasks.
        """
        from riso.template import get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        copier_yml = template_path / "copier.yml"
        return _read_with_limit(copier_yml)

    @mcp.resource("riso://template/files/python/pyproject.toml.jinja")
    def get_pyproject_template() -> str:
        """Get the Python pyproject.toml template.

        The main Python project configuration template with
        dependencies, tool configs, and Jinja templating.
        """
        from riso.template import get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        pyproject = template_path / "files" / "python" / "pyproject.toml.jinja"
        return _read_with_limit(pyproject)

    @mcp.resource("riso://template/files/shared/module_catalog.json.jinja")
    def get_module_catalog_template() -> str:
        """Get the module catalog template.

        Contains definitions for all available modules including
        dependencies, features, and compatibility information.
        """
        from riso.template import get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        catalog = template_path / "files" / "shared" / "module_catalog.json.jinja"
        if not catalog.exists():
            catalog = template_path / "files" / "shared" / "module_catalog.json"

        return _read_with_limit(catalog)

    @mcp.resource("riso://template/hooks/pre_gen_project.py")
    def get_pre_gen_hook() -> str:
        """Get the pre-generation hook script.

        Validates tooling requirements before project generation.
        """
        from riso.template import get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        hook = template_path / "hooks" / "pre_gen_project.py"
        return _read_with_limit(hook)

    @mcp.resource("riso://template/hooks/post_gen_project.py")
    def get_post_gen_hook() -> str:
        """Get the post-generation hook script.

        Runs after project generation to finalize setup.
        """
        from riso.template import get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        hook = template_path / "hooks" / "post_gen_project.py"
        return _read_with_limit(hook)

    @mcp.resource("riso://template/structure")
    def get_template_structure() -> str:
        """Get the template directory structure.

        Returns a tree-like representation of the template files.
        """
        from riso.template import get_template_path

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        def build_tree(path: Path, prefix: str = "", depth: int = 0) -> list[str]:
            if depth > 3:
                return [f"{prefix}..."]

            lines = []
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    connector = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{connector}{item.name}")

                    if item.is_dir() and not item.name.startswith("."):
                        extension = "    " if is_last else "│   "
                        lines.extend(build_tree(item, prefix + extension, depth + 1))
            except PermissionError:
                lines.append(f"{prefix}[permission denied]")

            return lines

        tree = [str(template_path.name) + "/"]
        tree.extend(build_tree(template_path))
        return "\n".join(tree)
