# Data Model: GitHub Actions CI/CD Workflows

**Feature**: 004-github-actions-workflows  
**Date**: 2025-10-30  
**Status**: Complete

## Overview

This document defines the data entities, their relationships, and state transitions for the GitHub Actions workflow feature. The model captures workflow configurations, execution results, caching state, and artifact metadata required for evidence-driven governance.

## Core Entities

### WorkflowConfiguration

Represents a generated GitHub Actions workflow YAML file with all job definitions, matrix specifications, caching strategies, and artifact upload configurations.

**Attributes**:

- `workflow_name` (string, required): Distinctive workflow name (e.g., `riso-quality`, `riso-matrix`)
- `workflow_path` (string, required): Relative path in rendered project (e.g., `.github/workflows/riso-quality.yml`)
- `trigger_events` (list[string], required): Events that trigger workflow (`pull_request`, `push`, `schedule`)
- `target_branches` (list[string], required): Branches workflow applies to (default: `['main']`)
- `jobs` (list[JobDefinition], required): Job configurations within workflow
- `env_variables` (dict[string, string], optional): Workflow-level environment variables
- `quality_profile` (enum['standard', 'strict'], required): Quality profile setting from copier answers
- `timeout_minutes` (int, required): Maximum workflow execution time
- `enabled_modules` (dict[string, bool], required): Module flags (`cli_module`, `api_tracks`, etc.)
- `validation_status` (enum['pending', 'valid', 'invalid'], required): actionlint validation result
- `validation_errors` (list[string], optional): Validation error messages if invalid
- `generated_at` (datetime, required): Timestamp of workflow generation
- `template_version` (string, required): Riso template version that generated workflow

**Uniqueness**: `workflow_name` is unique per rendered project

**Relationships**:

- Has many `JobDefinition` (composition)
- References `CacheManifest` for caching configuration
- Produces `MatrixBuildResult` when matrix strategy defined

**State Transitions**:

```
pending → valid (actionlint passes)
pending → invalid (actionlint fails)
```

**Validation Rules**:

- `workflow_name` must start with `riso-` prefix
- `timeout_minutes` must be 10 (standard) or 20 (strict)
- At least one job required
- `quality_profile` must match copier answers

---

### JobDefinition

Represents a single job within a GitHub Actions workflow, including its steps, matrix configuration, and execution environment.

**Attributes**:

- `job_id` (string, required): Unique job identifier within workflow (e.g., `python-quality`, `node-quality`)
- `job_name` (string, required): Human-readable job name displayed in GitHub UI
- `runs_on` (string, required): Runner environment (default: `ubuntu-latest`)
- `strategy` (MatrixStrategy, optional): Matrix configuration if applicable
- `steps` (list[StepDefinition], required): Sequential steps to execute
- `timeout_minutes` (int, optional): Job-specific timeout (inherits from workflow if not set)
- `needs` (list[string], optional): Job IDs this job depends on
- `if_condition` (string, optional): Jinja2 expression determining if job runs
- `env_variables` (dict[string, string], optional): Job-level environment variables
- `enabled` (bool, required): Whether job is conditionally enabled based on module flags

**Uniqueness**: `job_id` unique per workflow

**Relationships**:

- Belongs to `WorkflowConfiguration`
- Has many `StepDefinition` (composition)
- May have `MatrixStrategy` (optional composition)
- Produces `MatrixBuildResult` entries when strategy defined

**Conditional Logic**:

```python
# Python quality job always enabled
python_quality.enabled = True

# Node.js job enabled only when api_tracks includes 'node'
node_quality.enabled = ('node' in api_tracks)

# CLI tests enabled only when cli_module enabled
cli_tests.enabled = (cli_module == 'enabled')
```

**Validation Rules**:

- `job_id` must be kebab-case alphanumeric
- At least one step required
- If `strategy` defined, must include `matrix` configuration
- If `needs` specified, referenced jobs must exist

---

### MatrixStrategy

Defines matrix build configuration for testing across multiple Python versions or other dimensions.

**Attributes**:

