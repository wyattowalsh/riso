# Research: GitHub Actions CI/CD Workflows

**Feature**: 004-github-actions-workflows  
**Date**: 2025-10-30  
**Status**: Complete

## Overview

This document consolidates research findings for implementing GitHub Actions workflow templates in the Riso project template. Research focused on best practices for matrix builds, caching strategies, workflow naming conventions, and integration with existing quality tooling from feature 003.

## Decision 1: Workflow File Naming Convention

**Decision**: Use distinctive `riso-` prefix for all template-generated workflows

**Rationale**:
- Prevents conflicts with custom workflows downstream projects may add
- Clear provenance - developers immediately recognize template-provided workflows
- Enables safe copier updates - template workflows can be updated without overwriting custom files
- Aligns with best practices from Cookiecutter, Copier, and other template ecosystems

**Alternatives Considered**:
- Generic names (`ci.yml`, `test.yml`) - **Rejected**: High conflict potential, poor copier update experience
- UUID-based names - **Rejected**: Loses human readability, poor developer experience
- Version suffixes (`ci-v1.yml`) - **Rejected**: Doesn't solve conflict problem, adds versioning complexity

**Implementation**:
- Main workflow: `riso-quality.yml`
- Matrix workflow: `riso-matrix.yml`
- Cache utilities: `riso-cache.yml` (if needed as separate workflow)
- Dependency updates: `riso-deps-update.yml`

**References**:
- GitHub Actions naming best practices: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#name
- Copier conflict resolution patterns: https://copier.readthedocs.io/en/stable/creating/#handle-file-conflicts

---

## Decision 2: Cache Key Strategy

**Decision**: Use hash of lock files with OS/Python version prefix: `${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('**/uv.lock', '**/pnpm-lock.yaml') }}`

**Rationale**:
- Automatic invalidation when dependencies change (lock file hash changes)
- Stable across commits with unchanged dependencies (high cache hit rate)
- Prevents cross-platform cache corruption (OS prefix)
- Prevents cross-version cache corruption (Python version prefix)
- Aligns with GitHub Actions caching best practices and uv's design philosophy

**Alternatives Considered**:
- Git commit SHA - **Rejected**: Extremely low cache hit rate (every commit misses)
- Branch name only - **Rejected**: Risk of stale dependencies when lock files change
- Time-based rotation - **Rejected**: Arbitrary invalidation unrelated to actual dependency changes
- pyproject.toml hash - **Rejected**: Doesn't capture resolved dependencies; version ranges cause issues

**Implementation**:
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      ~/.cache/pip
      node_modules
      .pnpm-store
    key: ${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('**/uv.lock', '**/pnpm-lock.yaml') }}
    restore-keys: |
      ${{ runner.os }}-py${{ matrix.python-version }}-
      ${{ runner.os }}-
```

**Performance Target**: 70%+ cache hit rate, <10 seconds cache restoration, 50%+ install time reduction

**References**:
- GitHub Actions caching guide: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
- uv caching architecture: https://github.com/astral-sh/uv/blob/main/ARCHITECTURE.md#caching

---

## Decision 3: Matrix Build Configuration

**Decision**: Test across Python 3.11, 3.12, 3.13 with fail-fast disabled and required status checks on all jobs

**Rationale**:
- Covers all supported Python versions per constitution (excludes 3.8-3.10 as uv requires 3.11+)
- Fail-fast disabled allows all matrix jobs to complete, showing full compatibility picture
- All jobs marked as required enforces "any single failure blocks merge" policy from clarifications
- Parallel execution maximizes feedback speed (8 minutes total vs 20+ sequential)

**Alternatives Considered**:
- Include Python 3.10 - **Rejected**: uv doesn't support it, adds unnecessary coverage
- Fail-fast enabled - **Rejected**: Hides multi-version issues, reduces debugging information
- Optional matrix jobs - **Rejected**: Defeats purpose of version compatibility guarantee
- Single Python version - **Rejected**: Misses version-specific bugs, defeats feature purpose

**Implementation**:
```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.11', '3.12', '3.13']
    
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
  - name: Install uv
    run: curl -LsSf https://astral.sh/uv/install.sh | sh
  - name: Run quality checks
    run: |
      uv sync
      uv run pytest
      uv run ruff check .
      uv run mypy .
