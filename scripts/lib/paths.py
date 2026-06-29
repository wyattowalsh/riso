"""Repository path helpers for maintainer CI scripts."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the riso repository root (scripts/lib -> scripts -> repo)."""
    return Path(__file__).resolve().parents[2]


def samples_dir() -> Path:
    """Return the samples directory."""
    return repo_root() / "samples"


def template_dir() -> Path:
    """Return the template directory."""
    return repo_root() / "template"
