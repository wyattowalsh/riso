"""Path resolution and validation for Riso CLI."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from riso.core.errors import (
    CopierOperationError,
    PermissionDeniedError,
    TemplateNotFoundError,
)


def packaged_template_path() -> Path | None:
    """Return the template shipped inside an installed Riso wheel, if present."""
    candidate = Path(__file__).resolve().parents[1] / "copier_template"
    return candidate.resolve() if (candidate / "copier.yml").is_file() else None


def bundled_template_path() -> Path:
    """Resolve the trusted template from the source checkout or installed wheel."""
    root = repo_root()
    checkout = root / "template"
    if (root / "pyproject.toml").is_file() and (checkout / "copier.yml").is_file():
        return checkout.resolve()
    return packaged_template_path() or checkout.resolve()


def is_bundled_template(path: Path) -> bool:
    """Whether a template is the verified template shipped with this Riso."""
    bundled = bundled_template_path()
    return (bundled / "copier.yml").is_file() and path.resolve() == bundled


def repo_root() -> Path:
    """Return the repository root when running from a checkout."""
    return Path(__file__).resolve().parents[3]


def external_template_warning(path: Path) -> str | None:
    """Return a warning when using a template outside this repository checkout."""
    bundled = bundled_template_path()
    if not bundled.exists():
        return None
    try:
        if path.resolve() != bundled.resolve():
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
    if (bundled / "copier.yml").is_file():
        return bundled

    raise TemplateNotFoundError("clone the riso repository or pass --template-path")


def resolve_samples_path(explicit: Path | None = None) -> Path:
    """Resolve samples directory from explicit path, env, or checkout."""
    if explicit is not None:
        return explicit.expanduser().resolve()

    env_path = os.environ.get("RISO_SAMPLES_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    return (repo_root() / "samples").resolve()


def _local_template_source(source: str) -> Path | None:
    path = Path(source).expanduser()
    # Copier also accepts remote URLs and SCP-style Git locations. These are
    # never a local bundled template, even if their text resembles a local path.
    if not path.is_absolute() and ":" in source:
        return None
    return path.resolve()


def resolve_project_template_path(
    answers: Mapping[str, Any],
    *,
    operation: str,
    explicit: Path | None = None,
    supplied: Mapping[str, Any] | None = None,
) -> Path | None:
    """Verify source selections against the source Copier actually persists.

    Copier update/recopy always select the saved ``_src_path``; a ``data=``
    override cannot change it. Return its local path for managed-hook selection,
    or None for a remote source. Never rewrite the answers to change sources.
    """
    source = answers.get("_src_path")
    if not isinstance(source, str) or not source.strip():
        raise CopierOperationError(
            operation, "No valid _src_path saved in .copier-answers.yml"
        )
    actual = _local_template_source(source)
    conflict = explicit is not None and actual != explicit.expanduser().resolve()
    proposed = supplied.get("_src_path", source) if supplied is not None else source
    if proposed != source:
        conflict = conflict or (
            not isinstance(proposed, str)
            or actual is None
            or _local_template_source(proposed) != actual
        )
    if conflict:
        raise CopierOperationError(
            operation,
            "Template override conflicts with the source saved in "
            ".copier-answers.yml. Update and recopy use the saved source; "
            "omit the override or use a project generated from that template.",
        )
    return actual


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
