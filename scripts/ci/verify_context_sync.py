#!/usr/bin/env python3
"""Verify that the template mirrors `.github/context` best-practice files."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from scripts.lib.logger import logger, configure_logging

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
    configure_logging()

    if not SOURCE_DIR.exists():
        logger.error("Source context directory missing.")
        sys.exit(1)
    if not TEMPLATE_DIR.exists():
        logger.error("Template context directory missing.")
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
        logger.info("Context directories are in sync.")
        return

    if missing:
        logger.error("Missing context files in template: " + ", ".join(missing))
    if extra:
        logger.error("Unexpected context files in template: " + ", ".join(extra))
    if mismatched:
        logger.error("Content mismatches detected: " + ", ".join(mismatched))
    sys.exit(1)


if __name__ == "__main__":
    main()
