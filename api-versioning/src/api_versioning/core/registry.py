"""
Version registry for fast O(1) metadata lookups.

This module implements a singleton in-memory registry for version metadata
with YAML configuration loading and validation.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import yaml

from api_versioning.core.version import VersionMetadata, VersionStatus


class VersionRegistry:
    """
    Singleton in-memory registry for O(1) version metadata lookups.
    
    This class maintains all version metadata in memory for fast access
    (50-200ns per lookup). Configuration is loaded from YAML files at
    startup and can be hot-reloaded in development.
    
    Thread Safety:
        - Read operations are thread-safe (immutable after load)
        - Reload operations use copy-on-write pattern
        - No locks needed for normal operation
    
    Performance:
        - Version lookup: O(1) hash map, 50-200ns
        - Memory footprint: ~10-50KB for typical configurations
        - Configuration load: <10ms for 100 versions
    
    Example:
        >>> from pathlib import Path
        >>> config_path = Path("config/api_versions.yaml")
        >>> VersionRegistry.load_from_file(config_path)
        >>> 
        >>> registry = VersionRegistry()
        >>> metadata = registry.get_version("v2")
        >>> if metadata:
        ...     print(f"Status: {metadata.status}")
    """
    
    _instance: Optional[VersionRegistry] = None
    _versions: dict[str, VersionMetadata] = {}
    _config_path: Optional[Path] = None
    _last_loaded: Optional[datetime] = None
    _config_checksum: Optional[str] = None
    
    def __new__(cls) -> VersionRegistry:
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> VersionRegistry:
        """
        Load version metadata from YAML configuration file.
        
        This method validates the configuration and populates the registry
        with version metadata. It must be called before any version lookups.
        
        Args:
            config_path: Path to YAML configuration file
        
        Returns:
            The singleton VersionRegistry instance
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
            yaml.YAMLError: If YAML parsing fails
        
        Validation Rules:
            - Exactly one version must have status "current"
            - All version IDs must be unique
            - All version IDs must match pattern ^v[0-9]+(-[a-z]+)?$
            - All breaking_changes_from references must exist
            - All date constraints must be satisfied
        
        Example:
            >>> from pathlib import Path
            >>> VersionRegistry.load_from_file(Path("config/api_versions.yaml"))
        """
        instance = cls()
        
        # Read and parse YAML
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config_text = f.read()
            config = yaml.safe_load(config_text)
        
        # Calculate checksum for integrity validation (FR-029)
        checksum = hashlib.sha256(config_text.encode()).hexdigest()
        
        # Validate configuration structure
        if not config or "versions" not in config:
            raise ValueError("Configuration must contain 'versions' key")
        
        versions_config = config["versions"]
        if not versions_config:
            raise ValueError("Configuration must contain at least one version")
        
        if not isinstance(versions_config, dict):
            raise ValueError("'versions' must be a dictionary")
        
        # Parse and validate all versions
        versions: dict[str, VersionMetadata] = {}
        current_versions: list[str] = []
        
        for version_id, version_data in versions_config.items():
            try:
                metadata = cls._parse_version_metadata(version_id, version_data)
                versions[version_id] = metadata
                
                if metadata.status == VersionStatus.CURRENT:
                    current_versions.append(version_id)
                    
            except Exception as e:
                raise ValueError(
                    f"Failed to parse version '{version_id}': {e}"
                ) from e
        
        # Validate exactly one current version
        if len(current_versions) == 0:
            raise ValueError(
                "Configuration must have exactly one version with status 'current'"
            )
        elif len(current_versions) > 1:
            raise ValueError(
                f"Multiple current versions detected: {', '.join(current_versions)}. "
                f"Only one version can have status 'current'"
            )
        
        # Validate all breaking_changes_from references exist
        for version_id, metadata in versions.items():
            if metadata.breaking_changes_from:
                if metadata.breaking_changes_from not in versions:
                    raise ValueError(
                        f"Version {version_id} references non-existent version "
                        f"in breaking_changes_from: {metadata.breaking_changes_from}"
                    )
        
        # Atomic update - replace entire registry
        cls._versions = versions
        cls._config_path = config_path
        cls._last_loaded = datetime.now()
        cls._config_checksum = checksum
        
        return instance
    
    @classmethod
    def _parse_version_metadata(
        cls,
        version_id: str,
        data: dict[str, any]
    ) -> VersionMetadata:
        """
        Parse version metadata from YAML configuration dict.
        
        Args:
            version_id: Version identifier
            data: Version configuration dictionary
        
        Returns:
            Parsed and validated VersionMetadata
        
        Raises:
            ValueError: If required fields missing or invalid
        """
        # Required fields
        if "status" not in data:
            raise ValueError("Missing required field: status")
        if "release_date" not in data:
            raise ValueError("Missing required field: release_date")
        
        # Parse status enum
        status_str = data["status"]
        try:
            status = VersionStatus(status_str)
        except ValueError:
            valid_statuses = [s.value for s in VersionStatus]
            raise ValueError(
                f"Invalid status '{status_str}'. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Parse dates
        release_date = cls._parse_date(data["release_date"], "release_date")
        deprecation_date = (
            cls._parse_date(data["deprecation_date"], "deprecation_date")
            if data.get("deprecation_date")
            else None
        )
        sunset_date = (
            cls._parse_date(data["sunset_date"], "sunset_date")
            if data.get("sunset_date")
            else None
        )
        
        # Parse supported features
        supported_features = frozenset(data.get("supported_features", []))
        
        # Create VersionMetadata (will validate in __post_init__)
        return VersionMetadata(
            version_id=version_id,
            status=status,
            release_date=release_date,
            deprecation_date=deprecation_date,
            sunset_date=sunset_date,
            description=data.get("description", ""),
            supported_features=supported_features,
            breaking_changes_from=data.get("breaking_changes_from"),
            migration_guide_url=data.get("migration_guide_url"),
            opt_in_required=data.get("opt_in_required", False),
        )
    
    @staticmethod
    def _parse_date(value: str, field_name: str) -> date:
        """
        Parse date from ISO 8601 string (YYYY-MM-DD).
        
        Args:
            value: Date string in ISO 8601 format
            field_name: Field name for error messages
        
        Returns:
            Parsed date object
        
        Raises:
            ValueError: If date parsing fails
        """
        try:
            # Parse ISO 8601 date format: YYYY-MM-DD
            return date.fromisoformat(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid date format for {field_name}: {value}. "
                f"Expected ISO 8601 format (YYYY-MM-DD)"
            ) from e
    
    def get_version(self, version_id: str) -> Optional[VersionMetadata]:
        """
        Get version metadata by ID (O(1) lookup).
        
        Expected latency: 50-200ns for hash map lookup.
        
        Args:
            version_id: Version identifier (e.g., "v1", "v2", "v3-beta")
        
        Returns:
            VersionMetadata if found, None otherwise
        
        Example:
            >>> registry = VersionRegistry()
            >>> metadata = registry.get_version("v2")
            >>> if metadata:
            ...     print(f"Status: {metadata.status}")
        """
        return self._versions.get(version_id)
    
    def get_current_version(self) -> Optional[VersionMetadata]:
        """
        Get the current default version.
        
        Returns:
            VersionMetadata for the version with status CURRENT, or None
        
        Example:
            >>> registry = VersionRegistry()
            >>> current = registry.get_current_version()
            >>> if current:
            ...     print(f"Current version: {current.version_id}")
        """
        for metadata in self._versions.values():
            if metadata.status == VersionStatus.CURRENT:
                return metadata
        return None
    
    def list_all_versions(self) -> list[VersionMetadata]:
        """
        List all versions including sunset versions.
        
        Returns:
            List of all VersionMetadata objects sorted by version ID
        
        Example:
            >>> registry = VersionRegistry()
            >>> all_versions = registry.list_all_versions()
            >>> for v in all_versions:
            ...     print(f"{v.version_id}: {v.status.value}")
        """
        return sorted(self._versions.values(), key=lambda v: v.version_id)
    
    def list_active_versions(
        self,
        include_prerelease: bool = False,
        include_sunset: bool = False
    ) -> list[VersionMetadata]:
        """
        List active versions (excludes sunset by default).
        
        Args:
            include_prerelease: Include pre-release versions
            include_sunset: Include sunset versions
        
        Returns:
            List of active VersionMetadata objects sorted by version ID
        
        Example:
            >>> registry = VersionRegistry()
            >>> active = registry.list_active_versions()
            >>> for v in active:
            ...     print(f"{v.version_id}: {v.status.value}")
        """
        versions = []
        for metadata in self._versions.values():
            # Exclude sunset versions unless explicitly included
            if metadata.status == VersionStatus.SUNSET and not include_sunset:
                continue
            
            # Exclude prerelease versions unless explicitly included
            if metadata.status == VersionStatus.PRERELEASE and not include_prerelease:
                continue
            
            versions.append(metadata)
        
        return sorted(versions, key=lambda v: v.version_id)
    
    def reload(self) -> None:
        """
        Reload configuration from file.
        
        This method re-reads the configuration file and atomically updates
        the registry. Useful for development hot-reload.
        
        Raises:
            ValueError: If configuration becomes invalid
            FileNotFoundError: If config file no longer exists
        
        Note:
            In-flight requests continue with old configuration.
            New requests see new configuration immediately.
        
        Example:
            >>> registry = VersionRegistry()
            >>> registry.reload()
        """
        if self._config_path is None:
            raise RuntimeError(
                "Cannot reload: registry not initialized from file. "
                "Call load_from_file() first."
            )
        
        self.load_from_file(self._config_path)
    
    @property
    def config_path(self) -> Optional[Path]:
        """Get the configuration file path."""
        return self._config_path
    
    @property
    def last_loaded(self) -> Optional[datetime]:
        """Get the timestamp of last configuration load."""
        return self._last_loaded
    
    @property
    def config_checksum(self) -> Optional[str]:
        """Get the SHA-256 checksum of configuration file (FR-029)."""
        return self._config_checksum
    
    @property
    def version_count(self) -> int:
        """Get the total number of versions in registry."""
        return len(self._versions)
