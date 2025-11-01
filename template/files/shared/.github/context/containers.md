# Container & Deployment Context

## Purpose

This document provides comprehensive context for GitHub Copilot when working with container-related code in Riso-generated projects. It covers extension patterns, troubleshooting, and advanced configurations.

## Container Architecture

### Multi-Stage Builds

All Dockerfiles use multi-stage builds:
- **Builder stage**: Install dependencies with package managers (uv, pnpm)
- **Runtime stage**: Copy artifacts, run as non-root UID 1000:1000

**Why**: Reduces final image size by 50-70%, improves security by removing build tools.

### Base Image Selection

- **Python**: `python:3.11-slim-bookworm` - Balance of size (~150MB) vs compatibility
- **Node.js**: `node:20-alpine` - Minimal footprint (~180MB)
- **Nginx** (docs): `nginx:1.25-alpine` - Ultra-light (~40MB)

**Pinning**: Always use SHA256 digests in production (see Phase 8 polish tasks).

## Registry Authentication

### GitHub Container Registry (OIDC)

**Recommended** - No secrets required:

```yaml
permissions:
  packages: write

- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**Access**: Images visible at `https://github.com/orgs/<org>/packages`

### Docker Hub (Username/Password)

Configure GitHub secrets:
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Personal access token (not password)

```yaml
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**Rate limits**: 100 pulls/6hrs (unauthenticated), 200 pulls/6hrs (authenticated free tier)

### AWS ECR (IAM Role OIDC)

**Recommended for AWS** - No long-lived credentials:

```yaml
permissions:
  id-token: write

- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ secrets.AWS_REGION }}

- uses: aws-actions/amazon-ecr-login@v2

- uses: docker/build-push-action@v5
  with:
    push: true
    tags: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ secrets.AWS_REGION }}.amazonaws.com/my-app:latest
```

**Setup**: Create IAM role with trust policy for GitHub OIDC provider.

## Extension Patterns

### Multi-Architecture Builds

Build for both amd64 and arm64:

```yaml
- uses: docker/setup-qemu-action@v3

- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
```

**Note**: Increases build time 2-3x but enables Apple Silicon, AWS Graviton support.

### Private Registry Integration

For self-hosted registries (Harbor, JFrog Artifactory):

```yaml
- uses: docker/login-action@v3
  with:
    registry: registry.company.com
    username: ${{ secrets.REGISTRY_USERNAME }}
    password: ${{ secrets.REGISTRY_TOKEN }}

- uses: docker/build-push-action@v5
  with:
    push: true
    tags: registry.company.com/team/my-app:latest
```

### Custom Build Arguments

Pass build-time variables:

```dockerfile
ARG BUILD_VERSION=dev
ARG BUILD_COMMIT=unknown

LABEL org.opencontainers.image.version="${BUILD_VERSION}"
LABEL org.opencontainers.image.revision="${BUILD_COMMIT}"
```

```yaml
- uses: docker/build-push-action@v5
  with:
    build-args: |
      BUILD_VERSION=${{ github.ref_name }}
      BUILD_COMMIT=${{ github.sha }}
