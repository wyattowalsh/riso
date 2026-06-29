"""Identity field validation for CLI and template operations."""

from __future__ import annotations

import re

_PACKAGE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,127}$")
_FORBIDDEN_SUBSTRINGS = ("..", "/", "\\", "{{", "}}", "\x00")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")


def _base_errors(name: str, field: str) -> list[str]:
    errors: list[str] = []
    if not name or not name.strip():
        errors.append(f"{field}: must not be empty")
        return errors
    stripped = name.strip()
    for bad in _FORBIDDEN_SUBSTRINGS:
        if bad in stripped:
            errors.append(f"{field}: must not contain '{bad}'")
    if _CONTROL_CHAR_RE.search(stripped):
        errors.append(f"{field}: must not contain control characters")
    return errors


def validate_project_name(name: str) -> list[str]:
    """Validate human-facing project_name."""
    errors = _base_errors(name, "project_name")
    if name.strip() and not _PROJECT_NAME_RE.match(name.strip()):
        errors.append(
            "project_name: must start with alphanumeric and use safe characters"
        )
    return errors


def validate_package_name(name: str) -> list[str]:
    """Validate Python package_name."""
    errors = _base_errors(name, "package_name")
    if name.strip() and not _PACKAGE_NAME_RE.match(name.strip()):
        errors.append(
            f"package_name: must match ^[a-z][a-z0-9_]*$ (got {name.strip()!r})"
        )
    return errors


def validate_identity_fields(answers: dict) -> list[str]:
    """Validate project_name and package_name when present in answers."""
    errors: list[str] = []
    if "project_name" in answers and answers["project_name"] is not None:
        errors.extend(validate_project_name(str(answers["project_name"])))
    if "package_name" in answers and answers["package_name"] is not None:
        errors.extend(validate_package_name(str(answers["package_name"])))
    return errors
