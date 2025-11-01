# Feature Specification: Container & Deployment Templates

**Feature Branch**: `005-container-deployment`  
**Created**: 2025-11-01  
**Status**: Draft  
**Input**: User description: "Container and deployment templates with Docker, docker-compose, and container registry integration for production-ready deployments"

## Clarifications

This feature provides production-ready containerization and deployment infrastructure for Riso-generated projects. It extends the existing CI/CD foundation (feature 004) with Docker build automation, local development orchestration via docker-compose, and container registry publishing patterns.

### Session 2025-11-01

- Q: For containerized applications running as non-root users, what specific user configuration should the Dockerfile templates enforce? → A: Non-root user with explicit UID 1000 and security hardening (USER 1000:1000, no sudo)
- Q: What health check protocol and configuration should be used for API service containers? → A: HTTP health checks with /health endpoint, 5s timeout, 3 retries with 2s interval
- Q: How should docker-compose handle database services (PostgreSQL, Redis) for different project configurations? → A: Conditional database services rendered only when API tracks enabled, with explicit opt-in via copier prompt

**Key Design Decisions:**

1. **Multi-stage Docker builds**: Separate builder and runtime stages to minimize image size and attack surface
2. **Conditional rendering**: Dockerfile templates adapt based on `api_tracks`, `cli_module`, `docs_site`, and `shared_logic` selections
3. **Security-first approach**: Non-root users, minimal base images, vulnerability scanning integration
4. **Local dev parity**: docker-compose configurations mirror production topology for consistent testing
5. **Registry agnostic**: Support GitHub Container Registry (ghcr.io), Docker Hub, and AWS ECR with template examples

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Python API Teams Need Production Containers (Priority: P1) 🎯 MVP

Python teams using FastAPI (or CLI-only projects) need battle-tested Dockerfile templates that produce secure, optimized images suitable for production deployment. The template must handle uv-based dependency installation, multi-stage builds, health checks, and non-root execution.

**Why this priority**: Core container infrastructure enables all deployment scenarios. Without this, teams cannot deploy Riso projects to production environments.

**Independent Test**: Render project with `api_tracks=python`, build container with `docker build -f Dockerfile -t test:latest .`, verify image size <500MB, run container with health check endpoint responding 200 OK, validate non-root user execution with `docker run --rm test:latest id`.

**Acceptance Scenarios**:

1. **Given** a rendered project with `api_tracks=python`, **When** running `docker build`, **Then** build completes in <3 minutes with multi-stage optimization
2. **Given** a built Python API container, **When** starting with `docker run -p 8000:8000`, **Then** health check at `/health` returns 200 OK within 5 seconds
3. **Given** a production Dockerfile, **When** inspecting running container, **Then** process runs as non-root user (UID 1000+)
4. **Given** a Python container image, **When** scanning with Trivy/Grype, **Then** zero HIGH or CRITICAL vulnerabilities reported
5. **Given** CLI-only project (`api_tracks=none`, `cli_module=enabled`), **When** building Dockerfile, **Then** container includes CLI entrypoint and runs `--help` successfully

---

### User Story 2 - Monorepo Teams Need Local Dev Orchestration (Priority: P2)

Teams building full-stack monorepos with Python + Node.js services need docker-compose configurations that orchestrate FastAPI backends, Fastify APIs, Fumadocs documentation sites, and shared dependencies (Redis, PostgreSQL) for local development that mirrors production topology.

**Why this priority**: docker-compose enables realistic local testing of multi-service architectures before deployment. Essential for monorepo layouts with `api_tracks=python+node`.

**Independent Test**: Render project with `api_tracks=python+node` and `docs_site=fumadocs`, run `docker-compose up -d`, verify all services healthy via `docker-compose ps`, test inter-service communication (API → shared logic → database), access Fumadocs at `http://localhost:3000`, validate logs with `docker-compose logs`.

**Acceptance Scenarios**:

1. **Given** a monorepo render, **When** running `docker-compose up`, **Then** all services (Python API, Node API, docs, database) start successfully within 30 seconds
2. **Given** running docker-compose services, **When** Python API makes a call to shared logic, **Then** response includes expected health payload structure
3. **Given** docker-compose with PostgreSQL, **When** FastAPI service starts, **Then** Alembic migrations auto-apply and database schema is current
4. **Given** local development mode, **When** editing source files, **Then** services hot-reload without manual container restarts (volume mounts working)
5. **Given** docker-compose services running, **When** executing `docker-compose down -v`, **Then** all containers and volumes clean up without orphaned resources