```

## Troubleshooting

### Build Context Size Issues

**Symptom**: Slow uploads to Docker daemon

**Diagnosis**:
```bash
docker build --no-cache --progress=plain . 2>&1 | grep "Sending build context"
```

**Solutions**:
1. Audit `.dockerignore` - ensure `node_modules/`, `.git/`, `*.pyc` excluded
2. Move large files outside project root
3. Use `.dockerignore` patterns like `**/__pycache__`, `**/*.egg-info`

### BuildKit Cache Misses

**Symptom**: Every build reinstalls dependencies

**Diagnosis**: Check cache mount paths match package manager

**Solutions**:
- Python: `--mount=type=cache,target=/root/.cache/uv`
- Node: `--mount=type=cache,target=/root/.pnpm-store`
- Ensure lock files (`uv.lock`, `pnpm-lock.yaml`) are copied before install

### Inter-Service Communication Failures

**Symptom**: API cannot connect to PostgreSQL/Redis

**Diagnosis**:
```bash
docker-compose exec api-python ping postgres
docker-compose exec api-python nc -zv postgres 5432
```

**Solutions**:
1. Verify `depends_on` with `service_healthy` condition
2. Check service names match in environment variables (`DATABASE_URL=postgresql://...@postgres:5432`)
3. Ensure services on same network (`networks: [my-network]`)
4. Wait for health checks before making requests

### Security Scan Failures

**Symptom**: Trivy reports HIGH/CRITICAL vulnerabilities

**Solutions**:
1. Update base images: `docker pull python:3.11-slim-bookworm`
2. Regenerate lock files: `uv lock --upgrade`, `pnpm update`
3. Check CVE database: `https://nvd.nist.gov/vuln/search`
4. If false positive, add to `.trivyignore`:
   ```
   # False positive: Dev dependency only
   CVE-2024-12345
   ```

## Performance Optimization

### Layer Caching Strategies

**Copy lock files first** - Invalidate cache only when dependencies change:

```dockerfile
# Good: Lock file layer cached separately
COPY pyproject.toml uv.lock ./
RUN uv sync

COPY src/ ./src/
```

```dockerfile
# Bad: Any source change invalidates dependency cache
COPY . .
RUN uv sync
```

### BuildKit Cache Backends

**Local** (default):
```yaml
cache-from: type=local,src=/tmp/.buildx-cache
cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

**GitHub Actions** (recommended):
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

**Registry** (best for team):
```yaml
cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache
cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache,mode=max
```

### Parallel Builds

Build multiple services simultaneously:

```yaml
strategy:
  matrix:
    service: [api-python, api-node, docs-fumadocs]
  max-parallel: 3
```

## Compliance & Governance

### SBOM Generation

Software Bill of Materials included automatically:

```yaml
- uses: docker/build-push-action@v5
  with:
    sbom: true
    provenance: true
```

**Access**: View in image manifest or download artifact.

### Vulnerability Scanning Policies

Enforce thresholds:
- **CRITICAL**: Zero tolerance, block merge
- **HIGH**: Zero tolerance, block merge
- **MEDIUM**: Allowed with justification in PR
- **LOW**: Informational only

**Override** for false positives:
```yaml
- uses: aquasecurity/trivy-action@0.20.0
  with:
    severity: 'CRITICAL,HIGH'
    ignore-unfixed: true  # Ignore if no fix available
```

### Image Signing (Advanced)

Use Cosign for supply-chain security:

```yaml
- uses: sigstore/cosign-installer@v3

- name: Sign image
  run: |
    cosign sign --yes ghcr.io/${{ github.repository }}:latest
```

## CI/CD Integration

### Matrix Testing Across Variants

Test all sample combinations:

```yaml
strategy:
  matrix:
    variant: [default, cli-docs, api-monorepo, full-stack]
```

### Conditional Workflow Execution

Skip container jobs if no Dockerfile changes:

```yaml
on:
  pull_request:
    paths:
      - 'Dockerfile'
      - 'docker-compose.yml'
      - 'src/**'
      - 'apps/**'
```

### Artifact Retention

Store build logs, SBOMs, scan reports for 90 days:

```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 90
```

## Development Workflow

### Local Development with Hot Reload

1. Uncomment volume mounts in `docker-compose.yml`
2. Use development Dockerfile: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`
3. Changes auto-reload (uvicorn --reload, pnpm dev)

### Debugging in Container

**Python** (debugpy):
```dockerfile
EXPOSE 5678
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "..."]
```

**Node.js** (inspector):
```dockerfile
EXPOSE 9229
CMD ["node", "--inspect=0.0.0.0:9229", "apps/api-node/dist/main.js"]
```

Then attach from VS Code with `.vscode/launch.json`.

## Migration Guide

### From Existing Dockerfiles

1. Backup existing `Dockerfile` to `Dockerfile.legacy`
2. Regenerate project with `copier update`
3. Merge custom logic from legacy file
4. Test with `docker-compose up`
5. Validate with `python scripts/ci/validate_dockerfiles.py .`

### Adding Databases to Existing Projects

1. Regenerate with `include_databases=yes`:
   ```bash
   copier update --data include_databases=yes
   ```
2. Update `.env` with credentials
3. Create database migrations (Alembic for Python, Prisma for Node)
4. Run `docker-compose up -d postgres redis`

## References

- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- BuildKit Documentation: https://docs.docker.com/build/buildkit/
- Trivy Scanning: https://aquasecurity.github.io/trivy/
- GitHub Actions OIDC: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
