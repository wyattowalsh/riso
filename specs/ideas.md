# Riso: Next Features & Specifications Roadmap

**Version**: 2.0  
**Last Updated**: 2025-11-01  
**Status**: Active  
**Context**: After completing 006-fastapi-api-scaffold

## Executive Summary

This document outlines a comprehensive, prioritized roadmap of the best next features and specifications to enhance the Riso template system. Features are organized by priority tier and scored using a quantitative framework based on user value, technical dependencies, and alignment with the project's core principles of template sovereignty, deterministic generation, and automation-governed compliance.

## Completed Features

- ✅ **001-build-riso-template**: Foundation template system with optional modules
- ✅ **002-docs-template-expansion**: Multiple documentation frameworks (Fumadocs, Sphinx Shibuya, Docusaurus)
- ✅ **003-code-quality-integrations**: Comprehensive quality suite (Ruff, Mypy, Pylint, pytest)
- ✅ **004-github-actions-workflows**: CI/CD workflows with matrix testing, retry logic, artifact management
- ✅ **005-container-deployment**: Docker/Compose support with multi-stage builds, registry integration
- ✅ **006-fastapi-api-scaffold**: Production-ready FastAPI scaffold
- 🚧 **015-codegen-scaffolding-tools**: Security-hardened code generation CLI with Jinja2 sandboxing, three-way merge, and comprehensive security controls (in progress)

## Prioritization Framework

Features are evaluated using a multi-factor scoring system:

### Scoring Formula
**Score** = (Impact + Alignment) × (6 - Effort) × (6 - Dependencies) / 100

### Factors
- **Impact** (1-5): Value delivered to template users
- **Effort** (1-5): Implementation complexity (1=easy, 5=hard)
- **Dependencies** (1-5): Blocking dependencies (1=none, 5=many)
- **Alignment** (1-5): Fit with Riso constitution principles

### Priority Tiers
- **P1 Critical** (Score ≥ 4.5): Must-have infrastructure and core capabilities
- **P1 High** (Score 4.0-4.4): High-impact features with clear user demand
- **P2 Medium** (Score 3.0-3.9): Valuable enhancements with moderate complexity
- **P3 Low** (Score 2.0-2.9): Specialized features or advanced use cases
- **Future** (Score < 2.0): Exploratory features requiring significant research

---

## Priority 1: Critical Infrastructure (Score ≥ 4.0)

### 015 - Code Generation & Scaffolding Tools (Security-Hardened)

**Score**: 4.9 | Impact: 5 | Effort: 3 | Dependencies: 1 | Alignment: 5  
**Category**: Core Infrastructure | **Status**: In Progress (Specification Complete)

**Description**: Security-first code generation CLI with sandboxed template rendering, three-way merge for updates, and comprehensive attack prevention.

**Why Critical**:

- Foundation for internal Riso template development and maintenance
- Enables teams to create secure, custom templates without security expertise
- Security-hardened design prevents template injection, path traversal, and code execution attacks
- Supports template lifecycle management (create, update, merge) with automated conflict resolution
- Industry research shows 2025 code generation tools must be "secure-by-design" from day one

**Key Security Capabilities**:

- **Template Injection Prevention**:
  - Jinja2 SandboxedEnvironment with restricted access to Python built-ins
  - Disabled dangerous filters (eval, exec, import, compile, __subclasses__)
  - AST parsing and validation before template execution
  - Custom is_safe_attribute() override to block unsafe object access
  - Computational limits (30s timeout, 1000 loop iterations max)
  
- **Input Validation & Sanitization**:
  - Multi-layer validation (shell, SQL, template, code injection)
  - Path canonicalization with traversal prevention (../../etc/passwd blocked)
  - Null byte detection and rejection
  - Type checking for all template variables
  - Maximum length enforcement (project name ≤100, paths ≤4096, vars ≤1024)
  - Reserved word detection (Python keywords, system paths)
  
- **File System Security**:
  - Atomic operations with rollback on failure
  - Symlink detection and rejection outside project boundaries
  - System directory write prevention (/etc, /usr, /bin blocked)
  - Secure default permissions (644 files, 755 executables, 700 cache)
  - File locking to prevent race conditions
  - Checksum validation after generation
  
- **Remote Template Security**:
  - SSRF protection (HTTPS/SSH only, private IPs rejected)
  - SSL/TLS certificate validation
  - Signature verification for template authenticity
  - Cache integrity validation with checksum verification
  - Cache poisoning prevention (isolated per-user, 700 permissions)
  - Credential handling (never logged, cleared from memory, secure storage)
  
- **Hook Execution Sandboxing**:
  - Pre/post-generation hooks run with restricted environment
  - No network access, no sudo/privileged commands
  - 10-second timeout, 100MB memory limit
  - World-writable script rejection
  - Audit logging for all hook executions
  
- **Generated Code Security**:
  - Hardcoded secret scanning (API keys, credentials, tokens)
  - Security linting integration (Semgrep, Bandit)
  - Insecure default detection (debug mode, weak crypto, permissive CORS)
  - Dependency vulnerability scanning
  - License compliance validation