---

### User Story 3 - DevOps Teams Publish to Container Registries (Priority: P3)

DevOps teams need CI/CD workflow templates that build, scan, tag, and publish container images to GitHub Container Registry (ghcr.io), Docker Hub, and AWS ECR with semantic versioning, caching, and security scanning before push.

**Why this priority**: Extends feature 004 CI/CD with container publishing automation. Critical for deployment but depends on P1 Dockerfile foundation.

**Independent Test**: Trigger GitHub Actions workflow with `riso-container-publish.yml`, verify image builds with layer caching, Trivy scan passes with zero HIGH/CRITICAL CVEs, image pushes to ghcr.io with tags `latest` and `v1.2.3`, workflow artifacts include SBOM and scan report, image pull succeeds with `docker pull ghcr.io/owner/project:latest`.

**Acceptance Scenarios**:

1. **Given** a GitHub Actions workflow, **When** pushing to main branch, **Then** container builds with BuildKit layer caching and publishes to ghcr.io
2. **Given** a container build workflow, **When** scanning with Trivy, **Then** HIGH/CRITICAL vulnerabilities fail the build with actionable report artifacts
3. **Given** semantic version tag `v1.2.3`, **When** workflow runs, **Then** image tagged with `v1.2.3`, `v1.2`, `v1`, and `latest`
4. **Given** AWS ECR target, **When** providing AWS credentials via secrets, **Then** image publishes to ECR repository with OIDC authentication
5. **Given** multi-architecture build requirement, **When** workflow runs, **Then** images built for `linux/amd64` and `linux/arm64` with manifest lists

---

### Edge Cases

- **Empty project (all modules disabled)**: Dockerfile should provide minimal Python runtime with `uv run python` entrypoint
- **CLI-only mode**: Container CMD defaults to `--help` output; users override with `docker run image command`
- **Docs-only mode**: Fumadocs/Sphinx containers serve static builds via Nginx/Caddy
- **Database services**: PostgreSQL/Redis rendered in docker-compose only when `api_tracks` includes python/node AND explicit copier prompt `include_databases` is enabled; CLI-only and docs-only projects exclude databases
- **Local vs. production Dockerfile**: Single Dockerfile with ARG-based dev/prod modes (or separate `Dockerfile.dev`)
- **Large dependency trees**: Multi-stage builds cache uv/pnpm lock files for faster rebuilds
- **Healthcheck failures**: Container orchestrators (Docker Compose, Kubernetes) respect health check failures and restart policies
- **Registry authentication**: Support both username/password and OIDC token-based auth patterns
- **Monorepo build contexts**: docker-compose uses correct build context paths for each service (`./apps/api-python`, `./apps/api-node`)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (B)**: System MUST generate production-ready Dockerfile templates that adapt to `api_tracks`, `cli_module`, `docs_site`, and `shared_logic` module selections
- **FR-002 (B)**: System MUST implement multi-stage Docker builds with separate builder and runtime stages to minimize final image size
- **FR-003 (B)**: System MUST configure containers to run as non-root users with explicit UID 1000 and GID 1000 (USER 1000:1000), no sudo capabilities, and minimal privileges for security hardening
- **FR-004 (B)**: System MUST include HTTP health check endpoints for API services at `/health` that return 200 OK when ready, with 5-second timeout, 3 retry attempts, and 2-second intervals between retries
- **FR-005 (B)**: System MUST generate `.dockerignore` files that exclude development artifacts, test files, and CI metadata
- **FR-006 (B)**: System MUST provide docker-compose templates for monorepo layouts with service orchestration, networking, and volume management
- **FR-007 (B)**: System MUST render docker-compose with conditional services based on enabled modules (API, docs, shared logic) and explicit database opt-in via copier prompt. Database rendering logic: PostgreSQL and Redis services are rendered if and only if BOTH conditions are true: (1) `api_tracks` is one of `['python', 'node', 'python+node']` (API track enabled), AND (2) `include_databases` prompt equals `'yes'` (explicit user opt-in). Truth table: `api_tracks=none` + `include_databases=yes` → No databases (no API to connect to), `api_tracks=python` + `include_databases=no` → No databases (user declined), `api_tracks=python` + `include_databases=yes` → Render PostgreSQL + Redis, `cli_module=enabled` + `include_databases=yes` → No databases (CLI-only projects don't need databases), `docs_site=fumadocs` + `include_databases=yes` → No databases (docs-only projects don't need databases)
- **FR-008 (O)**: System MUST generate GitHub Actions workflows for container building, scanning, and registry publishing
- **FR-009 (O)**: System MUST integrate Trivy or Grype security scanning into container build workflows with configurable severity thresholds
- **FR-010 (O)**: System MUST support semantic version tagging for container images with the following logic: (1) Primary: Parse Git tags matching semver pattern `v?[0-9]+\.[0-9]+\.[0-9]+` using `git describe --tags`, (2) Validate semver format and extract version components, (3) Generate multiple tags: `latest`, `v{major}.{minor}.{patch}`, `v{major}.{minor}`, `v{major}`, (4) Fallback: If no valid Git tag exists, use `latest` tag only and log warning, (5) For conventional commits: Extract version from commit message if following `chore(release): v1.2.3` pattern
- **FR-011 (O)**: System MUST provide template examples for GitHub Container Registry (ghcr.io), Docker Hub, and AWS ECR authentication
- **FR-012 (O)**: System MUST document container registry authentication patterns (OIDC, username/password, service accounts)
- **FR-013 (B)**: System MUST generate container build documentation covering local builds, docker-compose usage, and CI/CD integration
- **FR-014 (O)**: System MUST support multi-architecture builds (amd64, arm64) via Docker Buildx and GitHub Actions matrix
- **FR-015 (B)**: System MUST validate generated Dockerfiles with hadolint linting during template rendering or CI

