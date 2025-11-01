# Data Model: Container & Deployment Templates

## Entity: DockerfileTemplate

**Description**: Rendered Dockerfile.jinja with conditional stages, base image selection, dependency installation, and entrypoint configuration based on enabled modules.

**Fields**:
- `template_path` (string, required): Path to source template (`template/files/shared/.docker/Dockerfile.jinja`)
- `base_image` (enum: `python:3.11-slim-bookworm`, `node:20-alpine`, `nginx:1.25-alpine`, required): Base image selection
- `base_image_digest` (string, required): SHA256 digest for pinned security
- `stages` (list[BuildStage], required): Multi-stage build configuration (builder, runtime)
- `user_config` (UserConfig, required): Non-root user configuration (UID 1000:1000)
- `health_check` (HealthCheck, optional): HTTP health check configuration (only for API services)
- `entrypoint` (list[string], required): Container entrypoint command
- `modules_enabled` (map[string, boolean], required): Module inclusion flags (`cli_module`, `api_tracks`, `docs_site`, `shared_logic`)
- `rendered_size` (integer, optional): Final image size in MB (captured during smoke tests)

**Relationships**:
- Rendered from `ComposeService` when docker-compose orchestration enabled
- References `HealthCheck` entity for API services
- Validated by `BuildWorkflow` during CI

**Validation Rules**:
- `base_image_digest` must be valid SHA256 hash
- `user_config.uid` must be >= 1000
- `stages` must include at least one runtime stage
- `health_check` required when `api_tracks` includes python or node
- `rendered_size` must meet NFR-002 targets (Python <500MB, Node <300MB)

---

## Entity: BuildStage

**Description**: Individual stage in multi-stage Docker build (builder or runtime).

**Fields**:
- `name` (enum: `builder`, `runtime`, required): Stage identifier
- `base_image` (string, required): FROM image for this stage
- `install_commands` (list[string], required): Dependency installation commands
- `copy_operations` (list[CopyOperation], required): COPY commands (from builder→runtime or context→stage)
- `environment_vars` (map[string, string], optional): ENV declarations
- `working_directory` (string, required): WORKDIR path
- `cache_mounts` (list[string], optional): BuildKit cache mount paths

**Relationships**:
- Part of `DockerfileTemplate` stages list
- Runtime stage may COPY from builder stage

**Validation Rules**:
- `name=builder` must include package manager commands (uv sync, pnpm install)
- `name=runtime` must COPY from builder or context
- `cache_mounts` paths must be valid absolute paths

---

## Entity: CopyOperation

**Description**: Docker COPY command with source/destination and optional stage reference.

**Fields**:
- `source_path` (string, required): Source path (relative to build context or stage)
- `destination_path` (string, required): Destination path in image
- `from_stage` (string, optional): Source stage name (for multi-stage COPY)
- `chown` (string, optional): Ownership for copied files (`1000:1000`)

**Validation Rules**:
- `from_stage` must reference existing BuildStage name if specified
- `chown` should match `UserConfig.uid:gid` for consistency

---

## Entity: UserConfig

**Description**: Non-root user configuration for container security.

**Fields**:
- `username` (string, required): User name (default: `appuser`)
- `uid` (integer, required): User ID (1000)
- `gid` (integer, required): Group ID (1000)
- `home_directory` (string, required): User home path (`/home/appuser`)
- `sudo_enabled` (boolean, required): Whether sudo is installed (always false for production)

**Relationships**:
- Part of `DockerfileTemplate` configuration

**Validation Rules**:
- `uid` and `gid` must be exactly 1000 (per clarification session)
- `sudo_enabled` must be false for production builds
- `username` must not be `root`

---

## Entity: HealthCheck

**Description**: HTTP health check configuration for API service containers.

**Fields**:
- `endpoint` (string, required): Health check URL path (`/health`)
- `protocol` (enum: `HTTP`, required): Health check protocol
- `port` (integer, required): Port to check (8000 for FastAPI, 3000 for Fastify)
- `timeout_seconds` (integer, required): Request timeout (5)
- `retries` (integer, required): Number of retry attempts (3)
- `interval_seconds` (integer, required): Interval between retries (2)
- `start_period_seconds` (integer, optional): Grace period for app startup (10)

