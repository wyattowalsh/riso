# Quickstart: API Versioning Strategy

**Feature**: 010-api-versioning-strategy  
**Date**: 2025-11-02  
**Audience**: Developers integrating API versioning into their applications

## Overview

This guide helps you quickly integrate the API versioning middleware into your Python API application. The versioning system supports:
- Multiple concurrent API versions (v1, v2, v3, etc.)
- Version specification via header, URL path, or query parameter
- Automatic deprecation warnings and sunset enforcement
- Version discovery endpoints
- Usage metrics logging for adoption tracking

## Prerequisites

- Python 3.11+ managed with `uv`
- ASGI-compatible framework (FastAPI, Starlette, Django ASGI, or Flask with adapter)
- Basic understanding of ASGI middleware

## Installation

```bash
# Install the API versioning library (once published)
uv pip install api-versioning

# Or for development, install from source
cd api-versioning
uv pip install -e .
```

## Quick Start (5 minutes)

### Step 1: Create Version Configuration

Create `config/api_versions.yaml`:

```yaml
versions:
  v1:
    status: deprecated
    release_date: "2024-01-15"
    deprecation_date: "2025-06-01"
    sunset_date: "2025-12-01"
    description: "Original API version"
    supported_features:
      - basic_crud
      - pagination
    migration_guide_url: "/docs/migrations/v1-to-v2"
    
  v2:
    status: current
    release_date: "2025-06-01"
    description: "Enhanced API with improved validation"
    supported_features:
      - basic_crud
      - pagination
      - advanced_filtering
      - batch_operations
    breaking_changes_from: v1
```

### Step 2: Initialize Version Registry

```python
# app/main.py
from fastapi import FastAPI
from pathlib import Path
from api_versioning import VersionRegistry, APIVersionMiddleware

# Load version configuration at startup
config_path = Path(__file__).parent.parent / "config" / "api_versions.yaml"
VersionRegistry.load_from_file(config_path)

# Create FastAPI app
app = FastAPI(title="My Versioned API")

# Add versioning middleware
app.add_middleware(
    APIVersionMiddleware,
    default_version="v2",
    precedence=("header", "url", "query")
)
```

### Step 3: Access Version in Endpoints

```python
# app/routes/users.py
from fastapi import APIRouter, Request
from api_versioning import get_version_metadata

router = APIRouter()

@router.get("/users")
async def get_users(request: Request):
    # Access resolved version from request scope
    version = request.scope["api_version"]
    
    # Route to version-specific handler
    if version == "v1":
        return await get_users_v1(request)
    elif version == "v2":
        return await get_users_v2(request)
    else:
        return {"error": "Unsupported version"}

async def get_users_v1(request: Request):
    """Version 1 implementation - deprecated"""
    return {"users": [], "version": "v1", "pagination": "offset-based"}

async def get_users_v2(request: Request):
    """Version 2 implementation - current"""
    return {
        "users": [],
        "version": "v2",
        "pagination": "cursor-based",
        "filtering": "advanced"
    }
```

### Step 4: Test Different Version Specifications

```bash
# Test with header (highest precedence)
curl -H "X-API-Version: v1" https://api.example.com/users

# Test with URL path
curl https://api.example.com/v2/users

# Test with query parameter
curl https://api.example.com/users?version=v1

# Test default version (no specification)
curl https://api.example.com/users
```

## Integration Examples

### FastAPI (Recommended)

```python
from fastapi import FastAPI, Request, HTTPException
from api_versioning import (
    VersionRegistry,
    APIVersionMiddleware,
    VersionDiscoveryRouter,
    get_version_metadata
)
from pathlib import Path

# Initialize
app = FastAPI()
config_path = Path(__file__).parent / "config" / "api_versions.yaml"
VersionRegistry.load_from_file(config_path)

# Add middleware
app.add_middleware(
    APIVersionMiddleware,
    default_version="v2"
)

# Add version discovery endpoints
app.include_router(VersionDiscoveryRouter(), prefix="/versions")

# Version-aware endpoint
@app.get("/users")
async def get_users(request: Request):
    version = request.scope["api_version"]
    metadata = get_version_metadata(version)
    
    # Check if deprecated
    if metadata.is_deprecated():
        # Deprecation header automatically added by middleware
        pass
    
    # Route to version-specific logic
    return version_handlers[version](request)
```

