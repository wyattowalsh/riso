"""Unit tests for version specification parsing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest

from api_versioning.middleware.parser import (
    SpecificationSource,
    _extract_from_header,
    _extract_from_query,
    _extract_from_url,
    extract_version_from_request,
)


def test_extract_from_header():
    """Test extracting version from HTTP header."""
    headers = {b"x-api-version": b"v2"}
    spec = _extract_from_header(headers)
    
    assert spec is not None
    assert spec.version_id == "v2"
    assert spec.source == SpecificationSource.HEADER
    assert spec.precedence_rank == 1


def test_extract_from_header_alternative():
    """Test extracting version from alternative header."""
    headers = {b"api-version": b"v1"}
    spec = _extract_from_header(headers)
    
    assert spec is not None
    assert spec.version_id == "v1"


def test_extract_from_url():
    """Test extracting version from URL path."""
    spec = _extract_from_url("/v2/users")
    
    assert spec is not None
    assert spec.version_id == "v2"
    assert spec.source == SpecificationSource.URL_PATH
    assert spec.precedence_rank == 2


def test_extract_from_url_with_suffix():
    """Test extracting version with suffix from URL."""
    spec = _extract_from_url("/v3-beta/users")
    
    assert spec is not None
    assert spec.version_id == "v3-beta"


def test_extract_from_query():
    """Test extracting version from query parameter."""
    spec = _extract_from_query(b"version=v2")
    
    assert spec is not None
    assert spec.version_id == "v2"
    assert spec.source == SpecificationSource.QUERY_PARAM
    assert spec.precedence_rank == 3


def test_extract_version_from_request():
    """Test extracting all version specifications from request."""
    scope = {
        "type": "http",
        "path": "/v1/users",
        "query_string": b"version=v2",
        "headers": [(b"x-api-version", b"v3")]
    }
    
    specs = extract_version_from_request(scope)
    
    # Should find all three specifications
    assert len(specs) == 3
    
    # Check each source is present
    sources = {spec.source for spec in specs}
    assert SpecificationSource.HEADER in sources
    assert SpecificationSource.URL_PATH in sources
    assert SpecificationSource.QUERY_PARAM in sources


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
