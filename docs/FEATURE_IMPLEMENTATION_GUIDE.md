# Feature Implementation Guide

**Version**: 1.0  
**Last Updated**: 2025-11-01  
**Purpose**: Tactical implementation guidance for next features

This guide complements `NEXT_FEATURES.md` by providing detailed implementation considerations, technical patterns, and best practices for each proposed feature.

---

## Implementation Patterns

### General Principles

All features should follow these core patterns:

1. **Optional by Default**: Features should be opt-in via `copier.yml` prompts
2. **Composable**: Features should work independently and together
3. **Deterministic**: Same inputs produce same outputs
4. **Tested**: Every feature needs smoke tests in `samples/`
5. **Documented**: Auto-generated docs in rendered projects
6. **Governed**: CI checks enforce quality standards

### Feature Scaffolding Structure

```
template/files/
├── modules/
│   └── {feature-name}/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       └── tests/
│           └── test_{feature}.py
├── configs/
│   └── {feature}.{toml|yml|json}
└── docs/
    └── modules/
        └── {feature}.md.jinja
```

---

## Priority 1 Features: Detailed Implementation

### 004 - Security & Vulnerability Management

**Implementation Approach**:

1. **Python Security**:
   ```yaml
   # Add to copier.yml
   security_scanning:
     type: str
     help: "Enable security vulnerability scanning?"
     choices:
       - disabled
       - standard
       - strict
   ```

   ```toml
   # template/files/pyproject.toml addition
   [tool.uv.tasks]
   security = "uv run python -m scripts.security.run_security_checks"
   ```

2. **Tools Integration**:
   - **Bandit**: Python SAST scanner
   - **pip-audit**: CVE scanning for Python deps
   - **Safety**: Alternative Python security checker
   - **gitleaks**: Secret detection
   - **Trivy**: Container and filesystem scanning

3. **GitHub Actions Workflow**:
   ```yaml
   # .github/workflows/security.yml
   name: Security Scanning
   on: [pull_request, schedule]
   jobs:
     security:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Run Bandit
           run: uv run bandit -r . -f json -o security-report.json
         - name: Run pip-audit
           run: uv run pip-audit --format json
         - name: Upload results
           uses: github/codeql-action/upload-sarif@v2
   ```

4. **Files to Create**:
   - `template/files/.bandit.yml`
   - `scripts/security/run_security_checks.py`
   - `.github/workflows/security.yml`
   - `docs/modules/security.md.jinja`

**Acceptance Tests**:
- Render with `security_scanning=standard`
- Inject known vulnerability (e.g., old dependency)
- Verify security check fails with actionable message

---

### 005 - Container & Deployment Patterns

**Implementation Approach**:

1. **Docker Strategy**:
   ```dockerfile
   # template/files/Dockerfile.jinja
   # Stage 1: Builder
   FROM python:3.11-slim as builder
   WORKDIR /app
   RUN pip install uv
   COPY pyproject.toml uv.lock ./
   RUN uv sync --no-dev --frozen
   
   # Stage 2: Runtime
   FROM python:3.11-slim
   WORKDIR /app
   COPY --from=builder /app/.venv /app/.venv
   COPY . .
   ENV PATH="/app/.venv/bin:$PATH"
   {% if api_tracks != 'none' %}
   EXPOSE 8000
   CMD ["uvicorn", "{{ package_name }}.api.main:app", "--host", "0.0.0.0"]
   {% endif %}
   ```

2. **Docker Compose for Local Dev**:
   ```yaml
   # template/files/docker-compose.yml.jinja
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://user:pass@db:5432/{{ project_slug }}
       depends_on:
         - db
     {% if 'database_module' == 'enabled' %}
     db:
       image: postgres:15-alpine
       environment:
         POSTGRES_DB: {{ project_slug }}
         POSTGRES_USER: user
         POSTGRES_PASSWORD: pass
       volumes:
         - postgres_data:/var/lib/postgresql/data
     {% endif %}
   volumes:
     postgres_data:
   ```

