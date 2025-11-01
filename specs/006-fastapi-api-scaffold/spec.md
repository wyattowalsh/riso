# Feature Specification: FastAPI API Scaffold

**Feature Branch**: `006-fastapi-api-scaffold`  
**Created**: November 1, 2025  
**Status**: Draft  
**Input**: User description: "Create FastAPI API scaffold with project structure, routing, and configuration"

## Scope & Boundaries

### In Scope

- **Core FastAPI Scaffold**: Project structure, routing, configuration, health checks
- **Development Experience**: Auto-reload, interactive documentation, example endpoints
- **Production Readiness**: Containerization, logging, monitoring, error handling
- **Quality Integration**: Ruff, mypy, pylint, pytest integration
- **Extensibility**: Middleware hooks, configuration extension, modular routing
- **Observability**: Structured logging, health checks, metrics endpoint
- **Security Basics**: CORS, input validation, request size limits, security headers
- **Deployment**: Docker support, Kubernetes-compatible health checks

### Out of Scope (Future Enhancements)

- **Authentication/Authorization**: OAuth2, JWT, API keys (extension points provided)
- **Database Integration**: ORM, migrations, connection pooling (templates available separately)
- **Advanced Security**: Rate limiting implementation, WAF, DDoS protection (configuration provided)
- **WebSocket Support**: Real-time bidirectional communication (optional module)
- **GraphQL**: Alternative API paradigm (separate scaffold)
- **Message Queues**: Async task processing, pub/sub (extension points available)
- **Caching**: Redis, Memcached integration (configuration examples only)
- **Advanced Monitoring**: APM, distributed tracing backends (headers/IDs provided)
- **Multi-tenancy**: Tenant isolation, per-tenant configuration
- **API Gateway**: Rate limiting, authentication, request transformation (deploy behind gateway)

### Assumptions

- **Development Environment**: Python 3.11+, uv package manager, Docker available
- **Deployment Target**: Container orchestration platform (Kubernetes, Docker Swarm, ECS)
- **Network**: HTTP/HTTPS traffic, standard ports (80, 443, 8000)
- **Scale**: Small to medium APIs (dozens to hundreds of endpoints, <10k requests/second)
- **Team Size**: 1-10 developers working on API codebase
- **External Dependencies**: Minimal (only FastAPI ecosystem for baseline)
- **Riso Integration**: Compatible with existing Riso template structure and quality tools
- **Platform**: Cross-platform (Linux, macOS, Windows) but optimized for Linux containers

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initialize New API Project (Priority: P1)

Template users can render a new project that includes a functional FastAPI application with a standardized directory structure, ready to serve HTTP endpoints.

**Why this priority**: This is the foundation of the feature - without a working API scaffold, none of the other capabilities matter. This delivers immediate value by providing a runnable API server out of the box.

**Independent Test**: Can be fully tested by rendering a project with FastAPI enabled, running the server, and making an HTTP request to a health check endpoint that returns a successful response.

**Acceptance Scenarios**:

1. **Given** a template user wants to create a new project with API capabilities, **When** they render the template with FastAPI selected, **Then** the generated project contains a complete API directory structure with a main application file
2. **Given** a newly rendered FastAPI project, **When** the user starts the development server, **Then** the server starts successfully on a configured port and can accept HTTP requests
3. **Given** a running FastAPI application, **When** a user makes a request to the health check endpoint, **Then** the response returns a 200 status code with application status information

---

### User Story 2 - Add New API Endpoints (Priority: P2)

Developers can add new API endpoints by creating route modules that automatically integrate with the application's routing system.

**Why this priority**: This enables the core workflow of API development - adding new endpoints. Without this, developers would have a static scaffold with no clear path to extension.

**Independent Test**: Can be tested by adding a new route file in the designated routes directory, importing it in the router configuration, and verifying the new endpoint is accessible via HTTP request.

**Acceptance Scenarios**:

