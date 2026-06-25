#!/usr/bin/env python3
"""Validate AGENTS.md ecosystem template artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_FILES = REPO_ROOT / "template" / "files"

REQUIRED_ALWAYS = [
    TEMPLATE_FILES / "AGENTS.md.jinja",
]

BRIDGE_FILES = [
    TEMPLATE_FILES / "CLAUDE.md.jinja",
    TEMPLATE_FILES / ".cursor" / "rules.jinja",
    TEMPLATE_FILES / ".warp" / "WARP.md.jinja",
]

MAX_BRIDGE_LINES = 15


def _fail(message: str) -> int:
    sys.stderr.write(f"agents-ecosystem: {message}\n")
    return 1


def check_required_files() -> int:
    """Ensure SSOT and bridge templates exist."""
    errors = 0
    for path in REQUIRED_ALWAYS:
        if not path.is_file():
            errors += _fail(f"missing required template: {path.relative_to(REPO_ROOT)}")
    for path in BRIDGE_FILES:
        if not path.is_file():
            errors += _fail(f"missing bridge template: {path.relative_to(REPO_ROOT)}")
    return errors


def check_bridge_pointer_only() -> int:
    """Bridge files must be short and reference AGENTS.md."""
    errors = 0
    for path in BRIDGE_FILES:
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) > MAX_BRIDGE_LINES:
            errors += _fail(
                f"{path.name} has {len(lines)} non-empty lines (max {MAX_BRIDGE_LINES})"
            )
        if "AGENTS.md" not in text:
            errors += _fail(f"{path.name} does not reference AGENTS.md")
        if "| Task | Command |" in text:
            errors += _fail(f"{path.name} duplicates command table from AGENTS.md")
    return errors


def check_copier_exclude() -> int:
    """copier.yml must exclude harness files when ai_tools_module is disabled."""
    copier_yml = REPO_ROOT / "template" / "copier.yml"
    text = copier_yml.read_text(encoding="utf-8")
    required_snippets = [
        "ai_tools_module != 'enabled' %}CLAUDE.md",
        "ai_tools_module != 'enabled' %}docs/ai-tools.md",
    ]
    errors = 0
    for snippet in required_snippets:
        if snippet not in text:
            errors += _fail(f"copier.yml missing ai_tools exclude: {snippet}")
    return errors


def check_render_tree(render_dir: Path, *, ai_tools_enabled: bool) -> int:
    """Validate AGENTS.md and optional harness files in a render directory."""
    errors = 0
    agents = render_dir / "AGENTS.md"
    if not agents.is_file():
        errors += _fail(f"render missing AGENTS.md: {render_dir}")
        return errors

    agents_text = agents.read_text(encoding="utf-8")
    agents_lines = [line for line in agents_text.splitlines() if line.strip()]
    if len(agents_lines) < 20:
        errors += _fail(
            f"AGENTS.md too short in {render_dir} ({len(agents_lines)} lines)"
        )

    if re.search(r"\|\|", agents_text):
        errors += _fail(
            f"AGENTS.md quick-reference table has merged rows in {render_dir}"
        )

    if (render_dir / "macros").exists():
        errors += _fail(f"render leaked template macros/: {render_dir / 'macros'}")

    bridge_paths = [
        render_dir / "CLAUDE.md",
        render_dir / ".warp" / "WARP.md",
        render_dir / ".cursor" / "rules",
    ]
    if ai_tools_enabled:
        for path in bridge_paths:
            if not path.is_file():
                errors += _fail(f"ai_tools enabled but missing bridge: {path}")
            else:
                lines = [
                    line
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                if len(lines) > MAX_BRIDGE_LINES:
                    errors += _fail(
                        f"{path.name} has {len(lines)} lines (max {MAX_BRIDGE_LINES})"
                    )
    else:
        for path in bridge_paths:
            if path.exists():
                errors += _fail(f"ai_tools disabled but bridge present: {path}")
        if (render_dir / "docs" / "ai-tools.md").exists():
            errors += _fail("ai_tools disabled but docs/ai-tools.md present")
    return errors


def main() -> int:
    """Run all AGENTS ecosystem checks."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate AGENTS.md ecosystem")
    parser.add_argument(
        "--render-enabled",
        type=Path,
        action="append",
        default=[],
        help="Render dir that should include harness bridge files",
    )
    parser.add_argument(
        "--render-disabled",
        type=Path,
        action="append",
        default=[],
        help="Render dir with ai_tools_module disabled (no harness files)",
    )
    args = parser.parse_args()

    errors = 0
    errors += check_required_files()
    errors += check_bridge_pointer_only()
    errors += check_copier_exclude()
    for render_dir in args.render_enabled:
        errors += check_render_tree(render_dir, ai_tools_enabled=True)
    for render_dir in args.render_disabled:
        errors += check_render_tree(render_dir, ai_tools_enabled=False)
    if errors:
        sys.stderr.write(f"agents-ecosystem: {errors} check(s) failed\n")
        return 1
    sys.stdout.write("agents-ecosystem: all checks passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
