"""Ensure Makefile and uv task definitions stay aligned for quality commands."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "template" / "files" / "quality" / "makefile.quality.jinja"
PYTHON_TASK = REPO_ROOT / "template" / "files" / "python" / "tasks" / "quality.py.jinja"

MAKEFILE_PATTERNS = [
    "ruff check",
    "ty check",
    "pylint",
    "coverage run",
    "coverage report",
]
TASK_PATTERNS = ['"ruff"', '"ty"', '"pylint"', '"coverage"']
NODE_MAKEFILE_PATTERNS = [
    "pnpm --filter api-node lint",
    "pnpm --filter api-node typecheck",
]
NODE_TASK_PATTERNS = [
    '"api-node", "lint"',
    '"api-node", "typecheck"',
]

# Backward-compatible aliases for older imports
REQUIRED_PATTERNS = MAKEFILE_PATTERNS
NODE_PATTERNS = NODE_MAKEFILE_PATTERNS
UV_TASK = PYTHON_TASK


def assert_contains(path: Path, fragments: list[str]) -> list[str]:
    missing: list[str] = []
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment not in text:
            missing.append(fragment)
    return missing


def main() -> int:
    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    task_text = PYTHON_TASK.read_text(encoding="utf-8")

    makefile_missing = [p for p in MAKEFILE_PATTERNS if p not in makefile_text]
    task_missing = [p for p in TASK_PATTERNS if p not in task_text]

    errors: list[str] = []
    if makefile_missing:
        errors.append(f"Makefile missing: {', '.join(makefile_missing)}")
    if task_missing:
        errors.append(f"python task missing: {', '.join(task_missing)}")

    # Only enforce Node parity when Node snippets exist in Makefile
    makefile_node_missing = [
        p for p in NODE_MAKEFILE_PATTERNS if p not in makefile_text
    ]
    if not makefile_node_missing:
        task_node_missing = [p for p in NODE_TASK_PATTERNS if p not in task_text]
        if task_node_missing:
            errors.append(
                f"python task missing Node commands: {', '.join(task_node_missing)}"
            )

    if errors:
        for error in errors:
            sys.stderr.write(f"[quality-parity] {error}\n")
        return 1

    sys.stdout.write("Quality parity checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
