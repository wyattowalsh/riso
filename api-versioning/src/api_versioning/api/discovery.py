"""
Version discovery endpoints for listing and querying API versions.

This module provides HTTP endpoints for discovering available versions,
retrieving version metadata, and accessing deprecation information.
"""

import json
from typing import Any, Awaitable, Callable, Optional

from api_versioning.core.registry import VersionRegistry
from api_versioning.core.version import VersionMetadata
from api_versioning.handlers.deprecation import check_deprecation


class VersionDiscoveryRouter:
    """
    Router for version discovery endpoints.
    
    This class provides HTTP endpoints for version discovery that can be
    integrated into any ASGI application.
    
    Endpoints:
        - GET /versions - List all available versions
        - GET /versions/{version_id} - Get specific version metadata
        - GET /versions/{version_id}/deprecation - Get deprecation notice
        - GET /versions/current - Get current default version
    
    Example:
        >>> from fastapi import FastAPI
        >>> from api_versioning import VersionDiscoveryRouter
        >>> 
        >>> app = FastAPI()
        >>> router = VersionDiscoveryRouter()
        >>> 
        >>> # Add discovery endpoints (framework-specific integration)
        >>> # For FastAPI:
        >>> app.get("/versions")(router.list_versions)
        >>> app.get("/versions/{version_id}")(router.get_version)
    """
    
    def __init__(self) -> None:
        """Initialize version discovery router."""
        self.registry = VersionRegistry()
    
    async def list_versions(
        self,
        include_sunset: bool = False,
        include_prerelease: bool = False
    ) -> dict[str, Any]:
        """
        List all available API versions.
        
        Args:
            include_sunset: Include sunset (removed) versions
            include_prerelease: Include pre-release (beta/alpha) versions
        
        Returns:
            Dictionary with version list and metadata
        
        Example:
            >>> router = VersionDiscoveryRouter()
            >>> response = await router.list_versions()
            >>> print(response["total_count"])
        """
        versions = self.registry.list_active_versions(
            include_prerelease=include_prerelease,
            include_sunset=include_sunset
        )
        
        current_version = self.registry.get_current_version()
        default_version_id = current_version.version_id if current_version else None
        
        return {
            "versions": [v.to_dict() for v in versions],
            "default_version": default_version_id,
            "total_count": len(versions)
        }
    
    async def get_version(self, version_id: str) -> dict[str, Any]:
        """
        Get detailed metadata for a specific version.
        
        Args:
            version_id: Version identifier
        
        Returns:
            Version metadata dictionary
        
        Raises:
            404: If version not found
        
        Example:
            >>> router = VersionDiscoveryRouter()
            >>> response = await router.get_version("v2")
            >>> print(response["status"])
        """
        metadata = self.registry.get_version(version_id)
        if metadata is None:
            raise VersionNotFoundError(version_id)
        
        return metadata.to_dict()
    
    async def get_current_version(self) -> dict[str, Any]:
        """
        Get the current default version.
        
        Returns:
            Current version metadata dictionary
        
        Raises:
            404: If no current version found
        
        Example:
            >>> router = VersionDiscoveryRouter()
            >>> response = await router.get_current_version()
            >>> print(response["version_id"])
        """
        current = self.registry.get_current_version()
        if current is None:
            raise VersionNotFoundError("current")
        
        return current.to_dict()
    
    async def get_deprecation_notice(self, version_id: str) -> dict[str, Any]:
        """
        Get deprecation notice for a version.
        
        Args:
            version_id: Version identifier
        
        Returns:
            Deprecation notice dictionary
        
        Raises:
            404: If version not found or not deprecated
        
        Example:
            >>> router = VersionDiscoveryRouter()
            >>> response = await router.get_deprecation_notice("v1")
            >>> print(response["days_until_sunset"])
        """
        metadata = self.registry.get_version(version_id)
        if metadata is None:
            raise VersionNotFoundError(version_id)
        
        notice = check_deprecation(metadata)
        if notice is None:
            raise VersionNotDeprecatedError(version_id)
        
        return notice.to_dict()


def create_discovery_app() -> Callable[[dict, Callable, Callable], Awaitable[None]]:
    """
    Create a standalone ASGI app for version discovery endpoints.
    
    This function creates a minimal ASGI application that serves only
    the version discovery endpoints. Useful for testing or standalone
    version metadata services.
    
    Returns:
        ASGI application callable
    
    Example:
        >>> from api_versioning import VersionRegistry, create_discovery_app
        >>> 
        >>> # Load configuration
        >>> VersionRegistry.load_from_file("config/api_versions.yaml")
        >>> 
        >>> # Create discovery app
        >>> app = create_discovery_app()
        >>> 
        >>> # Run with uvicorn
        >>> # uvicorn app:app --host 0.0.0.0 --port 8000
    """
    router = VersionDiscoveryRouter()
    
    async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """ASGI application for version discovery."""
        if scope["type"] != "http":
            return
        
        path = scope["path"]
        method = scope["method"]
        
        # Route requests
        if method == "GET":
            try:
                if path == "/versions":
                    response_data = await router.list_versions()
                    await _send_json_response(send, 200, response_data)
                
                elif path == "/versions/current":
                    response_data = await router.get_current_version()
                    await _send_json_response(send, 200, response_data)
                
                elif path.startswith("/versions/"):
                    parts = path.split("/")
                    if len(parts) == 3:
                        version_id = parts[2]
                        response_data = await router.get_version(version_id)
                        await _send_json_response(send, 200, response_data)
                    
                    elif len(parts) == 4 and parts[3] == "deprecation":
                        version_id = parts[2]
                        response_data = await router.get_deprecation_notice(version_id)
                        await _send_json_response(send, 200, response_data)
                    
                    else:
                        await _send_json_response(send, 404, {
                            "error": {"code": "NOT_FOUND", "message": "Endpoint not found"}
                        })
                
                else:
                    await _send_json_response(send, 404, {
                        "error": {"code": "NOT_FOUND", "message": "Endpoint not found"}
                    })
            
            except Exception as e:
                error_response = {"error": {"code": "ERROR", "message": str(e)}}
                await _send_json_response(send, 500, error_response)
        
        else:
            await _send_json_response(send, 405, {
                "error": {"code": "METHOD_NOT_ALLOWED", "message": "Method not allowed"}
            })
    
    return app


async def _send_json_response(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int,
    data: dict[str, Any]
) -> None:
    """
    Send JSON response.
    
    Args:
        send: ASGI send callable
        status: HTTP status code
        data: Response data dictionary
    """
    body = json.dumps(data, indent=2).encode()
    
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode())
        ]
    })
    
    await send({
        "type": "http.response.body",
        "body": body
    })


class VersionNotFoundError(Exception):
    """Version not found error."""
    
    def __init__(self, version_id: str):
        """Initialize error."""
        super().__init__(f"Version '{version_id}' not found")
        self.version_id = version_id


class VersionNotDeprecatedError(Exception):
    """Version not deprecated error."""
    
    def __init__(self, version_id: str):
        """Initialize error."""
        super().__init__(f"Version '{version_id}' is not deprecated")
        self.version_id = version_id
