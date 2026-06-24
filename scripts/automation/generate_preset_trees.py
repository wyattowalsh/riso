#!/usr/bin/env python3
"""Generate file trees for preset configurations.

This script renders each preset configuration using Copier in dry-run mode
and captures the resulting file structure. The output is saved as JSON
for the web configurator to display.

Usage:
    uv run python scripts/automation/generate_preset_trees.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, TypedDict

# Preset configurations matching web/src/components/presets/presets.tsx
PRESETS: list[dict[str, Any]] = [
    {
        "id": "minimal-python",
        "name": "Python CLI Tool",
        "config": {
            "project_name": "my-cli",
            "project_layout": "single-package",
            "quality_profile": "standard",
            "cli_module": "enabled",
            "cli_languages": ["python"],
            "api_module": "disabled",
            "docs_module": "disabled",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "python-api",
        "name": "Python REST API",
        "config": {
            "project_name": "my-api",
            "project_layout": "single-package",
            "quality_profile": "standard",
            "cli_module": "disabled",
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": "none",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "fumadocs_openapi": "enabled",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "rust-cli-python-api",
        "name": "Rust CLI + Python API",
        "config": {
            "project_name": "my-hybrid",
            "project_layout": "monorepo",
            "quality_profile": "strict",
            "cli_module": "enabled",
            "cli_languages": ["rust"],
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": "none",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "go-api",
        "name": "Go API + CLI",
        "config": {
            "project_name": "my-go-service",
            "project_layout": "single-package",
            "quality_profile": "strict",
            "cli_module": "enabled",
            "cli_languages": ["go"],
            "api_module": "enabled",
            "api_languages": ["go"],
            "api_features": "none",
            "docs_module": "enabled",
            "docs_framework": "docusaurus",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "typescript-mcp",
        "name": "TypeScript MCP Server",
        "config": {
            "project_name": "my-mcp",
            "project_layout": "single-package",
            "quality_profile": "standard",
            "cli_module": "disabled",
            "api_module": "disabled",
            "mcp_module": "enabled",
            "mcp_languages": ["typescript"],
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "graphql-api",
        "name": "GraphQL API",
        "config": {
            "project_name": "my-graphql",
            "project_layout": "single-package",
            "quality_profile": "strict",
            "cli_module": "disabled",
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": "graphql,websocket",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "fumadocs_openapi": "enabled",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "fullstack",
        "name": "Full-Stack Monorepo",
        "config": {
            "project_name": "my-fullstack",
            "project_layout": "monorepo",
            "quality_profile": "strict",
            "cli_module": "enabled",
            "cli_languages": ["python"],
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": "graphql,websocket",
            "mcp_module": "enabled",
            "mcp_languages": ["python"],
            "shared_logic": "enabled",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "fumadocs_openapi": "enabled",
            "fumadocs_llms_txt": "enabled",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "polyglot-monorepo",
        "name": "Polyglot Monorepo",
        "config": {
            "project_name": "my-polyglot",
            "project_layout": "monorepo",
            "quality_profile": "strict",
            "cli_module": "enabled",
            "cli_languages": ["rust"],
            "api_module": "enabled",
            "api_languages": ["go"],
            "mcp_module": "enabled",
            "mcp_languages": ["typescript"],
            "shared_logic": "enabled",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "ml-ai-project",
        "name": "ML/AI Project",
        "config": {
            "project_name": "my-ml-project",
            "project_layout": "monorepo",
            "quality_profile": "standard",
            "cli_module": "enabled",
            "cli_languages": ["python"],
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": "websocket",
            "mcp_module": "enabled",
            "mcp_languages": ["python"],
            "docs_module": "enabled",
            "docs_framework": "sphinx-shibuya",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "saas-starter",
        "name": "SaaS Starter",
        "config": {
            "project_name": "my-saas",
            "project_layout": "monorepo",
            "quality_profile": "strict",
            "api_module": "enabled",
            "api_languages": ["node"],
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "saas_infra_module": "enabled",
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "neon",
            "saas_orm": "prisma",
            "saas_auth_module": "enabled",
            "saas_auth_provider": "clerk",
            "saas_billing_module": "enabled",
            "saas_billing_provider": "stripe",
            "saas_app_module": "enabled",
            "saas_analytics": "posthog",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "microservices",
        "name": "Microservices Monorepo",
        "config": {
            "project_name": "my-platform",
            "project_layout": "monorepo",
            "quality_profile": "strict",
            "cli_module": "enabled",
            "cli_languages": ["python"],
            "api_module": "enabled",
            "api_languages": ["python"],
            "api_features": "graphql",
            "shared_logic": "enabled",
            "docs_module": "enabled",
            "docs_framework": "docusaurus",
            "docusaurus_openapi": "enabled",
            "docusaurus_mermaid": "enabled",
            "saas_infra_module": "disabled",
            "ai_tools_module": "enabled",
        },
    },
    {
        "id": "docs-only",
        "name": "Documentation Site",
        "config": {
            "project_name": "my-docs",
            "project_layout": "single-package",
            "quality_profile": "standard",
            "cli_module": "disabled",
            "api_module": "disabled",
            "docs_module": "enabled",
            "docs_framework": "docusaurus",
            "docusaurus_faster": "enabled",
            "docusaurus_blog": "enabled",
            "docusaurus_mermaid": "enabled",
            "docusaurus_llms_txt": "enabled",
            "saas_infra_module": "disabled",
            "ai_tools_module": "disabled",
        },
    },
    {
        "id": "enterprise-saas",
        "name": "Enterprise SaaS",
        "config": {
            "project_name": "my-enterprise",
            "project_layout": "monorepo",
            "quality_profile": "strict",
            "api_module": "enabled",
            "api_languages": ["node"],
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "saas_infra_module": "enabled",
            "saas_runtime": "nextjs-16",
            "saas_hosting": "vercel",
            "saas_database": "neon",
            "saas_orm": "prisma",
            "saas_auth_module": "enabled",
            "saas_auth_provider": "clerk",
            "saas_billing_module": "enabled",
            "saas_billing_provider": "stripe",
            "saas_app_module": "enabled",
            "saas_analytics": "posthog",
            "changelog_module": "enabled",
            "ai_tools_module": "enabled",
        },
    },
]


class FileTreeNode(TypedDict, total=False):
    """A node in the file tree."""

    name: str
    type: str  # 'file' or 'folder'
    children: list["FileTreeNode"]
    description: str


def build_tree_from_paths(paths: list[str], max_depth: int = 3) -> list[FileTreeNode]:
    """Build a file tree structure from a list of file paths.

    Args:
        paths: List of relative file paths
        max_depth: Maximum depth to show (deeper items collapsed)

    Returns:
        List of FileTreeNode representing the root level
    """
    # Build a nested dict structure first
    tree_dict: dict[str, Any] = {}

    for path in sorted(paths):
        parts = Path(path).parts
        current = tree_dict
        for part in parts[:-1]:  # All but last (folders)
            if part not in current:
                current[part] = {}
            current = current[part]
        # Last part (file)
        if parts:
            current[parts[-1]] = None  # None indicates a file

    def dict_to_nodes(d: dict[str, Any], depth: int = 0) -> list[FileTreeNode]:
        """Convert dict structure to FileTreeNode list."""
        nodes: list[FileTreeNode] = []
        for name, children in sorted(d.items()):
            if children is None:
                # It's a file
                nodes.append({"name": name, "type": "file"})
            else:
                # It's a folder
                node: FileTreeNode = {"name": name + "/", "type": "folder"}
                if depth < max_depth and children:
                    node["children"] = dict_to_nodes(children, depth + 1)
                elif children:
                    # Collapse deeper levels
                    file_count = count_files(children)
                    node["description"] = f"{file_count} files"
                nodes.append(node)
        return nodes

    def count_files(d: dict[str, Any]) -> int:
        """Count total files in a tree dict."""
        count = 0
        for children in d.values():
            if children is None:
                count += 1
            else:
                count += count_files(children)
        return count

    return dict_to_nodes(tree_dict)


def render_preset_tree(preset: dict[str, Any], template_path: Path) -> dict[str, Any]:
    """Render a preset and return its file tree.

    Args:
        preset: Preset configuration dict
        template_path: Path to the template directory

    Returns:
        Dict with preset ID, file count, and file tree
    """
    try:
        import copier
    except ImportError:
        print(
            "Error: copier not installed. Run: uv pip install copier", file=sys.stderr
        )
        sys.exit(1)

    preset_id = preset["id"]
    config = preset["config"]

    print(f"  Rendering {preset_id}...", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "output"

        try:
            # Run copier in non-interactive mode
            copier.run_copy(
                str(template_path),
                str(dest),
                data=config,
                defaults=True,
                unsafe=True,
                quiet=True,
            )

            # Collect all files
            files: list[str] = []
            for path in dest.rglob("*"):
                if path.is_file():
                    rel_path = path.relative_to(dest)
                    files.append(str(rel_path))

            # Build tree
            tree = build_tree_from_paths(files)

            return {
                "id": preset_id,
                "name": preset["name"],
                "fileCount": len(files),
                "fileTree": tree,
            }

        except Exception as e:
            print(f"    Warning: Failed to render {preset_id}: {e}", file=sys.stderr)
            return {
                "id": preset_id,
                "name": preset["name"],
                "fileCount": 0,
                "fileTree": [],
                "error": str(e),
            }


def main() -> None:
    """Generate preset file trees and save to JSON."""
    # Find template directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    template_path = repo_root / "template"

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    output_path = repo_root / "web" / "src" / "data" / "preset-trees.json"

    print(f"Generating preset file trees from {template_path}", file=sys.stderr)
    print(f"Output: {output_path}", file=sys.stderr)

    results: list[dict[str, Any]] = []
    for preset in PRESETS:
        result = render_preset_tree(preset, template_path)
        results.append(result)

    # Write output
    output_data = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "presets": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nGenerated {len(results)} preset trees", file=sys.stderr)
    total_files = sum(r.get("fileCount", 0) for r in results)
    print(f"Total files across all presets: {total_files}", file=sys.stderr)


if __name__ == "__main__":
    main()
