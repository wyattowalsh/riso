"""Unit tests for version registry."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from api_versioning.core.registry import VersionRegistry
from api_versioning.core.version import VersionStatus


@pytest.fixture
def config_path():
    """Get test configuration path."""
    return Path(__file__).parent.parent.parent / "config" / "api_versions.yaml"


def test_registry_load_from_file(config_path):
    """Test loading registry from YAML file."""
    VersionRegistry.load_from_file(config_path)
    
    registry = VersionRegistry()
    assert registry.version_count == 2


def test_registry_get_version(config_path):
    """Test getting version by ID."""
    VersionRegistry.load_from_file(config_path)
    
    registry = VersionRegistry()
    v1 = registry.get_version("v1")
    
    assert v1 is not None
    assert v1.version_id == "v1"
    assert v1.status == VersionStatus.DEPRECATED


def test_registry_get_current_version(config_path):
    """Test getting current version."""
    VersionRegistry.load_from_file(config_path)
    
    registry = VersionRegistry()
    current = registry.get_current_version()
    
    assert current is not None
    assert current.version_id == "v2"
    assert current.status == VersionStatus.CURRENT


def test_registry_list_all_versions(config_path):
    """Test listing all versions."""
    VersionRegistry.load_from_file(config_path)
    
    registry = VersionRegistry()
    versions = registry.list_all_versions()
    
    assert len(versions) == 2
    assert versions[0].version_id == "v1"
    assert versions[1].version_id == "v2"


def test_registry_list_active_versions(config_path):
    """Test listing active versions."""
    VersionRegistry.load_from_file(config_path)
    
    registry = VersionRegistry()
    versions = registry.list_active_versions()
    
    # Should include both v1 (deprecated) and v2 (current)
    assert len(versions) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
