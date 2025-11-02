# API Versioning Middleware

Framework-agnostic ASGI middleware for comprehensive API version management with support for multiple concurrent versions, deprecation workflows, version discovery, and usage metrics tracking.

## Features

- **Version Specification**: Support for header, URL path, and query parameter version specification with precedence rules (Header > URL > Query)
- **Multiple Concurrent Versions**: Run v1, v2, v3 simultaneously with strict contract isolation
- **Deprecation Management**: Automatic deprecation warnings via RFC 8594 headers and sunset enforcement
- **Version Discovery**: Built-in endpoints for discovering available versions and their metadata
- **Pre-release Support**: Beta/alpha versions with explicit opt-in requirements
- **Usage Metrics**: Structured logging for adoption tracking and analytics
- **High Performance**: <10ms routing overhead, 1000+ req/s throughput
- **Framework Agnostic**: Works with FastAPI, Starlette, Django ASGI, Flask (via adapter)

## Installation

```bash
# Using uv (recommended)
uv pip install api-versioning

# Using pip
pip install api-versioning

# With optional dependencies
uv pip install api-versioning[hotreload]  # Development hot-reload
uv pip install api-versioning[all]        # All optional dependencies
```

## Quick Start

### 1. Create Version Configuration

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

### 2. Initialize Version Registry

```python
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

### 3. Access Version in Endpoints

```python
from fastapi import APIRouter, Request

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
```

### 4. Test Different Version Specifications

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

## Version Specification Methods

### Header (Highest Precedence)
```bash
curl -H "X-API-Version: v2" https://api.example.com/users
curl -H "API-Version: v2" https://api.example.com/users  # Alternative header
```

### URL Path
```bash
curl https://api.example.com/v2/users
```

### Query Parameter (Lowest Precedence)
```bash
curl https://api.example.com/users?version=v2
```

## Response Headers

All versioned responses include:

```http
X-API-Version: v2  # Version used for this request
```

For deprecated versions:

```http
X-API-Version: v1
Deprecation: date="2025-12-01"        # RFC 8594
Sunset: Sun, 01 Dec 2025 00:00:00 GMT # RFC 8594
Link: </docs/migrations/v1-to-v2>; rel="migration-guide"
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

### Version Sunset (410 Gone)
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

### Version Conflict (400 Bad Request)
```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "Contradictory version headers: X-API-Version=v1, API-Version=v2",
    "detected_specifications": [
      {"source": "HEADER", "value": "v1", "from": "X-API-Version"},
      {"source": "HEADER", "value": "v2", "from": "API-Version"}
    ]
  }
}
```

## Framework Integration Examples

### FastAPI
```python
from fastapi import FastAPI
from api_versioning import VersionRegistry, APIVersionMiddleware

app = FastAPI()
VersionRegistry.load_from_file("config/api_versions.yaml")
app.add_middleware(APIVersionMiddleware, default_version="v2")
```

### Starlette
```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from api_versioning import VersionRegistry, APIVersionMiddleware

VersionRegistry.load_from_file("config/api_versions.yaml")
middleware = [Middleware(APIVersionMiddleware, default_version="v2")]
app = Starlette(middleware=middleware)
```

### Flask (via ASGI Adapter)
```python
from flask import Flask
from asgiref.wsgi import WsgiToAsgi
from api_versioning import VersionRegistry, APIVersionMiddleware

flask_app = Flask(__name__)
asgi_app = WsgiToAsgi(flask_app)
VersionRegistry.load_from_file("config/api_versions.yaml")
app = APIVersionMiddleware(asgi_app, default_version="v2")
```

## Configuration Reference

### Version Status Values

- `current`: Active stable version (usually the default)
- `deprecated`: Still supported but scheduled for removal
- `sunset`: No longer supported, returns 410 Gone
- `prerelease`: Beta/alpha version requiring opt-in

### Required Fields

- `version_id`: Unique identifier (e.g., "v1", "v2", "v3-beta")
- `status`: One of the status values above
- `release_date`: ISO 8601 date when version was released

### Optional Fields

- `deprecation_date`: When version was marked deprecated
- `sunset_date`: When version will be/was removed (must be ?12 months after deprecation)
- `description`: Human-readable description
- `supported_features`: List of feature flags
- `breaking_changes_from`: Previous version ID
- `migration_guide_url`: URL to migration documentation
- `opt_in_required`: Whether pre-release opt-in is required

## Performance

- Version routing overhead: **<10ms** (typically 0.1-1ms)
- Version lookup latency: **50-200ns** (O(1) hash map)
- Throughput: **1000+ req/s** sustained, 5000+ req/s burst
- Memory footprint: **10-50KB** for typical configurations

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/riso-template/api-versioning
cd api-versioning

# Install with development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run quality checks
uv run ruff check src tests
uv run mypy src
uv run pytest --cov

# Run performance benchmarks
uv run pytest tests/performance --benchmark-only
```

### Testing

```bash
# Unit tests
uv run pytest tests/unit

# Integration tests
uv run pytest tests/integration

# Contract tests
uv run pytest tests/contract

# Performance tests
uv run pytest tests/performance --benchmark-only

# All tests with coverage
uv run pytest --cov --cov-report=html
```

## Documentation

- [Quickstart Guide](docs/quickstart.md)
- [Data Model](docs/data-model.md)
- [API Contract (OpenAPI)](docs/contracts/api-versioning.openapi.yaml)
- [Migration Guide](docs/migrations/)
- [Edge Cases](docs/edge-cases.md)
- [Testing Strategy](docs/testing-strategy.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Support

- Documentation: https://riso-template.github.io/api-versioning
- Issues: https://github.com/riso-template/api-versioning/issues
- Discussions: https://github.com/riso-template/api-versioning/discussions
