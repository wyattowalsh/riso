"""
API Versioning Middleware - Comprehensive version management for ASGI applications.

This package provides a framework-agnostic ASGI middleware for managing API versions
with support for multiple concurrent versions, deprecation workflows, version discovery,
and usage metrics tracking.

Key Features:
- Version specification via header, URL path, or query parameter
- Automatic deprecation warnings and sunset enforcement
- Version discovery endpoints
- Pre-release version support
- Usage metrics logging
- <10ms routing overhead

Example:
    >>> from api_versioning import VersionRegistry, APIVersionMiddleware
    >>> from pathlib import Path
    >>> 
    >>> # Load version configuration
    >>> config_path = Path("config/api_versions.yaml")
    >>> VersionRegistry.load_from_file(config_path)
    >>> 
    >>> # Add middleware to ASGI app
    >>> app.add_middleware(APIVersionMiddleware, default_version="v2")

Public API:
- VersionRegistry: Singleton for version metadata management
- APIVersionMiddleware: ASGI middleware for version routing
- VersionStatus: Enum for version lifecycle states
- VersionMetadata: Immutable version metadata
- get_version_metadata: Helper to access version info
"""

from api_versioning.core.registry import VersionRegistry
from api_versioning.core.version import VersionMetadata, VersionStatus
from api_versioning.middleware import APIVersionMiddleware
from api_versioning.utils.helpers import get_version_metadata

__version__ = "1.0.0"
__all__ = [
    "VersionRegistry",
    "VersionMetadata",
    "VersionStatus",
    "APIVersionMiddleware",
    "get_version_metadata",
]