- `fail_fast` (bool, required): Whether to cancel other jobs on first failure (always `false` per research)
- `matrix_dimensions` (dict[string, list], required): Matrix variables and their values (e.g., `{'python-version': ['3.11', '3.12', '3.13']}`)
- `exclude` (list[dict], optional): Specific matrix combinations to exclude
- `include` (list[dict], optional): Additional matrix combinations to include
- `max_parallel` (int, optional): Maximum concurrent matrix jobs (default: unlimited)

**Uniqueness**: Part of JobDefinition (composition)

**Relationships**:

- Belongs to `JobDefinition`

**Default Configuration**:

```yaml
fail_fast: false
matrix_dimensions:
  python-version: ['3.11', '3.12', '3.13']
max_parallel: 3  # All versions in parallel
```

**Validation Rules**:

- `fail_fast` must be `false` (per constitution and clarifications)
- `matrix_dimensions` must include at least one dimension
- Python versions must be in supported range (3.11-3.13)

---

### StepDefinition

Represents a single step within a job, either using a GitHub Action or running a shell command.

**Attributes**:

- `step_id` (string, optional): Unique step identifier for referencing outputs
- `step_name` (string, required): Human-readable step name
- `uses` (string, optional): GitHub Action to use (e.g., `actions/checkout@v4`)
- `with` (dict[string, any], optional): Input parameters for action
- `run` (string, optional): Shell command to execute (mutually exclusive with `uses`)
- `env` (dict[string, string], optional): Step-level environment variables
- `if_condition` (string, optional): Condition determining if step runs
- `continue_on_error` (bool, optional): Whether to continue workflow on step failure
- `timeout_minutes` (int, optional): Step-specific timeout
- `retry_config` (RetryConfiguration, optional): Retry settings for transient failures

**Uniqueness**: Order-based within job (not explicitly unique)

**Relationships**:

- Belongs to `JobDefinition`
- May have `RetryConfiguration` (optional composition)

**Validation Rules**:

- Either `uses` or `run` must be specified, not both
- If `uses` specified, must be valid action reference
- Step names should be descriptive and unique within job

---

### RetryConfiguration

Defines retry behavior for steps that may encounter transient failures (e.g., GitHub Actions service outages).

**Attributes**:

- `max_attempts` (int, required): Maximum retry attempts (always `3` per research)
- `timeout_minutes` (int, required): Timeout per attempt
- `retry_wait_seconds` (int, required): Base wait time between retries
- `exponential_backoff` (bool, required): Whether to use exponential backoff (always `true`)
- `on_failure` (enum['fail', 'service_issue'], required): How to handle exhausted retries

**Uniqueness**: Part of StepDefinition (composition)

**Relationships**:

- Belongs to `StepDefinition`

**Backoff Calculation**:

```
attempt_1: wait 30 seconds
attempt_2: wait 60 seconds (30 * 2^1)
attempt_3: wait 120 seconds (30 * 2^2)
```

**Implementation**:

```yaml
uses: nick-fields/retry@v3
with:
  max_attempts: 3
  timeout_minutes: 10
  retry_wait_seconds: 30
  exponential_backoff: true
  command: uv run task quality
```

**Validation Rules**:

- `max_attempts` must be exactly 3
- `exponential_backoff` must be true
- `timeout_minutes` must be <= job timeout

---

### CacheManifest

Defines cache key patterns and restoration strategies for accelerating dependency installation.

**Attributes**:

- `cache_id` (string, required): Unique cache identifier (e.g., `python-deps`, `node-deps`)
- `cache_paths` (list[string], required): Directories to cache (e.g., `~/.cache/uv`, `node_modules`)
- `primary_key` (string, required): Cache key template with hash placeholders
- `restore_keys` (list[string], required): Fallback keys for partial cache hits
- `os_prefix` (string, required): Operating system prefix (e.g., `ubuntu-latest`, `macos-latest`)
- `python_version_prefix` (string, optional): Python version prefix for Python caches
- `lock_files` (list[string], required): Lock files used in hash calculation
- `enabled` (bool, required): Whether caching is active for this dependency type

**Uniqueness**: `cache_id` unique per workflow

**Relationships**:

- Referenced by `WorkflowConfiguration`
- Produces `CacheHitResult` on workflow execution

**Python Cache Example**:

```yaml
cache_id: python-deps
cache_paths:
  - ~/.cache/uv
  - ~/.cache/pip
primary_key: "${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}"
restore_keys:
  - "${{ runner.os }}-py${{ matrix.python-version }}-"
  - "${{ runner.os }}-"
lock_files: ['uv.lock']
enabled: true
```