### Key Entities *(include if feature involves data)*

- **DockerTemplate**: Rendered Dockerfile.jinja with conditional stages, base image selection, dependency installation, and entrypoint configuration
- **ComposeService**: docker-compose service definition with build context, ports, volumes, health checks, and environment variables
- **ContainerImage**: Built Docker image with metadata (tags, digest, size, scan results, SBOM)
- **RegistryConfig**: Container registry authentication and repository configuration (ghcr.io, Docker Hub, ECR)
- **BuildWorkflow**: GitHub Actions workflow that orchestrates container building, scanning, and publishing
- **HealthCheck**: HTTP or TCP health check configuration for container orchestrators

### Non-Functional Requirements

- **NFR-001 (Performance)**: Docker builds MUST complete in <3 minutes for Python projects and <5 minutes for Python+Node monorepos on GitHub Actions standard runners
- **NFR-002 (Performance)**: Python container images MUST be <500MB, Node.js images <300MB, documentation images <200MB
- **NFR-003 (Performance)**: docker-compose services MUST achieve healthy status within 30 seconds of `docker-compose up`
- **NFR-004 (Security)**: Containers MUST pass Trivy/Grype scans with zero HIGH or CRITICAL vulnerabilities (MEDIUM acceptable with justification)
- **NFR-005 (Security)**: Dockerfiles MUST pass hadolint linting with zero errors (warnings acceptable)
- **NFR-006 (Reliability)**: Container health checks MUST succeed within 5 seconds of service readiness, with 3 retry attempts and 2-second intervals to prevent false negatives during startup
- **NFR-007 (Maintainability)**: Dockerfile templates MUST use official base images (python:3.11-slim-bookworm, node:20-alpine, nginx:1.25-alpine) with pinned SHA256 digests in format `@sha256:<64-char-hex>`, validated by `scripts/ci/validate_dockerfiles.py` to ensure reproducible builds and supply-chain security
- **NFR-008 (Maintainability)**: docker-compose configurations MUST support both local development (hot reload) and CI testing modes
- **NFR-009 (Observability)**: Container workflows MUST upload build logs, scan reports, and SBOMs as GitHub Actions artifacts with 90-day retention
- **NFR-010 (Compatibility)**: Container templates MUST support Docker Engine 24+, Docker Compose v2, and Kubernetes 1.28+ deployment targets

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of sample variants render with valid Dockerfiles that pass hadolint linting (zero errors)
- **SC-002**: All rendered projects successfully build containers with `docker build` completing in target time (Python <3min, Python+Node <5min)
- **SC-003**: Container images meet size targets: Python <500MB, Node.js <300MB, docs <200MB
- **SC-004**: docker-compose configurations start all services successfully and pass health checks within 30 seconds for 95%+ of renders
- **SC-005**: Trivy/Grype security scans pass with zero HIGH/CRITICAL vulnerabilities in 100% of default sample images
- **SC-006**: GitHub Actions container workflows execute successfully in `samples/default`, `samples/full-stack`, and `samples/api-monorepo` with artifact uploads
- **SC-007**: Documentation includes container quickstart, docker-compose usage, registry authentication, and troubleshooting guides validated by render smoke tests
- **SC-008**: Inter-service communication tests pass in docker-compose (API → shared logic → database) for monorepo layouts
- **SC-009**: Container entrypoints correctly invoke CLI commands, API servers, or documentation builds based on module selections
- **SC-010**: 90%+ of users successfully deploy rendered containers to local Docker Desktop, GitHub Container Registry, or cloud platforms without manual Dockerfile edits (measured via: GitHub issue labels tracking deployment failures, optional telemetry in rendered projects with user consent, community survey responses quarterly)

