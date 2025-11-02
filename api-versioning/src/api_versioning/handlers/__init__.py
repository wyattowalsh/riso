"""Version-specific handlers for deprecation, errors, and pre-release access."""

from api_versioning.handlers.deprecation import DeprecationNotice, check_deprecation
from api_versioning.handlers.error import (
    PrereleaseOptInRequiredError,
    VersionConflictError,
    VersionError,
    VersionNotFoundError,
    VersionSunsetError,
)
from api_versioning.handlers.prerelease import check_prerelease_access

__all__ = [
    "VersionError",
    "VersionNotFoundError",
    "VersionSunsetError",
    "VersionConflictError",
    "PrereleaseOptInRequiredError",
    "DeprecationNotice",
    "check_deprecation",
    "check_prerelease_access",
]