**Three-Way Merge Innovation**:

- Automated template updates while preserving user modifications
- Git-style conflict markers (<<<<<<, =======, >>>>>>>) for manual review
- Merge input validation to prevent malicious content injection
- Security-sensitive file warnings (.env, credentials, config)
- Merge output validation before writing
- Provenance tracking for audit trails

**Core Generation Features**:

- Template-based code generation with variable substitution
- Interactive prompts with validation and type coercion
- Dry-run mode for preview without file creation
- Template inheritance and composition
- Conditional file generation based on user selections
- Metadata tracking (.scaffold-metadata.json) with template version, variables, timestamp
- Multi-file atomic generation (all-or-nothing)
- Quality validation (linting, type checking) with warnings (non-blocking)

**Integration Points**:

- Quality suite (003): Generated code passes ruff, mypy, pylint
- Containers (005): Template generation for Docker/Compose configurations
- CI/CD (004): Integration with GitHub Actions workflows
- FastAPI (006): API endpoint scaffolding templates
- Documentation (002): Auto-generated README and setup guides

**Research-Informed Design**:

Based on 2025 industry best practices research:

1. **Secure-by-Design Pipeline** (GoCodeo model):
   - Pre-generation: Prompt engineering with security constraints
   - Mid-generation: AST parsing and policy enforcement
   - Post-generation: SAST integration and mandatory review
   
2. **Template Security** (Industry standard):
   - Version-controlled registry with signed commits
   - Manual security audits for templates
   - Automated diff checks between versions
   - Template immutability enforcement
   
3. **Observability** (Forensic requirements):
   - Metadata in generated code (tool version, timestamp, agent)
   - Centralized logging for all generation events
   - Anomalous activity alerting
   - Generation-to-merge timeline tracking
   
4. **Access Control** (Enterprise readiness):
   - RBAC for generation operations
   - Separate read/write privileges
   - Immutable infrastructure (isolated environments)
   - Audit logs and session recording

**Tool Ecosystem Positioning**:

Compared to existing tools (Cookiecutter, Yeoman, Copier, Plop):

- **Security Focus**: Only scaffolder with comprehensive security-first design
- **Lifecycle Management**: Supports updates via three-way merge (like Copier)
- **Simplicity**: Python-based like Cookiecutter, no JS required
- **Template Updates**: Git-based smart updates with conflict resolution
- **Flexibility**: Jinja2 templates (any output language), not framework-specific
- **Enterprise Ready**: Built-in security controls, audit trails, provenance tracking

**Success Criteria**:

- **SC-001**: Generate new project in <30 seconds from command to first test run
- **SC-002**: Generated projects have zero critical errors (warnings allowed)
- **SC-003**: 95% of users succeed without docs (generate + test + complete in <5 min)
- **SC-011**: 100% detection of path traversal, template injection, code execution test cases
- **SC-012**: Generated code passes security linting with zero critical vulnerabilities
- **SC-013**: Zero credential leakage in logs, errors, or temp files during security audits

**Implementation Notes**:

- Python 3.11+ with Jinja2 ≥3.1.5 (security fixes, bytecode caching)
- Typer ≥0.20.0 for CLI with Rich integration
- merge3 ≥0.0.13 for three-way merge algorithm
- GitPython for remote template fetching
- Pydantic for validation, Loguru for logging
- AST parsing via Python's ast module
- SAST integration via subprocess (Semgrep, Bandit)

**Dependencies**: Quality suite (003) for validation, Git for template management

---

### 007 - Typer CLI Scaffold

**Score**: 4.8 | Impact: 5 | Effort: 2 | Dependencies: 1 | Alignment: 5  
**Category**: Core Feature | **Status**: Recommended Next

**Description**: Generate CLI applications using Typer with command groups, rich output, configuration, and interactive prompts.

**Why Now**:

- Natural complement to FastAPI (same Pydantic foundation)
- CLI tools are essential for automation and tooling projects
- Low implementation complexity (similar patterns to FastAPI)
- No blocking dependencies (pure Python module)
- Highest score in prioritization framework

**Key Capabilities**:

- Command groups and subcommands with nested structure
- Rich terminal output (colors, tables, progress bars, spinners)
- Interactive prompts with validation and type coercion
- Configuration file support (TOML, JSON, YAML) with precedence
- Shell completion generation (bash, zsh, fish, PowerShell)
- Testing with CliRunner and fixture patterns
- Environment variable integration
- Man page and help text generation

**Integration Points**:

- Quality suite (003): pytest, ruff, mypy integration
- Containers (005): CLI tools packaged in containers
- Documentation (002): Auto-generated man pages and command docs
- FastAPI (006): Shared Pydantic models and validation

**Success Criteria**:

- Users can render CLI tool in <2 minutes
- Commands work immediately with rich output
- Shell completion generates for all major shells
- Test coverage ≥80%
- Generated CLI passes all quality checks

**Implementation Notes**:

- Use Typer 0.9+ for latest features
- Integrate with Rich for terminal formatting
- Provide click migration guide for compatibility
- Include common patterns: config files, logging, error handling

