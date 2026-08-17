"""Ensure task-runner and uv task definitions stay aligned for quality commands."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "template" / "files" / "quality" / "makefile.quality.jinja"
JUSTFILE = REPO_ROOT / "template" / "files" / "quality" / "justfile.quality.jinja"
PYTHON_TASK = REPO_ROOT / "template" / "files" / "python" / "tasks" / "quality.py.jinja"
UV_TASK = REPO_ROOT / "template" / "files" / "quality" / "uv_tasks" / "quality.py.jinja"

MAKEFILE_PATTERNS = [
    "ruff check",
    "ty check",
    "pylint",
    "coverage run",
    "coverage report",
    "ruff format",
    "--rcfile",
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

NODE_SECTION_PATTERN = re.compile(
    r"\{%\s*if\s+api_module\s*==\s*'enabled'\s+and\s+'node'\s+in\s+api_languages\s*%\}"
    r".*?"
    r"\{%\s*endif\s*%\}",
    re.DOTALL,
)

_SPLIT_CMD = re.compile(
    r'"(ruff|ty|pylint|coverage)"\s*,\s*(?:\n\s*)?"(check|format|run|report)"',
    re.MULTILINE,
)
_TY_LINE = re.compile(r"ty\s+check\b", re.IGNORECASE)
_PYLINT_LINE = re.compile(r"\bpylint\b", re.IGNORECASE)
_FORMAT_LINE = re.compile(r"ruff\s+format\b", re.IGNORECASE)
_COVERAGE_RUN = re.compile(r"coverage\s+run\b", re.IGNORECASE)


def _collapse_argv_lists(text: str) -> str:
    """Join split quoted argv items so ``"ty",\\n "check"`` becomes ``ty check``."""
    collapsed = text
    for _ in range(12):
        nxt = re.sub(
            r'"([^"\n]+)"\s*,\s*\n\s*"([^"\n]+)"',
            r'"\1" "\2"',
            collapsed,
        )
        if nxt == collapsed:
            break
        collapsed = nxt
    replacements = (
        ('"ty" "check"', "ty check"),
        ('"ruff" "check"', "ruff check"),
        ('"ruff" "format"', "ruff format"),
        ('"coverage" "run"', "coverage run"),
        ('"coverage" "report"', "coverage report"),
        ('"--rcfile"', "--rcfile"),
    )
    for src, dest in replacements:
        collapsed = collapsed.replace(src, dest)
    return collapsed


def _normalize_vars(text: str) -> str:
    return (
        text.replace("$(PACKAGE_NAME)", "{{ package_name }}")
        .replace("$(PYLINT_FLAGS)", "")
        .replace("$(TY_FLAGS)", "")
        .replace("$(RUFF_FLAGS)", "")
        .replace("$(COVERAGE_RCFILE)", "coverage.cfg")
        .replace("$(COVERAGE_FLAGS)", "--rcfile coverage.cfg")
    )


def _command_present(text: str, command: str) -> bool:
    """Return True when *command* appears as a shell string or split argv list."""
    if command in text:
        return True
    collapsed = _collapse_argv_lists(text)
    if command in collapsed:
        return True
    parts = command.split()
    if len(parts) == 2:
        tool, sub = parts
        if re.search(
            rf'"{re.escape(tool)}"\s*,\s*(?:\n\s*)?"{re.escape(sub)}"',
            text,
        ):
            return True
    return bool(
        _SPLIT_CMD.search(text)
        and command.replace(" ", "") in collapsed.replace(" ", "")
    )


def _window_after(text: str, pattern: re.Pattern[str], size: int = 240) -> str | None:
    match = pattern.search(text)
    if match is None:
        return None
    return text[match.start() : match.start() + size]


def _path_token(window: str) -> str | None:
    normalized = _normalize_vars(window)
    if "src/{{ package_name }}" in normalized or "src/PKG" in normalized:
        return "src/PKG"
    if (
        re.search(r'"src"|ty check[^\n]*\bsrc\b', normalized)
        and "src/" not in normalized
    ):
        return "src"
    if "{{ package_name }}" in normalized:
        return "PKG"
    return None


def _normalize_checker_paths(text: str) -> tuple[str | None, str | None, str | None]:
    """Return (ty, pylint, format) path signatures when present."""
    collapsed = _normalize_vars(_collapse_argv_lists(text))
    ty_sig: str | None = None
    pylint_sig: str | None = None
    format_sig: str | None = None

    ty_window = _window_after(collapsed, _TY_LINE)
    if ty_window:
        ty_sig = _path_token(ty_window)

    for raw_line in collapsed.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if _PYLINT_LINE.search(line) and "run" in line:
            tokens: list[str] = []
            if "src/{{ package_name }}" in line or "src/PKG" in line:
                tokens.append("src/PKG")
            elif "{{ package_name }}" in line:
                tokens.append("PKG")
            if "tests" in line:
                tokens.append("tests")
            if tokens:
                pylint_sig = "+".join(sorted(set(tokens)))

    fmt_window = _window_after(collapsed, _FORMAT_LINE)
    if fmt_window:
        tokens = []
        if "src/{{ package_name }}" in fmt_window or "src/PKG" in fmt_window:
            tokens.append("src/PKG")
        if "tests" in fmt_window:
            tokens.append("tests")
        format_sig = "+".join(tokens) if tokens else "bare"

    return ty_sig, pylint_sig, format_sig


def _coverage_run_has_rcfile(text: str) -> bool:
    collapsed = _collapse_argv_lists(text)
    window = _window_after(collapsed, _COVERAGE_RUN, size=320)
    return bool(window and "--rcfile" in window)


def _checker_path_errors(
    surfaces: dict[str, str],
) -> list[str]:
    """Compare ty/pylint/format paths and coverage --rcfile across surfaces."""
    errors: list[str] = []
    signatures = {
        name: _normalize_checker_paths(text) for name, text in surfaces.items()
    }
    ty_values = {name: sig[0] for name, sig in signatures.items() if sig[0] is not None}
    pylint_surfaces = {
        name: sig[1]
        for name, sig in signatures.items()
        if sig[1] is not None and name in {"Makefile", "justfile", "uv_tasks"}
    }
    format_surfaces = {
        name: sig[2]
        for name, sig in signatures.items()
        if sig[2] is not None and name in {"Makefile", "justfile"}
    }
    if len(ty_values) >= 2 and len(set(ty_values.values())) > 1:
        errors.append(f"ty check path mismatch: {ty_values}")
    if len(pylint_surfaces) >= 2 and len(set(pylint_surfaces.values())) > 1:
        errors.append(f"pylint path mismatch: {pylint_surfaces}")
    if len(format_surfaces) >= 2 and len(set(format_surfaces.values())) > 1:
        errors.append(f"ruff format path mismatch: {format_surfaces}")

    for name, text in surfaces.items():
        if "coverage" in text.lower() and not _coverage_run_has_rcfile(text):
            # Taskipy python/tasks is allowed to be the coverage SSOT; flag uv_tasks
            # and aggregators that already emit coverage run.
            if name in {"Makefile", "justfile", "uv_tasks"} or _command_present(
                text, "coverage run"
            ):
                errors.append(f"{name} coverage run missing --rcfile")
    return errors


def _has_unconditional_patterns(text: str, patterns: list[str]) -> bool:
    """Return True when patterns appear outside optional Node API Jinja blocks."""
    stripped = NODE_SECTION_PATTERN.sub("", text)
    return all(_command_present(stripped, pattern) for pattern in patterns)


def assert_contains(path: Path, fragments: list[str]) -> list[str]:
    missing: list[str] = []
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment not in text:
            missing.append(fragment)
    return missing


def _missing_patterns(text: str, patterns: list[str]) -> list[str]:
    return [pattern for pattern in patterns if not _command_present(text, pattern)]


def main() -> int:
    task_text = PYTHON_TASK.read_text(encoding="utf-8")
    task_missing = [p for p in TASK_PATTERNS if p not in task_text]

    errors: list[str] = []
    if task_missing:
        errors.append(f"python task missing: {', '.join(task_missing)}")

    requires_node_parity = False

    if MAKEFILE.exists():
        makefile_text = MAKEFILE.read_text(encoding="utf-8")
        makefile_missing = _missing_patterns(makefile_text, MAKEFILE_PATTERNS)
        if makefile_missing:
            errors.append(f"Makefile missing: {', '.join(makefile_missing)}")
        if _has_unconditional_patterns(makefile_text, NODE_MAKEFILE_PATTERNS):
            requires_node_parity = True

    if JUSTFILE.exists():
        justfile_text = JUSTFILE.read_text(encoding="utf-8")
        justfile_missing = _missing_patterns(justfile_text, JUSTFILE_PATTERNS)
        if justfile_missing:
            errors.append(f"justfile missing: {', '.join(justfile_missing)}")
        if _has_unconditional_patterns(justfile_text, NODE_JUSTFILE_PATTERNS):
            requires_node_parity = True

    if UV_TASK.exists():
        uv_text = UV_TASK.read_text(encoding="utf-8")
        uv_missing = [p for p in TASK_PATTERNS if p not in uv_text]
        if uv_missing:
            errors.append(f"uv_tasks missing: {', '.join(uv_missing)}")
        uv_cmd_missing = _missing_patterns(
            uv_text, ["ruff check", "ty check", "pylint", "coverage run", "--rcfile"]
        )
        if uv_cmd_missing:
            errors.append(f"uv_tasks missing command: {', '.join(uv_cmd_missing)}")
        if _has_unconditional_patterns(uv_text, NODE_TASK_PATTERNS):
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
    if UV_TASK.exists():
        surfaces["uv_tasks"] = UV_TASK.read_text(encoding="utf-8")
    errors.extend(_checker_path_errors(surfaces))

    if errors:
        for error in errors:
            sys.stderr.write(f"[quality-parity] {error}\n")
        return 1

    sys.stdout.write("Quality parity checks passed.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