**Relationships**:
- Part of `DockerfileTemplate` for API services
- Implemented by health endpoint code in Python/Node API modules

**Validation Rules**:
- `endpoint` must start with `/`
- `timeout_seconds` must be 5 (per clarification session)
- `retries` must be 3 (per clarification session)
- `interval_seconds` must be 2 (per clarification session)
- `port` must match API service port configuration

---

## Entity: ComposeService

**Description**: docker-compose service definition with build context, ports, volumes, health checks, and environment variables.

**Fields**:
- `service_name` (string, required): Service identifier (`api-python`, `api-node`, `docs-fumadocs`, `postgres`, `redis`)
- `build_context` (string, optional): Path to build context (`.` for single package, `./apps/api-python` for monorepo)
- `dockerfile_path` (string, optional): Path to Dockerfile relative to context
- `image_name` (string, optional): Pre-built image name (for databases)
- `ports` (list[PortMapping], required): Port exposures
- `volumes` (list[VolumeMount], optional): Volume mounts for persistence or hot reload
- `environment` (map[string, string], optional): Environment variables
- `health_check` (HealthCheck, optional): Service health check configuration
- `depends_on` (list[ServiceDependency], optional): Service dependencies with conditions
- `networks` (list[string], required): Docker networks (`default`, `backend`, etc.)

**Relationships**:
- References `DockerfileTemplate` via `dockerfile_path`
- References `HealthCheck` for API services
- References `DatabaseService` via `depends_on`

**Validation Rules**:
- At least one of `build_context` or `image_name` must be specified
- `ports` must not conflict within compose configuration
- `depends_on` services must exist in same compose file
- Database services (`postgres`, `redis`) only rendered when `include_databases=yes`

---

## Entity: PortMapping

**Description**: Port mapping for docker-compose service.

**Fields**:
- `host_port` (integer, required): Port on host machine
- `container_port` (integer, required): Port inside container
- `protocol` (enum: `tcp`, `udp`, required): Network protocol (default: tcp)

**Validation Rules**:
- `host_port` must be unique across all services in compose file
- `container_port` must match application configuration

---

## Entity: VolumeMount

**Description**: Volume mount for docker-compose service (persistence or development hot reload).

**Fields**:
- `host_path` (string, required): Path on host (relative or absolute)
- `container_path` (string, required): Mount point in container
- `mode` (enum: `rw`, `ro`, required): Read-write or read-only
- `type` (enum: `bind`, `volume`, `tmpfs`, required): Mount type

**Validation Rules**:
- `type=bind` requires valid `host_path` (checked at runtime)
- `type=volume` requires volume declaration in top-level `volumes` section

---

## Entity: ServiceDependency

**Description**: Dependency relationship between docker-compose services with health check conditions.

**Fields**:
- `service_name` (string, required): Name of dependent service
- `condition` (enum: `service_started`, `service_healthy`, required): Wait condition

**Validation Rules**:
- `service_name` must reference existing service in compose file
- `condition=service_healthy` requires dependent service to have `health_check` configured

---

## Entity: DatabaseService

**Description**: Pre-configured database service for docker-compose (PostgreSQL or Redis).

**Fields**:
- `database_type` (enum: `postgres`, `redis`, required): Database type
- `version` (string, required): Database version (`16-alpine`, `7-alpine`)
- `environment` (map[string, string], required): Database configuration (credentials, database name)
- `volumes` (list[VolumeMount], required): Data persistence volumes
- `ports` (list[PortMapping], required): Port exposures (5432 for postgres, 6379 for redis)

**Relationships**:
- Rendered as `ComposeService` when `include_databases=yes` AND `api_tracks` includes python/node
- Referenced by API services via `ServiceDependency`

**Validation Rules**:
- Only rendered when `include_databases` copier prompt is `yes`
- `include_databases` prompt only shown when `api_tracks` includes python or node
- Credentials must use environment variable substitution (not hardcoded)

---

## Entity: ContainerImage

**Description**: Built Docker image with metadata (tags, digest, size, scan results, SBOM).