**Dependencies**: None (pure Python module)

---

### 008 - Database Integration (SQLAlchemy/PostgreSQL)

**Score**: 4.2 | Impact: 5 | Effort: 3 | Dependencies: 2 | Alignment: 4  
**Category**: Core Feature | **Status**: Recommended

**Description**: Optional database module with SQLAlchemy ORM, Alembic migrations, and PostgreSQL/SQLite support for production-grade persistence.

**Why Now**:

- Most production APIs require database persistence
- Complements FastAPI scaffold (006) perfectly
- Opt-in design maintains minimal baseline principle
- Reuses existing container infrastructure (005)
- Foundation for many downstream features (auth, background tasks)

**Key Capabilities**:

- **ORM & Query Builder**:
  - SQLAlchemy 2.0 ORM with async support (asyncpg/aiosqlite)
  - Repository pattern examples and base classes
  - Query optimization patterns (eager loading, subqueryload)
  - Raw SQL support for complex queries
  
- **Migration Management**:
  - Alembic migrations with auto-generation from models
  - Migration testing and validation
  - Data migrations alongside schema changes
  - Migration rollback procedures
  
- **Database Options**:
  - PostgreSQL 15+ (production, with pgvector for embeddings)
  - SQLite (development/testing, with WAL mode)
  - MySQL/MariaDB support (optional)
  - Connection string configuration via environment
  
- **Reliability & Performance**:
  - Connection pooling with configurable limits
  - Health checks and connectivity probes
  - Automatic reconnection with exponential backoff
  - Query logging and slow query detection
  - Database-specific optimizations
  
- **Testing Support**:
  - Test database fixtures with isolation
  - Transaction rollback for test cleanup
  - Database seeding utilities
  - Factory patterns for test data
  - Snapshot testing for query results

**Integration Points**:

- FastAPI (006): Database-backed API endpoints with dependency injection
- Containers (005): PostgreSQL service in docker-compose
- Health checks: Database connectivity probes with retry logic
- Quality suite (003): Database testing patterns and fixtures
- Monitoring (010): Query performance metrics and slow query logs

**Success Criteria**:

- Users can add database to FastAPI project in <5 minutes
- Migrations run successfully in dev/test/prod environments
- Connection pooling handles 100+ concurrent requests
- Test database isolation works correctly (no test pollution)
- Zero connection leaks detected in stress tests
- Query performance meets <100ms target for simple queries

**Implementation Notes**:

- Provide both sync and async ORM examples
- Include common patterns: soft deletes, timestamps, UUID primary keys
- Add migration best practices guide
- Support for read replicas and connection routing
- Include database backup documentation

**Dependencies**: Containers (005) for PostgreSQL, Testing framework (006)

---

### 009 - Authentication & Authorization (OAuth2/JWT)

**Score**: 4.1 | Impact: 5 | Effort: 3 | Dependencies: 2 | Alignment: 4  
**Category**: Security | **Status**: Recommended

**Description**: Optional authentication module with OAuth2, JWT tokens, role-based access control, and multi-provider support.

**Why Now**:

- Security is critical for production APIs
- Natural extension of FastAPI scaffold (006)
- Leverages database module (008) for user storage
- High user demand for secure API templates
- Establishes foundation for multi-tenancy

**Key Capabilities**:

- **Authentication Strategies**:
  - OAuth2 password flow with JWT access/refresh tokens
  - API key authentication for service-to-service
  - Session-based authentication (cookie-based)
  - OAuth2 social providers (Google, GitHub, etc.)
  - SAML/SSO integration patterns
  
- **Authorization Patterns**:
  - Role-based access control (RBAC) with hierarchical roles
  - Permission-based authorization (fine-grained)
  - Resource-level permissions
  - Attribute-based access control (ABAC) foundations
  - Policy-based authorization with rule engine
  
- **Security Features**:
  - Secure password hashing (bcrypt/argon2) with configurable rounds
  - Token refresh and revocation mechanisms
  - Account lockout after failed attempts
  - Password complexity requirements
  - MFA/2FA scaffolding (TOTP, SMS)
  - Rate limiting on auth endpoints
  - Security headers (HSTS, CSP, etc.)
  - Audit logging for auth events
  
- **User Management**:
  - User registration with email verification
  - Password reset flows
  - Account activation/deactivation
  - User profile management
  - Session management and device tracking

**Integration Points**:

- FastAPI (006): Protected endpoints with dependency injection
- Database (008): User, role, and permission storage
- Testing (006): Auth fixture patterns and test users
- Monitoring (010): Auth metrics and failed login alerts
- Task Queue (011): Email verification and password reset emails

**Success Criteria**:

- Users can add auth to API in <10 minutes
- Token generation/validation completes in <50ms
- RBAC permissions enforce access control correctly
- Security audit passes with zero high/critical vulnerabilities
- Auth flows tested with E2E tests
- MFA implementation passes TOTP test vectors

**Implementation Notes**:

- Use PyJWT or python-jose for token handling
- Include password strength estimation (zxcvbn)
- Provide Auth0/Clerk/Supabase integration examples
- Document security best practices
- Include common attack prevention (CSRF, XSS, SQL injection)

