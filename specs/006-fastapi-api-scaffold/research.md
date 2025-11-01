# Research: FastAPI API Scaffold

**Date**: November 1, 2025  
**Feature**: 006-fastapi-api-scaffold  
**Phase**: 0 - Research & Technical Decisions

## Overview

This document captures research findings, technology decisions, and best practices for implementing the FastAPI API scaffold within the Riso template system. All technical decisions are made to align with Riso's constitution principles (minimal baseline, deterministic generation, template sovereignty).

## Technology Decisions

### 1. FastAPI Framework

**Decision**: Use FastAPI 0.104+ as the ASGI web framework

**Rationale**:

- Native async/await support for high-performance concurrent request handling
- Automatic OpenAPI (Swagger) and JSON Schema generation from Python type hints
- Built-in request/response validation via Pydantic models
- Extensive ecosystem (Uvicorn for ASGI serving, Starlette for routing)
- Excellent documentation and active community
- Production-ready and widely adopted (Uber, Netflix, Microsoft)

**Alternatives Considered**:

- **Flask**: Synchronous by default, requires extensions for async, no built-in OpenAPI generation
- **Django REST Framework**: Heavy framework with ORM coupling, violates minimal baseline principle
- **Starlette**: Lower-level than FastAPI, requires manual OpenAPI generation
- **Litestar**: Newer framework with less ecosystem maturity

**Integration with Riso**:

- FastAPI dependencies only added when `api_tracks` includes `python`
- No conflicts with existing Python 3.11+ baseline
- Compatible with uv dependency management

### 2. ASGI Server

**Decision**: Use Uvicorn 0.24+ with standard workers for development, gunicorn+uvicorn workers for production

**Rationale**:

- Industry-standard ASGI server for FastAPI applications
- Excellent development experience with auto-reload
- Production-grade performance with worker process management
- Simple CLI interface: `uvicorn app.main:app --reload`
- Native HTTP/1.1 and WebSocket support

**Alternatives Considered**:

- **Hypercorn**: Less mature, smaller ecosystem
- **Daphne**: Django-focused, heavier dependencies

**Development Command**: `uv run uvicorn {package_name}.api.main:app --reload --host 0.0.0.0 --port 8000`

**Production Recommendation**: Document gunicorn+uvicorn workers pattern in deployment guide

### 3. Request/Response Validation

**Decision**: Use Pydantic 2.x for all request/response model definitions

**Rationale**:

- Native integration with FastAPI (FastAPI built on Pydantic)
- Automatic JSON schema generation for OpenAPI docs
- Rich validation with helpful error messages
- Type-safe with full mypy support
- Performance optimized in v2 (Rust core)

**Best Practices**:

- Define request models in `models/requests.py`
- Define response models in `models/responses.py`
- Use Pydantic's `Field()` for additional validation and documentation
- Leverage `ConfigDict` for model behavior customization

**Example Pattern**:

```python
from pydantic import BaseModel, Field

class ExampleCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Example name")
    value: int = Field(..., ge=0, description="Non-negative integer value")

class ExampleResponse(BaseModel):
    id: str
    name: str
    value: int
    created_at: str
```

### 4. Configuration Management

**Decision**: Use Pydantic Settings with environment variable support

**Rationale**:

- Type-safe configuration with validation
- Automatic loading from `.env` files via python-dotenv
- Environment-specific overrides (dev/staging/prod)
- No additional dependencies (Pydantic already required)

**Best Practices**:

- Define settings in `config.py` with `BaseSettings`
- Use `model_config = SettingsConfigDict(env_file=".env")` for automatic loading
- Provide sensible defaults for development
- Document required vs optional environment variables

**Example Pattern**:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # CORS configuration
    cors_origins: list[str] = ["http://localhost:3000"]
    
    # Application metadata
    app_name: str = "FastAPI Application"
    version: str = "0.1.0"
```

### 5. Routing Architecture

**Decision**: Use modular route organization with APIRouter

**Rationale**:

- Logical grouping of related endpoints (health, examples, future domains)
- Independent development and testing of route modules
- Clean separation of concerns
- Easy to add new route files without modifying main app

**Best Practices**:

- One router per logical domain (e.g., `routes/health.py`, `routes/users.py`)
- Register routers in `main.py` with appropriate prefix and tags
- Use consistent naming: `router = APIRouter(prefix="/prefix", tags=["Tag"])`
- Keep route handlers thin, delegate to service layer for business logic

**Example Pattern**:

```python
# routes/health.py
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

