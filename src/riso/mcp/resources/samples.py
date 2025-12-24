"""Sample project resources for MCP.

Exposes sample project configurations and their answer files.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from ..config import get_config

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_sample_resources(mcp: FastMCP) -> None:
    """Register sample resources with the MCP server.

    Resources registered:
    - riso://samples - List all sample variants
    - riso://samples/{variant}/answers - Sample answer files

    Parameters
    ----------
    mcp
        FastMCP server instance
    """
    config = get_config()

    @mcp.resource("riso://samples")
    def list_samples() -> str:
        """List all available sample project variants.

        Returns a formatted list of sample projects with their
        configurations and status.
        """
        from riso.template import get_samples_path, list_sample_variants

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        variants = list_sample_variants(samples_path)

        if not variants:
            return "No sample variants found."

        lines = ["# Sample Variants\n"]
        for variant in variants:
            status = "✓" if variant.get("has_render") else "○"
            lines.append(f"## {status} {variant['name']}")
            lines.append(f"Path: {variant['path']}")

            if variant.get("has_answers") and "answers" in variant:
                answers = variant["answers"]
                project_name = answers.get("project_name", "unknown")
                layout = answers.get("project_layout", "single-package")
                api = answers.get("api_tracks", "none")
                lines.append(f"Project: {project_name} ({layout})")
                lines.append(f"API Tracks: {api}")

            lines.append("")

        return "\n".join(lines)

    @mcp.resource("riso://samples/default/answers")
    def get_default_sample_answers() -> str:
        """Get the default sample's answer configuration.

        The default sample represents the baseline project setup.
        """
        from riso.template import get_samples_path

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        answers_file = samples_path / "default" / "copier-answers.yml"
        if not answers_file.exists():
            return "# Default sample answers not found"

        return answers_file.read_text(encoding="utf-8")

    @mcp.resource("riso://samples/full-stack/answers")
    def get_fullstack_sample_answers() -> str:
        """Get the full-stack sample's answer configuration.

        The full-stack sample includes Python API, Node.js, and docs.
        """
        from riso.template import get_samples_path

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        # Try various naming conventions
        for name in ["full-stack", "fullstack", "python-fastapi-react-vite"]:
            answers_file = samples_path / name / "copier-answers.yml"
            if answers_file.exists():
                return answers_file.read_text(encoding="utf-8")

        return "# Full-stack sample answers not found"

    @mcp.resource("riso://samples/monorepo/answers")
    def get_monorepo_sample_answers() -> str:
        """Get the monorepo sample's answer configuration.

        The monorepo sample demonstrates the turborepo layout.
        """
        from riso.template import get_samples_path

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        for name in ["monorepo", "monorepo-turborepo"]:
            answers_file = samples_path / name / "copier-answers.yml"
            if answers_file.exists():
                return answers_file.read_text(encoding="utf-8")

        return "# Monorepo sample answers not found"

    @mcp.resource("riso://samples/metadata/render_matrix.json")
    def get_render_matrix() -> str:
        """Get the render matrix metadata.

        Contains information about all rendered variants and their status.
        """
        from riso.template import get_samples_path

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        matrix_file = samples_path / "metadata" / "render_matrix.json"
        if not matrix_file.exists():
            return '{"variants": [], "note": "Render matrix not found"}'

        return matrix_file.read_text(encoding="utf-8")

    @mcp.resource("riso://samples/metadata/module_success.json")
    def get_module_success() -> str:
        """Get the module success rates metadata.

        Aggregated success rates for each template module.
        """
        from riso.template import get_samples_path

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        success_file = samples_path / "metadata" / "module_success.json"
        if not success_file.exists():
            return '{"modules": {}, "note": "Module success data not found"}'

        return success_file.read_text(encoding="utf-8")
