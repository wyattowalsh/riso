# Data Model: FastAPI API Scaffold

**Date**: November 1, 2025  
**Feature**: 006-fastapi-api-scaffold  
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data entities and validation rules for the FastAPI API scaffold. Since this is a scaffold/template feature, the data model focuses on the *structure* of how data is modeled in generated projects, not domain-specific entities.

## Core Entities

### 1. Configuration (Settings)

**Purpose**: Application-wide configuration loaded from environment variables

**Attributes**:

| Field | Type | Validation | Default | Description |
|-------|------|------------|---------|-------------|
| `host` | `str` | Valid IPv4 or hostname | `"0.0.0.0"` | Server bind address |
| `port` | `int` | Range: 1024-65535 | `8000` | Server port |
| `reload` | `bool` | Boolean | `True` | Enable auto-reload (dev only) |
| `cors_origins` | `list[str]` | Valid URLs | `["http://localhost:3000"]` | Allowed CORS origins |
| `app_name` | `str` | 1-100 characters | `"FastAPI Application"` | Application name |
| `version` | `str` | Semantic version | `"0.1.0"` | Application version |
| `log_level` | `str` | Enum: DEBUG, INFO, WARNING, ERROR | `"INFO"` | Logging level |
| `environment` | `str` | Enum: development, staging, production | `"development"` | Deployment environment |

**Relationships**: None (singleton configuration)

**State Transitions**: Immutable after initialization (loaded once at startup)

**Validation Rules**:

- Port must be available (not already bound)
- CORS origins must be valid URLs
- Version must follow semver format
- Environment-specific validation (e.g., reload=False in production)

**Implementation Note**: Uses Pydantic `BaseSettings` for automatic environment variable loading

### 2. Health Check Response

**Purpose**: Standard response format for health check endpoints

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| `status` | `str` | Enum: healthy, unhealthy, degraded | Yes | Overall health status |
| `version` | `str` | Semantic version | Yes | Application version |
| `timestamp` | `str` | ISO 8601 datetime | Yes | Response timestamp |
| `checks` | `dict[str, str]` | Map of check name to status | No | Individual health checks |

**Relationships**: None

**State Transitions**: N/A (computed on each request)

**Validation Rules**:

- Status must be one of predefined values
- Timestamp must be valid ISO 8601 format
- Checks dictionary values must be "pass" or "fail"

### 3. Error Response

**Purpose**: Standard error response format for all API errors

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| `detail` | `str` or `list[dict]` | Non-empty | Yes | Error message or validation errors |
| `status_code` | `int` | HTTP status code | No | Error status code (for logging) |
| `request_id` | `str` | UUID format | No | Request identifier for tracing |

**Relationships**: None

**State Transitions**: N/A (created on error)

**Validation Rules**:

- Detail must not be empty
- Status code must be valid HTTP error code (400-599)
- Request ID must be valid UUID if provided

### 4. Example Request (Scaffold Demo)

**Purpose**: Example request model demonstrating validation patterns

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| `name` | `str` | 1-100 characters | Yes | Example name |
| `value` | `int` | Non-negative | Yes | Example integer value |
| `description` | `str` | Max 500 characters | No | Optional description |
| `tags` | `list[str]` | Max 10 tags, each 1-50 chars | No | Optional tags |

**Relationships**: None (scaffold example)

**State Transitions**: N/A

**Validation Rules**:

- Name must not be empty or whitespace-only
- Value must be >= 0
- Description cannot exceed 500 characters
- Each tag must be between 1-50 characters
- Maximum 10 tags allowed

### 5. Example Response (Scaffold Demo)

**Purpose**: Example response model demonstrating response structure

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| `id` | `str` | UUID format | Yes | Example identifier |
| `name` | `str` | 1-100 characters | Yes | Example name |
| `value` | `int` | Non-negative | Yes | Example integer value |
| `description` | `str` | Max 500 characters | No | Optional description |
| `tags` | `list[str]` | List of strings | No | Optional tags |
| `created_at` | `str` | ISO 8601 datetime | Yes | Creation timestamp |
| `updated_at` | `str` | ISO 8601 datetime | Yes | Last update timestamp |

**Relationships**: None (scaffold example)

**State Transitions**: Created → Updated (via PUT/PATCH)

**Validation Rules**:

- ID must be valid UUID
- Timestamps must be valid ISO 8601 format
- All request validation rules apply to corresponding fields

## Additional Entities

### 6. Metrics Response

**Purpose**: Prometheus-compatible metrics for monitoring

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| metrics | `str` | Prometheus text format | Yes | Metrics in Prometheus exposition format |

**Relationships**: None (computed on demand)

**State Transitions**: N/A (real-time metrics)

**Validation Rules**:

- Must follow Prometheus text exposition format
- Metric names must follow naming conventions
- Labels must be valid key-value pairs

### 7. Middleware Context

**Purpose**: Request context passed through middleware chain

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| request_id | `str` | UUID format | Yes | Unique request identifier |
| start_time | `float` | Unix timestamp | Yes | Request start time |
| user_agent | `str` | Non-empty | No | Client user agent |
| ip_address | `str` | Valid IP | No | Client IP address |

**Relationships**: Attached to each request

**State Transitions**: Created → Enriched → Completed

**Validation Rules**:

- Request ID must be unique per request
- Start time must be in the past
- IP address must be valid IPv4 or IPv6

### 8. Circuit Breaker State