3. **Deployment Targets** (conditional generation):
   - `deploy/cloud-run/service.yaml`
   - `deploy/kubernetes/deployment.yaml`
   - `deploy/aws/task-definition.json`
   - `deploy/fly.toml`

4. **Health Checks**:
   ```python
   # template/files/modules/health/main.py
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.get("/health")
   async def health_check():
       return {"status": "healthy"}
   
   @router.get("/ready")
   async def readiness_check():
       # Check database, redis, etc.
       return {"status": "ready"}
   ```

**Acceptance Tests**:
- `docker build` completes successfully
- `docker-compose up` boots all services
- Health endpoints return 200
- Container passes security scan (Trivy)

---

### 006 - Testing Framework Enhancement

**Implementation Approach**:

1. **Enhanced pytest Configuration**:
   ```toml
   # template/files/pyproject.toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   python_files = "test_*.py"
   python_functions = "test_*"
   addopts = [
       "-v",
       "--strict-markers",
       "--cov={{ package_name }}",
       "--cov-report=html",
       "--cov-report=term-missing",
       "--cov-fail-under=80",
   ]
   markers = [
       "unit: Unit tests",
       "integration: Integration tests",
       "e2e: End-to-end tests",
       "slow: Slow tests",
   ]
   ```

2. **Test Structure**:
   ```
   tests/
   ├── unit/
   │   ├── test_models.py
   │   └── test_utils.py
   ├── integration/
   │   ├── test_api.py
   │   └── test_database.py
   ├── e2e/
   │   └── test_workflows.py
   ├── fixtures/
   │   ├── __init__.py
   │   └── database.py
   └── conftest.py
   ```

3. **Fixture Patterns**:
   ```python
   # template/files/tests/conftest.py
   import pytest
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   
   @pytest.fixture(scope="session")
   def db_engine():
       engine = create_engine("sqlite:///:memory:")
       yield engine
       engine.dispose()
   
   @pytest.fixture
   def db_session(db_engine):
       Session = sessionmaker(bind=db_engine)
       session = Session()
       yield session
       session.rollback()
       session.close()
   
   @pytest.fixture
   def api_client():
       from fastapi.testclient import TestClient
       from {{ package_name }}.api.main import app
       return TestClient(app)
   ```

4. **Integration Test Patterns**:
   ```python
   # template/files/tests/integration/test_api.py
   import pytest
   
   @pytest.mark.integration
   def test_create_item(api_client, db_session):
       response = api_client.post("/items", json={"name": "test"})
       assert response.status_code == 201
       
       # Verify in database
       from {{ package_name }}.models import Item
       item = db_session.query(Item).filter_by(name="test").first()
       assert item is not None
   ```

5. **Coverage Configuration**:
   ```toml
   [tool.coverage.run]
   branch = true
   source = ["{{ package_name }}"]
   omit = [
       "*/tests/*",
       "*/migrations/*",
       "*/__init__.py",
   ]
   
   [tool.coverage.report]
   exclude_lines = [
       "pragma: no cover",
       "def __repr__",
       "raise AssertionError",
       "raise NotImplementedError",
       "if __name__ == .__main__.:",
       "if TYPE_CHECKING:",
   ]
   ```

**Acceptance Tests**:
- All test types (unit, integration, e2e) run successfully
- Coverage meets threshold (>80%)
- Test isolation verified (tests can run in any order)
- Fixtures work correctly

---

### 007 - Database & Persistence Layer

**Implementation Approach**:

1. **Database Selection Prompt**:
   ```yaml
   # copier.yml
   database_module:
     type: str
     help: "Enable database integration?"
     choices:
       - disabled
       - postgresql
       - mysql
       - sqlite
       - mongodb
   
   orm_choice:
     type: str
     help: "Select ORM/Query Builder"
     choices:
       - sqlalchemy
       - tortoise
       - prisma
   ```

