"""
Error classes for version-related failures.

This module defines exception classes for various version-related error
scenarios with appropriate HTTP status codes and error messages.
"""

from typing import Any, Optional


class VersionError(Exception):
    """
    Base exception for all version-related errors.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error context
    """
    
    def __init__(
        self,
        message: str,
        code: str = "VERSION_ERROR",
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None
    ):
        """
        Initialize version error.
        
        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert error to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of error
        """
        error_dict: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        
        if self.details:
            error_dict["details"] = self.details
        
        return {"error": error_dict}


class VersionNotFoundError(VersionError):
    """
    Exception raised when requested version doesn't exist.
    
    HTTP Status: 404 Not Found
    
    Example:
        >>> raise VersionNotFoundError(
        ...     "v99",
        ...     available_versions=["v1", "v2"]
        ... )
    """
    
    def __init__(
        self,
        version_id: str,
        available_versions: Optional[list[str]] = None
    ):
        """
        Initialize version not found error.
        
        Args:
            version_id: Version identifier that was not found
            available_versions: List of valid version IDs
        """
        message = f"API version '{version_id}' not found"
        
        details: dict[str, Any] = {}
        if available_versions:
            details["available_versions"] = available_versions
        
        super().__init__(
            message=message,
            code="VERSION_NOT_FOUND",
            status_code=404,
            details=details
        )


class VersionSunsetError(VersionError):
    """
    Exception raised when accessing a sunset (removed) version.
    
    HTTP Status: 410 Gone
    
    Example:
        >>> raise VersionSunsetError(
        ...     "v1",
        ...     sunset_date="2025-12-01",
        ...     recommended_version="v2",
        ...     migration_guide_url="/docs/migrations/v1-to-v2"
        ... )
    """
    
    def __init__(
        self,
        version_id: str,
        sunset_date: str,
        recommended_version: Optional[str] = None,
        migration_guide_url: Optional[str] = None
    ):
        """
        Initialize version sunset error.
        
        Args:
            version_id: Version identifier that is sunset
            sunset_date: ISO 8601 date when version was sunset
            recommended_version: Recommended version to migrate to
            migration_guide_url: URL to migration documentation
        """
        message = f"API version '{version_id}' was sunset on {sunset_date}"
        
        details: dict[str, Any] = {"sunset_date": sunset_date}
        if recommended_version:
            details["recommended_version"] = recommended_version
        if migration_guide_url:
            details["migration_guide_url"] = migration_guide_url
        
        super().__init__(
            message=message,
            code="VERSION_SUNSET",
            status_code=410,
            details=details
        )


class VersionConflictError(VersionError):
    """
    Exception raised when contradictory version specifications detected.
    
    HTTP Status: 400 Bad Request
    
    This error occurs when the same specification source provides multiple
    different version values (e.g., two different version headers).
    
    Note: Cross-source conflicts (e.g., header vs URL) are resolved by
    precedence rules and do not trigger this error.
    
    Example:
        >>> raise VersionConflictError(
        ...     "Contradictory version headers",
        ...     conflicting_specs=[
        ...         {"source": "HEADER", "value": "v1", "from": "X-API-Version"},
        ...         {"source": "HEADER", "value": "v2", "from": "API-Version"}
        ...     ]
        ... )
    """
    
    def __init__(
        self,
        message: str,
        conflicting_specs: list[dict[str, str]]
    ):
        """
        Initialize version conflict error.
        
        Args:
            message: Human-readable error message
            conflicting_specs: List of conflicting version specifications
        """
        super().__init__(
            message=message,
            code="VERSION_CONFLICT",
            status_code=400,
            details={"detected_specifications": conflicting_specs}
        )


class PrereleaseOptInRequiredError(VersionError):
    """
    Exception raised when accessing pre-release version without opt-in.
    
    HTTP Status: 403 Forbidden
    
    Pre-release versions require explicit opt-in via the
    X-API-Prerelease-Opt-In header.
    
    Example:
        >>> raise PrereleaseOptInRequiredError(
        ...     "v3-beta",
        ...     required_header="X-API-Prerelease-Opt-In"
        ... )
    """
    
    def __init__(
        self,
        version_id: str,
        required_header: str = "X-API-Prerelease-Opt-In"
    ):
        """
        Initialize prerelease opt-in required error.
        
        Args:
            version_id: Pre-release version identifier
            required_header: Header name required for opt-in
        """
        message = (
            f"Version '{version_id}' is a pre-release version and requires "
            f"explicit opt-in via '{required_header}: true' header"
        )
        
        details: dict[str, Any] = {
            "version_id": version_id,
            "required_header": required_header,
            "opt_in_value": "true"
        }
        
        super().__init__(
            message=message,
            code="PRERELEASE_OPT_IN_REQUIRED",
            status_code=403,
            details=details
        )


class InvalidVersionFormatError(VersionError):
    """
    Exception raised when version identifier has invalid format.
    
    HTTP Status: 400 Bad Request
    
    Example:
        >>> raise InvalidVersionFormatError(
        ...     "V1",
        ...     required_pattern="^v[0-9]+(-[a-z]+)?$"
        ... )
    """
    
    def __init__(
        self,
        provided_value: str,
        required_pattern: str = "^v[0-9]+(-[a-z]+)?$"
    ):
        """
        Initialize invalid version format error.
        
        Args:
            provided_value: Invalid version value provided
            required_pattern: Required regex pattern
        """
        message = (
            f"Version identifier '{provided_value}' has invalid format. "
            f"Must match pattern: {required_pattern}"
        )
        
        details: dict[str, Any] = {
            "provided_value": provided_value,
            "required_pattern": required_pattern
        }
        
        super().__init__(
            message=message,
            code="INVALID_VERSION_FORMAT",
            status_code=400,
            details=details
        )
