"""
FastAPI integration example for API versioning middleware.

This example demonstrates how to integrate the API versioning middleware
with a FastAPI application.

Usage:
    pip install fastapi uvicorn
    python examples/fastapi_app.py
    
    # Or with uvicorn:
    uvicorn examples.fastapi_app:app --reload
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_versioning import APIVersionMiddleware, VersionRegistry


# Load version configuration
config_path = Path(__file__).parent.parent / "config" / "api_versions.yaml"
VersionRegistry.load_from_file(config_path)

# Create FastAPI application
app = FastAPI(
    title="API Versioning Example",
    description="FastAPI application with API versioning middleware",
    version="1.0.0"
)

# Add versioning middleware
app.add_middleware(
    APIVersionMiddleware,
    default_version="v2",
    precedence=("header", "url", "query")
)


# Example endpoints with version-aware routing


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "API Versioning Example",
        "docs": "/docs",
        "versions": "/versions"
    }


@app.get("/users")
async def get_users(request: Request):
    """
    Get users - version-aware endpoint.
    
    Different behavior based on API version:
    - v1: Basic user list with offset pagination
    - v2: Enhanced user list with cursor pagination and filtering
    """
    version = request.scope["api_version"]
    metadata = request.scope["api_version_metadata"]
    
    if version == "v1":
        # Version 1 implementation
        return {
            "version": "v1",
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "pagination": {
                "offset": 0,
                "limit": 10
            },
            "deprecated": metadata.is_deprecated()
        }
    
    elif version == "v2":
        # Version 2 implementation with enhanced features
        return {
            "version": "v2",
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ],
            "pagination": {
                "cursor": "eyJpZCI6Mn0=",
                "has_more": False
            },
            "filtering": {
                "available_filters": ["name", "email", "created_at"]
            }
        }
    
    else:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported version: {version}"}
        )


@app.get("/products")
async def get_products(request: Request):
    """Get products - demonstrating version-specific features."""
    version = request.scope["api_version"]
    
    base_products = [
        {"id": 1, "name": "Product A", "price": 29.99},
        {"id": 2, "name": "Product B", "price": 49.99}
    ]
    
    if version == "v1":
        # v1: Basic product list
        return {"products": base_products}
    
    else:
        # v2+: Add inventory information
        for product in base_products:
            product["inventory"] = {"in_stock": True, "quantity": 100}
        
        return {
            "products": base_products,
            "features": ["inventory_tracking", "batch_operations"]
        }


# Health check endpoint (version-independent)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    registry = VersionRegistry()
    return {
        "status": "healthy",
        "versions": {
            "loaded": registry.version_count,
            "current": registry.get_current_version().version_id
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("Starting FastAPI application with API versioning...")
    print("Visit http://localhost:8000/docs for interactive documentation")
    print()
    print("Try these examples:")
    print("  curl http://localhost:8000/users")
    print("  curl -H 'X-API-Version: v1' http://localhost:8000/users")
    print("  curl http://localhost:8000/v2/users")
    print("  curl http://localhost:8000/users?version=v1")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
