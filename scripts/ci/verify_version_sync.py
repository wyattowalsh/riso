#!/usr/bin/env python3
"""Verify version constants are synchronized across all configuration files.

This script ensures that version requirements in:
- scripts/setup/lib/versions.sh (source of truth)
- template/hooks/pre_gen_project.py (tool_matrix)
- template/files/python/pyproject.toml.jinja (quality tool versions)
- template/files/.mise.toml.jinja (mise tool versions)

are all consistent.

Exit codes:
- 0: All versions synchronized
- 1: Version mismatch detected
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


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
    pattern = r'\("([^"]+)",\s*"([^"]+)",\s*[^)]*\)'
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
    return version.strip()


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
        if source_version != other_version:
            errors.append(
                f"  {tool}: versions.sh={source_version} vs {other.file.name}={other_version}"
            )

    return errors


def main() -> int:
    """Check version synchronization and report mismatches."""
    repo_root = Path(__file__).resolve().parents[2]

    # Define all version sources
    versions_sh_path = repo_root / "scripts" / "setup" / "lib" / "versions.sh"
    pre_gen_path = repo_root / "template" / "hooks" / "pre_gen_project.py"
    pyproject_path = (
        repo_root / "template" / "files" / "python" / "pyproject.toml.jinja"
    )
    mise_path = repo_root / "template" / "files" / ".mise.toml.jinja"

    # Verify all files exist
    missing_files = []
    for path in [versions_sh_path, pre_gen_path, pyproject_path, mise_path]:
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
        VersionSource(file=mise_path, versions=parse_mise_toml(mise_path)),
    ]

    print("Verifying version synchronization...")
    print(f"Source of truth: {versions_sh_path.relative_to(repo_root)}")
    print()

    # Check each tool defined in source of truth
    all_errors = []
    for tool in sorted(source_of_truth.versions.keys()):
        errors = compare_versions(source_of_truth, other_sources, tool)
        all_errors.extend(errors)

    if all_errors:
        print("❌ Version mismatches detected:", file=sys.stderr)
        print(file=sys.stderr)
        for error in all_errors:
            print(error, file=sys.stderr)
        print(file=sys.stderr)
        print(
            "Please update the mismatched files to match versions.sh", file=sys.stderr
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