1. **Given** an existing FastAPI application, **When** a developer adds a new route module following the project conventions, **Then** the new endpoints are automatically discovered and registered with the router
2. **Given** a newly added route module, **When** the application restarts, **Then** the new endpoints are accessible at their expected paths
3. **Given** multiple route modules, **When** the application starts, **Then** all routes are organized logically and accessible through the API documentation

---

### User Story 3 - Configure Application Settings (Priority: P3)

Operators can customize application behavior through environment-based configuration without modifying code.

**Why this priority**: This supports deployment flexibility and operational best practices, but is not essential for initial development and testing.

**Independent Test**: Can be tested by modifying environment variables or configuration files and verifying that the application behavior changes accordingly (e.g., changing port, logging level, or feature flags).

**Acceptance Scenarios**:

1. **Given** a FastAPI application, **When** an operator sets environment variables for application settings, **Then** the application uses those values at runtime
2. **Given** different deployment environments (development, staging, production), **When** environment-specific configuration is provided, **Then** the application adapts its behavior appropriately
3. **Given** configuration errors or missing required values, **When** the application starts, **Then** it provides clear error messages indicating what needs to be corrected

---

### User Story 4 - Access API Documentation (Priority: P2)

Developers and API consumers can view interactive API documentation that is automatically generated from the code.

**Why this priority**: Documentation is crucial for API usability and adoption, making it high priority though not as critical as the basic functionality.

**Independent Test**: Can be tested by navigating to the documentation URL (e.g., /docs or /redoc) and verifying that all endpoints are listed with their parameters, request/response schemas, and the ability to test endpoints interactively.

**Acceptance Scenarios**:

1. **Given** a running FastAPI application, **When** a user navigates to the documentation endpoint, **Then** they see a complete list of all available endpoints with descriptions
2. **Given** the interactive documentation interface, **When** a user fills in request parameters and submits a test request, **Then** they receive a real response from the API
3. **Given** route modules with type hints and docstrings, **When** the documentation is generated, **Then** it accurately reflects the API contract including request/response schemas

---

### User Story 5 - Extend API with Custom Middleware (Priority: P3)

Developers can add custom middleware to extend application behavior (authentication, logging, rate limiting) without modifying core scaffold code.

**Why this priority**: Extensibility is essential for real-world applications but can be addressed after core functionality is stable.

**Independent Test**: Can be tested by creating a custom middleware file, registering it with the FastAPI app, and verifying that it intercepts and modifies requests/responses appropriately.

**Acceptance Scenarios**:

1. **Given** an existing FastAPI application, **When** a developer adds custom middleware following the extension pattern, **Then** the middleware is executed for all matching requests
2. **Given** multiple middleware components, **When** the application starts, **Then** middleware executes in the correct order (LIFO for request, FIFO for response)
3. **Given** a middleware error, **When** an exception occurs during middleware execution, **Then** the error is properly handled and logged without crashing the application

---

### User Story 6 - Monitor Application Health and Performance (Priority: P2)

Operations teams can monitor application health, performance metrics, and logs for troubleshooting and capacity planning.

**Why this priority**: Observability is critical for production deployments, enabling proactive issue detection and resolution.

**Independent Test**: Can be tested by accessing health check endpoints, metrics endpoint, and structured logs, verifying that all monitoring data is accurate and complete.

**Acceptance Scenarios**:

1. **Given** a running FastAPI application, **When** an operator queries health check endpoints, **Then** the response accurately reflects application and dependency status
2. **Given** application under load, **When** an operator accesses the metrics endpoint, **Then** Prometheus-compatible metrics are exposed (request rate, latency, errors)
3. **Given** application processing requests, **When** an operator reviews structured logs, **Then** all log entries include correlation IDs, timestamps, and relevant context for debugging

---

### User Story 7 - Deploy API in Containerized Environment (Priority: P2)

DevOps engineers can build and deploy the API as a container with proper health checks, security hardening, and orchestration compatibility.

**Why this priority**: Containerization is the standard deployment model for modern APIs, essential for scalability and consistency.