**Dependencies**: Database (008), FastAPI (006), Testing framework (006)

---

### 010 - Monitoring & Observability

**Score**: 4.0 | Impact: 4 | Effort: 2 | Dependencies: 2 | Alignment: 5  
**Category**: Operations | **Status**: Recommended

**Description**: Production monitoring with Prometheus metrics, structured logging, distributed tracing, and comprehensive observability.

**Why Now**:

- Essential for production deployments and debugging
- Builds on FastAPI health checks (006)
- Low implementation complexity (mostly configuration)
- High alignment with operational excellence
- Critical for diagnosing production issues

**Key Capabilities**:

- **Structured Logging**:
  - JSON-formatted logs with consistent schema
  - Log levels with dynamic configuration
  - Correlation IDs for request tracing
  - Context propagation across async boundaries
  - Log sampling for high-volume scenarios
  - PII redaction and sensitive data masking
  
- **Metrics Collection**:
  - Prometheus metrics endpoint (/metrics)
  - Application metrics (RED: Rate, Errors, Duration)
  - System metrics (CPU, memory, disk, network)
  - Database metrics (connection pool, query duration)
  - Business metrics (custom counters, gauges, histograms)
  - Metric labels and cardinality management
  
- **Distributed Tracing**:
  - OpenTelemetry integration with auto-instrumentation
  - Trace context propagation (W3C standard)
  - Span attributes and events
  - Sampling strategies (head-based, tail-based)
  - Trace baggage for cross-service context
  
- **Observability Platforms**:
  - Prometheus + Grafana dashboards
  - Jaeger/Zipkin for tracing
  - ELK/Loki for log aggregation
  - Datadog/New Relic integration examples
  - CloudWatch (AWS) / Cloud Monitoring (GCP)
  
- **Alerting**:
  - Alert rule templates (error rate, latency, saturation)
  - Prometheus Alertmanager configuration
  - PagerDuty/Opsgenie integration
  - Alert severity levels and escalation
  - Runbook links in alert annotations

**Integration Points**:

- FastAPI (006): Metrics middleware, logging, tracing
- Containers (005): Prometheus/Grafana in docker-compose
- Database (008): Query performance tracking
- Health checks: Dependency monitoring with custom probes
- CI/CD (004): Metrics collection in workflows, performance regression detection

**Success Criteria**:

- Metrics endpoint exposes standard RED metrics
- Logs include correlation IDs automatically
- Tracing spans propagate correctly across service boundaries
- Grafana dashboards visualize key metrics
- Alerts fire correctly in test scenarios
- Log aggregation queries complete in <1 second
- Zero sensitive data leaked in logs

**Implementation Notes**:

- Use structlog or python-json-logger
- Configure prometheus_client for metrics
- Integrate OpenTelemetry SDK
- Provide Grafana dashboard JSON exports
- Include common alert rules (4xx/5xx rates, p99 latency)
- Document metrics naming conventions

**Dependencies**: FastAPI (006), Containers (005)

---

## Priority 2: Core Enhancements (Score 3.0-3.9)

### 011 - Background Tasks (Celery/RQ)

**Score**: 3.8 | Impact: 4 | Effort: 3 | Dependencies: 3 | Alignment: 4

**Description**: Async task queue with Celery or RQ for background job processing.

**Why Important**:

- Essential for long-running operations (emails, reports, data processing)
- Enables API responsiveness (offload work to workers)
- Common requirement for production APIs

**Key Features**:

- Celery with Redis/RabbitMQ broker
- Task scheduling and periodic tasks
- Task result tracking
- Retry logic and error handling
- Monitoring and task visibility

**Dependencies**: Database (008), Containers (005)

---

### 012 - GraphQL API Scaffold (Strawberry)

**Score**: 3.6 | Impact: 4 | Effort: 4 | Dependencies: 2 | Alignment: 4

**Description**: Alternative to REST API using Strawberry GraphQL framework.

**Why Important**:

- Growing adoption for flexible APIs
- Client-driven data fetching
- Alternative to REST for specific use cases

**Key Features**:

- Strawberry GraphQL schema generation
- DataLoaders for N+1 query optimization
- Subscriptions for real-time updates
- GraphiQL playground
- Schema stitching support

**Dependencies**: FastAPI patterns (006), Database (008)

---

### 013 - WebSocket Support

**Score**: 3.5 | Impact: 4 | Effort: 3 | Dependencies: 2 | Alignment: 4

**Description**: Real-time bidirectional communication using FastAPI WebSockets.

**Why Important**:

- Required for real-time features (chat, notifications, live updates)
- Complements REST API with push capabilities
- Growing demand for real-time applications

**Key Features**:

- WebSocket endpoint patterns
- Connection management and heartbeats
- Broadcasting to multiple clients
- Authentication for WebSocket connections
- Testing WebSocket endpoints

**Dependencies**: FastAPI (006), Authentication (009)

---

### 014 - API Versioning Strategy

**Score**: 3.4 | Impact: 3 | Effort: 2 | Dependencies: 1 | Alignment: 5

