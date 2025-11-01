# FastAPI Patterns and Best Practices

This document provides advanced patterns and best practices for extending the FastAPI scaffold beyond the baseline implementation.

## Table of Contents

- [Configuration Patterns](#configuration-patterns)
- [Authentication & Authorization](#authentication--authorization)
- [Database Integration](#database-integration)
- [Background Tasks](#background-tasks)
- [WebSockets](#websockets)
- [Caching](#caching)
- [Rate Limiting](#rate-limiting)
- [API Versioning](#api-versioning)
- [Testing Patterns](#testing-patterns)
- [Deployment & Operations](#deployment--operations)

## Configuration Patterns

### Environment-Specific Configuration

Organize configuration by environment:

```python
from typing import Literal
from pydantic_settings import BaseSettings

class ApiConfig(BaseSettings):
    environment: Literal["development", "staging", "production"]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def debug_mode(self) -> bool:
        return self.environment == "development"
```

### Feature Flags

Implement feature flags for gradual rollouts:

```python
class ApiConfig(BaseSettings):
    feature_new_endpoint: bool = Field(default=False)
    feature_enhanced_logging: bool = Field(default=True)

# In route modules:
@router.get("/new-feature/")
async def new_feature():
    if not get_config().feature_new_endpoint:
        raise HTTPException(status_code=404, detail="Feature not enabled")
    return {"message": "New feature"}
```

### Secrets Management

Use dedicated secret managers in production:

```python
import boto3
from functools import lru_cache

@lru_cache
def get_secret(secret_name: str) -> str:
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]

class ApiConfig(BaseSettings):
    database_password: str = Field(default="")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.is_production:
            self.database_password = get_secret("db_password")
```

## Authentication & Authorization

### JWT Authentication

Implement JWT-based authentication:

```python
from datetime import datetime, timedelta
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """Generate JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """Verify JWT and extract user information."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Use in routes:
@router.get("/protected/")
async def protected_route(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"message": f"Hello {current_user['username']}"}
```

### Role-Based Access Control

Implement permission checks:

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

def require_role(required_role: Role):
    """Dependency for role-based access control."""
    async def role_checker(current_user: Annotated[dict, Depends(get_current_user)]):
        user_role = current_user.get("role")
        if user_role != required_role and user_role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Use in routes:
@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: Annotated[dict, Depends(require_role(Role.ADMIN))],
):
    return {"message": f"User {user_id} deleted by {admin['username']}"}
```

### API Key Authentication

For service-to-service communication:

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: Annotated[str, Depends(api_key_header)]) -> str:
    """Verify API key."""
    valid_keys = get_config().api_keys  # Load from secure storage
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@router.post("/webhook/")
async def webhook(api_key: Annotated[str, Depends(verify_api_key)]):
    return {"message": "Webhook received"}
```

## Database Integration

### SQLAlchemy with Async

Integrate SQLAlchemy for database operations:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# In config.py:
class ApiConfig(BaseSettings):
    database_url: str = Field(default="postgresql+asyncpg://user:pass@localhost/db")

# Database setup:
engine = create_async_engine(get_config().database_url)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    """Database session dependency."""
    async with async_session_maker() as session:
        yield session

# Use in routes:
@router.get("/users/")
async def list_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

### Connection Pooling

Configure connection pool parameters:

```python
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
)
```

### Database Migrations

Use Alembic for schema migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head
```

## Background Tasks

### FastAPI Background Tasks

For lightweight background processing:

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    """Background task to send email."""
    # Send email logic
    print(f"Sending email to {email}: {message}")

@router.post("/users/")
async def create_user(user: User, background_tasks: BackgroundTasks):
    # Create user
    background_tasks.add_task(send_email, user.email, "Welcome!")
    return {"message": "User created"}
```

### Task Queue (Celery)

For heavy background processing:

```python
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

@celery_app.task
def process_data(data: dict):
    """Heavy processing task."""
    # Long-running computation
    return {"result": "processed"}

# In route:
@router.post("/process/")
async def trigger_processing(data: dict):
    task = process_data.delay(data)
    return {"task_id": task.id}
```

## WebSockets

### Real-Time Communication

Implement WebSocket endpoints:

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Caching

### Response Caching

Cache expensive responses:

```python
from functools import lru_cache
from fastapi import Response
import redis.asyncio as redis

# In-memory cache:
@lru_cache(maxsize=128)
def get_expensive_data(key: str) -> dict:
    # Expensive computation
    return {"data": "cached"}

# Redis cache:
redis_client = redis.from_url("redis://localhost:6379")

@router.get("/cached-data/")
async def get_cached_data(response: Response):
    cached = await redis_client.get("cached_key")
    if cached:
        response.headers["X-Cache"] = "HIT"
        return {"data": cached}
    
    # Compute and cache
    data = compute_expensive_data()
    await redis_client.setex("cached_key", 300, data)
    response.headers["X-Cache"] = "MISS"
    return {"data": data}
```

## Rate Limiting

### Request Rate Limiting

Implement rate limiting middleware:

```python
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.get("/limited/")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "Rate limited endpoint"}
```

### Per-User Rate Limiting

```python
def get_user_id(request: Request) -> str:
    """Extract user ID from token for rate limiting."""
    token = request.headers.get("Authorization")
    # Decode token and get user ID
    return user_id

limiter = Limiter(key_func=get_user_id)

@router.post("/api/action/")
@limiter.limit("100/hour")
async def user_action(request: Request):
    return {"message": "Action performed"}
```

## API Versioning

### URL Path Versioning

Organize routes by version:

```python
# v1/users.py
router_v1 = APIRouter(prefix="/v1/users", tags=["Users V1"])

@router_v1.get("/")
async def list_users_v1():
    return {"version": "v1", "users": []}

# v2/users.py
router_v2 = APIRouter(prefix="/v2/users", tags=["Users V2"])

@router_v2.get("/")
async def list_users_v2():
    return {"version": "v2", "users": [], "enhanced": True}

# main.py
app.include_router(router_v1)
app.include_router(router_v2)
```

### Header-Based Versioning

```python
from fastapi import Header

@router.get("/users/")
async def list_users(api_version: str = Header(default="v1", alias="X-API-Version")):
    if api_version == "v2":
        return {"version": "v2", "enhanced": True}
    return {"version": "v1"}
```

## Testing Patterns

### Fixture Organization

Organize test fixtures efficiently:

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers():
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_db():
    # Setup test database
    yield mock_db
    # Teardown
```

### Parametrized Tests

Test multiple scenarios:

```python
@pytest.mark.parametrize("status_code,expected", [
    (200, "healthy"),
    (503, "unhealthy"),
])
def test_health_status(client, status_code, expected):
    # Test logic
    pass
```

### Async Testing

Test async endpoints:

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    response = await async_client.get("/async-endpoint/")
    assert response.status_code == 200
```

## Deployment & Operations

### Graceful Shutdown

Handle shutdown signals properly:

```python
import signal

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    print("Shutting down gracefully...")
    # Close database connections
    # Finish in-flight requests
    # Clean up resources

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
```

### Health Check Best Practices

Comprehensive health checks:

```python
@router.get("/health/")
async def health_check():
    checks = {}
    
    # Database check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "pass"
    except Exception:
        checks["database"] = "fail"
    
    # Redis check
    try:
        await redis_client.ping()
        checks["redis"] = "pass"
    except Exception:
        checks["redis"] = "fail"
    
    # External API check
    try:
        response = await httpx.get("https://api.example.com/health")
        checks["external_api"] = "pass" if response.status_code == 200 else "fail"
    except Exception:
        checks["external_api"] = "fail"
    
    overall_status = "healthy" if all(v == "pass" for v in checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "checks": checks,
        "version": get_config().version,
        "timestamp": datetime.utcnow().isoformat(),
    }
```

### Metrics and Monitoring

Export Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter("api_requests_total", "Total requests")
request_duration = Histogram("api_request_duration_seconds", "Request duration")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Structured Logging

Implement structured logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("api")
logger.addHandler(handler)
```

## Security Best Practices

1. **Input Validation**: Always validate and sanitize user input
2. **SQL Injection**: Use parameterized queries with SQLAlchemy
3. **CORS**: Configure specific origins, avoid wildcards in production
4. **Rate Limiting**: Implement rate limits to prevent abuse
5. **Authentication**: Use strong authentication mechanisms (JWT, OAuth2)
6. **HTTPS Only**: Enforce HTTPS in production
7. **Security Headers**: Set appropriate security headers
8. **Secrets Management**: Never commit secrets, use environment variables or secret managers
9. **Dependency Updates**: Keep dependencies up to date
10. **Error Messages**: Don't leak sensitive information in error messages

## Performance Optimization

1. **Connection Pooling**: Use connection pools for databases and external services
2. **Async Operations**: Use async/await for I/O-bound operations
3. **Caching**: Cache expensive computations and database queries
4. **Database Indexes**: Create appropriate database indexes
5. **Query Optimization**: Optimize database queries (N+1 problem, select fields)
6. **Response Pagination**: Paginate large result sets
7. **Compression**: Enable response compression
8. **CDN**: Serve static assets from CDN
9. **Monitoring**: Monitor response times and optimize slow endpoints
10. **Load Testing**: Regular load testing to identify bottlenecks
