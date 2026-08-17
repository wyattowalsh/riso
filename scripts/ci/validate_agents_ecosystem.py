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

PLUGIN_SETTINGS_FILES = [
    TEMPLATE_FILES / ".cursor" / "settings.json.jinja",
    TEMPLATE_FILES / ".claude" / "settings.json.jinja",
    TEMPLATE_FILES / ".github" / "copilot" / "settings.json.jinja",
]

AGENTS_PLUGIN_MARKERS = (
    "wyattowalsh/agents",
    "agents@agents",
)


def _enables_agents_plugin(text: str) -> bool:
    """Return True if settings text enables the wyattowalsh/agents plugin."""
    if any(marker in text for marker in AGENTS_PLUGIN_MARKERS):
        return True
    return '"plugins"' in text and '"agents"' in text and '"enabled"' in text


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
    for path in PLUGIN_SETTINGS_FILES:
        if not path.is_file():
            errors += _fail(
                "missing agents plugin settings template: "
                f"{path.relative_to(REPO_ROOT)}"
            )
        else:
            text = path.read_text(encoding="utf-8")
            if not _enables_agents_plugin(text):
                errors += _fail(
                    f"{path.relative_to(REPO_ROOT)} does not enable wyattowalsh/agents"
                )
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
        "ai_tools_module != 'enabled' %}.github/copilot/",
    ]
    errors = 0
    for snippet in required_snippets:
        if snippet not in text:
            errors += _fail(f"copier.yml missing ai_tools exclude: {snippet}")
    return errors


def _plugin_settings_paths(render_dir: Path) -> list[Path]:
    """Return rendered Agents plugin settings paths."""
    return [
        render_dir / ".cursor" / "settings.json",
        render_dir / ".claude" / "settings.json",
        render_dir / ".github" / "copilot" / "settings.json",
    ]


def _check_render_plugin_settings(render_dir: Path, *, ai_tools_enabled: bool) -> int:
    """Require or forbid Agents plugin settings in a render tree."""
    errors = 0
    for path in _plugin_settings_paths(render_dir):
        if ai_tools_enabled:
            if not path.is_file():
                errors += _fail(f"ai_tools enabled but missing plugin settings: {path}")
            elif not _enables_agents_plugin(path.read_text(encoding="utf-8")):
                errors += _fail(f"{path} does not enable wyattowalsh/agents")
        elif path.exists():
            errors += _fail(f"ai_tools disabled but plugin settings present: {path}")
    return errors


def _bridge_paths(render_dir: Path) -> list[Path]:
    """Return rendered harness pointer files."""
    return [
        render_dir / "CLAUDE.md",
        render_dir / ".warp" / "WARP.md",
        render_dir / ".cursor" / "rules",
    ]


def _check_render_bridges(render_dir: Path, *, ai_tools_enabled: bool) -> int:
    """Require or forbid short AGENTS.md pointer files in a render tree."""
    errors = 0
    for path in _bridge_paths(render_dir):
        if ai_tools_enabled:
            if not path.is_file():
                errors += _fail(f"ai_tools enabled but missing bridge: {path}")
                continue
            lines = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            if len(lines) > MAX_BRIDGE_LINES:
                errors += _fail(
                    f"{path.name} has {len(lines)} lines (max {MAX_BRIDGE_LINES})"
                )
        elif path.exists():
            errors += _fail(f"ai_tools disabled but bridge present: {path}")
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

    errors += _check_render_bridges(render_dir, ai_tools_enabled=ai_tools_enabled)
    errors += _check_render_plugin_settings(
        render_dir, ai_tools_enabled=ai_tools_enabled
    )
    if not ai_tools_enabled and (render_dir / "docs" / "ai-tools.md").exists():
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
