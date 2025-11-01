# Feature Specification: GitHub Actions CI/CD Workflows

**Feature Branch**: `004-github-actions-workflows`  
**Created**: 2025-10-30  
**Status**: Draft  
**Input**: User description: "GitHub Actions CI/CD Workflows - Implement comprehensive GitHub Actions workflow templates that automate testing, quality checks, building, and deployment for rendered projects. Include matrix builds for Python versions, parallel job execution, caching strategies, and artifact management."

## Clarifications

### Session 2025-10-30

- Q: When a matrix build shows divergent results across Python versions (e.g., tests pass on 3.11 and 3.12 but fail on 3.13), how should the overall PR status be determined? → A: All matrix jobs must pass - Any single version failure blocks merge (strictest quality gate)
- Q: When a workflow encounters a GitHub Actions service outage or runner availability issue, how should the system communicate this to developers? → A: Retry with exponential backoff and show "Service Issue" badge if persistent after 3 attempts
- Q: When a rendered project has custom workflow files that conflict with template-provided workflows (e.g., both define `.github/workflows/ci.yml`), what should happen during a copier update? → A: Template workflows use distinctive names (e.g., `riso-quality.yml`) to avoid conflicts; document extension pattern
- Q: For projects with Node.js API tracks, when should Node.js CI jobs run relative to Python jobs? → A: Always parallel when both enabled - Maximum speed, independent failure reporting
- Q: What cache key strategy should workflows use to balance cache hit rate with freshness when dependencies change? → A: Hash of lock files with OS/Python version prefix - Automatic invalidation on dependency changes, stable otherwise

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Quality Validation on PR (Priority: P1)

A developer opens a pull request on a rendered project and GitHub Actions automatically runs the quality suite (ruff, mypy, pylint, pytest) with clear pass/fail status, blocking merge when checks fail.

**Why this priority**: This is the foundational CI capability that prevents broken code from entering the main branch. Without this, the quality tools installed in 003 remain manual, reducing their effectiveness.

**Independent Test**: Create a test PR with intentional lint/type errors in a rendered project, observe GitHub Actions workflows execute automatically, and verify the PR shows failed checks with actionable error messages.

**Acceptance Scenarios**:

1. **Given** a rendered project with GitHub Actions workflows enabled, **When** a developer opens a PR with clean code, **Then** all quality checks pass and the PR shows green status.
2. **Given** a rendered project with quality workflows, **When** a PR introduces a ruff violation, **Then** the workflow fails and displays the specific lint error in the GitHub UI.
3. **Given** a failing quality workflow, **When** the developer fixes the code and pushes, **Then** the workflow re-runs automatically and passes.

---

### User Story 2 - Matrix Testing Across Python Versions (Priority: P2)

A project maintainer relies on automated matrix builds to test their package across multiple Python versions (3.11, 3.12, 3.13) simultaneously, catching version-specific compatibility issues before release.

**Why this priority**: Python version compatibility is critical for library/package projects. Matrix testing catches issues that single-version testing misses without requiring manual multi-version setup.

**Independent Test**: Render a project with matrix testing enabled, introduce a Python 3.13-specific breaking change, and verify that only the 3.13 matrix job fails while others pass, clearly showing the compatibility issue.

**Acceptance Scenarios**:

1. **Given** a rendered project with matrix testing enabled, **When** CI runs on a commit, **Then** workflows execute in parallel for each configured Python version (3.11, 3.12, 3.13).
2. **Given** matrix builds running in parallel, **When** code uses a feature deprecated in Python 3.13, **Then** only the Python 3.13 job fails with clear error messaging and the overall PR status shows failure (all matrix jobs must pass).
3. **Given** successful matrix builds, **When** viewing the GitHub Actions summary, **Then** the UI shows individual status for each Python version with execution times.

---

### User Story 3 - Dependency Caching for Fast Builds (Priority: P2)

A contributor pushes frequent commits during development and benefits from cached dependencies that reduce CI runtime from 5 minutes to under 90 seconds, accelerating feedback loops.