## Principle Compliance Evidence *(mandatory)*

### Template-First Philosophy

- **Containers as optional infrastructure**: Container templates render only when deployment contexts require them; CLI-only projects get minimal containers, API projects get production configs
- **Module composition**: Dockerfiles adapt to enabled modules (CLI, API, docs, shared logic) without manual configuration
- **Render-time validation**: Hadolint checks run during post-generation hooks to catch Dockerfile issues immediately

### Automation-Governed Compliance

- **CI integration**: `scripts/ci/validate_dockerfiles.py` runs hadolint on all rendered Dockerfiles and fails builds on errors
- **Smoke testing**: `scripts/render-samples.sh` builds containers for each variant and validates health checks
- **Security gates**: Trivy scans integrated into container workflows block merges on HIGH/CRITICAL vulnerabilities
- **Evidence capture**: Build logs, scan reports, SBOMs uploaded as artifacts with 90-day retention

### Documented Scaffolds

- **Container quickstart**: `docs/quickstart.md.jinja` expanded with container build commands, docker-compose usage, and health check validation
- **Module documentation**: `docs/modules/containers.md.jinja` covers Dockerfile structure, multi-stage builds, security hardening, and registry publishing
- **Workflow reference**: `.github/context/containers.md` provides extension patterns for custom build steps, multi-arch builds, and private registries
- **Troubleshooting guide**: Common container build failures, health check debugging, registry authentication issues

## Assumptions

- Users have Docker Engine 24+ and Docker Compose v2 installed locally for container builds and orchestration
- GitHub Actions workflows assume access to GitHub Container Registry (ghcr.io) via `GITHUB_TOKEN` or external registries via repository secrets
- Base images (python:3.11-slim, node:20-alpine) remain available and receive security updates from official maintainers
- Trivy or Grype security scanners are available as GitHub Actions marketplace actions or local CLI tools
- Hadolint linting tool is available via GitHub Actions or local installation for Dockerfile validation
- Teams have basic Docker knowledge (build, run, logs, exec) for local development workflows
- Container orchestration platforms (Kubernetes, ECS, Cloud Run) support standard Docker health checks and OCI image specs

## Dependencies & External Inputs

### External Tools & Services

- **Docker Engine 24+**: Container build and runtime (local development)
- **Docker Compose v2**: Multi-service orchestration (local development)
- **Docker Buildx**: Multi-architecture builds and BuildKit features
- **hadolint**: Dockerfile linting (GitHub Actions: `hadolint/hadolint-action@v3`)
- **Trivy**: Vulnerability scanner (GitHub Actions: `aquasecurity/trivy-action@0.20.0`)
- **Grype** (alternative): Vulnerability scanner (Anchore)
- **GitHub Container Registry (ghcr.io)**: Default container registry for GitHub Actions workflows
- **Docker Hub**: Alternative registry with rate limiting considerations
- **AWS ECR**: Alternative registry requiring AWS credentials and OIDC setup