```

**Branch Protection**: All matrix jobs (`python-3.11-quality`, `python-3.12-quality`, `python-3.13-quality`) marked as required checks

**References**:
- GitHub matrix builds: https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
- Python version support: https://devguide.python.org/versions/

---

## Decision 4: Retry Logic for Service Outages

**Decision**: Implement workflow-level retry with exponential backoff (3 attempts) using `uses: nick-fields/retry@v3`

**Rationale**:
- Distinguishes transient service issues from code failures
- Exponential backoff prevents thundering herd during outages
- 3 attempts balances recovery probability vs. CI runtime impact
- Reusable GitHub Action simplifies implementation across workflows
- Status badge shows "Service Issue" after exhausting retries

**Alternatives Considered**:
- Immediate failure - **Rejected**: Frustrating developer experience during GitHub outages
- Infinite retry - **Rejected**: Can block PRs indefinitely, wastes Actions minutes
- Manual retry only - **Rejected**: Poor automation experience, requires human intervention
- Custom retry script - **Rejected**: Reinvents wheel, maintenance burden

**Implementation**:
```yaml
- name: Run quality checks with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    exponential_backoff: true
    command: |
      uv sync
      uv run task quality
```

**Error Messaging**: After 3 failures, workflow sets output `service_issue: true` and displays custom status badge

**References**:
- GitHub Actions retry action: https://github.com/nick-fields/retry
- Exponential backoff patterns: https://cloud.google.com/iot/docs/how-tos/exponential-backoff

---

## Decision 5: Node.js Track Parallelization

**Decision**: Run Python and Node.js CI jobs in parallel using separate workflow jobs with no dependency between them

**Rationale**:
- Maximizes feedback speed (halves total CI time for full-stack projects)
- Independent failure reporting (clear which track failed)
- Reflects architectural independence of Python and Node codebases
- Aligns with clarification decision for "always parallel when both enabled"
- Each track has independent timeout (10/20 minutes)

**Alternatives Considered**:
- Sequential (Python first) - **Rejected**: Doubles CI time, provides no debugging benefit
- Node only after Python passes - **Rejected**: Delays feedback, wastes developer time
- Configurable via prompt - **Rejected**: Adds complexity without clear use case
- Single job with sequential steps - **Rejected**: Loses granular failure reporting

**Implementation**:
```yaml
jobs:
  python-quality:
    name: Python Quality Checks
    runs-on: ubuntu-latest
    steps: [...]
  
  node-quality:
    name: Node.js Quality Checks
    runs-on: ubuntu-latest
    if: ${{ contains(fromJSON('[\"python+node\"]'), env.API_TRACKS) }}
    steps: [...]
```

**Status Reporting**: Both jobs contribute to overall PR status; either failure blocks merge

**References**:
- GitHub parallel jobs: https://docs.github.com/en/actions/using-workflows/about-workflows#creating-dependent-jobs
- Conditional job execution: https://docs.github.com/en/actions/using-jobs/using-conditions-to-control-job-execution

---

## Decision 6: Artifact Retention and Structure

**Decision**: Upload artifacts with 90-day retention using structured naming: `{workflow}-{python-version}-{run-id}`

**Rationale**:
- 90 days balances debugging needs vs storage costs (aligns with constitution and SC-006)
- Structured naming enables filtering by workflow, Python version, or run
- Separate artifacts per matrix job enables parallel debugging
- JUnit XML + coverage HTML covers testing and coverage use cases
- Logs captured for failure forensics

**Alternatives Considered**:
- 30-day retention - **Rejected**: Insufficient for compliance auditing
- Single merged artifact - **Rejected**: Loses per-version granularity
- Unlimited retention - **Rejected**: Excessive storage costs for free tier
- 180-day retention - **Rejected**: Overkill for template projects, increases costs

**Implementation**:
```yaml
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results-py${{ matrix.python-version }}-${{ github.run_id }}
    path: |
      test-results.xml
      htmlcov/
      .coverage
    retention-days: 90
```

**Artifact Types**:
- `test-results-py{version}`: JUnit XML + coverage reports
- `quality-logs-py{version}`: Ruff/mypy/pylint output
- `workflow-metadata`: Run duration, cache hit stats, resource usage

**References**:
- GitHub artifacts: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts
- JUnit XML format: https://github.com/testmoapp/junitxml

---

## Decision 7: Workflow Validation Strategy

**Decision**: Use actionlint in post-generation hook to validate generated workflow YAML before project use

**Rationale**:
- Catches syntax errors before workflows ever run (fail-fast at render time)
- Validates GitHub Actions syntax including action versions, job dependencies
- Lightweight CLI tool, easy to integrate into hooks
- Provides actionable error messages for template maintainers
- Constitution-compliant: single validation attempt, explicit failure path

**Alternatives Considered**:
- No validation - **Rejected**: Syntax errors only discovered on first push, poor UX
- GitHub Actions validation API - **Rejected**: Requires authentication, network dependency
- Custom YAML parser - **Rejected**: Doesn't understand GitHub Actions semantics
- yamllint only - **Rejected**: Too generic, misses Actions-specific issues

**Implementation**:
```python
# template/hooks/post_gen_project.py
import subprocess
import sys

