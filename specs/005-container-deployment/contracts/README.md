# Container & Deployment Contracts

This directory contains API contracts and interface definitions for container-related functionality.

## Health Check Endpoints

### FastAPI Health Check

**File**: `health_check_fastapi.py`

**Contract**:
```python
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str | None = None
    
@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """HTTP health check endpoint for container orchestrators.
    
    Returns:
        HealthResponse with status="healthy" when service is ready
    
    Response Codes:
        200: Service is healthy and ready to accept requests
        503: Service is starting or degraded (not yet implemented)
    """
    return HealthResponse(status="healthy", service="api-python")
```

**Contract Guarantees**:
- Endpoint path: `/health` (immutable)
- Response time: <100ms (p95)
- Status code: 200 OK when healthy
- Content-Type: `application/json`
- No authentication required (public endpoint)
- No side effects (idempotent)

---

### Fastify Health Check

**File**: `health_check_fastify.ts`

**Contract**:
```typescript
interface HealthResponse {
  status: string;
  service: string;
  version?: string;
}

app.get<{ Reply: HealthResponse }>('/health', async (request, reply) => {
  /**
   * HTTP health check endpoint for container orchestrators.
   * 
   * @returns HealthResponse with status="healthy" when service is ready
   * 
   * Response Codes:
   *   200: Service is healthy and ready to accept requests
   *   503: Service is starting or degraded (not yet implemented)
   */
  return reply.code(200).send({
    status: 'healthy',
    service: 'api-node',
  });
});
```

**Contract Guarantees**:
- Endpoint path: `/health` (immutable)
- Response time: <100ms (p95)
- Status code: 200 OK when healthy
- Content-Type: `application/json`
- No authentication required (public endpoint)
- No side effects (idempotent)

---

## Dockerfile Template Interface

### Conditional Module Rendering

**Contract**: Dockerfile.jinja must adapt based on copier prompts

**Variables**:
- `api_tracks` (str): One of `"none"`, `"python"`, `"node"`, `"python+node"`
- `cli_module` (str): One of `"enabled"`, `"disabled"`
- `docs_site` (str): One of `"fumadocs"`, `"sphinx-shibuya"`, `"docusaurus"`, `"none"`
- `shared_logic` (str): One of `"enabled"`, `"disabled"`

**Rendering Rules**:
```jinja2
{%- if api_tracks | contains("python") %}
# Python API stage
FROM python:3.11-slim-bookworm AS builder-python
# ... builder logic ...
{%- endif %}

{%- if api_tracks | contains("node") %}
# Node.js API stage
FROM node:20-alpine AS builder-node
# ... builder logic ...
{%- endif %}

{%- if cli_module == "enabled" %}
# CLI entrypoint
CMD ["uv", "run", "python", "-m", "{{ package_name }}.cli", "--help"]
{%- endif %}
```

**Contract Guarantees**:
- Minimal baseline: `api_tracks=none` + `cli_module=disabled` produces <200MB Python runtime
- API projects: Include health check endpoint and EXPOSE declaration
- CLI projects: Set CMD to CLI entrypoint with --help default
- Docs projects: Multi-stage build with Nginx/Caddy serving static files

---

## docker-compose Template Interface

### Service Orchestration

**Contract**: docker-compose.yml.jinja must orchestrate services based on enabled modules

**Variables**:
- `api_tracks` (str): Determines which API services to include
- `docs_site` (str): Determines docs service configuration
- `include_databases` (bool): Controls PostgreSQL/Redis inclusion

**Service Definitions**:
```yaml
services:
  {%- if api_tracks | contains("python") %}
  api-python:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 2s
      timeout: 5s
      retries: 3
    {%- if include_databases %}
    depends_on:
      postgres:
        condition: service_healthy
    {%- endif %}
  {%- endif %}
  
  {%- if include_databases and (api_tracks | contains("python") or api_tracks | contains("node")) %}
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-riso}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dev_password}
      POSTGRES_DB: ${POSTGRES_DB:-riso_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-riso}"]
      interval: 2s
      timeout: 5s
      retries: 3
  {%- endif %}
```

**Contract Guarantees**:
- Database services only rendered when `include_databases=yes` AND `api_tracks` includes API
- Health checks configured with 5s timeout, 3 retries, 2s intervals
- Service dependencies use `condition: service_healthy` for proper startup order
- Environment variables use `${VAR:-default}` pattern for flexibility
- Volume persistence for databases declared in top-level `volumes` section

---

## GitHub Actions Workflow Interface

