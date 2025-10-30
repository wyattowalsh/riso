#!/usr/bin/env python3
"""Ensure Makefile and uv task definitions stay aligned for quality commands."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "template" / "files" / "shared" / "quality" / "makefile.quality.jinja"
UV_TASK = REPO_ROOT / "template" / "files" / "shared" / "quality" / "uv_tasks" / "quality.py.jinja"

REQUIRED_PATTERNS = [
    "ruff check",
    "mypy",
    "pylint",
    "coverage run",
    "coverage report",
]
NODE_PATTERNS = [
    "pnpm --filter api-node lint",
    "pnpm --filter api-node typecheck",
]


def assert_contains(path: Path, fragments: list[str]) -> list[str]:
    missing: list[str] = []
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment not in text:
            missing.append(fragment)
    return missing


def main() -> int:
    makefile_missing = assert_contains(MAKEFILE, REQUIRED_PATTERNS)
    task_missing = assert_contains(UV_TASK, REQUIRED_PATTERNS)

    errors: list[str] = []
    if makefile_missing:
        errors.append(f"Makefile missing: {', '.join(makefile_missing)}")
    if task_missing:
        errors.append(f"uv task missing: {', '.join(task_missing)}")

    # Only enforce Node parity when Node snippets exist in Makefile
    makefile_node_missing = assert_contains(MAKEFILE, NODE_PATTERNS)
    if not makefile_node_missing:
        task_node_missing = assert_contains(UV_TASK, NODE_PATTERNS)
        if task_node_missing:
            errors.append(f"uv task missing Node commands: {', '.join(task_node_missing)}")

    if errors:
        for error in errors:
            sys.stderr.write(f"[quality-parity] {error}\n")
        return 1

    sys.stdout.write("Quality parity checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
