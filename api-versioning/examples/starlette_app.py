"""
Starlette integration example for API versioning middleware.

This example demonstrates how to integrate the API versioning middleware
with a Starlette application.

Usage:
    pip install starlette uvicorn
    python examples/starlette_app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from api_versioning import APIVersionMiddleware, VersionRegistry


# Load configuration
config_path = Path(__file__).parent.parent / "config" / "api_versions.yaml"
VersionRegistry.load_from_file(config_path)


# Define endpoints


async def homepage(request: Request):
    """Homepage endpoint."""
    return JSONResponse({
        "message": "Starlette API Versioning Example",
        "endpoints": {
            "/users": "Get users (version-aware)",
            "/versions": "List API versions"
        }
    })


async def get_users(request: Request):
    """Get users with version-aware response."""
    version = request.scope["api_version"]
    
    if version == "v1":
        return JSONResponse({
            "version": "v1",
            "users": [{"id": 1, "name": "Alice"}]
        })
    else:
        return JSONResponse({
            "version": "v2",
            "users": [{"id": 1, "name": "Alice", "email": "alice@example.com"}]
        })


# Define routes
routes = [
    Route("/", homepage),
    Route("/users", get_users)
]

# Configure middleware
middleware = [
    Middleware(APIVersionMiddleware, default_version="v2")
]

# Create application
app = Starlette(
    routes=routes,
    middleware=middleware
)


if __name__ == "__main__":
    import uvicorn
    
    print("Starting Starlette application with API versioning...")
    print("Visit http://localhost:8000/")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