**Independent Test**: Can be tested by building a Docker image, running it in a container, and verifying health checks, resource limits, and orchestration compatibility (Kubernetes).

**Acceptance Scenarios**:

1. **Given** a FastAPI project, **When** a DevOps engineer builds the Docker image, **Then** the build completes successfully with optimized layer caching and minimal image size
2. **Given** a container running the API, **When** the orchestrator queries health endpoints, **Then** liveness, readiness, and startup probes return appropriate responses
3. **Given** a container security scan, **When** Trivy analyzes the image, **Then** no high or critical vulnerabilities are detected

---

### User Story 8 - Handle Errors and Recover Gracefully (Priority: P1)

The application can detect errors, provide meaningful error messages, and recover from failures without crashing or losing data.

**Why this priority**: Error handling is fundamental to application reliability and user experience, essential for production readiness.

**Independent Test**: Can be tested by triggering various error conditions (invalid input, missing dependencies, resource exhaustion) and verifying appropriate error responses and recovery behavior.

**Acceptance Scenarios**:

1. **Given** invalid request data, **When** validation fails, **Then** the API returns a 422 response with field-level error details
2. **Given** an unhandled exception in a route handler, **When** the error occurs, **Then** the API returns a 500 response with sanitized error details and logs the full stack trace
3. **Given** a failing external dependency, **When** the circuit breaker opens, **Then** subsequent requests fail fast with 503 status and the circuit recovers automatically after a timeout

---

### Edge Cases

#### Error Handling & Recovery

- What happens when a route module has syntax errors or import failures during application startup?
- How does the system handle conflicting route paths defined in different modules?
- What happens when required environment variables or configuration values are missing?
- How does the application behave when the specified port is already in use?
- What happens when route handlers raise unhandled exceptions?
- How are CORS settings managed for cross-origin requests?
- What happens when request validation fails for malformed input?
- What happens when extremely large request bodies exceed size limits?
- How does the system handle timeout scenarios for long-running requests?
- What happens during graceful shutdown if requests are still in-flight?

#### Configuration & Deployment

- What happens when configuration changes require application restart?
- How does the system handle invalid configuration values at startup?
- What happens when environment-specific configuration files are missing?
- How does the system behave in containerized environments with limited resources?
- What happens when the application runs out of memory or file descriptors?
- How does the system handle timezone differences in timestamp generation?

#### Routing & API Contract

- What happens when no routes are registered (zero-route scenario)?
- How does the system handle trailing slashes in route paths (/api/users vs /api/users/)?
- What happens when special characters appear in path parameters?
- How does the system handle API versioning when breaking changes occur?
- What happens when adding multiple route modules simultaneously?
- How does the system handle updating existing routes without breaking contracts?

#### Security & Access Control

- What happens when rate limits are exceeded?
- How does the system handle authentication failures (when auth is added)?
- What happens when CORS violations occur?
- How does the system detect and block malicious requests?
- What happens when security headers are misconfigured?

#### Performance & Scalability

- What happens under high concurrent load (>1000 requests/second)?
- How does the system handle connection pool exhaustion?
- What happens when external dependencies become unavailable?
- How does the system recover from transient network failures?
- What happens when the circuit breaker opens for a critical dependency?

#### Monitoring & Observability

- What happens when logging systems become unavailable?
- How does the system handle metrics collection failures?
- What happens when distributed tracing context is missing or corrupted?
- How are health checks affected when dependencies are degraded?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a project structure that includes a dedicated directory for FastAPI application code with clear separation between routes, models, and configuration
  - Directory structure: `{package_name}/api/routes/`, `{package_name}/api/models/`, `{package_name}/api/middleware/`, `{package_name}/api/config/`
  - Each directory includes `__init__.py` for proper Python module structure
  - Example files provided in each directory demonstrating usage patterns