**Description**: Comprehensive API versioning with URL path, header, and content negotiation strategies.

**Why Important**:

- Essential for API evolution and backward compatibility
- Prevents breaking changes for existing clients
- Professional API design practice

**Key Features**:

- URL path versioning (/v1/, /v2/)
- Header-based versioning
- Deprecation warnings
- Version-specific documentation
- Migration guides

**Dependencies**: FastAPI (006)

---

### 015 - File Upload & Storage (S3/MinIO)

**Score**: 3.3 | Impact: 4 | Effort: 3 | Dependencies: 2 | Alignment: 3

**Description**: File upload handling with local storage, S3, or MinIO backends.

**Why Important**:

- Common requirement for user-generated content
- Enables document management and media uploads
- Cloud storage integration essential for scalability

**Key Features**:

- Multi-part file upload handling
- Storage backend abstraction (local, S3, MinIO)
- File validation (type, size, virus scanning)
- Presigned URL generation
- Image processing (resize, thumbnail)

**Dependencies**: FastAPI (006), Containers (005)

---

### 016 - API Rate Limiting & Throttling

**Score**: 3.2 | Impact: 3 | Effort: 2 | Dependencies: 1 | Alignment: 4

**Description**: Request rate limiting and throttling to prevent abuse and ensure fair usage.

**Why Important**:

- Protects API from abuse and DoS attacks
- Enforces fair usage policies
- Production-ready API requirement

**Key Features**:

- Per-user/IP rate limiting
- Configurable rate limits per endpoint
- Token bucket algorithm
- Redis-backed distributed rate limiting
- Rate limit headers (X-RateLimit-*)

**Dependencies**: FastAPI (006)

---

### 017 - Caching Layer (Redis)

**Score**: 3.1 | Impact: 4 | Effort: 3 | Dependencies: 2 | Alignment: 3

**Description**: Redis-based caching for API responses and data.

**Why Important**:

- Reduces database load and improves performance
- Essential for high-traffic APIs
- Enables session storage and distributed locking

**Key Features**:

- Response caching middleware
- Cache invalidation strategies
- Redis connection pooling
- Cache-aside pattern examples
- TTL configuration

**Dependencies**: Containers (005), FastAPI (006)

---

## Lower Priority (Score 2.0-2.9)

### 018 - Email Integration (SendGrid/SES)

**Score**: 2.9 | Impact: 3 | Effort: 2 | Dependencies: 2 | Alignment: 3

**Description**: Email sending with templates and transactional email support.

**Why Deferred**: Specialized use case, many alternatives, external service dependencies

**Key Features**:

- Template-based emails (Jinja2)
- Transactional email providers (SendGrid, SES, SMTP)
- Email queueing and retries
- Tracking (opens, clicks)

---

### 019 - Payment Integration (Stripe)

**Score**: 2.7 | Impact: 4 | Effort: 4 | Dependencies: 3 | Alignment: 2

**Description**: Payment processing with Stripe integration.

**Why Deferred**: Highly specialized, external service, significant complexity

**Key Features**:

- Stripe payment intents
- Webhook handling
- Subscription management
- Invoice generation

---

### 020 - Multi-tenancy Support

**Score**: 2.6 | Impact: 4 | Effort: 5 | Dependencies: 4 | Alignment: 2

**Description**: Multi-tenant architecture with tenant isolation.

**Why Deferred**: Complex architectural change, affects many components

**Key Features**:

- Tenant identification (subdomain, path, header)
- Data isolation strategies
- Per-tenant configuration
- Tenant-specific migrations

---

### 021 - Search Integration (Elasticsearch)

**Score**: 2.5 | Impact: 3 | Effort: 4 | Dependencies: 3 | Alignment: 2

**Description**: Full-text search with Elasticsearch integration.

**Why Deferred**: Infrastructure complexity, specialized use case

**Key Features**:

- Document indexing
- Full-text search queries
- Aggregations and faceting
- Search suggestions

---

### 022 - Admin Panel (FastAPI-Admin)

**Score**: 2.4 | Impact: 3 | Effort: 4 | Dependencies: 3 | Alignment: 2

**Description**: Auto-generated admin panel for database models.

**Why Deferred**: UI complexity, framework-specific, maintenance overhead

---

### 023 - Mobile API (Firebase Push Notifications)

**Score**: 2.2 | Impact: 3 | Effort: 3 | Dependencies: 2 | Alignment: 2

**Description**: Mobile-specific features like push notifications.

**Why Deferred**: Specialized use case, external dependencies

---

## Future Exploration (Score < 2.0)

### 024 - Machine Learning Model Serving

**Score**: 1.9 | Impact: 3 | Effort: 5 | Dependencies: 4 | Alignment: 1

**Why Deferred**: Highly specialized, complex infrastructure, niche use case

---

### 025 - Blockchain Integration

**Score**: 1.5 | Impact: 2 | Effort: 5 | Dependencies: 4 | Alignment: 1

**Why Deferred**: Niche use case, high complexity, uncertain value

---

## Recommended Implementation Order

Based on prioritization framework, dependencies, and user value:

