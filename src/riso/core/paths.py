"""Path resolution and validation for Riso CLI."""

from __future__ import annotations

import os
from pathlib import Path

from riso.core.errors import PermissionDeniedError, TemplateNotFoundError


def repo_root() -> Path:
    """Return the repository root when running from a checkout."""
    return Path(__file__).resolve().parents[3]


def resolve_template_path(explicit: Path | None = None) -> Path:
    """Resolve template directory from explicit path, env, or checkout."""
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.exists():
            raise TemplateNotFoundError(str(path))
        return path

    env_path = os.environ.get("RISO_TEMPLATE_PATH")
    if env_path:
        path = Path(env_path).expanduser().resolve()
        if not path.exists():
            raise TemplateNotFoundError(str(path))
        return path

    checkout = repo_root() / "template"
    if checkout.exists() and (checkout / "copier.yml").exists():
        return checkout.resolve()

    raise TemplateNotFoundError("clone the riso repository or pass --template-path")


def resolve_samples_path(explicit: Path | None = None) -> Path:
    """Resolve samples directory from explicit path, env, or checkout."""
    if explicit is not None:
        return explicit.expanduser().resolve()

    env_path = os.environ.get("RISO_SAMPLES_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    return (repo_root() / "samples").resolve()


def validate_destination(dest: str, safe_parent: Path | None = None) -> Path:
    """Validate destination does not escape safe directory or system paths."""
    path = Path(dest).expanduser().resolve()

    if safe_parent:
        safe_parent = safe_parent.resolve()
        try:
            path.relative_to(safe_parent)
        except ValueError as err:
            raise PermissionDeniedError(
                "destination", f"Outside allowed parent: {safe_parent}"
            ) from err

    dangerous_paths = [
        "/etc",
        "/usr",
        "/bin",
        "/sbin",
        "/root",
        "/private/etc",
        "/var/log",
        "/var/db",
        "/var/mail",
        "/var/spool",
        "/private/var/log",
        "/private/var/db",
        "/private/var/mail",
        "/private/var/spool",
        "/System/Volumes/Data/home",
        "/home",
    ]
    path_str = str(path)

    for dangerous in dangerous_paths:
        if path_str == dangerous or path_str.startswith(dangerous + "/"):
            raise PermissionDeniedError(
                "destination", "Cannot write to system directories"
            )

    return path