- **FR-002**: System MUST provide a main application entry point that initializes FastAPI with CORS middleware, error handlers, and automatic documentation
  - Main application file: `{package_name}/api/main.py`
  - CORS middleware configuration with explicit allowed origins (no wildcard defaults)
  - Global exception handler for unhandled errors returning structured ErrorResponse
  - Custom error handlers for HTTPException, RequestValidationError, and generic Exception
  - OpenAPI documentation enabled at `/docs` (Swagger UI) and `/redoc` (ReDoc)
  - OpenAPI schema available at `/openapi.json`
- **FR-003**: System MUST include a health check endpoint that returns application status and version information
  - Primary health endpoint: `GET /health/` returning overall status
  - Liveness probe: `GET /health/live` for container orchestration
  - Readiness probe: `GET /health/ready` checking dependency availability
  - Startup probe: `GET /health/startup` for slow-starting applications
  - Response includes: status (healthy/unhealthy/degraded), version (semver), timestamp (ISO 8601), optional dependency checks
- **FR-004**: System MUST support modular route organization where each route module can define multiple endpoints
  - Route modules in `{package_name}/api/routes/` directory
  - Each route module is a Python file defining an APIRouter instance
  - Routes automatically discovered and registered through explicit imports in `main.py`
  - Route module naming convention: `{domain}_routes.py` (e.g., `user_routes.py`, `product_routes.py`)
  - Each route module includes prefix, tags, and dependencies configuration
- **FR-005**: System MUST provide configuration management that supports environment variables and default values
  - Configuration class using Pydantic BaseSettings
  - Configuration file: `{package_name}/api/config/settings.py`
  - Environment variable naming convention: `{APP_NAME}_{SETTING_NAME}` (e.g., `MYAPP_PORT`)
  - Support for `.env` files in development (using python-dotenv)
  - Environment-specific configuration profiles: development, staging, production
  - Configuration validation at application startup (fail fast on invalid values)
- **FR-006**: System MUST generate automatic OpenAPI documentation accessible at standard endpoints (/docs and /redoc)
  - Swagger UI at `/docs` with interactive request testing
  - ReDoc at `/redoc` with three-panel layout
  - OpenAPI 3.1.0 schema at `/openapi.json`
  - Documentation includes: endpoint descriptions, request/response schemas, examples, parameter details, authentication requirements
  - Auto-generated from type hints, Pydantic models, and docstrings
- **FR-007**: System MUST include proper error handling that returns structured error responses with appropriate HTTP status codes
  - Structured error response format with `detail`, `status_code`, `request_id` fields
  - HTTP status code mapping: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 422 (validation error), 500 (internal error), 503 (service unavailable)
  - Validation errors include field-level details from Pydantic
  - Error responses include request tracking ID for debugging
  - Production mode hides internal error details (no stack traces in responses)
- **FR-008**: System MUST support request validation through type hints and Pydantic models
  - Path parameters validated through type hints in route signatures
  - Query parameters validated through Pydantic models or type hints with Field()
  - Request bodies validated through Pydantic models
  - Header validation supported through Header() dependencies
  - Validation includes: type checking, range constraints, regex patterns, custom validators
  - Validation errors return 422 status with detailed field errors
- **FR-009**: System MUST provide a development server command that includes auto-reload on code changes
  - Command: `uv run uvicorn {package_name}.api.main:app --reload --host 0.0.0.0 --port 8000`
  - Auto-reload watches Python files for changes
  - Configurable host and port through environment variables
  - Development mode includes: detailed error pages, auto-reload, debug logging
- **FR-010**: System MUST include example route implementations demonstrating common patterns (GET, POST, path parameters, query parameters, request bodies)
  - Example routes file: `{package_name}/api/routes/examples.py`
  - GET endpoint with query parameters: `GET /examples/?skip=0&limit=10`
  - POST endpoint with request body validation: `POST /examples/`
  - GET endpoint with path parameter: `GET /examples/{id}`
  - PUT endpoint for updates: `PUT /examples/{id}`
  - DELETE endpoint: `DELETE /examples/{id}`
  - Each endpoint includes: docstring, type hints, Pydantic models, response examples
