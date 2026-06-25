"""Catalog command — module catalog introspection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from riso.template import get_module_catalog

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_catalog_modules(config: CliConfig) -> dict:
    """Return rendered module catalog."""
    catalog = get_module_catalog(config.template_path)
    return {"catalog": catalog}


def run_catalog_dependencies(config: CliConfig) -> dict:
    """Summarize lock files and tooling versions."""
    root = config.template_path.parent
    summary: dict[str, object] = {"template_path": str(config.template_path)}

    lock_files = {
        "uv.lock": root / "uv.lock",
        "pnpm-lock.yaml": root / "pnpm-lock.yaml",
        "web/pnpm-lock.yaml": root / "web" / "pnpm-lock.yaml",
    }
    summary["lock_files"] = {
        name: {"exists": path.exists(), "path": str(path)}
        for name, path in lock_files.items()
    }

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        summary["pyproject"] = str(pyproject)

    return summary