def validate_workflows():
    result = subprocess.run(
        ['actionlint', '.github/workflows/*.yml'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Workflow validation failed:\n{result.stderr}")
        sys.exit(1)
    print("✅ Workflows validated successfully")
```

**Fallback**: If actionlint not installed, emit warning but allow render to proceed (constitution: single attempt, non-blocking)

**References**:
- actionlint: https://github.com/rhysd/actionlint
- GitHub Actions syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions

---

## Decision 8: Quality Profile Integration

**Decision**: Read `quality_profile` from copier answers and conditionally enable strict checks in workflows

**Rationale**:
- Reuses existing quality infrastructure from feature 003
- Workflows execute same commands as local development (`make quality`)
- Strict profile adds extended timeout (20min) and additional checks
- Maintains parity between local and CI quality gates
- No duplicate configuration - workflows respect `pyproject.toml` settings

**Alternatives Considered**:
- Separate workflow files - **Rejected**: Duplication, maintenance burden
- Hardcoded profile - **Rejected**: Ignores project configuration
- Profile override via workflow env - **Rejected**: CI/local parity breaks
- No profile support - **Rejected**: Defeats feature 003 design

**Implementation**:
```yaml
env:
  QUALITY_PROFILE: {{ quality_profile }}

jobs:
  quality:
    timeout-minutes: {% if quality_profile == 'strict' %}20{% else %}10{% endif %}
    steps:
      - name: Run quality checks
        run: |
          uv sync
          QUALITY_PROFILE={{ quality_profile }} uv run task quality
```

**Conditional Checks**: Strict profile adds `pylint --fail-under=9.0`, extended coverage thresholds

**References**:
- Feature 003 quality profiles: `../003-code-quality-integrations/spec.md`
- Environment variable propagation: https://docs.github.com/en/actions/learn-github-actions/variables

---

## Decision 9: Module-Conditional Workflow Logic

**Decision**: Use Jinja2 conditionals to skip module-specific checks when modules disabled

**Rationale**:
- Avoids running CLI tests when CLI module not enabled (saves CI time)
- Prevents false failures from missing module code
- Maintains clean workflow YAML (conditions resolved at render time, not runtime)
- Aligns with template composition principle (constitution III)

**Alternatives Considered**:
- Runtime conditionals - **Rejected**: Complex workflow logic, poor readability
- Always run all checks - **Rejected**: Wastes CI minutes, causes false failures
- Separate workflow per module - **Rejected**: Excessive file proliferation
- Manual enable/disable - **Rejected**: Error-prone, poor automation

**Implementation**:
```yaml
{% if cli_module == 'enabled' %}
- name: Test CLI module
  run: uv run pytest tests/test_cli.py
{% endif %}

{% if 'node' in api_tracks %}
- name: Test Node.js API
  run: |
    cd api-node
    pnpm test
{% endif %}
```

**Modules Tracked**: `cli_module`, `api_tracks`, `mcp_module`, `docs_site`, `shared_logic`

**References**:
- Jinja2 conditionals: https://jinja.palletsprojects.com/en/3.1.x/templates/#if
- Module catalog: `../../template/files/shared/module_catalog.json.jinja`

---

## Decision 10: Timeout Configuration

**Decision**: 10-minute timeout for standard profile, 20-minute for strict profile, with early termination on cache hits

**Rationale**:
- Respects GitHub Actions free tier limits (2000 minutes/month private repos)
- Prevents runaway jobs from consuming quota
- Standard profile timeout aligns with SC-002 (<6 minutes expected)
- Strict profile allows for extended static analysis without false timeouts
- Early termination (<3 minutes on cache hit) improves developer experience

**Alternatives Considered**:
- Fixed 30-minute timeout - **Rejected**: Wastes free tier quota on hung jobs
- No timeout - **Rejected**: Jobs can run indefinitely, blocking PRs
- Same timeout for both profiles - **Rejected**: Strict checks legitimately need more time
- 5-minute standard - **Rejected**: Too aggressive, risks false timeouts on cache miss

**Implementation**:
```yaml
jobs:
  quality:
    timeout-minutes: {% if quality_profile == 'strict' %}20{% else %}10{% endif %}
    
  matrix:
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    timeout-minutes: 15  # Slightly longer for matrix builds
```

**Escalation**: If jobs consistently timeout, workflow emits actionable error suggesting cache debugging or self-hosted runner

**References**:
- GitHub Actions pricing: https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions
- Timeout syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idtimeout-minutes

---

## Open Questions

None - all clarification questions resolved in spec.md clarifications section.

## Next Steps

1. Proceed to Phase 1: Design & Contracts
2. Generate data-model.md with workflow entities (WorkflowConfiguration, MatrixBuildResult, CacheManifest, ArtifactMetadata)
3. Create contracts for workflow generation (Jinja2 template inputs/outputs)
4. Author quickstart.md with workflow setup instructions
5. Update agent context files with GitHub Actions patterns

---

**Research Complete**: 2025-10-30  
**Approved By**: Implementation planning agent  
**Next Phase**: Phase 1 - Design & Contracts