2. **SQLAlchemy Setup** (most common):
   ```python
   # template/files/modules/database/config.py
   from sqlalchemy import create_engine
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.orm import sessionmaker
   import os
   
   DATABASE_URL = os.getenv(
       "DATABASE_URL",
       "postgresql://user:pass@localhost:5432/{{ project_slug }}"
   )
   
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
   )
   
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   Base = declarative_base()
   
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

3. **Migration Setup** (Alembic):
   ```python
   # template/files/alembic/env.py
   from alembic import context
   from {{ package_name }}.database.config import Base, DATABASE_URL
   
   config = context.config
   config.set_main_option("sqlalchemy.url", DATABASE_URL)
   target_metadata = Base.metadata
   
   def run_migrations_online():
       with engine.connect() as connection:
           context.configure(
               connection=connection,
               target_metadata=target_metadata
           )
           with context.begin_transaction():
               context.run_migrations()
   ```

4. **Model Example**:
   ```python
   # template/files/modules/models/base.py
   from sqlalchemy import Column, Integer, DateTime
   from datetime import datetime
   from {{ package_name }}.database.config import Base
   
   class TimestampMixin:
       created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   
   class BaseModel(Base, TimestampMixin):
       __abstract__ = True
       id = Column(Integer, primary_key=True, index=True)
   ```

5. **Database Commands**:
   ```toml
   # pyproject.toml
   [tool.uv.tasks]
   db-upgrade = "alembic upgrade head"
   db-downgrade = "alembic downgrade -1"
   db-migration = "alembic revision --autogenerate -m"
   db-reset = "alembic downgrade base && alembic upgrade head"
   ```

**Acceptance Tests**:
- Database connection succeeds
- Migrations run without errors
- Models CRUD operations work
- Connection pooling configured correctly
- Test database isolation works

---

## Priority 2 Features: Key Considerations

### 009 - Authentication & Authorization

**Key Decision Points**:
- JWT vs Session-based auth
- Password hashing (bcrypt, argon2)
- Token refresh strategies
- OAuth provider selection

**Critical Files**:
- `modules/auth/jwt.py`
- `modules/auth/dependencies.py` (FastAPI dependencies)
- `modules/auth/models.py` (User, Token models)
- `modules/auth/schemas.py` (Pydantic models)

**Security Checklist**:
- [ ] Password complexity requirements
- [ ] Rate limiting on auth endpoints
- [ ] Secure password storage (never plaintext)
- [ ] Token expiration configured
- [ ] HTTPS enforced in production
- [ ] CSRF protection enabled
- [ ] SQL injection prevented (ORM parameterization)

---

### 010 - Monitoring & Observability

**Implementation Strategy**:

1. **Structured Logging**:
   ```python
   # template/files/modules/logging/config.py
   import structlog
   
   structlog.configure(
       processors=[
           structlog.stdlib.filter_by_level,
           structlog.stdlib.add_logger_name,
           structlog.stdlib.add_log_level,
           structlog.processors.TimeStamper(fmt="iso"),
           structlog.processors.StackInfoRenderer(),
           structlog.processors.format_exc_info,
           structlog.processors.JSONRenderer()
       ],
       wrapper_class=structlog.stdlib.BoundLogger,
       logger_factory=structlog.stdlib.LoggerFactory(),
   )
   ```

2. **Metrics with Prometheus**:
   ```python
   # template/files/modules/metrics/middleware.py
   from prometheus_client import Counter, Histogram
   
   REQUEST_COUNT = Counter(
       'http_requests_total',
       'Total HTTP requests',
       ['method', 'endpoint', 'status']
   )
   
   REQUEST_DURATION = Histogram(
       'http_request_duration_seconds',
       'HTTP request duration',
       ['method', 'endpoint']
   )
   ```

3. **OpenTelemetry Integration**:
   ```python
   # template/files/modules/tracing/config.py
   from opentelemetry import trace
   from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
   from opentelemetry.sdk.trace import TracerProvider
   from opentelemetry.sdk.trace.export import BatchSpanProcessor
   
   provider = TracerProvider()
   processor = BatchSpanProcessor(OTLPSpanExporter())
   provider.add_span_processor(processor)
   trace.set_tracer_provider(provider)
   ```

---

### 011 - Task Queue & Background Jobs

**Celery Setup Example**:
```python
# template/files/modules/tasks/celery_app.py
from celery import Celery

