"""Repository path helpers for maintainer CI scripts."""

from __future__ import annotations

import os
from pathlib import Path

_SAMPLE_WALK_SKIP = frozenset(
    {"render", "metadata", "node_modules", ".venv", ".git", "__pycache__"}
)


def repo_root() -> Path:
    """Return the riso repository root (scripts/lib -> scripts -> repo)."""
    return Path(__file__).resolve().parents[2]


def samples_dir() -> Path:
    """Return the samples directory."""
    return repo_root() / "samples"


def iter_sample_answer_files(samples_root: Path) -> list[Path]:
    """Return ``copier-answers.yml`` paths under ``samples_root``.

    Uses a pruned ``os.walk`` (not ``Path.rglob``) so ``render/`` and
    package trees are not entered and ``ScandirIterator`` handles close.
    """
    if not samples_root.is_dir():
        return []
    found: list[Path] = []
    for root, dirnames, filenames in os.walk(
        samples_root, topdown=True, followlinks=False
    ):
        dirnames[:] = [name for name in dirnames if name not in _SAMPLE_WALK_SKIP]
        if "copier-answers.yml" in filenames:
            found.append(Path(root) / "copier-answers.yml")
    found.sort()
    return found


def template_dir() -> Path:
    """Return the template directory."""
    return repo_root() / "template"
