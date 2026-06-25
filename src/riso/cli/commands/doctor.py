"""Doctor command — verify environment and paths."""

from __future__ import annotations

import importlib.metadata
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_doctor(*, config: CliConfig) -> dict:
    """Check tooling and resolved paths."""
    checks: dict[str, object] = {}

    template_path, template_error = config.optional_template_path()
    if template_path is not None:
        checks["template_path"] = str(template_path)
        checks["template_exists"] = template_path.exists()
        checks["copier_yml"] = str(template_path / "copier.yml")
    else:
        checks["template_path"] = None
        checks["template_exists"] = False
        checks["template_error"] = template_error
        checks["copier_yml"] = None

    samples_path = config.samples_path
    checks["samples_path"] = str(samples_path)
    checks["samples_exists"] = samples_path.exists()

    copier_path = shutil.which("copier")
    checks["copier"] = {
        "available": copier_path is not None,
        "path": copier_path,
    }
    if copier_path:
        try:
            proc = subprocess.run(
                ["copier", "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            checks["copier"]["version"] = (proc.stdout or proc.stderr).strip()
        except (subprocess.SubprocessError, OSError):
            checks["copier"]["version"] = None

    uv_path = shutil.which("uv")
    checks["uv"] = {"available": uv_path is not None, "path": uv_path}

    try:
        checks["riso_version"] = importlib.metadata.version("riso")
    except importlib.metadata.PackageNotFoundError:
        checks["riso_version"] = "unknown"

    checks["ready"] = bool(
        template_path is not None
        and checks["template_exists"]
        and (template_path / "copier.yml").exists()
        and checks["copier"]["available"]
    )

    return {"checks": checks, "ready": checks["ready"]}