**Node.js Cache Example**:

```yaml
cache_id: node-deps
cache_paths:
  - node_modules
  - .pnpm-store
primary_key: "${{ runner.os }}-node-${{ hashFiles('**/pnpm-lock.yaml') }}"
restore_keys:
  - "${{ runner.os }}-node-"
lock_files: ['pnpm-lock.yaml']
enabled: (api_tracks includes 'node')
```

**State Transitions**:

```
enabled=false → enabled=true (when module enabled)
```

**Validation Rules**:

- `primary_key` must include `runner.os` and hash of lock files
- `restore_keys` must be prefixes of `primary_key`
- At least one lock file required
- `cache_paths` must be absolute or tilde-prefixed

---

### MatrixBuildResult

Captures the outcome, duration, and artifact metadata for each matrix job execution.

**Attributes**:

- `run_id` (string, required): GitHub Actions run ID
- `job_id` (string, required): Job identifier from workflow
- `matrix_values` (dict[string, string], required): Matrix variable values for this execution (e.g., `{'python-version': '3.11'}`)
- `status` (enum['pending', 'in_progress', 'success', 'failure', 'cancelled', 'skipped'], required): Job execution status
- `started_at` (datetime, optional): Job start timestamp
- `completed_at` (datetime, optional): Job completion timestamp
- `duration_seconds` (int, optional): Total execution time
- `cache_hit` (bool, optional): Whether cache was restored successfully
- `cache_hit_duration_seconds` (int, optional): Time saved by cache hit
- `artifacts` (list[ArtifactMetadata], optional): Uploaded artifacts for this job
- `error_message` (string, optional): Error details if status is failure
- `logs_url` (string, optional): GitHub Actions logs URL
- `required_check` (bool, required): Whether this job is a required status check

**Uniqueness**: `(run_id, job_id, matrix_values)` tuple is unique

**Relationships**:

- Belongs to workflow execution
- References `JobDefinition`
- Has many `ArtifactMetadata` (composition)

**State Transitions**:

```
pending → in_progress → (success | failure | cancelled)
pending → skipped (if condition not met)
```

**Success Criteria Mapping**:

- SC-002: `duration_seconds` <= 180 on cache hit, <= 360 on cache miss
- SC-003: Sum of parallel matrix `duration_seconds` <= 480
- SC-004: `cache_hit` rate >= 0.70 across runs

**Validation Rules**:

- If `status` is success/failure, `completed_at` required
- If `cache_hit` true, `cache_hit_duration_seconds` must be > 0
- If `status` is failure, `error_message` recommended

---

### ArtifactMetadata

Stores metadata about artifacts uploaded during workflow execution for governance and debugging.

**Attributes**:

- `artifact_id` (string, required): GitHub-assigned artifact ID
- `artifact_name` (string, required): Structured artifact name (e.g., `test-results-py3.11-12345`)
- `artifact_type` (enum['test_results', 'coverage_report', 'quality_logs', 'workflow_metadata'], required): Classification of artifact content
- `file_paths` (list[string], required): Relative paths of files in artifact
- `size_bytes` (int, required): Total artifact size
- `uploaded_at` (datetime, required): Upload timestamp
- `expires_at` (datetime, required): Expiration timestamp (90 days from upload)
- `download_url` (string, required): GitHub artifact download URL
- `retention_days` (int, required): Configured retention period (always 90)
- `python_version` (string, optional): Python version if applicable (from matrix)
- `job_id` (string, required): Job that produced artifact

**Uniqueness**: `artifact_id` is unique across GitHub

**Relationships**:

- Belongs to `MatrixBuildResult`

**Naming Convention**:

```
test-results-py{version}-{run_id}
quality-logs-py{version}-{run_id}
coverage-report-py{version}-{run_id}
workflow-metadata-{run_id}
```

**State Transitions**:

```
uploaded → active (within retention period)
active → expired (after 90 days)
```

**Success Criteria Mapping**:

- SC-006: Upload success rate >= 0.98, `expires_at` always 90 days after `uploaded_at`

**Validation Rules**:

