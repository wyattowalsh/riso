#!/usr/bin/env python3
"""Refresh vendored shadcn/ui components in the SaaS template.

Runs ``pnpm dlx shadcn@latest add`` in a throwaway probe directory, then copies
generated ``components/ui/*.tsx`` files into
``template/files/node/saas/components/ui/*.tsx.jinja``.

Usage:
  uv run python scripts/ci/sync_template_shadcn_components.py
  uv run python scripts/ci/sync_template_shadcn_components.py --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_DIR = REPO_ROOT / "tmp" / "shadcn-probe"
TEMPLATE_UI = REPO_ROOT / "template" / "files" / "node" / "saas" / "components" / "ui"

COMPONENTS = (
    "button",
    "card",
    "dialog",
    "command",
    "dropdown-menu",
    "avatar",
    "label",
    "switch",
    "tabs",
    "table",
    "badge",
    "select",
    "input",
    "collapsible",
    "separator",
)


def _run(cmd: list[str], *, cwd: Path) -> None:
    print(f"+ {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def sync(*, dry_run: bool) -> int:
    if not PROBE_DIR.exists():
        print(f"Probe directory missing: {PROBE_DIR}", file=sys.stderr)
        print(
            "Create tmp/shadcn-probe with components.json + lib/utils.ts first.",
            file=sys.stderr,
        )
        return 1

    _run(
        [
            "pnpm",
            "dlx",
            "shadcn@latest",
            "add",
            *COMPONENTS,
            "-y",
        ],
        cwd=PROBE_DIR,
    )

    source_ui = PROBE_DIR / "components" / "ui"
    TEMPLATE_UI.mkdir(parents=True, exist_ok=True)

    copied = 0
    for name in COMPONENTS:
        src = source_ui / f"{name}.tsx"
        dst = TEMPLATE_UI / f"{name}.tsx.jinja"
        if not src.exists():
            print(f"WARNING: missing generated component: {src}", file=sys.stderr)
            continue
        if dry_run:
            print(f"would copy {src} -> {dst}")
        else:
            shutil.copy2(src, dst)
            print(f"copied {dst.name}")
        copied += 1

    print(f"\nSynced {copied} shadcn components into {TEMPLATE_UI}")
    return 0 if copied == len(COMPONENTS) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Show copies without writing."
    )
    args = parser.parse_args()
    try:
        return sync(dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