- **FR-011**: System MUST generate test files with examples of testing API endpoints
  - Test file: `tests/test_api_{module}.py` for each route module
  - Uses pytest with httpx (FastAPI TestClient)
  - Example tests for each HTTP method: GET, POST, PUT, DELETE
  - Tests include: success cases, validation errors, error handling, status code checks
  - Test fixtures for common setup (test client, mock data)
  - Async test support with pytest-asyncio
- **FR-012**: System MUST integrate with the existing Riso quality suite (ruff, mypy, pylint, pytest)
  - Ruff configuration in `pyproject.toml`: linting rules, line length, import sorting
  - Mypy configuration: strict mode, type checking for all API code
  - Pylint configuration: code quality rules, minimum code score threshold
  - Pytest configuration: test discovery patterns, coverage requirements, markers
  - All generated code must pass quality checks without modification
- **FR-013**: System MUST support containerization with appropriate Dockerfile configuration for API deployment
  - Multi-stage Dockerfile with builder and runtime stages
  - Base image: python:3.11-slim-bookworm
  - Non-root user execution (UID 1000:1000)
  - HEALTHCHECK instruction using /health/live endpoint
  - Optimized layer caching for dependencies
  - Final image size target: <200MB
  - Security: no secrets in image, minimal attack surface
- **FR-014**: System MUST provide logging configuration with appropriate log levels for different environments
  - Structured JSON logging in production
  - Human-readable logging in development
  - Log levels: DEBUG (development), INFO (staging), WARNING (production)
  - Sensitive data sanitization: passwords, tokens, API keys, PII
  - Request/response logging with configurable detail level
  - Correlation IDs (X-Request-ID) included in all log entries
  - Log rotation and retention configurable through environment variables

### Non-Functional Requirements

#### Security Requirements

- **NFR-001**: System MUST provide CORS configuration with explicit allowed origins, methods, and headers (no wildcard defaults in production)
- **NFR-002**: System MUST implement request size limits to prevent denial-of-service attacks (default: 10MB request body limit)
- **NFR-003**: System MUST validate all input parameters (path, query, body, headers) using Pydantic models to prevent injection attacks
- **NFR-004**: System MUST include security headers in responses (X-Content-Type-Options, X-Frame-Options, Content-Security-Policy)
- **NFR-005**: System MUST provide configuration for HTTPS/TLS enforcement in production deployments
- **NFR-006**: System MUST sanitize sensitive data from logs (passwords, tokens, API keys, personal information)
- **NFR-007**: System MUST support secure secrets management through environment variables (no hardcoded credentials)
- **NFR-008**: System MUST include rate limiting middleware configuration to prevent abuse (configurable per-endpoint)
- **NFR-009**: System MUST provide authentication/authorization extension points (middleware hooks for future integration)

#### Operational Requirements

- **NFR-010**: System MUST implement structured logging with JSON format for machine parsing
- **NFR-011**: System MUST expose Prometheus-compatible metrics endpoint (/metrics) for observability
- **NFR-012**: System MUST include distributed tracing headers (X-Request-ID) for request flow tracking
- **NFR-013**: System MUST differentiate health checks: liveness (/health/live), readiness (/health/ready), startup (/health/startup)
- **NFR-014**: System MUST implement graceful shutdown on SIGTERM/SIGINT signals with connection draining
- **NFR-015**: System MUST provide configuration validation at startup (fail fast on invalid configuration)
- **NFR-016**: System MUST include retry logic with exponential backoff for transient external dependency failures
- **NFR-017**: System MUST implement circuit breaker pattern for external service dependencies
- **NFR-018**: System MUST support zero-downtime deployment through health check integration
- **NFR-019**: System MUST provide rollback capability documentation and validation procedures

#### Performance Requirements

