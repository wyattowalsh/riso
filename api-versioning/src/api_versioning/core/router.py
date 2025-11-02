"""
Version-aware routing for isolating handler implementations per version.

This module provides version-specific routing to ensure strict contract
isolation between API versions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from api_versioning.core.registry import VersionRegistry


# Type alias for ASGI application callable
ASGIApp = Callable[[dict[str, Any], Callable[[], Awaitable[dict[str, Any]]], Callable[[dict[str, Any]], Awaitable[None]]], Awaitable[None]]


@dataclass
class VersionRoute:
    """
    Maps a version to a specific endpoint handler.
    
    This dataclass represents a version-specific route registration,
    enabling different handler implementations for the same endpoint
    across multiple API versions.
    
    Attributes:
        version_id: Version this route applies to
        endpoint_pattern: Endpoint path pattern (e.g., "/users", "/orders/{id}")
        handler: Version-specific handler function
        request_schema: Optional Pydantic model for request validation
        response_schema: Optional Pydantic model for response validation
    
    Example:
        >>> async def get_users_v1(request):
        ...     return {"users": [], "version": "v1"}
        >>> 
        >>> route = VersionRoute(
        ...     version_id="v1",
        ...     endpoint_pattern="/users",
        ...     handler=get_users_v1
        ... )
    """
    
    version_id:       str
    endpoint_pattern: str
    handler:          Callable[..., Awaitable[Any]]
    request_schema:   Optional[type] = None
    response_schema:  Optional[type] = None
    
    def __post_init__(self) -> None:
        """Validate route after initialization."""
        # Verify version exists in registry
        registry = VersionRegistry()
        if registry.get_version(self.version_id) is None:
            raise ValueError(
                f"Version {self.version_id} not found in registry. "
                f"Load configuration first with VersionRegistry.load_from_file()"
            )


class VersionRouter:
    """
    Version-aware router maintaining separate route maps per version.
    
    This router enables strict contract isolation by maintaining separate
    handler registrations for each version. The same endpoint pattern can
    have different handlers for v1, v2, v3, etc.
    
    Thread Safety:
        - Read operations are thread-safe
        - Route registration should happen at startup only
    
    Example:
        >>> router = VersionRouter()
        >>> 
        >>> @router.register("v1", "/users")
        >>> async def get_users_v1(request):
        ...     return {"users": [], "version": "v1"}
        >>> 
        >>> @router.register("v2", "/users")
        >>> async def get_users_v2(request):
        ...     return {"users": [], "version": "v2", "advanced": True}
        >>> 
        >>> handler = router.get_handler("v2", "/users")
    """
    
    def __init__(self) -> None:
        """Initialize the version router."""
        # Maps (version_id, endpoint_pattern) -> handler
        self._routes: dict[tuple[str, str], Callable[..., Awaitable[Any]]] = {}
        
        # Maps version_id -> list of endpoint patterns
        self._version_endpoints: dict[str, list[str]] = {}
    
    def register_route(
        self,
        version_id: str,
        endpoint_pattern: str,
        handler: Callable[..., Awaitable[Any]],
        request_schema: Optional[type] = None,
        response_schema: Optional[type] = None
    ) -> None:
        """
        Register a version-specific route handler.
        
        Args:
            version_id: Version this route applies to
            endpoint_pattern: Endpoint path pattern
            handler: Async handler function
            request_schema: Optional request validation schema
            response_schema: Optional response validation schema
        
        Raises:
            ValueError: If version not found or route already registered
        
        Example:
            >>> router = VersionRouter()
            >>> 
            >>> async def get_users_v1(request):
            ...     return {"users": []}
            >>> 
            >>> router.register_route("v1", "/users", get_users_v1)
        """
        # Validate version exists
        registry = VersionRegistry()
        if registry.get_version(version_id) is None:
            raise ValueError(
                f"Version {version_id} not found in registry. "
                f"Load configuration first."
            )
        
        # Check for duplicate registration
        route_key = (version_id, endpoint_pattern)
        if route_key in self._routes:
            raise ValueError(
                f"Route already registered for version {version_id}, "
                f"endpoint {endpoint_pattern}"
            )
        
        # Register route
        self._routes[route_key] = handler
        
        # Track endpoints per version
        if version_id not in self._version_endpoints:
            self._version_endpoints[version_id] = []
        self._version_endpoints[version_id].append(endpoint_pattern)
    
    def get_handler(
        self,
        version_id: str,
        endpoint_pattern: str
    ) -> Optional[Callable[..., Awaitable[Any]]]:
        """
        Get handler for specific version and endpoint (O(1) lookup).
        
        Args:
            version_id: Version identifier
            endpoint_pattern: Endpoint path pattern
        
        Returns:
            Handler function if found, None otherwise
        
        Example:
            >>> router = VersionRouter()
            >>> handler = router.get_handler("v2", "/users")
            >>> if handler:
            ...     result = await handler(request)
        """
        route_key = (version_id, endpoint_pattern)
        return self._routes.get(route_key)
    
    def get_version_endpoints(self, version_id: str) -> list[str]:
        """
        Get all endpoints registered for a specific version.
        
        Args:
            version_id: Version identifier
        
        Returns:
            List of endpoint patterns for this version
        
        Example:
            >>> router = VersionRouter()
            >>> endpoints = router.get_version_endpoints("v2")
            >>> print(f"v2 endpoints: {endpoints}")
        """
        return self._version_endpoints.get(version_id, [])
    
    def has_version_handler(self, version_id: str, endpoint_pattern: str) -> bool:
        """
        Check if a handler is registered for version and endpoint.
        
        Args:
            version_id: Version identifier
            endpoint_pattern: Endpoint path pattern
        
        Returns:
            True if handler exists, False otherwise
        
        Example:
            >>> router = VersionRouter()
            >>> if router.has_version_handler("v2", "/users"):
            ...     print("Handler found")
        """
        route_key = (version_id, endpoint_pattern)
        return route_key in self._routes
    
    def register(
        self,
        version_id: str,
        endpoint_pattern: str,
        request_schema: Optional[type] = None,
        response_schema: Optional[type] = None
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        """
        Decorator for registering version-specific route handlers.
        
        Args:
            version_id: Version this route applies to
            endpoint_pattern: Endpoint path pattern
            request_schema: Optional request validation schema
            response_schema: Optional response validation schema
        
        Returns:
            Decorator function
        
        Example:
            >>> router = VersionRouter()
            >>> 
            >>> @router.register("v1", "/users")
            >>> async def get_users_v1(request):
            ...     return {"users": [], "version": "v1"}
            >>> 
            >>> @router.register("v2", "/users")
            >>> async def get_users_v2(request):
            ...     return {"users": [], "version": "v2"}
        """
        def decorator(
            handler: Callable[..., Awaitable[Any]]
        ) -> Callable[..., Awaitable[Any]]:
            self.register_route(
                version_id,
                endpoint_pattern,
                handler,
                request_schema,
                response_schema
            )
            return handler
        
        return decorator
    
    def clear(self) -> None:
        """
        Clear all registered routes.
        
        Useful for testing. Should not be called in production.
        
        Example:
            >>> router = VersionRouter()
            >>> router.clear()  # Remove all routes
        """
        self._routes.clear()
        self._version_endpoints.clear()
