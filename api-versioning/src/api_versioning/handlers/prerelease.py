"""
Pre-release version access control.

This module provides utilities for checking pre-release opt-in requirements
and enforcing access restrictions.
"""

from typing import Optional

from api_versioning.core.version import VersionMetadata
from api_versioning.handlers.error import PrereleaseOptInRequiredError


def check_prerelease_access(
    metadata: VersionMetadata,
    opt_in_value: Optional[str]
) -> None:
    """
    Check if consumer has opted into pre-release version access.
    
    Pre-release versions require explicit opt-in via the
    X-API-Prerelease-Opt-In header with value "true".
    
    Args:
        metadata: Version metadata
        opt_in_value: Value from X-API-Prerelease-Opt-In header
    
    Raises:
        PrereleaseOptInRequiredError: If opt-in required but not provided
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v3-beta")
        >>> if metadata:
        ...     check_prerelease_access(metadata, "true")  # OK
        ...     check_prerelease_access(metadata, None)    # Raises error
    """
    if not metadata.is_prerelease():
        return  # Not a pre-release version, no check needed
    
    if not metadata.opt_in_required:
        return  # Opt-in not required for this version
    
    # Check if opt-in header is present and set to "true"
    if opt_in_value is None or opt_in_value.lower() != "true":
        raise PrereleaseOptInRequiredError(metadata.version_id)


def extract_opt_in_header(headers: dict[bytes, bytes]) -> Optional[str]:
    """
    Extract pre-release opt-in value from request headers.
    
    Args:
        headers: Request headers as bytes dictionary
    
    Returns:
        Opt-in header value if present, None otherwise
    
    Example:
        >>> headers = {b"x-api-prerelease-opt-in": b"true"}
        >>> extract_opt_in_header(headers)
        "true"
    """
    # Check for X-API-Prerelease-Opt-In header (case-insensitive)
    for header_name, header_value in headers.items():
        if header_name.lower() == b"x-api-prerelease-opt-in":
            return header_value.decode("utf-8", errors="ignore")
    
    return None


def format_stability_header(metadata: VersionMetadata) -> str:
    """
    Format X-API-Version-Stability header value.
    
    Args:
        metadata: Version metadata
    
    Returns:
        Stability header value ("stable" or "prerelease")
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v2")
        >>> if metadata:
        ...     stability = format_stability_header(metadata)
        ...     print(f"X-API-Version-Stability: {stability}")
        X-API-Version-Stability: stable
    """
    return "prerelease" if metadata.is_prerelease() else "stable"