### Starlette

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route
from api_versioning import VersionRegistry, APIVersionMiddleware

# Load config
VersionRegistry.load_from_file("config/api_versions.yaml")

# Define middleware
middleware = [
    Middleware(APIVersionMiddleware, default_version="v2")
]

# Define routes
async def users_endpoint(request):
    version = request.scope["api_version"]
    return JSONResponse({"version": version, "users": []})

routes = [
    Route("/users", users_endpoint)
]

# Create app
app = Starlette(routes=routes, middleware=middleware)
```

### Flask (via ASGI Adapter)

```python
from flask import Flask, request
from asgiref.wsgi import WsgiToAsgi
from api_versioning import VersionRegistry, APIVersionMiddleware

# Create Flask app
flask_app = Flask(__name__)

@flask_app.route("/users")
def get_users():
    # Access version from ASGI scope (available via request context)
    version = request.environ.get("api_version", "v1")
    return {"version": version, "users": []}

# Convert to ASGI and wrap with versioning middleware
asgi_app = WsgiToAsgi(flask_app)
VersionRegistry.load_from_file("config/api_versions.yaml")
app = APIVersionMiddleware(asgi_app, default_version="v2")
```

## Advanced Usage

### Version-Specific Route Handlers

```python
from api_versioning import VersionRouter

# Create version-aware router
router = VersionRouter()

# Register version-specific handlers
@router.get("/users", versions=["v1"])
async def get_users_v1(request: Request):
    return {"version": "v1", "users": []}

@router.get("/users", versions=["v2"])
async def get_users_v2(request: Request):
    return {"version": "v2", "users": [], "advanced": True}

# Automatically routes based on request version
app.include_router(router)
```

### Custom Version Resolution Logic

```python
from api_versioning import APIVersionMiddleware

class CustomVersionMiddleware(APIVersionMiddleware):
    def _extract_version(self, scope: dict) -> str:
        """Override to add custom version resolution logic."""
        # Try custom header first
        headers = dict(scope.get("headers", []))
        if b"x-client-version" in headers:
            return headers[b"x-client-version"].decode()
        
        # Fall back to default logic
        return super()._extract_version(scope)

app.add_middleware(CustomVersionMiddleware)
```

### Pre-Release Version Access

```python
# Configure pre-release version in config
# config/api_versions.yaml
versions:
  v3-beta:
    status: prerelease
    release_date: "2025-11-01"
    opt_in_required: true
    description: "Beta version with new features"

# Access pre-release version with opt-in header
curl -H "X-API-Version: v3-beta" \
     -H "X-API-Prerelease-Opt-In: true" \
     https://api.example.com/users
```

### Usage Metrics Logging

```python
from api_versioning import VersionMetricsLogger
import structlog

# Configure structured logging
logger = structlog.get_logger()
metrics_logger = VersionMetricsLogger(logger)

# Add metrics middleware (automatically logs version usage)
app.add_middleware(
    VersionMetricsMiddleware,
    metrics_logger=metrics_logger
)

# Metrics are logged as structured JSON
# {
#   "timestamp": "2025-11-02T10:30:45Z",
#   "version_id": "v2",
#   "endpoint_path": "/users",
#   "http_status": 200,
#   "latency_ms": 45.3,
#   "consumer_id": "client_abc123",
#   "source": "header"
# }
```

### Hot Reload (Development)

```python
from api_versioning import start_config_watcher

# Start file watcher for development hot-reload
if app.debug:
    observer = start_config_watcher(config_path)
    # Config automatically reloads when file changes
