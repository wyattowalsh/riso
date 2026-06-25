"""Ensure task-runner and uv task definitions stay aligned for quality commands."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "template" / "files" / "quality" / "makefile.quality.jinja"
JUSTFILE = REPO_ROOT / "template" / "files" / "quality" / "justfile.quality.jinja"
PYTHON_TASK = REPO_ROOT / "template" / "files" / "python" / "tasks" / "quality.py.jinja"

MAKEFILE_PATTERNS = [
    "ruff check",
    "ty check",
    "pylint",
    "coverage run",
    "coverage report",
]
JUSTFILE_PATTERNS = MAKEFILE_PATTERNS
TASK_PATTERNS = ['"ruff"', '"ty"', '"pylint"', '"coverage"']
NODE_MAKEFILE_PATTERNS = [
    "pnpm --filter api-node lint",
    "pnpm --filter api-node typecheck",
]
NODE_JUSTFILE_PATTERNS = NODE_MAKEFILE_PATTERNS
NODE_TASK_PATTERNS = [
    '"api-node", "lint"',
    '"api-node", "typecheck"',
]

# Backward-compatible aliases for older imports
REQUIRED_PATTERNS = MAKEFILE_PATTERNS
NODE_PATTERNS = NODE_MAKEFILE_PATTERNS
UV_TASK = PYTHON_TASK

NODE_SECTION_PATTERN = re.compile(
    r"\{%\s*if\s+api_module\s*==\s*'enabled'\s+and\s+'node'\s+in\s+api_languages\s*%\}"
    r".*?"
    r"\{%\s*endif\s*%\}",
    re.DOTALL,
)


def _has_unconditional_patterns(text: str, patterns: list[str]) -> bool:
    """Return True when patterns appear outside optional Node API Jinja blocks."""
    stripped = NODE_SECTION_PATTERN.sub("", text)
    return all(pattern in stripped for pattern in patterns)


def assert_contains(path: Path, fragments: list[str]) -> list[str]:
    missing: list[str] = []
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment not in text:
            missing.append(fragment)
    return missing


def main() -> int:
    task_text = PYTHON_TASK.read_text(encoding="utf-8")
    task_missing = [p for p in TASK_PATTERNS if p not in task_text]

    errors: list[str] = []
    if task_missing:
        errors.append(f"python task missing: {', '.join(task_missing)}")

    requires_node_parity = False

    if MAKEFILE.exists():
        makefile_text = MAKEFILE.read_text(encoding="utf-8")
        makefile_missing = [p for p in MAKEFILE_PATTERNS if p not in makefile_text]
        if makefile_missing:
            errors.append(f"Makefile missing: {', '.join(makefile_missing)}")
        if _has_unconditional_patterns(makefile_text, NODE_MAKEFILE_PATTERNS):
            requires_node_parity = True

    if JUSTFILE.exists():
        justfile_text = JUSTFILE.read_text(encoding="utf-8")
        justfile_missing = [p for p in JUSTFILE_PATTERNS if p not in justfile_text]
        if justfile_missing:
            errors.append(f"justfile missing: {', '.join(justfile_missing)}")
        if _has_unconditional_patterns(justfile_text, NODE_JUSTFILE_PATTERNS):
            requires_node_parity = True

    if requires_node_parity:
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
