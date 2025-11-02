"""
Semantic versioning utilities for version parsing and validation.

This module provides utilities for parsing and validating version identifiers
according to the pattern: v{major}[-{suffix}]
"""

import re
from dataclasses import dataclass
from typing import Optional


# Version ID pattern: v{major}[-{suffix}]
VERSION_PATTERN = re.compile(r"^v([0-9]+)(?:-([a-z]+))?$")


@dataclass(frozen=True)
class ParsedVersion:
    """
    Parsed version components.
    
    Attributes:
        major: Major version number
        suffix: Optional suffix (e.g., "beta", "alpha")
        raw: Original version string
    """
    
    major:  int
    suffix: Optional[str]
    raw:    str
    
    def __str__(self) -> str:
        """String representation of version."""
        return self.raw
    
    def is_prerelease(self) -> bool:
        """Check if this is a pre-release version (has suffix)."""
        return self.suffix is not None


def parse_version(version_id: str) -> Optional[ParsedVersion]:
    """
    Parse version identifier into components.
    
    Args:
        version_id: Version identifier (e.g., "v1", "v2", "v3-beta")
    
    Returns:
        ParsedVersion if valid, None if invalid
    
    Example:
        >>> parsed = parse_version("v2")
        >>> print(f"Major: {parsed.major}, Suffix: {parsed.suffix}")
        Major: 2, Suffix: None
        
        >>> parsed = parse_version("v3-beta")
        >>> print(f"Major: {parsed.major}, Suffix: {parsed.suffix}")
        Major: 3, Suffix: beta
    """
    match = VERSION_PATTERN.match(version_id)
    if not match:
        return None
    
    major_str, suffix = match.groups()
    major = int(major_str)
    
    return ParsedVersion(major=major, suffix=suffix, raw=version_id)


def validate_version_id(version_id: str) -> bool:
    """
    Validate version identifier format.
    
    Args:
        version_id: Version identifier to validate
    
    Returns:
        True if valid, False otherwise
    
    Example:
        >>> validate_version_id("v1")
        True
        >>> validate_version_id("v2-beta")
        True
        >>> validate_version_id("V1")  # Case-sensitive
        False
        >>> validate_version_id("v1.0")  # Dots not allowed
        False
    """
    return VERSION_PATTERN.match(version_id) is not None


def extract_major_version(version_id: str) -> Optional[int]:
    """
    Extract major version number from version ID.
    
    Args:
        version_id: Version identifier
    
    Returns:
        Major version number if valid, None otherwise
    
    Example:
        >>> extract_major_version("v2")
        2
        >>> extract_major_version("v3-beta")
        3
    """
    parsed = parse_version(version_id)
    return parsed.major if parsed else None


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version identifiers by major version.
    
    Args:
        version1: First version identifier
        version2: Second version identifier
    
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    
    Raises:
        ValueError: If either version is invalid
    
    Example:
        >>> compare_versions("v1", "v2")
        -1
        >>> compare_versions("v2", "v2")
        0
        >>> compare_versions("v3", "v2")
        1
    """
    parsed1 = parse_version(version1)
    parsed2 = parse_version(version2)
    
    if parsed1 is None:
        raise ValueError(f"Invalid version ID: {version1}")
    if parsed2 is None:
        raise ValueError(f"Invalid version ID: {version2}")
    
    if parsed1.major < parsed2.major:
        return -1
    elif parsed1.major > parsed2.major:
        return 1
    else:
        return 0
