"""Path resolution and validation for Riso CLI."""

from __future__ import annotations

import os
from pathlib import Path

from riso.core.errors import PermissionDeniedError, TemplateNotFoundError


def repo_root() -> Path:
    """Return the repository root when running from a checkout."""
    return Path(__file__).resolve().parents[3]


BUNDLED_UPDATE_UNSAFE_POLICY = (
    "Copier 9.16 _check_unsafe('update') flags subproject.template.tasks "
    "without consulting skip_tasks. Bundled-template UPDATE sets unsafe=True. "
    "External RISO_TEMPLATE_PATH still requires --force-unsafe. "
    "skip_tasks remains True for copy/update/recopy."
)


def bundled_template_path() -> Path:
    """Return this checkout's template/ directory (may not exist)."""
    return repo_root() / "template"


def is_bundled_template(path: Path) -> bool:
    """Return True when *path* is this repository's bundled template root."""
    bundled = bundled_template_path()
    if not bundled.exists():
        return False
    try:
        return path.resolve() == bundled.resolve()
    except OSError:
        return False


def external_template_warning(path: Path) -> str | None:
    """Return a warning when using a template outside this repository checkout."""
    if not bundled_template_path().exists():
        return None
    try:
        if not is_bundled_template(path):
            return (
                f"Template path {path} is outside this repository. "
                "Only use templates from sources you trust."
            )
    except OSError:
        return None
    return None


def resolve_template_path(explicit: Path | None = None) -> Path:
    """Resolve template directory from explicit path, env, or checkout."""
    if explicit is not None:
        path = Path(os.path.expandvars(str(explicit))).expanduser().resolve()
        if not path.exists():
            raise TemplateNotFoundError(str(path))
        return path

    env_path = os.environ.get("RISO_TEMPLATE_PATH")
    if env_path:
        path = Path(os.path.expandvars(env_path)).expanduser().resolve()
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


_HOME_SECRET_DIR_NAMES = (".ssh", ".gnupg", ".aws")


def _home_secret_dirs() -> list[Path]:
    home = Path.home().resolve()
    return [(home / name).resolve() for name in _HOME_SECRET_DIR_NAMES]


def _raises_if_under_secret_dir(path: Path) -> None:
    for secret_dir in _home_secret_dirs():
        if path == secret_dir:
            raise PermissionDeniedError(
                "destination", f"Cannot write to secret directory: {secret_dir}"
            )
        try:
            path.relative_to(secret_dir)
        except ValueError:
            continue
        raise PermissionDeniedError(
            "destination", f"Cannot write under secret directory: {secret_dir}"
        )


def validate_destination(dest: str, safe_parent: Path | None = None) -> Path:
    """Validate destination does not escape safe directory or system paths."""
    path = Path(os.path.expandvars(dest)).expanduser().resolve()

    if safe_parent:
        safe_parent = safe_parent.resolve()
        try:
            path.relative_to(safe_parent)
        except ValueError as err:
            raise PermissionDeniedError(
                "destination", f"Outside allowed parent: {safe_parent}"
            ) from err

    dangerous_exact = {
        "/",
        "/etc",
        "/usr",
        "/bin",
        "/sbin",
        "/root",
        "/private/etc",
        "/var",
        "/private/var",
        "/System",
        "/System/Volumes/Data",
    }
    dangerous_prefixes = (
        "/etc/",
        "/usr/",
        "/bin/",
        "/sbin/",
        "/root/",
        "/private/etc/",
        "/var/log/",
        "/var/db/",
        "/var/mail/",
        "/var/spool/",
        "/private/var/log/",
        "/private/var/db/",
        "/private/var/mail/",
        "/private/var/spool/",
        "/System/",
    )
    path_str = str(path)

    if path_str in dangerous_exact:
        raise PermissionDeniedError("destination", "Cannot write to system directories")
    for prefix in dangerous_prefixes:
        if path_str.startswith(prefix):
            raise PermissionDeniedError(
                "destination", "Cannot write to system directories"
            )

    _raises_if_under_secret_dir(path)

    return path