- **NFR-020**: System MUST support horizontal scaling (stateless design, no local session storage)
- **NFR-021**: System MUST handle minimum 1000 requests per second on standard hardware (4 cores, 8GB RAM)
- **NFR-022**: System MUST maintain p95 latency under 200ms for standard CRUD operations
- **NFR-023**: System MUST implement connection pooling for external dependencies
- **NFR-024**: System MUST support async/await patterns for I/O-bound operations

#### Maintainability Requirements

- **NFR-025**: System MUST enforce consistent directory structure: api/{routes,models,middleware,config,tests}/
- **NFR-026**: System MUST follow PEP 8 naming conventions enforced by ruff configuration
- **NFR-027**: System MUST require type hints on all public functions and methods (mypy strict mode)
- **NFR-028**: System MUST maintain minimum 80% documentation coverage (docstrings on all public APIs)
- **NFR-029**: System MUST use absolute imports for all internal modules
- **NFR-030**: System MUST provide API versioning strategy (URL path versioning: /v1/, /v2/)
- **NFR-031**: System MUST include deprecation warning mechanism for API changes
- **NFR-032**: System MUST generate changelog from commit messages (conventional commits format)

#### Availability Requirements

- **NFR-033**: System MUST target 99.9% uptime for production deployments (43 minutes downtime per month)
- **NFR-034**: System MUST implement health check timeouts (5 second maximum response time)
- **NFR-035**: System MUST support degraded mode operation when non-critical dependencies fail
- **NFR-036**: System MUST provide automatic error reporting to monitoring systems (configurable)

#### Integration Requirements

- **NFR-037**: System MUST generate multi-stage Dockerfile with build optimization (minimal final image size)
- **NFR-038**: System MUST run containers as non-root user (UID 1000:1000)
- **NFR-039**: System MUST include HEALTHCHECK instruction in Dockerfile for container orchestration
- **NFR-040**: System MUST provide docker-compose.yml for local development with all dependencies
- **NFR-041**: System MUST generate Kubernetes-compatible health check endpoints
- **NFR-042**: System MUST integrate with CI/CD pipelines through standardized test commands
- **NFR-043**: System MUST generate Software Bill of Materials (SBOM) during container builds
- **NFR-044**: System MUST pass container security scanning (Trivy) with no high/critical vulnerabilities
- **NFR-045**: System MUST include smoke tests for post-deployment validation

#### Extensibility Requirements

- **NFR-046**: System MUST provide middleware extension points for custom authentication
- **NFR-047**: System MUST support custom error handler registration
- **NFR-048**: System MUST allow configuration extension through custom settings classes
- **NFR-049**: System MUST provide database connectivity templates (optional, disabled by default)
- **NFR-050**: System MUST support WebSocket endpoints (optional module, disabled by default)

### Key Entities

- **API Application**: The main FastAPI application instance that orchestrates all routes, middleware, and configuration
- **Route Module**: A logical grouping of related endpoints (e.g., user routes, data routes) that can be independently developed and tested
- **Configuration**: Environment-specific settings including server port, CORS origins, logging levels, and feature flags
- **Request/Response Models**: Data structures that define the contract between clients and the API, including validation rules
- **Health Check**: Status information about the application including readiness, liveness, and version details

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can render a FastAPI project and have a running API server within 2 minutes of completion
  - Measurement: Time from `copier copy` completion to successful `curl http://localhost:8000/health/` response
  - Steps included: render, `cd` to project, `uv sync`, `uv run uvicorn` command
  - Success: HTTP 200 response with valid JSON health status
  - Validation: Automated in CI/CD through render matrix script
- **SC-002**: Generated API applications pass all quality checks (ruff, mypy, pylint, pytest) without modification
  - Measurement: Exit code 0 from `make quality` or `uv run task quality` on freshly rendered project
  - Tools: ruff (linting), mypy (type checking), pylint (code quality), pytest (testing)
  - Success: All checks pass, no errors or warnings
  - Validation: CI/CD quality workflow on rendered samples