### Phase 1: Core Infrastructure & Security (Current - Q1 2026)
**Timeline**: 3-6 months | **Focus**: Foundation for secure template development

1. **015 - Code Generation & Scaffolding Tools** (Score 4.9) 🚧 **IN PROGRESS**
   - Security specification complete with 40+ security requirements
   - Security checklist complete (120 items validated)
   - Foundation for all future Riso template development
   - Enables secure, automated template updates
   - Critical for maintaining template quality and security
   - **Status**: Specification complete, ready for implementation
   - **Next**: Implement core CLI, sandboxed rendering, security validations

2. **007 - Typer CLI Scaffold** (Score 4.8)
   - No dependencies, immediate value
   - Complements FastAPI (shared Pydantic foundation)
   - Can use 015 for self-hosting (dogfooding)
   - Foundation for CLI-based tooling

### Phase 2: Data & Persistence (Q2 2026)
**Timeline**: 4-6 months | **Focus**: Production API capabilities

3. **008 - Database Integration** (Score 4.2)
   - Foundation for Auth, Background Tasks, Multi-tenancy
   - Critical for production applications
   - Enables most subsequent features

4. **010 - Monitoring & Observability** (Score 4.0)
   - Production essential, operational excellence
   - Low complexity, high impact
   - Enables debugging and performance optimization
   - Critical for production deployments

### Phase 3: Security & Access Control (Q3 2026)
**Timeline**: 3-4 months | **Focus**: Production security & compliance

5. **009 - Authentication & Authorization** (Score 4.1)
   - Requires Database (008)
   - Security-critical for production APIs
   - Enables tenant isolation, admin panels
   - Foundation for enterprise features

6. **016 - API Rate Limiting** (Score 3.2)
   - Security enhancement, DoS protection
   - Builds on FastAPI (006)
   - Production security requirement

### Phase 4: Advanced API Patterns (Q4 2026)
**Timeline**: 6-9 months | **Focus**: Modern API capabilities

7. **011 - Background Tasks** (Score 3.8)
   - Async processing for long-running operations
   - Requires Database (008)
   - Enables email, reports, data processing

8. **013 - WebSocket Support** (Score 3.5)
   - Real-time communication
   - Requires Auth (009)
   - Enables chat, notifications, live updates

9. **012 - GraphQL API** (Score 3.6)
   - Alternative to REST
   - Requires Database (008)
   - Modern API pattern

10. **014 - API Versioning** (Score 3.4)
    - API maturity and backward compatibility
    - Builds on FastAPI (006)
    - Professional API design

### Phase 5: Storage & Performance (Q1 2027)
**Timeline**: 4-6 months | **Focus**: Scalability & optimization

11. **017 - Caching Layer** (Score 3.1)
    - Performance optimization
    - Reduces database load
    - Production scalability

12. **015 - File Upload & Storage** (Score 3.3)
    - Content management
    - Requires Containers (005)
    - User-generated content support

13. **018 - Email Integration** (Score 2.9)
    - Communication infrastructure
    - Requires Background Tasks (011)
    - Transactional email support

### Phase 6: Specialized Features (Q2-Q3 2027)
**Timeline**: 6-12 months | **Focus**: Enterprise & advanced use cases

- Multi-tenancy Support (020)
- Search Integration (021)
- Admin Panel (022)
- Payment Integration (019)
- Compliance & Audit Logging
- Data Privacy & GDPR Toolkit

---

## Recent Updates (November 2025)

### Specification 015: Security-Hardened Code Generation

**Major Accomplishment**: Comprehensive security specification completed with industry-leading security controls.

**Key Additions**:
- 40 new security requirements (FR-025 to FR-064) covering all attack vectors
- 120-item security checklist validating requirements completeness
- 14 security-focused edge cases (path traversal, template injection, SSRF, etc.)
- 3 security success criteria (100% attack detection, zero critical vulnerabilities, zero credential leakage)

**Security Requirements Summary**:
- Input validation & sanitization (6 requirements)
- Template processing security (8 requirements)
- File system security (7 requirements)
- Remote template security (6 requirements)
- Merge & update security (3 requirements)
- Error handling & logging (4 requirements)
- Generated code security (3 requirements)
- Supply chain security (3 requirements)

**Research Integration**:
- Incorporated 2025 secure-by-design best practices from GoCodeo model
- Jinja2 sandboxing patterns from industry security research
- Three-way merge security considerations from academic literature
- Comparison analysis with Cookiecutter, Yeoman, Copier, Plop ecosystem

**Status**: Specification complete, security checklist validated, ready for implementation phase.

**Impact**: Positions Riso as the only security-first scaffolding tool in the Python ecosystem, enabling enterprise adoption and secure template development workflows.

---

## Additional Features from Extended Roadmap

The following features are documented in detail in the extended planning documents but deferred to later phases based on complexity and dependencies:

