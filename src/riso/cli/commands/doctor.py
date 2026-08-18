"""Doctor command — verify environment and paths."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
import subprocess
from typing import TYPE_CHECKING, Any

from riso.core.paths import (
    BUNDLED_UPDATE_UNSAFE_POLICY,
    external_template_warning,
    is_bundled_template,
)
from riso.template import load_copier_config

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def _version_tuple(raw: str) -> tuple[int, int, int]:
    """Numeric major.minor.patch prefix of a version string."""
    text = raw.strip()
    candidate = ""
    for token in text.replace(",", " ").split():
        stripped = token.lstrip("vV")
        if stripped and stripped[0].isdigit():
            candidate = stripped
            break
    if not candidate:
        candidate = text.lstrip("vV")
    parts: list[int] = []
    for chunk in candidate.split("."):
        digits = ""
        for char in chunk:
            if char.isdigit():
                digits += char
            else:
                break
        if digits:
            parts.append(int(digits))
        if len(parts) >= 3:
            break
    padded = (parts + [0, 0, 0])[:3]
    return padded[0], padded[1], padded[2]


def meets_min_copier(installed: str | None, minimum: str | None) -> bool:
    """Return True when *installed* satisfies *minimum* (or no minimum)."""
    if not minimum:
        return True
    if not installed:
        return False
    return _version_tuple(installed) >= _version_tuple(minimum)


def _copier_package_version() -> str | None:
    try:
        return importlib.metadata.version("copier")
    except importlib.metadata.PackageNotFoundError:
        return None


def run_doctor(*, config: CliConfig) -> dict:
    """Check tooling and resolved paths."""
    checks: dict[str, object] = {}

    warnings: list[str] = []
    copier_cfg: dict[str, Any] | None = None
    template_path, template_error = config.optional_template_path()
    if template_path is not None:
        checks["template_path"] = str(template_path)
        checks["template_exists"] = template_path.exists()
        try:
            copier_cfg = load_copier_config(template_path)
            checks["copier_config_valid"] = True
            checks["copier_yml"] = str(template_path / "copier.yml")
        except (FileNotFoundError, RuntimeError) as exc:
            checks["copier_config_valid"] = False
            checks["copier_yml"] = None
            checks["copier_config_error"] = str(exc)
        trust_warning = external_template_warning(template_path)
        if trust_warning:
            warnings.append(trust_warning)
    else:
        checks["template_path"] = None
        checks["template_exists"] = False
        checks["template_error"] = template_error
        checks["copier_yml"] = None

    min_raw = None
    if copier_cfg:
        min_raw = copier_cfg.get("_min_copier_version") or copier_cfg.get(
            "_min_copier_version"
        )
    min_copier = str(min_raw).strip() if min_raw else None
    checks["min_copier_version"] = min_copier

    samples_path = config.samples_path
    checks["samples_path"] = str(samples_path)
    checks["samples_exists"] = samples_path.exists()

    copier_importable = importlib.util.find_spec("copier") is not None
    copier_path = shutil.which("copier")
    package_version = _copier_package_version()
    copier_meets_min = meets_min_copier(package_version, min_copier)
    checks["copier"] = {
        "available": copier_importable,
        "path": copier_path,
        "package_version": package_version,
        "meets_min": copier_meets_min,
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

    git_path = shutil.which("git")
    checks["git"] = {"available": git_path is not None, "path": git_path}

    try:
        checks["riso_version"] = importlib.metadata.version("riso")
    except importlib.metadata.PackageNotFoundError:
        checks["riso_version"] = "unknown"

    bundled = bool(template_path is not None and is_bundled_template(template_path))
    template_has_tasks = bool(
        copier_cfg and (copier_cfg.get("_tasks") or copier_cfg.get("tasks"))
    )
    update_sets_unsafe = bundled
    checks["template_has_tasks"] = template_has_tasks
    checks["update_sets_unsafe"] = update_sets_unsafe
    checks["bundled_update_unsafe"] = {
        "applies": bundled,
        "unsafe": bundled,
        "policy": BUNDLED_UPDATE_UNSAFE_POLICY,
    }
    if update_sets_unsafe and template_has_tasks:
        warnings.append(BUNDLED_UPDATE_UNSAFE_POLICY)

    checks["ready"] = bool(
        template_path is not None
        and checks["template_exists"]
        and checks.get("copier_config_valid")
        and copier_importable
        and uv_path is not None
        and git_path is not None
        and copier_meets_min
    )

    # Always emit envelope-friendly top-level keys (empty warnings list when clean).
    return {
        "checks": checks,
        "ready": checks["ready"],
        "warnings": warnings,
    }