**Why this priority**: Developer productivity depends on fast feedback. Caching is essential for making CI practical for iterative development rather than just a pre-merge gate.

**Independent Test**: Run CI twice on identical dependency specifications, compare execution times, and verify the second run completes significantly faster (50%+ speedup) due to cache hits.

**Acceptance Scenarios**:

1. **Given** a rendered project with caching enabled, **When** CI runs for the first time, **Then** dependencies install fully and the cache saves successfully with a key based on lock file hash and OS/Python version.
2. **Given** a cached CI run, **When** a subsequent commit runs with unchanged lock files, **Then** dependency installation completes in under 10 seconds via cache restoration using the matching cache key.
3. **Given** a PR that updates `pyproject.toml` dependencies, **When** CI runs, **Then** the lock file hash changes, cache key misses, and dependencies reinstall fresh.

---

### User Story 4 - Artifact Collection and Retention (Priority: P3)

A team lead reviews CI artifacts (test results, coverage reports, build logs) uploaded by workflows, enabling post-mortem debugging and compliance auditing for up to 90 days.

**Why this priority**: Artifacts provide forensic capability for debugging flaky tests and maintaining audit trails. Less critical than running tests, but essential for production-grade CI.

**Independent Test**: Trigger a workflow run, wait for completion, navigate to GitHub Actions artifacts section, and verify downloadable artifacts exist with correct retention policy.

**Acceptance Scenarios**:

1. **Given** a workflow that generates test results, **When** the workflow completes, **Then** JUnit XML and coverage HTML artifacts upload to GitHub Actions with 90-day retention.
2. **Given** uploaded artifacts, **When** a maintainer views the workflow run page, **Then** artifact download links appear with file sizes and expiration dates.
3. **Given** a failed workflow run, **When** reviewing artifacts, **Then** detailed error logs capture the full failure context for debugging.

---

### User Story 5 - Optional Node.js Track CI Integration (Priority: P3)

A full-stack project with both Python and Node API tracks benefits from automated Node.js linting, type checking, and testing that runs in parallel with Python jobs when `api_tracks` includes `node`, maximizing feedback speed.

**Why this priority**: Ensures Node.js modules receive the same quality guarantees as Python modules. Lower priority because it's conditional on optional module selection.

**Independent Test**: Render a project with `api_tracks=python+node`, verify both Python and Node CI jobs appear in the workflow, and confirm they execute in parallel (not sequentially) with independent pass/fail status.

**Acceptance Scenarios**:

1. **Given** a rendered project with Node API enabled, **When** CI runs, **Then** separate workflow jobs execute for ESLint, TypeScript checking, and Vitest tests.
2. **Given** parallel Python and Node jobs, **When** Python tests pass but Node tests fail, **Then** the overall PR status shows failure with clear indication of which track failed.
3. **Given** a project with only Python API enabled, **When** CI runs, **Then** Node.js jobs are skipped automatically without errors.

---

### Edge Cases

- What happens when a workflow runs on a fork with limited GitHub Actions minutes (workflows MUST be efficient to respect free tier; document optimization strategies including aggressive timeouts and cache reuse patterns)?
- How does the system handle workflow failures due to GitHub Actions service outages (retry with exponential backoff per FR-006b, show "Service Issue" badge after 3 failed attempts per FR-006c)?
- What if a rendered project has custom workflow files that conflict with template workflows (template uses distinctive names like `riso-quality.yml` to avoid conflicts per FR-016; document extension pattern)?
- How are workflows maintained when template updates add new CI capabilities (provide copier update guidance in upgrade-guide.md.jinja)?
- What happens when matrix builds across Python versions have divergent results (all matrix jobs must pass per FR-002; any single failure blocks merge)?

---

## Terminology Clarifications

**actionlint**: YAML/workflow validation tool used to check GitHub Actions workflow syntax and semantics. Runs as a command-line tool during post-generation validation.

**workflow_validator.py**: Python wrapper script in `scripts/hooks/` that invokes actionlint and formats output for template hooks. Not a separate validator—merely an integration layer for actionlint.