### Infrastructure & Operations
- **Security & Vulnerability Management**: Automated scanning, SAST, secret detection (P1 Critical)
- **Testing Framework Enhancement**: E2E testing, performance testing, mutation testing (P1 High)
- **Dev Environment Management**: Devcontainers, IDE integrations, hot reload (P2 Medium)
- **Backup & Disaster Recovery**: Automated backups, point-in-time recovery (P3 Low-Medium)
- **Cost Optimization & FinOps**: Cloud cost tracking, optimization recommendations (P3 Low)

### Features & Integrations
- **Event-Driven Architecture**: Event buses, event sourcing, CQRS patterns (P2 Medium)
- **Code Generation Tools**: Scaffold generators, CRUD automation (P2 Medium)
- **Performance Optimization**: Profiling, caching strategies, load testing (P2 Medium)
- **Notifications & Messaging**: Multi-channel notifications (email, SMS, push, in-app) (P3 Low-Medium)
- **Webhook Management**: Webhook emission and consumption patterns (P3 Low)
- **AI/ML Integration**: LLM integration, vector databases, RAG patterns (P3 Low)

### Governance & Compliance
- **Compliance & Audit Logging**: SOC 2, HIPAA, GDPR compliance helpers (P3 Low-Medium)
- **Data Privacy & GDPR Toolkit**: Data export, deletion, consent management (P3 Low)
- **Changelog & Release Management**: Automated changelogs, semantic versioning (P3 Low-Medium)
- **Architecture Decision Records**: ADR tooling and templates (P3 Low)

---

## Evaluation Criteria

When selecting next feature, evaluate against these dimensions:

### Constitutional Alignment
- ✅ **Minimal Baseline**: Feature is opt-in, doesn't bloat default renders
- ✅ **Deterministic Generation**: Produces identical output with same inputs
- ✅ **Template Sovereignty**: No manual edits required after generation
- ✅ **Comprehensive Documentation**: Complete docs, examples, and guides
- ✅ **Automation-Governed**: Quality checks automated, no manual gates

### Technical Feasibility
- **Clear Integration Points**: Well-defined interfaces with existing modules
- **Well-Defined Scope**: Boundaries clear, avoiding scope creep
- **Proven Technology**: Battle-tested tools and frameworks
- **Testable Success Criteria**: Measurable outcomes with clear targets

### User Value
- **Real Problems Solved**: Addresses actual pain points from user feedback
- **Common Requirements**: Needed by significant portion of users
- **Production-Ready**: Works reliably at scale from day one
- **Clear Documentation**: Users can adopt without extensive support

### Maintenance Burden
- **Sustainable Long-Term**: Can be maintained with available resources
- **Limited External Dependencies**: Fewer moving parts, less breakage
- **Clear Ownership**: Designated maintainer or team
- **Automated Testing**: ≥80% coverage, CI/CD integration

### Success Metrics
Each feature tracks:
- **Adoption Rate**: % of new renders enabling the feature
- **Stability**: % of renders with feature passing all checks
- **Performance**: Time to complete feature-specific operations
- **Quality**: Test coverage, security scan results, linting compliance
- **Documentation**: Completeness score (0-100), user feedback ratings
- **Support Load**: GitHub issues/discussions related to feature

---

## Contributing Ideas

### Proposal Process

To propose a new feature:

1. **Create GitHub Issue** with label `feature-proposal`
   
2. **Include Required Information**:
   - **Problem Statement**: What user need does this solve?
   - **Proposed Solution**: High-level approach and key capabilities
   - **Integration Points**: How does it fit with existing modules?
   - **Success Criteria**: How do we know it works?
   - **Impact/Effort Estimates**: Scoring against framework dimensions
   - **Dependencies**: What must exist first?
   - **Alternative Approaches**: What else was considered?

3. **Community Discussion**:
   - Maintainers and community discuss and refine proposal
   - Clarify scope, requirements, and implementation approach
   - Identify potential challenges and mitigation strategies

4. **Approval Decision**:
   - Feature added to roadmap if approved
   - Priority tier assigned based on scoring
   - Timeline estimate provided

5. **Specification Creation**:
   - Full spec created following template in `specs/006-fastapi-api-scaffold/`
   - Includes: data model, plan, quickstart, research, tasks
   - Checklist created using `.specify/checklist.prompt.md`
   - Reviewed by maintainers before implementation

### Feature Proposal Template

```markdown
## Feature Title

**Category**: [Infrastructure | Core Feature | Security | Operations | Documentation]
**Estimated Priority**: [P1 Critical | P1 High | P2 Medium | P3 Low | Future]

### Problem Statement
[What user problem does this solve? Include specific scenarios and pain points.]

### Proposed Solution
[High-level description of the feature and how it addresses the problem.]

### Key Capabilities
- Capability 1
- Capability 2
- ...

### Integration Points
- Existing Module 1: How it integrates
- Existing Module 2: How it integrates

### Success Criteria
- Measurable outcome 1
- Measurable outcome 2

### Scoring Estimates
- **Impact** (1-5): [Score and justification]
- **Effort** (1-5): [Score and justification]
- **Dependencies** (1-5): [Score and justification]
- **Alignment** (1-5): [Score and justification]
- **Calculated Score**: [Formula result]

### Dependencies
- Required Feature 1 (spec NNN)
- Required Feature 2 (spec NNN)

### Alternative Approaches
[What other solutions were considered and why this approach is preferred?]
```

