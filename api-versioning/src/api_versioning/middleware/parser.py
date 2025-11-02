"""
Version specification parsing from HTTP requests.

This module provides utilities for extracting version specifications from
headers, URL paths, and query parameters.
"""

import re
from enum import Enum
from typing import Optional
from urllib.parse import parse_qs


class SpecificationSource(str, Enum):
    """
    Source of version specification in request.
    
    Values:
        HEADER: Version from HTTP header
        URL_PATH: Version from URL path segment
        QUERY_PARAM: Version from query parameter
        DEFAULT: No version specified, using default
    """
    
    HEADER      = "header"
    URL_PATH    = "url_path"
    QUERY_PARAM = "query_param"
    DEFAULT     = "default"


class VersionSpecification:
    """
    Represents how a consumer specified their desired version.
    
    Attributes:
        version_id: The resolved version identifier
        source: Where the version was specified
        raw_value: Original value from request
        precedence_rank: Priority order (1=header, 2=url, 3=query, 4=default)
    """
    
    def __init__(
        self,
        version_id: str,
        source: SpecificationSource,
        raw_value: str,
        precedence_rank: int
    ):
        """Initialize version specification."""
        self.version_id = version_id
        self.source = source
        self.raw_value = raw_value
        self.precedence_rank = precedence_rank
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"VersionSpecification(version_id={self.version_id!r}, "
            f"source={self.source.value!r}, raw_value={self.raw_value!r})"
        )


# URL path pattern to extract version: /v{N}/...
URL_VERSION_PATTERN = re.compile(r"^/v(\d+(?:-[a-z]+)?)/")


def extract_version_from_request(scope: dict) -> list[VersionSpecification]:
    """
    Extract all version specifications from ASGI request scope.
    
    This function extracts version indicators from:
    1. HTTP headers (X-API-Version, API-Version)
    2. URL path segment (/v2/users)
    3. Query parameter (?version=v2)
    
    Args:
        scope: ASGI connection scope
    
    Returns:
        List of VersionSpecification objects (may be empty)
    
    Example:
        >>> scope = {
        ...     "type": "http",
        ...     "path": "/v2/users",
        ...     "query_string": b"",
        ...     "headers": [(b"x-api-version", b"v1")]
        ... }
        >>> specs = extract_version_from_request(scope)
        >>> print(len(specs))  # 2 specs found (header and URL)
        2
    """
    specs: list[VersionSpecification] = []
    
    # Extract from headers
    headers_dict = dict(scope.get("headers", []))
    header_version = _extract_from_header(headers_dict)
    if header_version:
        specs.append(header_version)
    
    # Extract from URL path
    path = scope.get("path", "")
    url_version = _extract_from_url(path)
    if url_version:
        specs.append(url_version)
    
    # Extract from query parameter
    query_string = scope.get("query_string", b"")
    query_version = _extract_from_query(query_string)
    if query_version:
        specs.append(query_version)
    
    return specs


def _extract_from_header(headers: dict[bytes, bytes]) -> Optional[VersionSpecification]:
    """
    Extract version from HTTP headers.
    
    Checks both X-API-Version and API-Version headers (case-insensitive).
    
    Args:
        headers: Request headers as bytes dictionary
    
    Returns:
        VersionSpecification if header found, None otherwise
    """
    # Check for X-API-Version or API-Version headers (case-insensitive)
    for header_name, header_value in headers.items():
        lower_name = header_name.lower()
        if lower_name in (b"x-api-version", b"api-version"):
            version_id = header_value.decode("utf-8", errors="ignore").strip()
            if version_id:
                return VersionSpecification(
                    version_id=version_id,
                    source=SpecificationSource.HEADER,
                    raw_value=version_id,
                    precedence_rank=1  # Highest precedence
                )
    
    return None


def _extract_from_url(path: str) -> Optional[VersionSpecification]:
    """
    Extract version from URL path segment.
    
    Pattern: /v{N}/... or /v{N}-{suffix}/...
    
    Args:
        path: URL path
    
    Returns:
        VersionSpecification if version found in path, None otherwise
    
    Example:
        >>> spec = _extract_from_url("/v2/users")
        >>> print(spec.version_id)
        v2
        >>> spec = _extract_from_url("/v3-beta/users")
        >>> print(spec.version_id)
        v3-beta
    """
    match = URL_VERSION_PATTERN.match(path)
    if match:
        version_number = match.group(1)
        version_id = f"v{version_number}"
        
        return VersionSpecification(
            version_id=version_id,
            source=SpecificationSource.URL_PATH,
            raw_value=version_id,
            precedence_rank=2  # Second precedence
        )
    
    return None


def _extract_from_query(query_string: bytes) -> Optional[VersionSpecification]:
    """
    Extract version from query parameter.
    
    Parameter: ?version=vN
    
    Args:
        query_string: URL query string as bytes
    
    Returns:
        VersionSpecification if version parameter found, None otherwise
    
    Example:
        >>> spec = _extract_from_query(b"version=v2")
        >>> print(spec.version_id)
        v2
    """
    if not query_string:
        return None
    
    # Parse query string
    query_params = parse_qs(query_string.decode("utf-8", errors="ignore"))
    
    # Check for 'version' parameter
    if "version" in query_params:
        version_values = query_params["version"]
        if version_values:
            version_id = version_values[0].strip()
            if version_id:
                return VersionSpecification(
                    version_id=version_id,
                    source=SpecificationSource.QUERY_PARAM,
                    raw_value=version_id,
                    precedence_rank=3  # Lowest precedence
                )
    
    return None