# main.py
from routes import health

app = FastAPI()
app.include_router(health.router)
```

### 6. Error Handling

**Decision**: Use FastAPI's exception handlers with custom error response models

**Rationale**:

- Consistent error response format across all endpoints
- Proper HTTP status codes for different error types
- Detailed error messages for debugging in development
- Sanitized messages for production
- Automatic OpenAPI documentation of error responses

**Best Practices**:

- Define `ErrorResponse` model in `models/responses.py`
- Register global exception handlers in `middleware/errors.py`
- Handle `RequestValidationError` for 422 responses
- Handle `HTTPException` for explicit error raising
- Log errors with appropriate severity levels

**Example Pattern**:

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 7. CORS Configuration

**Decision**: Use FastAPI's built-in CORSMiddleware with configurable origins

**Rationale**:

- Simple middleware integration
- Environment-specific configuration (allow all in dev, restricted in prod)
- Supports preflight requests automatically
- No additional dependencies

**Best Practices**:

- Configure CORS in `middleware/cors.py`
- Load allowed origins from environment variables
- Use restrictive defaults for production
- Document CORS configuration in deployment guide

**Example Pattern**:

```python
from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app: FastAPI, settings: Settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### 8. Testing Strategy

**Decision**: Use pytest with FastAPI's TestClient for endpoint testing

**Rationale**:

- Aligns with existing Riso quality suite (pytest already baseline)
- TestClient simulates real HTTP requests without running server
- Supports async tests with pytest-asyncio
- Excellent fixture support for test data and mocking
- Coverage integration for quality metrics (≥80% requirement)

**Best Practices**:

- Define TestClient fixture in `tests/conftest.py`
- One test file per route module
- Test happy paths and error cases
- Use parametrized tests for multiple scenarios
- Mock external dependencies (if any added later)

**Example Pattern**:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from {package_name}.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

# tests/test_health.py
def test_health_check(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 9. OpenAPI Documentation

**Decision**: Use FastAPI's automatic OpenAPI generation with customization

**Rationale**:

- Zero-effort documentation from type hints and docstrings
- Interactive Swagger UI at `/docs`
- Alternative ReDoc UI at `/redoc`
- Downloadable OpenAPI spec at `/openapi.json`
- Supports custom schemas and examples

**Best Practices**:

- Add docstrings to route handlers for operation descriptions
- Use Pydantic `Field()` descriptions for parameter documentation
- Provide example values in model definitions
- Customize OpenAPI metadata in FastAPI constructor
- Version API endpoints appropriately

**Example Pattern**:

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API for managing examples",
    version="0.1.0",
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Examples", "description": "Example CRUD operations"},
    ]
)

@app.post("/examples/", response_model=ExampleResponse, tags=["Examples"])
async def create_example(request: ExampleCreateRequest):
    """
    Create a new example.
    
    - **name**: The name of the example (1-100 characters)
    - **value**: A non-negative integer value
    """
    # Implementation
```

### 10. Health Check Endpoints

**Decision**: Implement three health check endpoints following industry standards

**Rationale**:

- `/health/` - Overall health status
- `/health/ready` - Readiness probe for Kubernetes/orchestrators
- `/health/live` - Liveness probe for container health
- Enables proper monitoring and orchestration
- Simple implementation, no external dependencies

**Best Practices**:

- Return 200 for healthy, 503 for unhealthy
- Include version and timestamp in response
- Keep health checks lightweight (<100ms)
- Consider adding dependency checks (DB, cache) in readiness

**Example Pattern**:

```python
from datetime import datetime

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/ready")
async def readiness_check():
    # Check dependencies if any
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    # Basic liveness check
    return {"status": "alive"}
```

## Integration with Riso Template System

### Copier Template Integration

**Approach**: Conditional generation based on `api_tracks` prompt

**Implementation**:

```yaml
# copier.yml
api_tracks:
  type: str
  default: ""
  help: "API framework selection (comma-separated): python, node"
  choices:
    - ""
    - python
    - node
    - python,node
