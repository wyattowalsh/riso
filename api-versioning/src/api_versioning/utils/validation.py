"""
Validation utilities for version configuration and input.

This module provides validation functions for ensuring configuration
integrity and input security.
"""

import re
from datetime import date
from typing import Optional

from api_versioning.core.version import VERSION_ID_PATTERN


def validate_version_format(version_id: str, max_length: int = 20) -> tuple[bool, Optional[str]]:
    """
    Validate version identifier format (FR-028).
    
    Args:
        version_id: Version identifier to validate
        max_length: Maximum allowed length (default 20)
    
    Returns:
        Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
    
    Validation Rules:
        - Must match pattern: ^v[0-9]+(-[a-z]+)?$
        - Length must be between 2 and max_length characters
        - Case-sensitive (v1 valid, V1 invalid)
        - No whitespace allowed
        - No control characters allowed
    
    Example:
        >>> validate_version_format("v2")
        (True, None)
        >>> validate_version_format("V2")
        (False, "Version identifier must match pattern: ^v[0-9]+(-[a-z]+)?$")
        >>> validate_version_format("v123456789012345678901")
        (False, "Version identifier must be 2-20 characters")
    """
    # Check length
    if len(version_id) < 2:
        return False, "Version identifier must be at least 2 characters"
    
    if len(version_id) > max_length:
        return False, f"Version identifier must be 2-{max_length} characters"
    
    # Check for control characters (security: prevent injection)
    if any(ord(c) < 32 or ord(c) == 127 for c in version_id):
        return False, "Version identifier contains invalid control characters"
    
    # Check format pattern
    if not VERSION_ID_PATTERN.match(version_id):
        return False, "Version identifier must match pattern: ^v[0-9]+(-[a-z]+)?$"
    
    return True, None


def sanitize_version_id(version_id: str) -> str:
    """
    Sanitize version identifier for logging (FR-024).
    
    Removes control characters and trims whitespace to prevent
    log injection attacks.
    
    Args:
        version_id: Version identifier to sanitize
    
    Returns:
        Sanitized version identifier
    
    Example:
        >>> sanitize_version_id(" v2 ")
        "v2"
        >>> sanitize_version_id("v1\\r\\nInjected")
        "v1Injected"
    """
    # Remove control characters
    sanitized = "".join(c for c in version_id if ord(c) >= 32 and ord(c) != 127)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_sunset_window(
    deprecation_date: date,
    sunset_date: date,
    minimum_days: int = 365
) -> tuple[bool, Optional[str]]:
    """
    Validate 12-month minimum support window between deprecation and sunset (FR-020).
    
    Args:
        deprecation_date: Date when version was deprecated
        sunset_date: Date when version will be sunset
        minimum_days: Minimum days required (default 365 for 12 months)
    
    Returns:
        Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
    
    Example:
        >>> from datetime import date
        >>> dep_date = date(2025, 1, 1)
        >>> sunset_date = date(2026, 1, 1)
        >>> validate_sunset_window(dep_date, sunset_date)
        (True, None)
        
        >>> sunset_date = date(2025, 6, 1)  # Only 5 months
        >>> validate_sunset_window(dep_date, sunset_date)
        (False, "sunset_date must be ?12 months after deprecation_date...")
    """
    days_diff = (sunset_date - deprecation_date).days
    
    if days_diff < minimum_days:
        return False, (
            f"sunset_date must be ?12 months after deprecation_date (FR-020). "
            f"Current difference: {days_diff} days (minimum: {minimum_days} days)"
        )
    
    return True, None


def detect_header_injection(value: str) -> bool:
    """
    Detect potential header injection attacks (FR-023).
    
    Args:
        value: Value to check
    
    Returns:
        True if injection detected, False otherwise
    
    Example:
        >>> detect_header_injection("v1")
        False
        >>> detect_header_injection("v1\\r\\nX-Injected: evil")
        True
    """
    # Check for CRLF injection patterns
    if "\\r" in value or "\\n" in value:
        return True
    
    # Check for actual newline characters
    if "\r" in value or "\n" in value:
        return True
    
    return False


def validate_date_order(
    release_date: date,
    deprecation_date: Optional[date],
    sunset_date: Optional[date]
) -> tuple[bool, Optional[str]]:
    """
    Validate date ordering: release < deprecation < sunset.
    
    Args:
        release_date: Version release date
        deprecation_date: Deprecation date (optional)
        sunset_date: Sunset date (optional)
    
    Returns:
        Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid
    
    Example:
        >>> from datetime import date
        >>> validate_date_order(
        ...     date(2024, 1, 1),
        ...     date(2025, 1, 1),
        ...     date(2026, 1, 1)
        ... )
        (True, None)
    """
    if deprecation_date and release_date > deprecation_date:
        return False, "release_date must be before deprecation_date"
    
    if sunset_date:
        if deprecation_date is None:
            return False, "sunset_date requires deprecation_date to be set"
        
        if deprecation_date > sunset_date:
            return False, "deprecation_date must be before sunset_date"
    
    return True, None
