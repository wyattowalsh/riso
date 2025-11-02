"""
Version precedence resolution for handling multiple version specifications.

This module implements precedence rules when consumers specify versions via
multiple methods (header, URL, query parameter).
"""

from typing import Optional

from api_versioning.handlers.error import VersionConflictError
from api_versioning.middleware.parser import SpecificationSource, VersionSpecification


def resolve_version_precedence(
    specs: list[VersionSpecification],
    default_version: str,
    precedence_order: tuple[str, ...] = ("header", "url", "query")
) -> str:
    """
    Resolve version from multiple specifications using precedence rules.
    
    Precedence Order (default):
        1. Header (X-API-Version, API-Version)
        2. URL path (/v2/users)
        3. Query parameter (?version=v2)
        4. Default version
    
    Cross-Source Resolution:
        When specifications from different sources conflict, the higher
        precedence source wins. For example, if header says v2 and URL
        says v1, header wins (v2).
    
    Same-Source Conflicts:
        If multiple specifications from the SAME source provide different
        values, a VersionConflictError is raised.
    
    Args:
        specs: List of version specifications extracted from request
        default_version: Default version to use if no specs provided
        precedence_order: Source precedence order (default: header > url > query)
    
    Returns:
        Resolved version identifier
    
    Raises:
        VersionConflictError: If same-source specifications conflict
    
    Example:
        >>> specs = [
        ...     VersionSpecification("v2", SpecificationSource.HEADER, "v2", 1),
        ...     VersionSpecification("v1", SpecificationSource.URL_PATH, "v1", 2)
        ... ]
        >>> resolve_version_precedence(specs, "v1")
        'v2'  # Header wins over URL
    """
    if not specs:
        return default_version
    
    # Check for same-source conflicts
    _check_same_source_conflicts(specs)
    
    # Sort by precedence rank (lower rank = higher precedence)
    sorted_specs = sorted(specs, key=lambda s: s.precedence_rank)
    
    # Return highest precedence specification
    return sorted_specs[0].version_id


def _check_same_source_conflicts(specs: list[VersionSpecification]) -> None:
    """
    Check for conflicting version specifications from the same source.
    
    Same-source conflicts occur when multiple specifications from the same
    source (e.g., two different version headers) provide different values.
    
    Args:
        specs: List of version specifications
    
    Raises:
        VersionConflictError: If same-source conflict detected
    
    Example:
        >>> specs = [
        ...     VersionSpecification("v1", SpecificationSource.HEADER, "v1", 1),
        ...     VersionSpecification("v2", SpecificationSource.HEADER, "v2", 1)
        ... ]
        >>> _check_same_source_conflicts(specs)  # Raises VersionConflictError
    """
    # Group specs by source
    by_source: dict[SpecificationSource, list[VersionSpecification]] = {}
    for spec in specs:
        if spec.source not in by_source:
            by_source[spec.source] = []
        by_source[spec.source].append(spec)
    
    # Check each source for conflicts
    for source, source_specs in by_source.items():
        if len(source_specs) > 1:
            # Multiple specs from same source - check if they agree
            version_ids = set(s.version_id for s in source_specs)
            if len(version_ids) > 1:
                # Conflict detected
                conflicting_specs = [
                    {
                        "source": s.source.value.upper(),
                        "value": s.version_id,
                        "from": _format_source_detail(s)
                    }
                    for s in source_specs
                ]
                
                message = _format_conflict_message(source, source_specs)
                
                raise VersionConflictError(message, conflicting_specs)


def _format_source_detail(spec: VersionSpecification) -> str:
    """
    Format detailed source information for error messages.
    
    Args:
        spec: Version specification
    
    Returns:
        Human-readable source detail
    """
    if spec.source == SpecificationSource.HEADER:
        # Infer which header based on typical patterns
        return "X-API-Version or API-Version header"
    elif spec.source == SpecificationSource.URL_PATH:
        return "URL path segment"
    elif spec.source == SpecificationSource.QUERY_PARAM:
        return "version query parameter"
    else:
        return spec.source.value


def _format_conflict_message(
    source: SpecificationSource,
    specs: list[VersionSpecification]
) -> str:
    """
    Format conflict error message.
    
    Args:
        source: Source where conflict occurred
        specs: Conflicting specifications
    
    Returns:
        Human-readable error message
    """
    source_name = source.value.replace("_", " ")
    version_list = ", ".join(f"{s.version_id}" for s in specs)
    
    if source == SpecificationSource.HEADER:
        return (
            f"Contradictory version headers detected: {version_list}. "
            f"Multiple version headers present with different values."
        )
    elif source == SpecificationSource.URL_PATH:
        return (
            f"Contradictory version URL paths detected: {version_list}. "
            f"This should not happen in normal usage."
        )
    elif source == SpecificationSource.QUERY_PARAM:
        return (
            f"Contradictory version query parameters detected: {version_list}. "
            f"Multiple version parameters present with different values."
        )
    else:
        return f"Contradictory version specifications from {source_name}: {version_list}"


def get_highest_precedence_source(
    precedence_order: tuple[str, ...] = ("header", "url", "query")
) -> SpecificationSource:
    """
    Get the highest precedence specification source.
    
    Args:
        precedence_order: Source precedence order
    
    Returns:
        Highest precedence SpecificationSource
    
    Example:
        >>> get_highest_precedence_source()
        SpecificationSource.HEADER
    """
    source_map = {
        "header": SpecificationSource.HEADER,
        "url": SpecificationSource.URL_PATH,
        "query": SpecificationSource.QUERY_PARAM,
    }
    
    for source_key in precedence_order:
        if source_key in source_map:
            return source_map[source_key]
    
    return SpecificationSource.HEADER  # Default fallback
