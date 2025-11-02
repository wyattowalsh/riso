#!/usr/bin/env python3
"""
Quick validation script for API versioning middleware.

This script performs basic smoke tests to ensure core functionality works.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Test imports
print("Testing imports...")
try:
    from api_versioning import (
        APIVersionMiddleware,
        VersionMetadata,
        VersionRegistry,
        VersionStatus,
        get_version_metadata,
    )
    print("? Core imports successful")
except ImportError as e:
    print(f"? Import failed: {e}")
    exit(1)

# Test registry loading
print("\nTesting registry loading...")
try:
    config_path = Path(__file__).parent / "config" / "api_versions.yaml"
    VersionRegistry.load_from_file(config_path)
    print(f"? Registry loaded from {config_path}")
except Exception as e:
    print(f"? Registry loading failed: {e}")
    exit(1)

# Test version lookup
print("\nTesting version lookup...")
try:
    registry = VersionRegistry()
    
    v1 = registry.get_version("v1")
    assert v1 is not None, "v1 not found"
    assert v1.status == VersionStatus.DEPRECATED, "v1 should be deprecated"
    print(f"? Found v1: {v1.status.value}")
    
    v2 = registry.get_version("v2")
    assert v2 is not None, "v2 not found"
    assert v2.status == VersionStatus.CURRENT, "v2 should be current"
    print(f"? Found v2: {v2.status.value}")
    
    current = registry.get_current_version()
    assert current is not None, "No current version"
    assert current.version_id == "v2", "Current should be v2"
    print(f"? Current version: {current.version_id}")
    
except AssertionError as e:
    print(f"? Assertion failed: {e}")
    exit(1)
except Exception as e:
    print(f"? Version lookup failed: {e}")
    exit(1)

# Test version metadata
print("\nTesting version metadata...")
try:
    v1 = registry.get_version("v1")
    assert v1 is not None
    
    # Check deprecation
    assert v1.is_deprecated(), "v1 should be deprecated"
    print(f"? v1 deprecation check passed")
    
    # Check features
    assert "basic_crud" in v1.supported_features
    assert "pagination" in v1.supported_features
    print(f"? v1 features: {len(v1.supported_features)}")
    
    # Check to_dict
    v1_dict = v1.to_dict()
    assert "version_id" in v1_dict
    assert v1_dict["version_id"] == "v1"
    print(f"? v1 serialization works")
    
except AssertionError as e:
    print(f"? Assertion failed: {e}")
    exit(1)
except Exception as e:
    print(f"? Metadata test failed: {e}")
    exit(1)

# Test version validation
print("\nTesting version validation...")
try:
    from api_versioning.utils.semver import parse_version, validate_version_id
    
    # Valid versions
    assert validate_version_id("v1")
    assert validate_version_id("v2")
    assert validate_version_id("v99")
    assert validate_version_id("v3-beta")
    assert validate_version_id("v3-alpha")
    print("? Valid version IDs accepted")
    
    # Invalid versions
    assert not validate_version_id("V1")  # Uppercase
    assert not validate_version_id("1")   # No 'v' prefix
    assert not validate_version_id("v1.0")  # Dots not allowed
    print("? Invalid version IDs rejected")
    
    # Test parsing
    parsed = parse_version("v2")
    assert parsed is not None
    assert parsed.major == 2
    assert parsed.suffix is None
    print("? Version parsing works")
    
    parsed_beta = parse_version("v3-beta")
    assert parsed_beta is not None
    assert parsed_beta.major == 3
    assert parsed_beta.suffix == "beta"
    print("? Beta version parsing works")
    
except AssertionError as e:
    print(f"? Assertion failed: {e}")
    exit(1)
except Exception as e:
    print(f"? Validation test failed: {e}")
    exit(1)

# Test error classes
print("\nTesting error classes...")
try:
    from api_versioning.handlers.error import (
        VersionConflictError,
        VersionNotFoundError,
        VersionSunsetError,
    )
    
    # Test VersionNotFoundError
    error = VersionNotFoundError("v99", ["v1", "v2"])
    assert error.status_code == 404
    assert error.code == "VERSION_NOT_FOUND"
    error_dict = error.to_dict()
    assert "error" in error_dict
    print("? VersionNotFoundError works")
    
    # Test VersionSunsetError
    error = VersionSunsetError("v1", "2026-06-01", "v2")
    assert error.status_code == 410
    assert error.code == "VERSION_SUNSET"
    print("? VersionSunsetError works")
    
except Exception as e:
    print(f"? Error class test failed: {e}")
    exit(1)

# Test deprecation handlers
print("\nTesting deprecation handlers...")
try:
    from api_versioning.handlers.deprecation import (
        check_deprecation,
        format_deprecation_header,
        is_sunset,
    )
    
    v1 = registry.get_version("v1")
    assert v1 is not None
    
    # Check deprecation notice
    notice = check_deprecation(v1)
    assert notice is not None, "v1 should have deprecation notice"
    assert notice.version_id == "v1"
    print(f"? Deprecation notice generated for v1")
    
    # Check deprecation header
    header = format_deprecation_header(v1)
    assert header is not None
    assert "date=" in header
    print(f"? Deprecation header: {header}")
    
    # Check sunset status
    assert not is_sunset(v1), "v1 should not be sunset yet"
    print(f"? Sunset check passed")
    
except Exception as e:
    print(f"? Deprecation test failed: {e}")
    exit(1)

print("\n" + "=" * 50)
print("? All validation tests passed!")
print("=" * 50)
print("\nCore functionality is working correctly.")
print("Ready for integration testing with ASGI frameworks.")