Usage: Throughout this specification, "actionlint validation" refers to validation performed via the workflow_validator.py wrapper, which in turn calls the actionlint binary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (B)**: Template MUST generate GitHub Actions workflow files (`.github/workflows/*.yml`) that execute quality suite checks (ruff, mypy, pylint, pytest, coverage) automatically on pull requests and pushes to main branch.
- **FR-002 (B)**: Workflows MUST implement matrix builds testing code across Python 3.11, 3.12, and 3.13 with parallel job execution, where all matrix jobs must pass for overall success.
- **FR-003 (B)**: Workflows MUST use cache keys based on hash of lock files (`uv.lock`, `pnpm-lock.yaml`) with OS/Python version prefix to restore dependencies when lock files are unchanged, achieving at least 50% install time reduction via cache hits.
- **FR-004 (B)**: Workflows MUST upload test results (JUnit XML), coverage reports (HTML/XML), and quality logs as GitHub Actions artifacts with 90-day retention.
- **FR-005 (B)**: Workflow status MUST block PR merges when quality checks fail, integrating with GitHub branch protection rules.
- **FR-006 (B)**: Workflows MUST provide comprehensive error handling including:
  - **(a)** Clear, actionable error messages in GitHub UI when jobs fail, including tool output and remediation hints
  - **(b)** Retry logic with exponential backoff (3 attempts) for transient failures
  - **(c)** "Service Issue" status badge when GitHub Actions service outages persist after retry exhaustion
- **FR-007 (O)**: When `api_tracks` includes `node`, workflows MUST generate Node.js CI jobs running pnpm-based linting (ESLint), type checking (TypeScript), and testing (Vitest) that execute in parallel with Python jobs for maximum speed.
- **FR-008 (O)**: When `api_tracks` includes `node`, workflows MUST implement pnpm caching to accelerate Node dependency installation.
- **FR-009 (B)**: Template MUST include workflow documentation in rendered project README explaining how to view CI status, download artifacts, and debug failures.
- **FR-010 (B)**: Workflows MUST respect the `quality_profile` setting, executing standard or strict quality checks based on project configuration.
- **FR-011 (B)**: Template automation MUST validate generated workflows using actionlint or similar YAML/workflow validators before render completion.
- **FR-012 (B)**: Workflows MUST include conditional logic to skip optional module checks (CLI, API, MCP, docs) when those modules are disabled in project configuration.
- **FR-013 (B)**: Workflows MUST set appropriate timeout limits (10 minutes for standard profiles, 20 minutes for strict) to prevent runaway jobs consuming Actions minutes.
- **FR-014 (O)**: Template MUST provide sample workflow for scheduled dependency update checks that run weekly and create automated PRs when updates are available.
- **FR-015 (B)**: Workflows MUST expose environment variables allowing downstream projects to customize behavior (Python versions, cache keys, timeout values) without editing workflow YAML directly.
- **FR-016 (B)**: Template-generated workflows MUST use distinctive names (e.g., `riso-quality.yml`, `riso-matrix.yml`) to prevent conflicts with custom workflows; documentation MUST describe extension patterns for downstream projects.

### Template Prompts & Variants

- **Prompt**: `ci_platform` — **Type**: Baseline — **Default**: `github-actions` — **Implication**: Enables GitHub Actions workflow generation; future may support GitLab CI, CircleCI, etc. Initial implementation focuses exclusively on GitHub Actions.
- **Existing Prompt**: `quality_profile` — **Modified**: Workflows respect `standard` vs `strict` profile settings to match quality tooling configuration.
- **Existing Prompt**: `api_tracks` — **Modified**: When includes `node`, workflows add parallel Node.js CI jobs with pnpm caching.
- **Existing Prompt**: `cli_module`, `mcp_module`, `docs_site`, `shared_logic` — **Modified**: Workflows conditionally execute module-specific validation when modules are enabled.

### Key Entities

