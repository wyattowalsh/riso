"""Unit tests for version metadata and status."""

import sys
from datetime import date
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from api_versioning.core.version import VERSION_ID_PATTERN, VersionMetadata, VersionStatus


def test_version_status_values():
    """Test VersionStatus enum values."""
    assert VersionStatus.CURRENT.value == "current"
    assert VersionStatus.DEPRECATED.value == "deprecated"
    assert VersionStatus.SUNSET.value == "sunset"
    assert VersionStatus.PRERELEASE.value == "prerelease"


def test_version_id_pattern_valid():
    """Test valid version ID patterns."""
    assert VERSION_ID_PATTERN.match("v1")
    assert VERSION_ID_PATTERN.match("v2")
    assert VERSION_ID_PATTERN.match("v99")
    assert VERSION_ID_PATTERN.match("v3-beta")
    assert VERSION_ID_PATTERN.match("v3-alpha")


def test_version_id_pattern_invalid():
    """Test invalid version ID patterns."""
    assert not VERSION_ID_PATTERN.match("V1")  # Uppercase
    assert not VERSION_ID_PATTERN.match("1")   # No prefix
    assert not VERSION_ID_PATTERN.match("v1.0")  # Dot
    assert not VERSION_ID_PATTERN.match("v1_beta")  # Underscore


def test_version_metadata_creation():
    """Test creating VersionMetadata."""
    metadata = VersionMetadata(
        version_id="v2",
        status=VersionStatus.CURRENT,
        release_date=date(2025, 6, 1),
        description="Test version"
    )
    
    assert metadata.version_id == "v2"
    assert metadata.status == VersionStatus.CURRENT
    assert metadata.release_date == date(2025, 6, 1)


def test_version_metadata_deprecated():
    """Test deprecated version metadata."""
    metadata = VersionMetadata(
        version_id="v1",
        status=VersionStatus.DEPRECATED,
        release_date=date(2024, 1, 1),
        deprecation_date=date(2025, 1, 1),
        sunset_date=date(2026, 1, 1)
    )
    
    assert metadata.is_deprecated()
    assert not metadata.is_sunset()
    assert not metadata.is_prerelease()


def test_version_metadata_sunset_window_validation():
    """Test 12-month sunset window validation."""
    # Valid: 12+ months
    metadata = VersionMetadata(
        version_id="v1",
        status=VersionStatus.DEPRECATED,
        release_date=date(2024, 1, 1),
        deprecation_date=date(2025, 1, 1),
        sunset_date=date(2026, 1, 1)  # Exactly 12 months
    )
    assert metadata.sunset_date == date(2026, 1, 1)
    
    # Invalid: less than 12 months
    with pytest.raises(ValueError, match="?12 months"):
        VersionMetadata(
            version_id="v1",
            status=VersionStatus.DEPRECATED,
            release_date=date(2024, 1, 1),
            deprecation_date=date(2025, 1, 1),
            sunset_date=date(2025, 6, 1)  # Only 5 months
        )


def test_version_metadata_days_until_sunset():
    """Test days until sunset calculation."""
    today = date(2025, 11, 1)
    metadata = VersionMetadata(
        version_id="v1",
        status=VersionStatus.DEPRECATED,
        release_date=date(2024, 1, 1),
        deprecation_date=date(2025, 1, 1),
        sunset_date=date(2025, 12, 1)
    )
    
    days = metadata.days_until_sunset(today)
    assert days == 30  # 30 days from Nov 1 to Dec 1


def test_version_metadata_to_dict():
    """Test serialization to dictionary."""
    metadata = VersionMetadata(
        version_id="v2",
        status=VersionStatus.CURRENT,
        release_date=date(2025, 6, 1),
        supported_features=frozenset(["feature1", "feature2"])
    )
    
    data = metadata.to_dict()
    assert data["version_id"] == "v2"
    assert data["status"] == "current"
    assert "feature1" in data["supported_features"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
