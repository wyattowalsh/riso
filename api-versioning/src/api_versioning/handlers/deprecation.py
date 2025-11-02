"""
Deprecation handling and sunset enforcement.

This module provides utilities for checking deprecation status and
generating deprecation notices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from api_versioning.core.version import VersionMetadata, VersionStatus


@dataclass
class DeprecationNotice:
    """
    Deprecation information for API consumers.
    
    This dataclass encapsulates all deprecation-related information
    that should be communicated to API consumers.
    
    Attributes:
        version_id: Version being deprecated
        announced_date: When deprecation was announced (deprecation_date)
        sunset_date: When version will be removed
        reason: Why the version is being deprecated
        recommended_version: Which version consumers should migrate to
        migration_guide_url: URL to migration documentation
        breaking_changes_summary: List of key breaking changes
        days_until_sunset: Number of days remaining until sunset
    
    Example:
        >>> from datetime import date
        >>> notice = DeprecationNotice(
        ...     version_id="v1",
        ...     announced_date=date(2025, 6, 1),
        ...     sunset_date=date(2025, 12, 1),
        ...     reason="Enhanced features in v2",
        ...     recommended_version="v2",
        ...     migration_guide_url="/docs/migrations/v1-to-v2"
        ... )
    """
    
    version_id:                str
    announced_date:            date
    sunset_date:               date
    reason:                    str
    recommended_version:       str
    migration_guide_url:       str
    breaking_changes_summary:  list[str] = None
    days_until_sunset:         Optional[int] = None
    
    def __post_init__(self) -> None:
        """Initialize defaults after dataclass initialization."""
        if self.breaking_changes_summary is None:
            self.breaking_changes_summary = []
        
        if self.days_until_sunset is None:
            today = date.today()
            self.days_until_sunset = (self.sunset_date - today).days
    
    def to_dict(self) -> dict[str, any]:
        """
        Convert deprecation notice to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of deprecation notice
        """
        return {
            "version_id":                self.version_id,
            "announced_date":            self.announced_date.isoformat(),
            "sunset_date":               self.sunset_date.isoformat(),
            "reason":                    self.reason,
            "recommended_version":       self.recommended_version,
            "migration_guide_url":       self.migration_guide_url,
            "breaking_changes_summary":  self.breaking_changes_summary,
            "days_until_sunset":         self.days_until_sunset,
        }


def check_deprecation(metadata: VersionMetadata) -> Optional[DeprecationNotice]:
    """
    Check if version is deprecated and generate deprecation notice.
    
    Args:
        metadata: Version metadata to check
    
    Returns:
        DeprecationNotice if version is deprecated, None otherwise
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v1")
        >>> if metadata:
        ...     notice = check_deprecation(metadata)
        ...     if notice:
        ...         print(f"Days until sunset: {notice.days_until_sunset}")
    """
    if not metadata.is_deprecated():
        return None
    
    # Must have deprecation and sunset dates
    if metadata.deprecation_date is None or metadata.sunset_date is None:
        return None
    
    # Generate deprecation notice
    notice = DeprecationNotice(
        version_id=metadata.version_id,
        announced_date=metadata.deprecation_date,
        sunset_date=metadata.sunset_date,
        reason=metadata.description or "Version deprecated",
        recommended_version=metadata.breaking_changes_from or "latest",
        migration_guide_url=metadata.migration_guide_url or "/docs/migrations",
        breaking_changes_summary=[],  # Could be loaded from config
    )
    
    return notice


def format_deprecation_header(metadata: VersionMetadata) -> Optional[str]:
    """
    Format RFC 8594 Deprecation header value.
    
    Args:
        metadata: Version metadata
    
    Returns:
        Deprecation header value if deprecated, None otherwise
    
    Format:
        date="YYYY-MM-DD"
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v1")
        >>> if metadata:
        ...     header = format_deprecation_header(metadata)
        ...     if header:
        ...         print(f"Deprecation: {header}")
        Deprecation: date="2025-12-01"
    """
    if not metadata.is_deprecated() or metadata.sunset_date is None:
        return None
    
    return f'date="{metadata.sunset_date.isoformat()}"'


def format_sunset_header(metadata: VersionMetadata) -> Optional[str]:
    """
    Format RFC 8594 Sunset header value (HTTP-date format).
    
    Args:
        metadata: Version metadata
    
    Returns:
        Sunset header value if deprecated, None otherwise
    
    Format:
        HTTP-date (e.g., "Sun, 01 Dec 2025 00:00:00 GMT")
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v1")
        >>> if metadata:
        ...     header = format_sunset_header(metadata)
        ...     if header:
        ...         print(f"Sunset: {header}")
        Sunset: Sun, 01 Dec 2025 00:00:00 GMT
    """
    if not metadata.is_deprecated() or metadata.sunset_date is None:
        return None
    
    # Convert to HTTP-date format
    # Format: Weekday, DD Mon YYYY HH:MM:SS GMT
    sunset_datetime = metadata.sunset_date.strftime("%a, %d %b %Y 00:00:00 GMT")
    return sunset_datetime


def format_migration_link_header(metadata: VersionMetadata) -> Optional[str]:
    """
    Format RFC 8288 Link header with migration guide URL.
    
    Args:
        metadata: Version metadata
    
    Returns:
        Link header value if migration guide available, None otherwise
    
    Format:
        </docs/migrations/v1-to-v2>; rel="migration-guide"
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v1")
        >>> if metadata:
        ...     header = format_migration_link_header(metadata)
        ...     if header:
        ...         print(f"Link: {header}")
        Link: </docs/migrations/v1-to-v2>; rel="migration-guide"
    """
    if not metadata.migration_guide_url:
        return None
    
    return f'<{metadata.migration_guide_url}>; rel="migration-guide"'


def is_sunset(metadata: VersionMetadata, today: Optional[date] = None) -> bool:
    """
    Check if version is past its sunset date.
    
    Args:
        metadata: Version metadata
        today: Reference date (defaults to today)
    
    Returns:
        True if sunset date has passed, False otherwise
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v1")
        >>> if metadata and is_sunset(metadata):
        ...     print("Version is sunset")
    """
    if metadata.status == VersionStatus.SUNSET:
        return True
    
    if metadata.sunset_date is None:
        return False
    
    if today is None:
        today = date.today()
    
    return today > metadata.sunset_date
