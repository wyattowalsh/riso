#!/usr/bin/env python3
"""Verify versions within maintainer, generated, and quality-tool scopes.

This script ensures that version requirements in:
- scripts/setup/lib/versions.sh (source of truth)
- template/hooks/pre_gen_project.py (tool_matrix)
- template/files/python/pyproject.toml.jinja (quality tool versions)
- template/files/.mise.toml.jinja (mise tool versions)

are consistent within their owning scope. Generated projects intentionally have
different runtime requirements from the template maintainer repository.

Exit codes:
- 0: All versions synchronized
- 1: Version mismatch detected
"""

from __future__ import annotations

import re
import sys
import json
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path

from jinja2 import Environment, StrictUndefined, TemplateError


@dataclass
class VersionSource:
    """A source of version information."""

    file: Path
    versions: dict[str, str] = field(default_factory=dict)


def parse_versions_sh(path: Path) -> dict[str, str]:
    """Parse version constants from versions.sh.

    Extracts patterns like: export PYTHON_MIN_VERSION="3.11"
    """
    versions = {}
    content = path.read_text()

    # Map environment variable names to canonical tool names
    var_to_tool = {
        "PYTHON_MIN_VERSION": "python",
        "UV_MIN_VERSION": "uv",
        "NODE_MIN_VERSION": "node",
        "PNPM_MIN_VERSION": "pnpm",
        "RUFF_VERSION": "ruff",
        "TY_VERSION": "ty",
        "PYLINT_VERSION": "pylint",
        "COVERAGE_VERSION": "coverage",
        "PRECOMMIT_VERSION": "pre-commit",
        "COPIER_MIN_VERSION": "copier",
        "MISE_MIN_VERSION": "mise",
    }

    for var_name, tool_name in var_to_tool.items():
        # Match: export VAR_NAME="version"
        pattern = rf'export {var_name}="([^"]+)"'
        match = re.search(pattern, content)
        if match:
            versions[tool_name] = match.group(1)

    return versions


def parse_pre_gen_project(path: Path) -> dict[str, str]:
    """Parse tool_matrix from pre_gen_project.py.

    Looks for patterns like: ("uv", "0.4", "uv@0.4")
    """
    versions = {}
    content = path.read_text()

    # Find the tool_matrix list
    pattern = r'\("(uv|node|pnpm|python)",\s*"([^"]+)"'
    matches = re.findall(pattern, content)

    for tool, version in matches:
        versions[tool] = version

    return versions


def parse_pyproject_jinja(path: Path) -> dict[str, str]:
    """Parse quality tool versions from pyproject.toml.jinja.

    Looks for patterns like: "ruff>=0.14.2"
    """
    versions = {}
    content = path.read_text()

    # Find dependency-groups.quality section
    quality_section_match = re.search(
        r"\[dependency-groups\]\nquality\s*=\s*\[(.*?)\]", content, re.DOTALL
    )

    if quality_section_match:
        quality_deps = quality_section_match.group(1)

        # Match patterns like "ruff>=0.14.2"
        tool_patterns = {
            "ruff": r'"ruff>=([^"]+)"',
            "ty": r'"ty>=([^"]+)"',
            "pylint": r'"pylint>=([^"]+)"',
            "coverage": r'"coverage>=([^"]+)"',
            "pre-commit": r'"pre-commit>=([^"]+)"',
        }

        for tool, pattern in tool_patterns.items():
            match = re.search(pattern, quality_deps)
            if match:
                versions[tool] = match.group(1)

    return versions


def parse_mise_toml(path: Path) -> dict[str, str]:
    """Parse tool versions from .mise.toml.jinja.

    Looks for patterns like: node = "20"
    """
    versions = {}
    content = path.read_text()

    # Match patterns like: toolname = "version"
    tools = ["python", "node", "pnpm", "uv"]
    for tool in tools:
        pattern = rf'{tool}\s*=\s*"([^"]+)"'
        match = re.search(pattern, content)
        if match:
            versions[tool] = match.group(1)

    return versions