**Purpose**: Track external dependency health and circuit breaker status

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| service_name | `str` | 1-100 characters | Yes | External service identifier |
| state | `str` | Enum: open, closed, half_open | Yes | Circuit breaker state |
| failure_count | `int` | Non-negative | Yes | Consecutive failures |
| last_failure_time | `str` | ISO 8601 datetime | No | Last failure timestamp |
| next_attempt_time | `str` | ISO 8601 datetime | No | When to retry (if open) |

**Relationships**: One per external dependency

**State Transitions**: Closed → Open → Half-Open → Closed (or back to Open)

**Validation Rules**:

- State must be valid enum value
- Failure count resets when state changes to closed
- Next attempt time required when state is open

### 9. Security Headers

**Purpose**: Standard security headers included in responses

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| x_content_type_options | `str` | Fixed: "nosniff" | Yes | Prevent MIME sniffing |
| x_frame_options | `str` | Enum: DENY, SAMEORIGIN | Yes | Clickjacking protection |
| content_security_policy | `str` | Valid CSP | No | Content Security Policy |
| strict_transport_security | `str` | Valid HSTS | No | Force HTTPS |

**Relationships**: None (applied to all responses)

**State Transitions**: N/A (static configuration)

**Validation Rules**:

- CSP must be valid policy syntax
- HSTS must include max-age directive

### 10. Log Entry

**Purpose**: Structured log entry format

**Attributes**:

| Field | Type | Validation | Required | Description |
|-------|------|------------|----------|-------------|
| timestamp | `str` | ISO 8601 datetime | Yes | Log entry timestamp |
| level | `str` | Enum: DEBUG, INFO, WARNING, ERROR, CRITICAL | Yes | Log level |
| message | `str` | Non-empty | Yes | Log message |
| request_id | `str` | UUID format | No | Associated request ID |
| logger_name | `str` | Non-empty | Yes | Logger name |
| extra | `dict` | Valid JSON | No | Additional context |

**Relationships**: Associated with request via request_id

**State Transitions**: N/A (immutable once created)

**Validation Rules**:

## Request/Response Patterns

### Common Patterns

All request/response models follow these patterns:

1. **Request Models** (`models/requests.py`):
   - Use Pydantic `BaseModel`
   - Define validation with `Field()`
   - Include docstrings for OpenAPI documentation
   - Use descriptive field names
   - Validate at model level (not in route handlers)

2. **Response Models** (`models/responses.py`):
   - Use Pydantic `BaseModel`
   - Include all fields that will be returned
   - Document field meanings
   - Use consistent field naming across endpoints
   - Include metadata (timestamps, IDs)

3. **Error Models**:
   - Consistent error response structure
   - Include actionable error messages
   - Provide validation details for 422 errors
   - Include request context when helpful

### Validation Strategy

**Field-Level Validation**:

```python
from pydantic import BaseModel, Field, field_validator

class ExampleCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Example name")
    value: int = Field(..., ge=0, description="Non-negative integer")
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be whitespace only')
        return v.strip()
```

**Model-Level Validation**:

```python
from pydantic import BaseModel, model_validator

class ExampleUpdateRequest(BaseModel):
    name: str | None = None
    value: int | None = None
    
    @model_validator(mode='after')
    def at_least_one_field(self):
        if self.name is None and self.value is None:
            raise ValueError('At least one field must be provided')
        return self
```

## Entity Relationships

Since this is a scaffold without domain logic, relationships are minimal:

```text
Configuration (1)
    ↓ (used by)
Application (1)
    ↓ (generates)
Health Check Response (*)
    
Application (1)
    ↓ (handles)
HTTP Requests (*)
    ↓ (validates to)
Request Models (*)
    ↓ (processes to)
Response Models (*)

Application (1)
    ↓ (catches)
Exceptions (*)
    ↓ (formats to)
Error Response (*)
```

**Key Points**:

- Configuration is loaded once at startup
- Each HTTP request creates new request/response model instances
- Error responses are created on exception
- No persistent state or database relationships in scaffold

## Extensibility

The scaffold provides patterns for extending the data model:

### Adding Domain Entities

Users can add new entities by creating models following the example pattern:

```python
# models/requests.py
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

# models/responses.py
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: str
```

### Adding Relationships

Future enhancements can add relationships through:

- Foreign key references (when database added)
- Nested models (for complex objects)
- List fields (for one-to-many relationships)

**Important**: All extensions remain opt-in, maintaining minimal baseline principle

## Validation Testing

All validation rules must be tested:

```python
# tests/test_models.py
def test_example_request_validation():
    # Valid request
    valid = ExampleCreateRequest(name="Test", value=42)
    assert valid.name == "Test"
    
    # Invalid: empty name
    with pytest.raises(ValidationError):
        ExampleCreateRequest(name="", value=42)
    
    # Invalid: negative value
    with pytest.raises(ValidationError):
        ExampleCreateRequest(name="Test", value=-1)
```

## OpenAPI Schema Generation

All models automatically generate OpenAPI schemas:

```json
{
  "ExampleCreateRequest": {
    "type": "object",
    "required": ["name", "value"],
    "properties": {
      "name": {
        "type": "string",
        "minLength": 1,
        "maxLength": 100,
        "description": "Example name"
      },
      "value": {
        "type": "integer",
        "minimum": 0,
        "description": "Non-negative integer"
      }
    }
  }
}
```

This schema is used for:

- Interactive API documentation (Swagger UI)
- Request validation
- Client SDK generation
- Contract testing

## Summary

The data model for the FastAPI scaffold:

- Defines structure, not domain logic
- Uses Pydantic for validation and documentation
- Provides extensible patterns for users
- Maintains minimal baseline (no database models)
- Supports all functional requirements from specification
- Enables automatic OpenAPI generation

**Next**: Create API contracts in `contracts/` directory