app = Celery(
    '{{ package_name }}',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
)

@app.task(bind=True, max_retries=3)
def example_task(self, data):
    try:
        # Task logic here
        return {"status": "success"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

---

## Testing Strategy for Features

### Test Categories

1. **Unit Tests**: Test individual functions/classes in isolation
2. **Integration Tests**: Test interactions between components
3. **Contract Tests**: Verify interfaces between modules
4. **E2E Tests**: Test complete user workflows
5. **Performance Tests**: Verify scalability and response times

### Feature-Specific Test Plans

Each feature needs:
- Smoke tests (basic functionality works)
- Happy path tests (normal usage scenarios)
- Error handling tests (edge cases, failures)
- Security tests (vulnerabilities, injection attacks)
- Performance tests (response times, resource usage)

---

## CI/CD Integration Patterns

### GitHub Actions Workflow Template

```yaml
name: Feature Test - {FEATURE_NAME}

on:
  pull_request:
    paths:
      - 'template/files/modules/{feature}/**'
      - '.github/workflows/test-{feature}.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      
      - name: Run feature tests
        run: |
          uv run pytest tests/integration/test_{feature}.py -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: {feature}
```

---

## Documentation Requirements

Every feature must include:

1. **User-Facing Documentation** (`docs/modules/{feature}.md.jinja`):
   - What the feature does
   - When to use it
   - Configuration options
   - Examples
   - Troubleshooting

2. **API Documentation** (for code features):
   - Function/class signatures
   - Parameters and return types
   - Examples
   - Docstrings following NumPy/Google style

3. **Architecture Documentation**:
   - Component diagram
   - Data flow
   - Integration points
   - Security considerations

4. **Operations Documentation**:
   - Deployment requirements
   - Monitoring and alerts
   - Backup/restore procedures
   - Troubleshooting guide

---

## Performance Benchmarks

### Target Metrics by Feature

| Feature | Metric | Target |
|---------|--------|--------|
| API Endpoints | Response time | <200ms (p95) |
| Database Queries | Query time | <50ms (p95) |
| Background Jobs | Queue time | <5s (p95) |
| Container Build | Build time | <5min |
| Test Suite | Total runtime | <10min |
| Static Analysis | Scan time | <2min |

---

## Security Considerations

### Security Checklist (All Features)

- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection where applicable
- [ ] Authentication required for sensitive operations
- [ ] Authorization checks enforced
- [ ] Secrets never committed to git
- [ ] Dependencies scanned for vulnerabilities
- [ ] HTTPS enforced in production
- [ ] Rate limiting on public endpoints
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't include secrets

---

## Dependency Management

### Python Dependencies
- Pin exact versions in `uv.lock`
- Use version ranges in `pyproject.toml` for flexibility
- Group dependencies by feature
- Regular security updates via Dependabot

### Node Dependencies
- Use exact versions in `package-lock.json` / `pnpm-lock.yaml`
- Audit regularly with `npm audit` / `pnpm audit`
- Keep TypeScript and tooling up-to-date

---

## Migration & Upgrade Paths

### Adding New Features to Existing Projects

Each feature should provide:
1. **Migration script** to add feature to existing project
2. **Configuration diff** showing what changed
3. **Breaking changes** documented clearly
4. **Rollback procedure** if migration fails

### Example Migration Script Structure:
```python
# scripts/migrations/add_{feature}.py
def migrate_project(project_path: Path):
    """Add {feature} to existing project."""
    # 1. Check prerequisites
    # 2. Add files
    # 3. Update configs
    # 4. Run tests
    # 5. Generate report
    pass
```

---

## Conclusion

This implementation guide provides tactical, actionable guidance for implementing the features outlined in `NEXT_FEATURES.md`. Each feature should follow these patterns to ensure consistency, quality, and maintainability across the Riso template ecosystem.

Regular updates to this guide will capture learnings and best practices as features are implemented.