**Fields**:
- `image_name` (string, required): Full image name with registry (`ghcr.io/owner/project`)
- `tags` (list[string], required): Image tags (`latest`, `v1.2.3`, `v1.2`, `v1`, commit SHA)
- `digest` (string, required): SHA256 digest of image manifest
- `size_mb` (integer, required): Image size in megabytes
- `build_time_seconds` (integer, required): Build duration
- `scan_results` (ScanResults, optional): Vulnerability scan output
- `sbom` (string, optional): Software Bill of Materials (SPDX or CycloneDX format)
- `built_at` (datetime, required): Build timestamp
- `git_commit` (string, required): Git commit SHA of source code

**Relationships**:
- Built by `BuildWorkflow` during CI/CD
- Published to `RegistryConfig`
- Scanned by `ScanResults`

**Validation Rules**:
- `size_mb` must meet NFR-002 targets (Python <500MB, Node <300MB, docs <200MB)
- `tags` must include at least `latest` for main branch builds
- `scan_results` must have zero HIGH/CRITICAL vulnerabilities (NFR-004)

---

## Entity: ScanResults

**Description**: Vulnerability scan results from Trivy/Grype.

**Fields**:
- `scanner` (enum: `trivy`, `grype`, required): Scanner tool used
- `scan_time` (datetime, required): When scan was performed
- `vulnerabilities` (list[Vulnerability], required): Detected vulnerabilities
- `summary` (VulnerabilitySummary, required): Counts by severity
- `passed` (boolean, required): Whether scan passed severity threshold

**Relationships**:
- Part of `ContainerImage` metadata
- Generated by `BuildWorkflow`

**Validation Rules**:
- `passed` must be true for merge to succeed
- `summary.critical` and `summary.high` must be 0 for `passed=true`

---

## Entity: Vulnerability

**Description**: Individual vulnerability detected by scanner.

