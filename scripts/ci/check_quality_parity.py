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

_TY_LINE = re.compile(r"ty\s+check\b", re.IGNORECASE)
_PYLINT_LINE = re.compile(r"\bpylint\b", re.IGNORECASE)


def _normalize_checker_paths(text: str) -> tuple[str | None, str | None]:
    """Return normalized ty/pylint path signatures when present in quality commands."""
    ty_sig: str | None = None
    pylint_sig: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        normalized = (
            line.replace("$(PACKAGE_NAME)", "{{ package_name }}")
            .replace("$(PYLINT_FLAGS)", "")
            .replace("$(TY_FLAGS)", "")
        )
        if _TY_LINE.search(normalized):
            if "src/{{ package_name }}" in normalized or "src/PKG" in normalized:
                ty_sig = "src/PKG"
            elif "{{ package_name }}" in normalized or "PKG" in normalized:
                ty_sig = "PKG"
        if _PYLINT_LINE.search(normalized) and "run" in normalized:
            tokens: list[str] = []
            if "src/{{ package_name }}" in normalized or "src/PKG" in normalized:
                tokens.append("src/PKG")
            if "{{ package_name }}" in normalized or "$(PACKAGE_NAME)" in line:
                tokens.append("PKG")
            if "tests" in normalized:
                tokens.append("tests")
            if tokens:
                pylint_sig = "+".join(sorted(set(tokens)))
    return ty_sig, pylint_sig


def _checker_path_errors(
    surfaces: dict[str, str],
) -> list[str]:
    """Compare ty/pylint path segments across makefile, justfile, and uv task."""
    errors: list[str] = []
    signatures = {
        name: _normalize_checker_paths(text) for name, text in surfaces.items()
    }
    ty_values = {name: sig[0] for name, sig in signatures.items() if sig[0] is not None}
    pylint_surfaces = {
        name: sig[1]
        for name, sig in signatures.items()
        if sig[1] is not None and name in {"Makefile", "justfile"}
    }
    if len(ty_values) >= 2 and len(set(ty_values.values())) > 1:
        errors.append(f"ty check path mismatch: {ty_values}")
    if len(pylint_surfaces) >= 2 and len(set(pylint_surfaces.values())) > 1:
        errors.append(f"pylint path mismatch: {pylint_surfaces}")
    return errors


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

    surfaces: dict[str, str] = {"python task": task_text}
    if MAKEFILE.exists():
        surfaces["Makefile"] = MAKEFILE.read_text(encoding="utf-8")
    if JUSTFILE.exists():
        surfaces["justfile"] = JUSTFILE.read_text(encoding="utf-8")
    errors.extend(_checker_path_errors(surfaces))

    if errors:
        for error in errors:
            sys.stderr.write(f"[quality-parity] {error}\n")
        return 1

    sys.stdout.write("Quality parity checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