---

## Review & Update Cadence

### Monthly Reviews
- Progress assessment on active features
- Blocker identification and resolution
- Community feedback incorporation

### Quarterly Planning
- Prioritize next 3-6 months of features
- Adjust scoring based on user feedback and ecosystem changes
- Review and retire obsolete or low-adoption features

### Semi-Annual Strategic Reviews
- Comprehensive roadmap review and adjustment
- Major version planning
- Constitutional principle compliance audit
- Technology stack updates and migrations

---

## Appendix: Quick Reference Matrix

| Spec | Feature | Score | Priority | Category | Effort | Dependencies | Status |
|------|---------|-------|----------|----------|--------|--------------|--------|
| 015 | Codegen & Scaffolding | 4.9 | P1 Critical | Core Infra | Medium | 003 | 🚧 In Progress (Spec Complete) |
| 007 | Typer CLI | 4.8 | P1 High | Core | Low | None | Recommended Next |
| 008 | Database | 4.2 | P1 High | Core | Medium | 005, 006 | Recommended |
| 009 | Auth/AuthZ | 4.1 | P1 High | Security | Medium | 008 | Recommended |
| 010 | Monitoring | 4.0 | P1 High | Operations | Low | 005, 006 | Recommended |
| 011 | Task Queue | 3.8 | P2 Medium | Core | Medium | 008, 010 | Planned |
| 012 | GraphQL | 3.6 | P2 Medium | Core | High | 006, 008 | Planned |
| 013 | WebSockets | 3.5 | P2 Medium | Core | Medium | 006, 009 | Planned |
| 014 | Versioning | 3.4 | P2 Medium | Core | Low | 006 | Planned |
| 015 | File Storage | 3.3 | P2 Medium | Core | Medium | 005, 006 | Planned |
| 016 | Rate Limiting | 3.2 | P2 Medium | Security | Low | 006 | Planned |
| 017 | Caching | 3.1 | P2 Medium | Performance | Medium | 005, 006 | Planned |
| 018 | Email | 2.9 | P3 Low | Feature | Low | 011 | Deferred |
| 019 | Payments | 2.7 | P3 Low | Feature | High | 008, 009 | Deferred |
| 020 | Multi-tenancy | 2.6 | P3 Low | Architecture | Very High | 008, 009 | Deferred |
| 021 | Search | 2.5 | P3 Low | Feature | High | 008, 011 | Deferred |
| 022 | Admin Panel | 2.4 | P3 Low | Feature | High | 008, 009 | Deferred |
| 023 | Mobile/Push | 2.2 | P3 Low | Feature | Medium | 008, 011 | Deferred |
| 024 | ML Serving | 1.9 | Future | Feature | Very High | 008, 010 | Exploratory |
| 025 | Blockchain | 1.5 | Future | Feature | Very High | Many | Exploratory |

**Legend**:
- ✅ Complete
- 🚧 In Progress
- 📋 Specification Complete
- 🎯 Recommended Next
- ⏳ Planned
- 🔮 Future/Exploratory

---

## Key Principles & Constraints

### Non-Negotiable Requirements
- **Test Coverage**: All features require ≥80% test coverage
- **Documentation**: Comprehensive docs with examples and quickstarts
- **Quality Gates**: Must pass ruff, mypy, pylint with zero errors
- **Security**: No high/critical vulnerabilities allowed
- **Performance**: Must meet specified performance targets
- **Opt-In Design**: Never modify minimal baseline without user choice

### Success Definition
A feature is considered "complete" when:
1. ✅ Code merged to main branch
2. ✅ All tests passing with ≥80% coverage
3. ✅ Documentation published and reviewed
4. ✅ Sample renders validated
5. ✅ Integration tests with existing modules passing
6. ✅ Security scan passing (no high/critical)
7. ✅ Performance benchmarks met
8. ✅ Feature flag enabled by default (if applicable)

### Deprecation Policy
Features may be deprecated if:
- Adoption rate <5% after 12 months
- Superior alternative exists in ecosystem
- Maintenance burden exceeds available resources
- Security/compliance risks cannot be mitigated
- Conflicts with constitutional principles

Deprecated features:
- Marked deprecated with warnings for 2 major versions
- Removed after 2 major versions (minimum 12 months)
- Migration guide provided
- Community notified via blog post and release notes

---

**Document Version**: 2.1  
**Status**: Active Roadmap  
**Next Review**: December 15, 2025  
**Maintainer**: @wyattowalsh  
**Last Updated**: November 2, 2025

**Changelog**:
- **v2.1** (2025-11-02): Added spec 015 (Code Generation & Scaffolding Tools) as highest priority (4.9), comprehensive security-first design with 40+ security requirements, 120-item security checklist, research-informed implementation, positioned as foundation for all future template development
- **v2.0** (2025-11-01): Merged ideas.md and NEXT_FEATURES.md, comprehensive expansion with 25 features
- **v1.0** (2025-11-01): Initial NEXT_FEATURES.md creation with 30 features across 5 priority levels