**Fields**:
- `vulnerability_id` (string, required): CVE identifier or scanner-specific ID
- `severity` (enum: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`, required): Severity level
- `package_name` (string, required): Affected package
- `installed_version` (string, required): Currently installed version
- `fixed_version` (string, optional): Version that fixes vulnerability
- `description` (string, required): Vulnerability description

**Validation Rules**:
- `severity` of CRITICAL or HIGH blocks merge (per NFR-004)
- `fixed_version` should be specified when available for remediation guidance

---

## Entity: VulnerabilitySummary

**Description**: Aggregated vulnerability counts by severity.

**Fields**:
- `critical` (integer, required): Count of CRITICAL vulnerabilities
- `high` (integer, required): Count of HIGH vulnerabilities
- `medium` (integer, required): Count of MEDIUM vulnerabilities
- `low` (integer, required): Count of LOW vulnerabilities
- `unknown` (integer, required): Count of UNKNOWN severity

**Validation Rules**:
- `critical` + `high` must equal 0 for scan to pass (NFR-004)

---

## Entity: RegistryConfig

**Description**: Container registry authentication and repository configuration.

**Fields**:
- `registry_type` (enum: `ghcr`, `dockerhub`, `ecr`, required): Registry provider
- `registry_url` (string, required): Registry base URL (`ghcr.io`, `docker.io`, `<aws-account>.dkr.ecr.<region>.amazonaws.com`)
- `repository_name` (string, required): Repository path within registry
- `auth_method` (enum: `oidc`, `username_password`, `iam_role`, required): Authentication method
- `credentials_source` (enum: `github_token`, `secrets`, `aws_sts`, required): Where credentials are retrieved

**Relationships**:
- Target for `ContainerImage` publishing
- Configured in `BuildWorkflow`

**Validation Rules**:
- `registry_type=ghcr` should use `auth_method=oidc` with `github_token`
- `registry_type=ecr` should use `auth_method=iam_role` with `aws_sts`
- `registry_url` must be valid URL format

---

## Entity: BuildWorkflow

**Description**: GitHub Actions workflow that orchestrates container building, scanning, and publishing.

**Fields**:
- `workflow_name` (string, required): Workflow file name (`riso-container-build.yml`, `riso-container-publish.yml`)
- `triggers` (list[WorkflowTrigger], required): Events that trigger workflow (push, pull_request, schedule)
- `jobs` (list[WorkflowJob], required): Jobs in workflow (build, scan, publish, multi-arch)
- `caching_strategy` (CacheConfig, required): BuildKit and actions/cache configuration
- `artifact_retention_days` (integer, required): How long to retain artifacts (90 days)

**Relationships**:
- Builds `ContainerImage`
- Generates `ScanResults`
- Publishes to `RegistryConfig`
- Extends feature 004 GitHub Actions infrastructure

**Validation Rules**:
- Must include hadolint linting job before build
- Must include Trivy/Grype scanning job after build
- `artifact_retention_days` must be 90 (per NFR-009)

---

## Entity: WorkflowTrigger

**Description**: Event that triggers a GitHub Actions workflow.

**Fields**:
- `event_type` (enum: `push`, `pull_request`, `workflow_dispatch`, `schedule`, required): Trigger event
- `branches` (list[string], optional): Branch filters (`main`, `develop`)
- `paths` (list[string], optional): Path filters for path-based triggering
- `cron_schedule` (string, optional): Cron expression for scheduled runs

**Validation Rules**:
- `event_type=schedule` requires `cron_schedule`
- `paths` should include Dockerfile and related files for efficiency

---

## Entity: WorkflowJob

**Description**: Individual job within a GitHub Actions workflow.

**Fields**:
- `job_name` (string, required): Job identifier (`hadolint`, `build`, `scan`, `publish`)
- `runs_on` (string, required): Runner label (`ubuntu-latest`, `macos-latest`)
- `steps` (list[WorkflowStep], required): Job execution steps
- `needs` (list[string], optional): Job dependencies (must complete first)
- `if_condition` (string, optional): Conditional execution expression

**Relationships**:
- Part of `BuildWorkflow`
- May depend on other jobs via `needs`

**Validation Rules**:
- `job_name=publish` must have `needs=[build, scan]` to ensure validation before push
- `steps` must include checkout, login, and registry-specific actions

---

## Entity: WorkflowStep

**Description**: Individual step within a workflow job.

**Fields**:
- `step_name` (string, required): Step identifier
- `action` (string, optional): GitHub Actions marketplace action (`actions/checkout@v4`, `docker/build-push-action@v5`)
- `run_command` (string, optional): Shell command to execute
- `environment_vars` (map[string, string], optional): Environment variables for step

**Validation Rules**:
- At least one of `action` or `run_command` must be specified
- `action` versions should be pinned (e.g., `@v4`, not `@latest`)

---

## Entity: CacheConfig

**Description**: Caching configuration for Docker builds and GitHub Actions.

**Fields**:
- `cache_key_template` (string, required): Cache key template with variables (`${{ runner.os }}-docker-${{ hashFiles('**/uv.lock', '**/pnpm-lock.yaml') }}`)
- `cache_paths` (list[string], required): Paths to cache (Docker BuildKit cache, layer cache)
- `cache_type` (enum: `gha`, `inline`, `registry`, required): Cache backend type
- `max_cache_size_gb` (integer, required): Maximum cache size (10GB for actions/cache)

**Relationships**:
- Part of `BuildWorkflow` configuration

**Validation Rules**:
- `cache_key_template` must include runner.os and lock file hashes
- `max_cache_size_gb` must be ≤10 for GitHub Actions free tier

---

## State Transitions

### ContainerImage Lifecycle

1. **Building**: Dockerfile rendered → docker build executing
2. **Built**: Image created with digest and tags
3. **Scanning**: Trivy/Grype analyzing image layers
4. **Scanned**: Scan results available (may fail if vulnerabilities found)
5. **Publishing**: Image pushing to registry
6. **Published**: Image available at registry URL with tags

**Failure States**:
- **Build Failed**: Dockerfile syntax error, dependency installation failure
- **Scan Failed**: HIGH/CRITICAL vulnerabilities detected
- **Publish Failed**: Registry authentication failure, network error

### BuildWorkflow Execution

1. **Triggered**: Workflow event (push, PR, schedule)
2. **Linting**: hadolint validates Dockerfile syntax
3. **Building**: Multi-stage build with caching
4. **Scanning**: Trivy/Grype security scan
5. **Publishing** (if main branch): Push to registry with tags
6. **Completed**: Artifacts uploaded, notifications sent

**Conditional Flows**:
- **PR builds**: Lint + Build + Scan (no publish)
- **Main branch**: Lint + Build + Scan + Publish
- **Tagged releases**: Lint + Build + Scan + Publish with semantic version tags
