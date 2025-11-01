# Research: Container & Deployment Templates

## Overview

This research phase validates technical choices for production-ready Docker containerization templates. All technologies are well-established with extensive community adoption and proven patterns in the Python/Node.js ecosystem.

## Docker Multi-Stage Builds

**Decision**: Use multi-stage builds with separate builder and runtime stages

**Rationale**:
- **Size optimization**: Final images 50-70% smaller by excluding build tools (gcc, headers, npm cache)
- **Security**: Minimal attack surface by removing compilers and development dependencies from runtime
- **Cache efficiency**: Builder stage caching accelerates incremental builds (uv/pnpm lock file layers)
- **Industry standard**: Adopted by official Python/Node.js Docker guides and major cloud platforms

**Alternatives considered**:
- Single-stage builds: Simpler but result in bloated images (800MB+ vs. <500MB target)
- BuildKit experimental features: Too cutting-edge, compatibility concerns for Docker Engine 24 baseline
- Distroless images: Considered but adds complexity for debugging; opt-in pattern for future enhancement

**References**:
- [Docker Multi-Stage Builds Best Practices](https://docs.docker.com/build/building/multi-stage/)
- [Python Docker Official Images](https://hub.docker.com/_/python) - recommend slim-bookworm for balance
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)

## Base Image Selection

**Decision**: 
- Python: `python:3.11-slim-bookworm` (Debian-based, ~150MB, official)
- Node.js: `node:20-alpine` (Alpine-based, ~180MB, official)
- Docs (Nginx): `nginx:1.25-alpine` (Alpine-based, ~40MB, official)

**Rationale**:
- **slim-bookworm** for Python: Balance of size (~150MB) vs. compatibility (glibc, standard libs)
- **alpine** for Node.js: Smaller footprint (~180MB), compatible with pnpm and modern tooling
- **Pinned with SHA256 digests**: Security best practice, prevents supply-chain attacks
- **Official images**: Trusted sources with automated security patches

**Alternatives considered**:
- `python:3.11-alpine`: Smaller (50MB) but musl libc causes issues with binary wheels (numpy, pandas)
- `python:3.11` (full Debian): Too large (1GB+), unnecessary packages for runtime
- Custom base images: Out of scope (deferred to downstream customization)

**References**:
- [Python Docker Image Comparison](https://pythonspeed.com/articles/base-image-python-docker-images/)
- [Alpine vs. Debian for Python](https://pythonspeed.com/articles/alpine-docker-python/)

## Non-Root User Configuration

**Decision**: Explicit UID 1000:1000, no sudo capabilities

**Rationale**:
- **Kubernetes compatibility**: Many orchestrators expect UID 1000+ for pod security policies
- **File permissions**: Predictable UID enables volume mounts without permission conflicts
- **Security hardening**: Removes sudo, prevents privilege escalation
- **Debuggability**: Consistent user across environments simplifies troubleshooting

**Alternatives considered**:
- Dynamic UID assignment: More flexible but complicates file permissions in dev environments
- Application-specific users ("apiuser"): Additional abstraction without security benefit
- Root with capabilities: Violates least-privilege principle, fails most security scans

**References**:
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

## Health Check Protocol

**Decision**: HTTP health checks at `/health` endpoint, 5s timeout, 3 retries with 2s intervals

**Rationale**:
- **Industry convention**: `/health` is de facto standard (Kubernetes liveness/readiness, ECS, Cloud Run)
- **5s timeout**: Aligns with NFR-006, reasonable for network latency + app startup
- **3 retries with 2s intervals**: Prevents false negatives during startup, total 11s before failure
- **HTTP vs. TCP**: HTTP provides richer diagnostics (200 OK, 503 Service Unavailable, dependency status)

**Alternatives considered**:
- TCP health checks: Simpler but less informative (can't distinguish app health vs. port listening)
- Multi-endpoint checks (/health, /ready, /startup): More sophisticated but adds complexity for P1 MVP
- Single attempt with 30s timeout: Too coarse-grained, delays failure detection

**References**:
- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Docker HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [AWS ECS Health Checks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definition_healthcheck)

## docker-compose Database Services

**Decision**: Conditional PostgreSQL/Redis rendering with explicit `include_databases` copier prompt

**Rationale**:
- **Template-first philosophy**: Databases are infrastructure dependencies, not universal defaults
- **Minimal baseline**: CLI-only and docs-only projects shouldn't bundle unused services
- **Explicit opt-in**: Clear user intent prevents accidental complexity
- **Prompt gating**: Only shown when `api_tracks` includes python/node (contextual relevance)

**Alternatives considered**:
- Always include databases: Bloats simple projects, violates minimal baseline principle
- No database services: Forces manual setup, reduces local dev parity
- Smart detection (Alembic imports): Too magical, breaks determinism, fragile to code changes

**References**:
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)
- [Twelve-Factor App: Backing Services](https://12factor.net/backing-services)

## Container Registry Integration

**Decision**: Primary support for GitHub Container Registry (ghcr.io), template examples for Docker Hub and AWS ECR

**Rationale**:
- **ghcr.io as default**: Free for public/private repos, OIDC authentication via GITHUB_TOKEN, no rate limits
- **Docker Hub**: Template example provided, document rate limit mitigation (authenticated pulls)
- **AWS ECR**: OIDC template with IAM roles, covers enterprise use cases
- **Registry-agnostic design**: Core workflows abstract registry URL/credentials

**Alternatives considered**:
- Docker Hub as default: Rate limiting (100 pulls/6hrs unauthenticated) problematic for CI/CD
- Private registry only: Limits open-source adoption, complicates quickstart
- Multiple registry publishing: Adds complexity, deferred to P3 or downstream customization

**References**:
- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Hub Rate Limiting](https://docs.docker.com/docker-hub/download-rate-limit/)
- [AWS ECR with OIDC](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-push-oidc.html)

## Security Scanning: Trivy vs. Grype

**Decision**: Trivy as primary scanner, Grype as documented alternative

**Rationale**:
- **Trivy**: Faster (10-30s per image), broader coverage (OS packages + language dependencies), SBOM generation
- **GitHub Actions integration**: `aquasecurity/trivy-action@0.20.0` well-maintained, active community
- **Grype alternative**: Some teams prefer Anchore ecosystem, provide template example
- **Fail on HIGH/CRITICAL**: Blocks merge on serious vulnerabilities, MEDIUM allowed with justification

**Alternatives considered**:
- Clair: More heavyweight, requires dedicated service, overkill for template use case
- Snyk: Commercial, API key requirements complicate open-source distribution
- Docker Scout: New, limited GitHub Actions support as of 2025-11

**References**:
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Grype Documentation](https://github.com/anchore/grype)
- [Container Scanning Comparison](https://sysdig.com/blog/container-image-scanning-comparison/)

## Dockerfile Linting: hadolint

**Decision**: hadolint with `.hadolint.yaml` configuration, zero errors required

**Rationale**:
- **Best practices enforcement**: Catches common mistakes (missing EXPOSE, hardcoded secrets, layer optimization)
- **GitHub Actions integration**: `hadolint/hadolint-action@v3` simple to add
- **Configurable**: `.hadolint.yaml` disables problematic rules (DL3008 apt pinning on slim images)
- **Fast**: <5s per Dockerfile, negligible CI overhead

**Alternatives considered**:
- Docker linting built into Buildx: Too new, limited adoption as of 2025-11
- Manual review: Not scalable, inconsistent enforcement
- No linting: Misses optimization opportunities, permits anti-patterns

**References**:
- [hadolint Documentation](https://github.com/hadolint/hadolint)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## Build Caching Strategy

**Decision**: GitHub Actions cache with uv.lock/pnpm-lock.yaml hashing, BuildKit layer caching

**Rationale**:
- **Lock file hashing**: Invalidates cache only when dependencies change (80%+ hit rate expected)
- **BuildKit**: Automatic layer caching, inline cache metadata in pushed images
- **actions/cache@v4**: Proven reliability from feature 004, 10GB cache limit sufficient
- **Cache key structure**: `${{ runner.os }}-docker-${{ hashFiles('**/uv.lock', '**/pnpm-lock.yaml') }}`

**Alternatives considered**:
- Docker layer caching (DLC): Deprecated, BuildKit supersedes
- External cache (S3, registry): More complex, unnecessary for free tier optimization
- No caching: 3-5min builds become 10-15min, violates performance goals

**References**:
- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Docker BuildKit Cache](https://docs.docker.com/build/cache/)

## Summary

All technical decisions validated with production patterns from existing Riso features (004 GitHub Actions, 003 quality suite, 001 template foundation). No unknowns requiring further clarification. Ready to proceed to Phase 1 (data model and contracts).

**Key Takeaways**:
- Multi-stage builds with official base images (python:3.11-slim-bookworm, node:20-alpine)
- Non-root UID 1000:1000 for security and compatibility
- HTTP health checks with /health endpoint (5s timeout, 3 retries)
- Conditional databases via explicit copier prompt
- Trivy security scanning with hadolint linting
- GitHub Container Registry (ghcr.io) as default with OIDC auth
- BuildKit + actions/cache for optimal build performance
