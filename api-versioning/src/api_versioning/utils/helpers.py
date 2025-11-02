"""Helper utilities for common operations."""

from typing import Optional

from api_versioning.core.registry import VersionRegistry
from api_versioning.core.version import VersionMetadata


def get_version_metadata(version_id: str) -> Optional[VersionMetadata]:
    """
    Helper function to get version metadata from registry.
    
    Args:
        version_id: Version identifier
    
    Returns:
        VersionMetadata if found, None otherwise
    
    Example:
        >>> from api_versioning import get_version_metadata
        >>> metadata = get_version_metadata("v2")
        >>> if metadata:
        ...     print(f"Status: {metadata.status}")
    """
    registry = VersionRegistry()
    return registry.get_version(version_id)