- **SC-003**: API documentation is automatically available and accurately reflects all endpoints without manual updates
  - Measurement: Access `/docs` and `/redoc` endpoints, verify all routes listed
  - Validation: Programmatic check comparing registered routes to OpenAPI schema
  - Success: 100% of routes documented with correct parameters, schemas, and examples
  - Test: Automated OpenAPI schema validation against route definitions
- **SC-004**: Developers can add a new endpoint by creating a single route module file in under 5 minutes
  - Measurement: Developer timing study from file creation to working endpoint
  - Steps: Create route file, define APIRouter, add endpoint function, import in main.py, test
  - Success: Endpoint accessible via HTTP request, appears in documentation
  - Validation: Documented in quickstart guide with step-by-step timing
- **SC-005**: Application startup time is under 3 seconds in development mode
  - Measurement: Time from `uvicorn` command execution to "Application startup complete" log
  - Conditions: Development environment, auto-reload enabled, default configuration
  - Success: Startup completes in <3 seconds measured by process timing
  - Validation: Automated benchmark script in CI/CD (average of 10 runs)
- **SC-006**: All example endpoints return successful responses with properly formatted JSON
  - Measurement: HTTP status code and JSON schema validation for each example endpoint
  - Endpoints: GET /examples/, POST /examples/, GET /examples/{id}, PUT /examples/{id}, DELETE /examples/{id}
  - Success: 200/201 status codes, valid JSON response matching response models
  - Validation: Integration tests in generated test suite
- **SC-007**: Health check endpoint responds in under 100ms
  - Measurement: p50, p95, p99 latency percentiles for GET /health/ endpoint
  - Tool: Load testing with `wrk` or `locust` (100 concurrent requests over 30 seconds)
  - Success: p95 latency <100ms, p99 latency <150ms
  - Validation: Performance test suite in CI/CD
- **SC-008**: Generated test suite achieves minimum 80% code coverage for scaffold code
  - Measurement: Coverage percentage from `pytest --cov` report
  - Scope: All generated scaffold code in `{package_name}/api/` directory
  - Exclusions: `__init__.py` files, test files themselves
  - Success: Line coverage ≥80%, branch coverage ≥75%
  - Validation: Coverage report in CI/CD with enforcement gate
- **SC-009**: Application handles 100 concurrent requests without errors in local development testing
  - Measurement: Success rate and error count during concurrent load test
  - Tool: `locust` or `wrk` generating 100 concurrent connections
  - Duration: 60 seconds sustained load
  - Success: 100% success rate (no 5xx errors), all responses valid
  - Validation: Load test script included in project, run in CI/CD

### Additional Success Criteria

- **SC-010**: Container image builds successfully and passes security scanning
  - Measurement: Docker build exit code and Trivy scan results
  - Success: Build completes, no high/critical vulnerabilities, image size <200MB
  - Validation: Container build workflow in CI/CD
- **SC-011**: All quality tools provision automatically on first run
  - Measurement: Quality suite execution on fresh environment without pre-installed tools
  - Success: Tools install automatically, checks run successfully
  - Validation: Clean CI/CD environment test
- **SC-012**: Generated project maintains ≥98% success rate in render matrix
  - Measurement: Module success rate from render matrix metadata
  - Success: Project renders successfully across all Python versions (3.11, 3.12, 3.13)
  - Validation: Render matrix CI/CD workflow
- **SC-013**: API documentation includes working examples for all endpoints
  - Measurement: "Try it out" functionality in Swagger UI for each endpoint
  - Success: All example values provided, requests execute successfully
  - Validation: Manual review and automated schema validation
- **SC-014**: Configuration validation fails fast with clear error messages
  - Measurement: Application startup with invalid configuration
  - Success: Application exits with status code 1, error message indicates problem
  - Validation: Test cases for invalid configuration scenarios
- **SC-015**: Render time completes within 10-minute budget
  - Measurement: Time from `copier copy` start to completion
  - Success: Render completes in <10 minutes including all template generation
  - Validation: Render performance metrics in CI/CD
