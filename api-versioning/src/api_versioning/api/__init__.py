"""Version discovery API endpoints."""

from api_versioning.api.discovery import VersionDiscoveryRouter, create_discovery_app

__all__ = ["VersionDiscoveryRouter", "create_discovery_app"]