def normalize_version(version: str) -> str:
    """Normalize version strings for comparison.

    Examples:
    - "0.4" -> "0.4"
    - "0.14.2" -> "0.14.2"
    - "3.11" -> "3.11"
    - "3.0" -> "3.0"
    - "latest" -> "latest"
    """
    text = version.strip()
    if "@" in text and text[0].isalpha():
        text = text.split("@", 1)[1]
    return re.sub(r"^(?:>=|<=|~=|==|~|\^|>|<|=)\s*", "", text)


def _package_versions(content: str) -> dict[str, str]:
    """Read Node and pnpm versions from emitted JSON."""
    if not content.strip():
        return {}
    data = json.loads(content)
    if isinstance(data, dict):
        engines = data.get("engines", {})
        node = engines.get("node") if isinstance(engines, dict) else None
        manager = data.get("packageManager")
    else:
        raise ValueError("Package manifest must be a JSON object")
    result = {}
    if isinstance(node, str):
        result["node"] = node
    if isinstance(manager, str) and manager.startswith("pnpm@"):
        result["pnpm"] = manager.removeprefix("pnpm@")
    return result


def parse_package_json(
    path: Path, *, context: dict[str, object] | None = None
) -> dict[str, str]:
    """Read JSON, rendering an explicitly supplied template context first."""
    content = path.read_text(encoding="utf-8")
    if path.suffix == ".jinja":
        content = (
            Environment(undefined=StrictUndefined)
            .from_string(content)
            .render(**(context or {}))
        )
    return _package_versions(content)


def generated_package_profiles(path: Path) -> list[VersionSource]:
    """Render all feature intersections that affect the root Node manifest."""
    template = Environment(undefined=StrictUndefined).from_string(
        path.read_text(encoding="utf-8")
    )
    enabled = ("disabled", "enabled")
    profiles = []
    for api, docs, mcp, desktop, release, saas in product(
        enabled,
        (None, "fumadocs", "docusaurus"),
        enabled,
        (None, "electron-vite", "tauri"),
        enabled,
        enabled,
    ):
        content = template.render(
            project_name="Version check",
            project_slug="version-check",
            package_name="version_check",
            project_layout="single-package",
            task_runner="just",
            api_module=api,
            api_languages=["node"],
            docs_module="enabled" if docs else "disabled",
            docs_framework=docs,
            docusaurus_openapi="enabled",
            mcp_module=mcp,
            mcp_languages=["typescript"],
            desktop_module="enabled" if desktop else "disabled",
            desktop_framework=desktop,
            changelog_module=release,
            saas_infra_module=saas,
        )
        if not content.strip():
            continue
        versions = _package_versions(content)
        if set(versions) != {"node", "pnpm"}:
            raise ValueError(
                f"Generated manifest missing runtime declarations: {versions}"
            )
        profiles.append(VersionSource(file=path, versions=versions))
    if not profiles:
        raise ValueError("Generated manifest emitted no Node package profiles")
    return profiles


def versions_compatible(required: str, configured: str, tool: str) -> bool:
    """Compare exact pins, dotted prefixes, and an allowed Node major floor."""
    if tool == "node" and "||" in configured:
        return any(
            versions_compatible(required, part.strip(), tool)
            for part in configured.split("||")
        )
    required = normalize_version(required)
    configured = normalize_version(configured)
    if required == configured:
        return True
    left = required.split(".")
    right = configured.split(".")
    if not all(part.isdigit() for part in (*left, *right)):
        return False
    shared = min(len(left), len(right))
    if left[:shared] == right[:shared]:
        return True
    # versions.sh declares a minimum; a more recent pin within its Node major
    # satisfies that minimum. A lower pin must still fail.
    return (
        tool == "node"
        and left[0] == right[0]
        and tuple(map(int, right)) >= tuple(map(int, left))
    )