- **WorkflowConfiguration**: Represents generated `.github/workflows/*.yml` files with job definitions, matrix specifications, caching strategies, and artifact upload configs.
- **MatrixBuildResult**: Captures per-Python-version test outcomes, durations, and artifact locations for trend tracking.
- **CacheManifest**: Defines cache key patterns using hash of lock files (`uv.lock`, `pnpm-lock.yaml`) with OS/Python version prefix (e.g., `ubuntu-22.04-py3.11-<lock-hash>`) for automatic invalidation on dependency changes while maintaining stability across commits.
- **ArtifactMetadata**: Stores artifact names, sizes, expiration dates, and download URLs for governance dashboards.
- **WorkflowValidationReport**: Documents workflow YAML lint results, syntax checks, and conditional logic verification from pre-render hooks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of rendered projects have passing GitHub Actions workflows within 5 minutes of first push to a new repository.
- **SC-002**: CI execution time for baseline quality checks completes in under 3 minutes on cache hits and under 6 minutes on cache misses across GitHub-hosted runners.
- **SC-003**: Matrix builds across Python 3.11, 3.12, 3.13 complete in under 8 minutes via parallel execution compared to 20+ minutes sequential execution.
- **SC-004**: Dependency caching achieves 70%+ cache hit rate across project commits, reducing redundant installation time by 50%+ compared to no caching.
- **SC-005**: 100% of workflow failures provide actionable error messages in GitHub UI that maintainers can understand without downloading logs.
- **SC-006**: Artifact uploads succeed in 98%+ of workflow runs with files accessible for the full 90-day retention period.
- **SC-007**: Downstream projects report 90%+ satisfaction with CI setup in "works out of the box" metric tracked via support tickets and GitHub Discussions.

## Assumptions

- GitHub Actions remains the primary CI/CD platform for Python/Node.js open source projects; rendered projects use GitHub for hosting.
- GitHub-hosted runners (ubuntu-latest) provide sufficient performance for baseline testing; projects can self-host runners if needed but template optimizes for free tier.
- Python 3.11, 3.12, 3.13 represent the supported version range; older versions (3.8-3.10) excluded based on uv and modern tooling requirements.
- Projects accept 90-day artifact retention as sufficient for debugging and compliance; longer retention requires custom configuration.
- Template consumers tolerate opinionated workflow structures; customization happens through environment variables and conditional logic rather than workflow file editing.

## Dependencies & External Inputs

- GitHub Actions service availability and pricing model (free tier provides 2,000 minutes/month for private repos, unlimited for public).
- Official GitHub Actions marketplace actions: `actions/checkout`, `actions/setup-python`, `actions/cache`, `actions/upload-artifact`.
- Workflow YAML linting tools (actionlint) for pre-render validation.
- Existing quality tools from feature 003 (ruff, mypy, pylint, pytest, coverage).
- Documentation from features 001-003 describing module validation commands and smoke test expectations.

## Risks & Mitigations

- **Risk**: Workflows consume excessive GitHub Actions minutes on free tier projects. **Mitigation**: Set aggressive timeout limits (10 min standard, 20 min strict), optimize caching, and document cost awareness in README.
- **Risk**: Matrix builds create confusing PR status when some Python versions fail. **Mitigation**: Provide clear job naming (`Python 3.11 Quality`, `Python 3.12 Quality`) and summary tables in workflow output.
- **Risk**: Cache invalidation logic fails, causing stale dependencies to be used. **Mitigation**: Cache keys incorporate lock file hashes; document manual cache clearing procedures.
- **Risk**: Template workflow updates conflict with downstream customizations. **Mitigation**: Document extension points (custom jobs, env vars) and provide copier update guidance for workflow changes.
- **Risk**: Node.js CI jobs double workflow runtime for full-stack projects. **Mitigation**: Parallelize Python and Node jobs; use pnpm caching aggressively; set independent timeouts.

## Out of Scope

- Support for non-GitHub CI platforms (GitLab CI, CircleCI, Jenkins) deferred to future features.
- Custom runner configurations or self-hosted runner setup beyond documentation links.
- Deployment workflows (covered in Phase 3, feature for deployment targets).
- Advanced workflow features like manual approval gates, environment-specific deployments, or release automation (covered in separate features).
- Integration with external quality dashboards or code coverage services beyond artifact uploads (teams can layer these on top).