```

**Template Guards**:

```jinja
{%- if 'python' in api_tracks.split(',') %}
# Generate FastAPI scaffold
{%- endif %}
```

### Dependency Management

**pyproject.toml additions** (conditional):

```toml
[project.optional-dependencies]
api = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
api-dev = [
    "httpx>=0.25.0",  # For TestClient
    "pytest-asyncio>=0.21.0",
]
```

### Quality Suite Integration

**No changes required** - FastAPI code will be validated by existing tools:

- **ruff**: Linting (already configured)
- **mypy**: Type checking (FastAPI is fully typed)
- **pylint**: Static analysis (existing config)
- **pytest**: Testing (TestClient integrates seamlessly)

### Container Integration

**Dockerfile additions** (conditional, if containerization enabled):

```dockerfile
# Install API dependencies
RUN uv sync --no-dev --extra api

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run API server
CMD ["uv", "run", "uvicorn", "{package_name}.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance Considerations

### Startup Time

**Target**: <3 seconds in development mode

**Optimizations**:

- Lazy import of large dependencies
- Avoid synchronous I/O during startup
- Minimal middleware stack
- No database connections in scaffold (opt-in)

### Response Time

**Target**: <100ms for health check, <500ms for typical CRUD operations

**Optimizations**:

- Use async route handlers for I/O-bound operations
- Keep route handlers thin (delegate to services)
- Use Pydantic v2 for fast validation
- Profile with FastAPI's built-in metrics

### Concurrent Requests

**Target**: Handle 100 concurrent requests in local development

**Approach**:

- Use async/await throughout
- Uvicorn's default worker configuration sufficient for development
- Document production deployment with multiple workers
- No blocking I/O in request handlers

## Documentation Strategy

### Module Documentation

**Location**: `docs/modules/api-fastapi.md.jinja`

**Contents**:

- Quick start guide
- Project structure explanation
- Adding new endpoints tutorial
- Configuration reference
- Testing guide
- Deployment patterns
- Troubleshooting section

### Context Documentation

**Location**: `.github/context/fastapi-patterns.md`

**Contents**:

- Extension patterns (adding auth, databases, caching)
- Middleware patterns
- Dependency injection patterns
- Background tasks
- WebSocket support
- Performance optimization

### In-Project Documentation

**Location**: Generated `README.md` sections

**Contents**:

- Running the API server
- Accessing documentation
- Running tests
- Environment configuration

## Migration Path (Future)

This scaffold provides a foundation for future enhancements:

- **Authentication**: JWT/OAuth2 middleware (opt-in module)
- **Database**: SQLAlchemy/Tortoise ORM integration (opt-in module)
- **Caching**: Redis integration (opt-in module)
- **Background Tasks**: Celery/ARQ integration (opt-in module)
- **GraphQL**: Strawberry GraphQL alternative (separate module)
- **WebSockets**: Real-time communication support

**Principle**: All enhancements remain opt-in, maintaining minimal baseline

## Success Metrics Validation

Research findings support all success criteria from spec:

- **SC-001**: Render in <2 min ✓ - Simple template generation, no complex build steps
- **SC-002**: Pass quality checks ✓ - FastAPI fully typed, linting-friendly
- **SC-003**: Auto documentation ✓ - FastAPI built-in OpenAPI generation
- **SC-004**: Add endpoint <5 min ✓ - Copy route template, register router
- **SC-005**: Startup <3s ✓ - Minimal dependencies, no database connections
- **SC-006**: Example endpoints work ✓ - Simple CRUD demonstrations included
- **SC-007**: Health check <100ms ✓ - In-memory status check, no I/O
- **SC-008**: ≥80% coverage ✓ - TestClient enables comprehensive testing
- **SC-009**: 100 concurrent requests ✓ - Async/await architecture supports this

## Research Conclusion

All technical decisions documented, no clarifications remaining. The FastAPI scaffold design:

- Aligns with Riso constitutional principles
- Uses industry-standard tools and patterns
- Maintains minimal baseline through opt-in architecture
- Supports all functional requirements from specification
- Achieves all success criteria

### Next Phase

Ready to proceed to Phase 1: Design & Contracts