```

## Response Headers

All versioned responses include these headers:

```http
X-API-Version: v2                     # Version used for this request
```

For deprecated versions:

```http
X-API-Version: v1
Deprecation: date="2025-12-01"        # RFC 8594 deprecation header
Sunset: Sun, 01 Dec 2025 00:00:00 GMT # RFC 8594 sunset header
Link: </docs/migrations/v1-to-v2>; rel="migration-guide"
```

## Error Responses

### Version Not Found (404)

```json
{
  "error": {
    "code": "VERSION_NOT_FOUND",
    "message": "API version 'v99' not found",
    "available_versions": ["v1", "v2"]
  }
}
```

### Version Sunset (410)

```json
{
  "error": {
    "code": "VERSION_SUNSET",
    "message": "API version 'v1' was sunset on 2025-12-01",
    "recommended_version": "v2",
    "migration_guide_url": "/docs/migrations/v1-to-v2"
  }
}
```

### Version Conflict (400)

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "Contradictory version specifications: header=v2, url=v1",
    "details": {
      "header_version": "v2",
      "url_version": "v1",
      "query_version": null
    }
  }
}
```

## Version Discovery API

The middleware automatically adds version discovery endpoints:

```bash
# List all active versions
curl https://api.example.com/versions

# Get specific version metadata
curl https://api.example.com/versions/v2

# Get deprecation notice
curl https://api.example.com/versions/v1/deprecation

# Get current default version
curl https://api.example.com/versions/current
```

## Testing

```python
# tests/test_versioning.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version_from_header():
    response = client.get("/users", headers={"X-API-Version": "v2"})
    assert response.status_code == 200
    assert response.headers["X-API-Version"] == "v2"

def test_version_from_url():
    response = client.get("/v1/users")
    assert response.status_code == 200
    assert response.headers["X-API-Version"] == "v1"

def test_version_precedence():
    # Header should take precedence over URL
    response = client.get(
        "/v1/users",
        headers={"X-API-Version": "v2"}
    )
    assert response.headers["X-API-Version"] == "v2"

def test_deprecated_version_warning():
    response = client.get("/users", headers={"X-API-Version": "v1"})
    assert "Deprecation" in response.headers
    assert "Sunset" in response.headers

def test_sunset_version_rejected():
    # Assuming v0 is sunset
    response = client.get("/users", headers={"X-API-Version": "v0"})
    assert response.status_code == 410
```

## Performance Tuning

### Optimize Version Lookup

```python
# Pre-compile regex patterns
import re

class OptimizedVersionMiddleware(APIVersionMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Compile URL pattern once at initialization
        self._url_pattern = re.compile(r"^/v(\d+)/")
```

### Benchmark Version Routing

```bash
# Run performance tests
uv run pytest tests/performance/test_version_routing.py --benchmark-only

# Expected results:
# Version lookup: ~50-200ns
# Total routing overhead: ~0.1-1ms
```

## Troubleshooting

### Issue: Version not detected from URL path

**Solution**: Ensure URL path starts with `/v{N}/`:
```python
# Correct
GET /v2/users

# Incorrect (version not detected)
GET /api/v2/users
GET /users/v2
```

### Issue: Deprecation headers not appearing

**Solution**: Check version status in config file:
```yaml
versions:
  v1:
    status: deprecated  # Must be explicitly set
    deprecation_date: "2025-06-01"  # Must be present
```

### Issue: High latency from version routing

**Solution**: Check middleware order - versioning should be early in stack:
```python
# Correct order
app.add_middleware(APIVersionMiddleware)  # First
app.add_middleware(CORSMiddleware)
app.add_middleware(AuthMiddleware)
```

## Next Steps

1. Read the [data model documentation](./data-model.md) for entity details
2. Review the [OpenAPI contract](./contracts/api-versioning.openapi.yaml)
3. Explore migration patterns in [migration guide](./docs/migrations/)
4. Set up monitoring for version adoption metrics

## Resources

- [ASGI Specification](https://asgi.readthedocs.io/)
- [RFC 8594: Deprecation HTTP Header](https://www.rfc-editor.org/rfc/rfc8594.html)
- [Semantic Versioning](https://semver.org/)
- [API Versioning Best Practices](https://www.example.com/api-versioning-guide)