def compare_versions(
    source: VersionSource, other_sources: list[VersionSource], tool: str
) -> list[str]:
    """Compare a tool's version across all sources.

    Returns list of error messages if mismatches found.
    """
    errors = []
    source_version = normalize_version(source.versions.get(tool, ""))

    if not source_version:
        return errors  # Tool not defined in source

    for other in other_sources:
        other_version = normalize_version(other.versions.get(tool, ""))

        # Skip if tool not defined in this source
        if not other_version:
            continue

        # Compare versions
        if not versions_compatible(source_version, other_version, tool):
            errors.append(
                f"  {tool}: {source.file.name}={source_version} vs "
                f"{other.file.name}={other_version}"
            )

    return errors


def compare_lane(label: str, sources: list[VersionSource]) -> list[str]:
    """Compare configured versions within one independent runtime scope."""
    if not sources:
        return []
    source, *others = sources
    return [
        f"[{label}] {error.strip()}"
        for tool in sorted(source.versions)
        for error in compare_versions(source, others, tool)
    ]


def main() -> int:
    """Check version synchronization and report mismatches."""
    repo_root = Path(__file__).resolve().parents[2]

    # Define all version sources
    versions_sh_path = repo_root / "scripts" / "setup" / "lib" / "versions.sh"
    pre_gen_path = repo_root / "template" / "hooks" / "pre_gen_project.py"
    maintainer_mise = repo_root / ".mise.toml"
    maintainer_package = repo_root / "package.json"
    pyproject_path = (
        repo_root / "template" / "files" / "python" / "pyproject.toml.jinja"
    )
    generated_mise = repo_root / "template" / "files" / "mise.toml.jinja"
    generated_package = repo_root / "template" / "files" / "package.json.jinja"

    # Verify all files exist
    missing_files = []
    for path in [
        versions_sh_path,
        pre_gen_path,
        pyproject_path,
        maintainer_mise,
        maintainer_package,
        generated_mise,
        generated_package,
    ]:
        if not path.exists():
            missing_files.append(str(path))

    if missing_files:
        print("ERROR: Missing required files:", file=sys.stderr)
        for path in missing_files:
            print(f"  - {path}", file=sys.stderr)
        return 1

    # Parse versions from each source
    source_of_truth = VersionSource(
        file=versions_sh_path, versions=parse_versions_sh(versions_sh_path)
    )

    other_sources = [
        VersionSource(file=pre_gen_path, versions=parse_pre_gen_project(pre_gen_path)),
        VersionSource(
            file=pyproject_path, versions=parse_pyproject_jinja(pyproject_path)
        ),
        VersionSource(file=maintainer_mise, versions=parse_mise_toml(maintainer_mise)),
        VersionSource(
            file=maintainer_package, versions=parse_package_json(maintainer_package)
        ),
    ]

    print(
        "Verifying maintainer, generated runtime, and quality-tool version synchronization..."
    )
    print(f"Source of truth: {versions_sh_path.relative_to(repo_root)}")
    print()

    # Check each tool defined in source of truth
    all_errors = []
    for tool in sorted(source_of_truth.versions.keys()):
        errors = compare_versions(source_of_truth, other_sources, tool)
        all_errors.extend(errors)

    generated_source = VersionSource(
        file=generated_mise, versions=parse_mise_toml(generated_mise)
    )
    try:
        generated_profiles = generated_package_profiles(generated_package)
    except (ValueError, TemplateError) as exc:
        print(f"ERROR: Generated package profile: {exc}", file=sys.stderr)
        return 1
    for tool in generated_source.versions:
        all_errors.extend(compare_versions(generated_source, generated_profiles, tool))

    if all_errors:
        print("❌ Version mismatches detected:", file=sys.stderr)
        print(file=sys.stderr)
        for error in all_errors:
            print(error, file=sys.stderr)
        print(file=sys.stderr)
        print(
            "Update versions within their owning scope; generated runtime floors "
            "are independent of maintainer pins.",
            file=sys.stderr,
        )
        return 1

    print("✅ All versions synchronized!")
    print()
    print("Verified versions:")
    for tool, version in sorted(source_of_truth.versions.items()):
        print(f"  {tool}: {version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