- `retention_days` must be exactly 90 (constitution requirement)
- `expires_at` must be `uploaded_at` + 90 days
- `artifact_type` determines expected `file_paths` contents
- `size_bytes` must be > 0

---

### WorkflowValidationReport

Documents the results of actionlint validation performed during post-generation hook.

**Attributes**:

- `validation_id` (string, required): Unique validation run ID
- `workflow_path` (string, required): Path to validated workflow file
- `validated_at` (datetime, required): Validation timestamp
- `actionlint_version` (string, required): Version of actionlint used
- `status` (enum['pass', 'fail', 'skipped'], required): Validation outcome
- `errors` (list[ValidationError], optional): Syntax/semantic errors found
- `warnings` (list[ValidationWarning], optional): Non-blocking issues found
- `render_id` (string, required): Associated copier render ID

**Uniqueness**: `(render_id, workflow_path)` tuple is unique

**Relationships**:

- References `WorkflowConfiguration`

**ValidationError Structure**:

```python
{
  "file": ".github/workflows/riso-quality.yml",
  "line": 15,
  "column": 3,
  "rule": "syntax-check",
  "message": "unexpected key 'stepss' (did you mean 'steps'?)",
  "severity": "error"
}
```

**ValidationWarning Structure**:

```python
{
  "file": ".github/workflows/riso-quality.yml",
  "line": 42,
  "rule": "action-version",
  "message": "action 'actions/checkout@v3' is outdated; v4 available",
  "severity": "warning"
}
```

**State Transitions**:

```
pending → pass (no errors)
pending → fail (errors found)
pending → skipped (actionlint not available)
```

**Validation Rules**:

- If `status` is fail, at least one error required
- Errors must reference valid line/column numbers
- `actionlint_version` should match documented requirement

---

## Entity Relationships

```
WorkflowConfiguration (1) -----> (N) JobDefinition
JobDefinition (1) -----> (1) MatrixStrategy [optional]
JobDefinition (1) -----> (N) StepDefinition
StepDefinition (1) -----> (1) RetryConfiguration [optional]
WorkflowConfiguration (1) -----> (N) CacheManifest
MatrixBuildResult (N) <----- (1) JobDefinition
MatrixBuildResult (1) -----> (N) ArtifactMetadata
WorkflowConfiguration (1) <----- (1) WorkflowValidationReport
```

## Aggregate Tracking

### Module Success Tracking

Extended `samples/metadata/module_success.json` to include workflow generation and execution:

```json
{
  "workflow_generation": {
    "total_renders": 25,
    "successful_validations": 24,
    "failed_validations": 1,
    "success_rate": 0.96
  },
  "workflow_execution": {
    "total_runs": 150,
    "passing_runs": 142,
    "failing_runs": 8,
    "success_rate": 0.95
  },
  "cache_performance": {
    "total_cache_attempts": 150,
    "cache_hits": 112,
    "cache_misses": 38,
    "hit_rate": 0.75
  }
}
```

### Smoke Results Extension

Extended `samples/*/smoke-results.json` to capture workflow-specific outcomes:

```json
{
  "workflows": {
    "riso-quality": {
      "status": "pass",
      "validation_status": "valid",
      "generated_at": "2025-10-30T12:00:00Z",
      "actionlint_output": "no errors"
    },
    "riso-matrix": {
      "status": "pass",
      "validation_status": "valid",
      "matrix_dimensions": ["3.11", "3.12", "3.13"]
    }
  }
}
```

---

## Invariants

1. **All matrix jobs must pass**: If `JobDefinition.strategy` is defined, all `MatrixBuildResult` entries must have `status='success'` for overall workflow success
2. **90-day retention**: All `ArtifactMetadata.retention_days` must equal 90
3. **Distinctive naming**: All `WorkflowConfiguration.workflow_name` must start with `riso-`
4. **Cache key integrity**: `CacheManifest.primary_key` must include hash of all `lock_files`
5. **Retry exhaustion**: `RetryConfiguration.max_attempts` must equal 3
6. **Timeout hierarchy**: `StepDefinition.timeout_minutes` <= `JobDefinition.timeout_minutes` <= `WorkflowConfiguration.timeout_minutes`

---

**Data Model Complete**: 2025-10-30  
**Next Step**: Generate contracts (Phase 1 continuation)
