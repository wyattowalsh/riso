#!/usr/bin/env python3
"""Verify that the template mirrors `.github/context` best-practice files."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / ".github" / "context"
TEMPLATE_DIR = (
    REPO_ROOT / "template" / "files" / "shared" / ".github" / "context"
)


def file_digest(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def collect_digests(directory: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for file in sorted(directory.glob("*")):
        if file.is_file():
            digests[file.name] = file_digest(file)
    return digests


def main() -> None:
    if not SOURCE_DIR.exists():
        print("Source context directory missing.", file=sys.stderr)
        sys.exit(1)
    if not TEMPLATE_DIR.exists():
        print("Template context directory missing.", file=sys.stderr)
        sys.exit(1)

    source = collect_digests(SOURCE_DIR)
    template = collect_digests(TEMPLATE_DIR)

    missing = sorted(set(source) - set(template))
    extra = sorted(set(template) - set(source))
    mismatched = sorted(
        name
        for name in source
        if name in template and source[name] != template[name]
    )

    if not missing and not extra and not mismatched:
        print("Context directories are in sync.")
        return

    if missing:
        print("Missing context files in template:", ", ".join(missing), file=sys.stderr)
    if extra:
        print("Unexpected context files in template:", ", ".join(extra), file=sys.stderr)
    if mismatched:
        print("Content mismatches detected:", ", ".join(mismatched), file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
