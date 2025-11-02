"""
Core version metadata entities and lifecycle management.

This module defines the fundamental version data structures used throughout
the versioning system.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class VersionStatus(str, Enum):
    """
    Lifecycle status of an API version.
    
    Values:
        CURRENT: Active stable version (usually the default)
        DEPRECATED: Still supported but scheduled for removal
        SUNSET: No longer supported, returns 410 Gone
        PRERELEASE: Beta/alpha version requiring opt-in
    """
    
    CURRENT     = "current"
    DEPRECATED  = "deprecated"
    SUNSET      = "sunset"
    PRERELEASE  = "prerelease"


# Version ID validation pattern: v{major}[-{suffix}]
VERSION_ID_PATTERN = re.compile(r"^v[0-9]+(-[a-z]+)?$")


@dataclass(frozen=True)
class VersionMetadata:
    """
    Immutable metadata for an API version.
    
    This dataclass is frozen for thread safety and to enable caching.
    All date fields use Python date objects for easy comparison.
    
    Attributes:
        version_id: Unique version identifier (e.g., "v1", "v2", "v3-beta")
        status: Current lifecycle status
        release_date: Date when version was released to production
        deprecation_date: Date when version was marked deprecated (optional)
        sunset_date: Date when version will be/was removed (optional)
        description: Human-readable description (optional)
        supported_features: Frozenset of feature flags enabled in this version
        breaking_changes_from: Version ID from which breaking changes occurred (optional)
        migration_guide_url: URL to migration documentation (optional)
        opt_in_required: Whether version requires explicit opt-in header
    
    Validation Rules:
        - version_id must match pattern ^v[0-9]+(-[a-z]+)?$
        - If status is DEPRECATED, deprecation_date must be set
        - If status is SUNSET, sunset_date must be in the past
        - If sunset_date is set, deprecation_date must also be set
        - sunset_date must be ?12 months after deprecation_date (FR-020)
        - release_date must be before deprecation_date (if set)
        - deprecation_date must be before sunset_date (if set)
    
    Example:
        >>> metadata = VersionMetadata(
        ...     version_id="v2",
        ...     status=VersionStatus.CURRENT,
        ...     release_date=date(2025, 6, 1),
        ...     description="Enhanced API with improved validation",
        ...     supported_features=frozenset(["basic_crud", "pagination"])
        ... )
    """
    
    version_id:            str
    status:                VersionStatus
    release_date:          date
    deprecation_date:      Optional[date] = None
    sunset_date:           Optional[date] = None
    description:           str = ""
    supported_features:    frozenset[str] = field(default_factory=frozenset)
    breaking_changes_from: Optional[str] = None
    migration_guide_url:   Optional[str] = None
    opt_in_required:       bool = False
    
    def __post_init__(self) -> None:
        """Validate version metadata after initialization."""
        # Validate version ID format
        if not VERSION_ID_PATTERN.match(self.version_id):
            raise ValueError(
                f"Invalid version_id '{self.version_id}'. "
                f"Must match pattern: ^v[0-9]+(-[a-z]+)?$"
            )
        
        # Validate status-specific requirements
        if self.status == VersionStatus.DEPRECATED and self.deprecation_date is None:
            raise ValueError(
                f"Version {self.version_id} has status DEPRECATED but "
                f"deprecation_date is not set"
            )
        
        if self.status == VersionStatus.SUNSET and self.sunset_date is None:
            raise ValueError(
                f"Version {self.version_id} has status SUNSET but "
                f"sunset_date is not set"
            )
        
        # Validate date relationships
        if self.deprecation_date and self.release_date > self.deprecation_date:
            raise ValueError(
                f"Version {self.version_id}: release_date "
                f"({self.release_date}) must be before deprecation_date "
                f"({self.deprecation_date})"
            )
        
        if self.sunset_date:
            if self.deprecation_date is None:
                raise ValueError(
                    f"Version {self.version_id}: sunset_date is set but "
                    f"deprecation_date is not set"
                )
            
            if self.deprecation_date > self.sunset_date:
                raise ValueError(
                    f"Version {self.version_id}: deprecation_date "
                    f"({self.deprecation_date}) must be before sunset_date "
                    f"({self.sunset_date})"
                )
            
            # FR-020: Minimum 12-month support window after deprecation
            days_diff = (self.sunset_date - self.deprecation_date).days
            if days_diff < 365:
                raise ValueError(
                    f"Version {self.version_id}: sunset_date must be ?12 months "
                    f"after deprecation_date (FR-020). Current difference: {days_diff} days"
                )
        
        # Validate migration guide URL format if provided
        if self.migration_guide_url:
            if not (
                self.migration_guide_url.startswith("http://")
                or self.migration_guide_url.startswith("https://")
                or self.migration_guide_url.startswith("/")
            ):
                raise ValueError(
                    f"Version {self.version_id}: migration_guide_url must be "
                    f"an absolute URL (http/https) or relative path (/...)"
                )
    
    def is_deprecated(self) -> bool:
        """
        Check if this version is deprecated.
        
        Returns:
            True if status is DEPRECATED or SUNSET, False otherwise
        """
        return self.status in (VersionStatus.DEPRECATED, VersionStatus.SUNSET)
    
    def is_sunset(self) -> bool:
        """
        Check if this version is sunset (no longer supported).
        
        Returns:
            True if status is SUNSET, False otherwise
        """
        return self.status == VersionStatus.SUNSET
    
    def is_prerelease(self) -> bool:
        """
        Check if this version is a pre-release (beta/alpha).
        
        Returns:
            True if status is PRERELEASE, False otherwise
        """
        return self.status == VersionStatus.PRERELEASE
    
    def days_until_sunset(self, today: Optional[date] = None) -> Optional[int]:
        """
        Calculate days remaining until sunset date.
        
        Args:
            today: Reference date (defaults to today)
        
        Returns:
            Number of days until sunset, or None if no sunset date set.
            Negative values indicate sunset date has passed.
        """
        if self.sunset_date is None:
            return None
        
        if today is None:
            from datetime import date as date_class
            today = date_class.today()
        
        return (self.sunset_date - today).days
    
    def to_dict(self) -> dict[str, any]:
        """
        Convert version metadata to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of version metadata
        """
        return {
            "version_id":            self.version_id,
            "status":                self.status.value,
            "release_date":          self.release_date.isoformat(),
            "deprecation_date":      (
                self.deprecation_date.isoformat()
                if self.deprecation_date
                else None
            ),
            "sunset_date":           (
                self.sunset_date.isoformat()
                if self.sunset_date
                else None
            ),
            "description":           self.description,
            "supported_features":    sorted(self.supported_features),
            "breaking_changes_from": self.breaking_changes_from,
            "migration_guide_url":   self.migration_guide_url,
            "opt_in_required":       self.opt_in_required,
        }
