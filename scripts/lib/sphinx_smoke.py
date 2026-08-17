"""Sphinx docs smoke argv for official sample renders."""

from __future__ import annotations

from pathlib import Path


def sphinx_linkcheck_command(
    python_cwd: Path,
    task_runner: str | None = None,
) -> list[str]:
    """Return the Sphinx linkcheck command for a rendered python/ tree.

    Default ``task_runner`` is ``just``. Prefer the matching recipe file when
    it exists; otherwise call ``sphinx-build`` directly (no dest-root make).
    """
    runner = str(task_runner or "just").strip().lower() or "just"
    if runner in {"just", "both"} and (python_cwd / "justfile").exists():
        return ["just", "linkcheck"]
    if runner in {"makefile", "both"} and (python_cwd / "Makefile").exists():
        return ["uv", "run", "make", "linkcheck"]
    return [
        "uv",
        "run",
        "--group",
        "docs",
        "sphinx-build",
        "-b",
        "linkcheck",
        "docs",
        "dist/docs-linkcheck",
    ]
