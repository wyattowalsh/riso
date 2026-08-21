"""Path resolution and validation for Riso CLI."""

from __future__ import annotations

import os
from pathlib import Path

from riso.core.errors import PermissionDeniedError, TemplateNotFoundError

# Hatch force-include maps repo ``template/`` → ``riso/copier_template`` in wheels.
PACKAGED_TEMPLATE_DIRNAME = "copier_template"

BUNDLED_UPDATE_UNSAFE_POLICY = (
    "Copier 9.16 _check_unsafe('update') flags subproject.template.tasks "
    "without consulting skip_tasks. Bundled-template UPDATE sets unsafe=True. "
    "External RISO_TEMPLATE_PATH still requires --force-unsafe. "
    "skip_tasks remains True for copy/update/recopy."
)


def repo_root() -> Path:
    """Return the src-layout parent (checkout root, or site-packages parent)."""
    return Path(__file__).resolve().parents[3]


def checkout_root() -> Path | None:
    """Return the git checkout root when this module is loaded from ``src/``."""
    candidate = Path(__file__).resolve().parents[3]
    if (candidate / "pyproject.toml").is_file() and (
        candidate / "template" / "copier.yml"
    ).is_file():
        return candidate
    return None


def packaged_template_path() -> Path | None:
    """Return the Copier template shipped inside the installed wheel, if present."""
    package_dir = Path(__file__).resolve().parents[1]
    candidate = package_dir / PACKAGED_TEMPLATE_DIRNAME
    if (candidate / "copier.yml").is_file():
        return candidate.resolve()
    return None


def bundled_template_path() -> Path:
    """Return the checkout or wheel-bundled Copier template directory."""
    checkout = checkout_root()
    if checkout is not None:
        return checkout / "template"
    packaged = packaged_template_path()
    if packaged is not None:
        return packaged
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
    """Resolve template directory from explicit path, env, checkout, or wheel."""
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

    bundled = bundled_template_path()
    if bundled.exists() and (bundled / "copier.yml").exists():
        return bundled.resolve()

    raise TemplateNotFoundError("clone the riso repository or pass --template-path")


def resolve_samples_path(explicit: Path | None = None) -> Path:
    """Resolve samples directory from explicit path, env, or checkout."""
    if explicit is not None:
        return explicit.expanduser().resolve()

    env_path = os.environ.get("RISO_SAMPLES_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    checkout = checkout_root()
    if checkout is not None:
        return (checkout / "samples").resolve()
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