### Internal Dependencies

- **Feature 004 (GitHub Actions)**: Container workflows extend existing CI/CD infrastructure with build/publish jobs
- **Feature 003 (Quality Suite)**: Security scanning integrates with quality gates (Trivy/Grype → artifacts → merge checks)
- **Feature 001 (Template Foundation)**: Module catalog and smoke testing infrastructure
- **copier.yml prompts**: Existing `api_tracks`, `cli_module`, `docs_site`, `shared_logic` selections drive Dockerfile rendering; new `include_databases` prompt controls PostgreSQL/Redis services in docker-compose (only shown when `api_tracks` includes python or node)

### Base Images

- **Python**: `python:3.11-slim-bookworm` (Debian-based, ~150MB, official)
- **Node.js**: `node:20-alpine` (Alpine-based, ~180MB, official)
- **Nginx** (docs): `nginx:1.25-alpine` (Alpine-based, ~40MB, official)
- **PostgreSQL** (optional): `postgres:16-alpine` (docker-compose development)
- **Redis** (optional): `redis:7-alpine` (docker-compose development)

## Risks & Mitigations

### Risk 1: Large Image Sizes

**Impact**: Images exceeding 1GB slow deployment pipelines and increase registry storage costs.

**Mitigation**: Multi-stage builds with aggressive layer caching, minimal base images (alpine/slim), `.dockerignore` exclusions, size validation in CI (<500MB Python, <300MB Node).

### Risk 2: Security Vulnerabilities in Base Images

**Impact**: Inherited CVEs from base images fail security scans and block deployments.

**Mitigation**: Pin base images with SHA256 digests, integrate Trivy/Grype scanning in CI, provide documentation for base image updates, monitor upstream security advisories.

### Risk 3: Docker Compose Complexity for Monorepos

**Impact**: Orchestrating 5+ services (APIs, docs, databases) leads to port conflicts, volume mount issues, and startup races.

**Mitigation**: Use health checks with `depends_on` conditions, document service startup order, provide troubleshooting guide for common issues, test in CI.

### Risk 4: Registry Authentication Failures

**Impact**: GitHub Actions workflows fail to push images due to expired tokens, permission issues, or rate limiting.

**Mitigation**: Document OIDC authentication for ghcr.io, provide token refresh patterns, implement retry logic with exponential backoff, test in sample renders.

### Risk 5: Hadolint False Positives

**Impact**: Overly strict linting rules block valid Dockerfiles or require excessive ignore comments.

**Mitigation**: Configure hadolint with `.hadolint.yaml` to disable problematic rules (DL3008, DL3009), document linting configuration, allow warnings vs. errors distinction.

### Risk 6: Multi-Architecture Build Times

**Impact**: Building for amd64 + arm64 doubles CI job duration, exceeding free tier limits.

**Mitigation**: Multi-arch builds as optional (P3), use GitHub Actions cache for cross-compilation toolchains, document when multi-arch is necessary vs. optional.

## Out of Scope

- **Kubernetes manifests**: Helm charts, kustomize configs, and K8s deployment YAMLs are separate features (consider for feature 006)
- **Container orchestration beyond docker-compose**: ECS task definitions, Cloud Run configs, Fly.io toml files are separate features
- **Database migration automation**: Alembic auto-migrations on container startup belong in feature 006 (database migrations)
- **Secrets management**: Vault integration, AWS Secrets Manager, encrypted env files are separate features
- **Service mesh integration**: Istio, Linkerd, Consul configs are out of scope
- **Custom base images**: Building organization-specific base images is a downstream customization pattern
- **Container registry mirroring**: Harbor, Nexus, Artifactory integrations are out of scope
- **Image signing and attestation**: Cosign, Notary v2, SLSA provenance are advanced security features for later
- **Monitoring integration**: Prometheus exporters, OpenTelemetry instrumentation belong in feature 008 (monitoring/observability)
- **CI platform support beyond GitHub Actions**: GitLab CI, Jenkins, CircleCI container workflows are out of scope

---

**Next Steps**: Run `/speckit.clarify` to validate requirements coverage, then `/speckit.plan` to generate implementation plan, followed by `/speckit.tasks` for phased task breakdown.
