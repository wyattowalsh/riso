"""Pre-generation hook that validates local tooling required by the Riso template.

The hook intentionally avoids network access and only checks for the presence of
executables so it remains compliant with the determinism requirements.
"""

from __future__ import annotations

import shutil
import sys

REQUIRED_BINARIES = [
    ("uv", "Install uv from https://github.com/astral-sh/uv"),
    ("python3", "Install Python 3.11 or newer"),
    ("pnpm", "Install pnpm 8+ from https://pnpm.io/installation"),
]


def main() -> None:
    missing: list[str] = []
    for binary, help_text in REQUIRED_BINARIES:
        if shutil.which(binary) is None:
            missing.append(f"- {binary}: {help_text}")

    if missing:
        formatted = "\n".join(missing)
        sys.stderr.write(
            "Riso template prerequisite check failed. Please install the "
            "following tools before rendering:\n"
        )
        sys.stderr.write(f"{formatted}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
