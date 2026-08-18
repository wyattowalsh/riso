#!/usr/bin/env python3
"""Verify version constants stay synchronized within maintainer and generated lanes.

Two lanes are compared independently so generated Node 22 is not failed against
maintainer Node 22.13.0 (major 22 is enough):

Maintainer
    scripts/setup/lib/versions.sh, .mise.toml, root package.json,
    template/hooks/pre_gen_project.py (tool_matrix)

Generated
    template/files/mise.toml.jinja, template/files/package.json.jinja

Node uses major-prefix comparison (22 matches 22.13.0 and 22.23.1). Other tools
use exact match after stripping operators, or dotted-prefix match (0.11 vs 0.11.26).

Exit codes:
- 0: All in-lane versions synchronized
- 1: Version mismatch detected or required files missing
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_VERSION_OPERATOR = re.compile(r"^(?:>=|<=|~=|==|~|\^|>|<|=)\s*")
_MISE_TOOLS = ("python", "node", "pnpm", "uv")


@dataclass
class VersionSource:
    """A source of version information."""

    file: Path
    versions: dict[str, str] = field(default_factory=dict)


def parse_versions_sh(path: Path) -> dict[str, str]:
    """Parse version constants from versions.sh.

    Extracts patterns like: export PYTHON_MIN_VERSION="3.11"
    """
    versions: dict[str, str] = {}
    content = path.read_text(encoding="utf-8")

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
        pattern = rf'export {var_name}="([^"]+)"'
        match = re.search(pattern, content)
        if match:
            versions[tool_name] = match.group(1)

    return versions


def parse_pre_gen_project(path: Path) -> dict[str, str]:
    """Parse tool_matrix tuples from pre_gen_project.py.

    Looks for patterns like: ("uv", "0.11.26", "uv@0.11.26")
    Restricted to known toolchain names so unrelated string tuples are ignored.
    """
    versions: dict[str, str] = {}
    content = path.read_text(encoding="utf-8")
    pattern = r'\("(uv|node|pnpm|python)",\s*"([^"]+)"'
    for tool, version in re.findall(pattern, content):
        versions[tool] = version
    return versions


def parse_mise_toml(path: Path) -> dict[str, str]:
    """Parse tool pins from mise.toml or mise.toml.jinja.

    Looks for patterns like: node = "20"
    """
    versions: dict[str, str] = {}
    content = path.read_text(encoding="utf-8")
    for tool in _MISE_TOOLS:
        pattern = rf'{tool}\s*=\s*"([^"]+)"'
        match = re.search(pattern, content)
        if match:
            versions[tool] = match.group(1)
    return versions


def parse_package_json(path: Path) -> dict[str, str]:
    """Parse node/pnpm pins from package.json or package.json.jinja.

    Uses engines.node as the Node floor and packageManager (pnpm@X) as the pnpm
    pin. engines.pnpm floors are ignored so 9.0.0 does not fight packageManager
    9.15.0 inside the generated lane.
    """
    content = path.read_text(encoding="utf-8")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return _parse_package_json_text(content)
    if not isinstance(data, dict):
        return {}
    versions: dict[str, str] = {}
    engines = data.get("engines")
    if isinstance(engines, dict) and "node" in engines:
        versions["node"] = str(engines["node"])
    package_manager = data.get("packageManager")
    if isinstance(package_manager, str) and package_manager.startswith("pnpm@"):
        versions["pnpm"] = package_manager.split("@", 1)[1]
    return versions


def _parse_package_json_text(content: str) -> dict[str, str]:
    """Regex fallback for Jinja-wrapped package.json templates."""
    versions: dict[str, str] = {}
    engines_match = re.search(r'"engines"\s*:\s*\{([^}]+)\}', content)
    if engines_match:
        node_match = re.search(r'"node"\s*:\s*"([^"]+)"', engines_match.group(1))
        if node_match:
            versions["node"] = node_match.group(1)
    pm_match = re.search(r'"packageManager"\s*:\s*"pnpm@([^"]+)"', content)
    if pm_match:
        versions["pnpm"] = pm_match.group(1)
    return versions


def normalize_version(version: str) -> str:
    """Normalize version strings for comparison.

    Strips PEP/semver operators and packageManager ``name@`` prefixes.
    """
    text = version.strip()
    if "@" in text and text[0].isalpha():
        text = text.split("@", 1)[1]
    text = _VERSION_OPERATOR.sub("", text).strip()
    return text


def _version_parts(version: str) -> list[str]:
    normalized = normalize_version(version)
    return [part for part in normalized.split(".") if part]


def versions_compatible(left: str, right: str, tool: str) -> bool:
    """Return True when two version strings represent the same pin.

    - Exact match after normalize.
    - Dotted prefix: ``0.11`` matches ``0.11.26``.
    - Node major-prefix: ``22`` matches ``22.13.0`` and ``22.23.1``.
    """
    left_n = normalize_version(left)
    right_n = normalize_version(right)
    if left_n == right_n:
        return True
    left_parts = _version_parts(left)
    right_parts = _version_parts(right)
    if not left_parts or not right_parts:
        return False
    shared = min(len(left_parts), len(right_parts))
    if left_parts[:shared] == right_parts[:shared]:
        return True
    return tool == "node" and left_parts[0] == right_parts[0]


def compare_versions(
    source: VersionSource,
    other_sources: list[VersionSource],
    tool: str,
    *,
    lane: str = "",
) -> list[str]:
    """Compare a tool's version across sources within one lane.

    Returns list of error messages if mismatches found.
    """
    errors: list[str] = []
    source_version = source.versions.get(tool, "")
    if not source_version:
        return errors

    prefix = f"  [{lane}] " if lane else "  "
    for other in other_sources:
        other_version = other.versions.get(tool, "")
        if not other_version:
            continue
        if versions_compatible(source_version, other_version, tool):
            continue
        errors.append(
            f"{prefix}{tool}: {source.file.name}={source_version} vs "
            f"{other.file.name}={other_version}"
        )
    return errors


def compare_lane(label: str, sources: list[VersionSource]) -> list[str]:
    """Compare every tool from the first source against the rest of the lane."""
    if len(sources) < 2:
        return []
    truth, *others = sources
    errors: list[str] = []
    for tool in sorted(truth.versions):
        errors.extend(compare_versions(truth, others, tool, lane=label))
    return errors


def _require_files(paths: list[Path]) -> list[str]:
    return [str(path) for path in paths if not path.exists()]


def main() -> int:
    """Check in-lane version synchronization and report mismatches."""
    repo_root = Path(__file__).resolve().parents[2]

    versions_sh_path = repo_root / "scripts" / "setup" / "lib" / "versions.sh"
    maintainer_mise_path = repo_root / ".mise.toml"
    root_package_json = repo_root / "package.json"
    pre_gen_path = repo_root / "template" / "hooks" / "pre_gen_project.py"
    generated_mise_path = repo_root / "template" / "files" / "mise.toml.jinja"
    generated_package_json = repo_root / "template" / "files" / "package.json.jinja"

    missing_files = _require_files(
        [
            versions_sh_path,
            maintainer_mise_path,
            root_package_json,
            pre_gen_path,
            generated_mise_path,
            generated_package_json,
        ]
    )
    if missing_files:
        print("ERROR: Missing required files:", file=sys.stderr)
        for path in missing_files:
            print(f"  - {path}", file=sys.stderr)
        return 1

    maintainer_lane = [
        VersionSource(
            file=versions_sh_path, versions=parse_versions_sh(versions_sh_path)
        ),
        VersionSource(
            file=maintainer_mise_path, versions=parse_mise_toml(maintainer_mise_path)
        ),
        VersionSource(
            file=root_package_json, versions=parse_package_json(root_package_json)
        ),
        VersionSource(file=pre_gen_path, versions=parse_pre_gen_project(pre_gen_path)),
    ]
    generated_lane = [
        VersionSource(
            file=generated_mise_path, versions=parse_mise_toml(generated_mise_path)
        ),
        VersionSource(
            file=generated_package_json,
            versions=parse_package_json(generated_package_json),
        ),
    ]

    print("Verifying dual-lane version synchronization...")
    print("Maintainer lane: versions.sh, .mise.toml, package.json, pre_gen tool_matrix")
    print(
        "Generated lane:  template/files/mise.toml.jinja, template/files/package.json.jinja"
    )
    print(
        "Lanes are independent: generated node 22 is not compared to "
        "maintainer 22.13.0."
    )
    print()

    all_errors = compare_lane("maintainer", maintainer_lane)
    all_errors.extend(compare_lane("generated", generated_lane))

    if all_errors:
        print("❌ Version mismatches detected:", file=sys.stderr)
        print(file=sys.stderr)
        for error in all_errors:
            print(error, file=sys.stderr)
        print(file=sys.stderr)
        print(
            "Update files within the same lane; do not copy maintainer "
            "Node 22.13.0 onto generated Node 22.",
            file=sys.stderr,
        )
        return 1

    print("✅ All in-lane versions synchronized!")
    print()
    print("Maintainer pins:")
    for tool, version in sorted(maintainer_lane[0].versions.items()):
        print(f"  {tool}: {version}")
    print()
    print("Generated pins:")
    for tool, version in sorted(generated_lane[0].versions.items()):
        print(f"  {tool}: {version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