### Container Build Workflow

**File**: `riso-container-build.yml.jinja`

**Contract**: Workflow must lint, build, scan, and upload artifacts

**Jobs**:
1. **hadolint**: Lint Dockerfile with hadolint
2. **build**: Build container with BuildKit caching
3. **scan**: Scan with Trivy for vulnerabilities
4. **upload-artifacts**: Upload build logs, SBOM, scan reports

**Artifact Structure**:
```text
artifacts/
├── build-log.txt           # Docker build output
├── image-sbom.json         # SPDX or CycloneDX SBOM
├── trivy-scan-report.json  # Vulnerability scan results
└── image-metadata.json     # Tags, digest, size, build time
```

**Contract Guarantees**:
- hadolint must pass with zero errors (warnings allowed)
- Trivy scan must pass with zero HIGH/CRITICAL vulnerabilities
- Artifacts retained for 90 days
- Build fails fast on linting or scanning errors
- Cache hit rate >70% for incremental builds

---

### Container Publish Workflow

**File**: `riso-container-publish.yml.jinja`

**Contract**: Workflow must build, scan, tag, and publish to registry

**Jobs**:
1. **build-and-scan**: Build + scan (reuses build workflow logic)
2. **publish-ghcr**: Publish to GitHub Container Registry
3. **publish-dockerhub** (optional): Publish to Docker Hub
4. **publish-ecr** (optional): Publish to AWS ECR

**Tagging Strategy**:
```bash
# For main branch push:
- latest
- <commit-sha-7-chars>

# For semantic version tag (v1.2.3):
- v1.2.3
- v1.2
- v1
- latest
```

**Contract Guarantees**:
- OIDC authentication for ghcr.io via `GITHUB_TOKEN`
- Image pushed only after successful scan (zero HIGH/CRITICAL)
- Multi-platform builds (amd64, arm64) optional via matrix
- Retry logic with exponential backoff (3 attempts)
- SBOM and scan reports attached as release artifacts

---

## Validation Scripts

### hadolint Configuration

**File**: `.hadolint.yaml.jinja`

**Contract**:
```yaml
ignored:
  - DL3008  # Pin versions in apt-get install (not applicable to slim images)
  - DL3009  # Delete apt-get lists (handled by slim base)
  
failure-threshold: error  # Warnings allowed, errors block build
```

---

### Dockerfile Validation Script

**File**: `scripts/ci/validate_dockerfiles.py`

**Contract**: Must validate all rendered Dockerfiles with hadolint

**Function Signature**:
```python
def validate_dockerfile(dockerfile_path: Path) -> ValidationResult:
    """Run hadolint on Dockerfile and return validation result.
    
    Args:
        dockerfile_path: Path to Dockerfile to validate
        
    Returns:
        ValidationResult with errors, warnings, and pass/fail status
        
    Raises:
        FileNotFoundError: If dockerfile_path does not exist
        ValidationError: If hadolint not installed
    """
```

**Exit Codes**:
- 0: All Dockerfiles pass hadolint (zero errors)
- 1: One or more Dockerfiles have hadolint errors
- 2: hadolint not installed or execution error

---

## Integration Points

### Feature 004 GitHub Actions Extension

**Contract**: Container workflows extend existing CI/CD infrastructure

**Shared Components**:
- `actions/checkout@v4`: Repository checkout
- `actions/setup-python@v5`: Python environment (for validation scripts)
- `actions/cache@v4`: BuildKit and layer caching
- `actions/upload-artifact@v4`: Artifact uploads (90-day retention)

**New Components**:
- `docker/setup-buildx-action@v3`: BuildKit configuration
- `docker/login-action@v3`: Registry authentication
- `docker/build-push-action@v5`: Container build and push
- `aquasecurity/trivy-action@0.20.0`: Vulnerability scanning
- `hadolint/hadolint-action@v3`: Dockerfile linting

**Contract Guarantees**:
- Workflows follow feature 004 naming convention (`riso-*`)
- Retry logic consistent with feature 004 (3 attempts, exponential backoff)
- Artifact retention matches feature 004 (90 days)
- Cache strategy aligns with feature 004 (lock file hashing)

---

## Summary

All contracts define clear interfaces for:
- Health check endpoints (Python/Node)
- Dockerfile conditional rendering
- docker-compose service orchestration
- GitHub Actions workflows
- Validation scripts
- Integration with existing features

Contracts guarantee compatibility with Docker Engine 24+, Kubernetes 1.28+, and GitHub Actions free tier constraints.
