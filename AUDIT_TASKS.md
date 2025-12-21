# Riso Audit Tasks

> **Generated**: 2025-12-21
> **Source**: AUDIT_REPORT.md
> **Optimized for**: Subagent execution

---

## Task Execution Guidelines

Each task is designed to be:
- **Self-contained**: All context needed is in the task
- **Atomic**: Single-purpose, completable in one session
- **Verifiable**: Includes validation steps
- **Prioritized**: P0 (Critical) → P3 (Low)

---

## P0: Critical Issues (Block Release)

### TASK-001: Fix Python camel_case filter syntax error

**Priority**: P0 (Critical)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**Context**:
The codegen engine template has invalid Python syntax using walrus operator in a tuple expression, which will cause SyntaxError when templates are rendered with `codegen_module=enabled`.

**File**: `/home/user/riso/template/files/python/src/{{ package_name }}/codegen/engine.py.jinja`

**Location**: Lines 55-58

**Current Code** (BROKEN):
```python
env.filters["camel_case"] = lambda s: (
    parts := s.replace("-", "_").split("_"),
    parts[0].lower() + "".join(word.capitalize() for word in parts[1:])
)[1] if "_" in s or "-" in s else s[0].lower() + s[1:]
```

**Required Fix**:
Replace lines 55-58 with a proper function definition:
```python
def _camel_case(s: str) -> str:
    """Convert string to camelCase."""
    if "_" not in s and "-" not in s:
        return s[0].lower() + s[1:] if len(s) > 1 else s
    parts = s.replace("-", "_").split("_")
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])

env.filters["camel_case"] = _camel_case
```

**Verification**:
```bash
# Validate Python syntax
python3 -c "
def _camel_case(s: str) -> str:
    if '_' not in s and '-' not in s:
        return s[0].lower() + s[1:] if len(s) > 1 else s
    parts = s.replace('-', '_').split('_')
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
print(_camel_case('hello_world'))  # Should print: helloWorld
print(_camel_case('hello-world'))  # Should print: helloWorld
print(_camel_case('HelloWorld'))   # Should print: helloWorld
"
```

---

### TASK-002: Fix CLI test template indentation error

**Priority**: P0 (Critical)
**Estimated Effort**: 5 minutes
**Dependencies**: None

**Context**:
The CLI test template has a leading space on line 14 that causes Python IndentationError. This breaks all templates rendered with `cli_module=enabled`.

**File**: `/home/user/riso/template/files/python/tests/test_cli.py.jinja`

**Location**: Line 14

**Current Code** (BROKEN):
```python
typer_testing = pytest.importorskip(
    "typer.testing",
    reason="Typer CLI dependencies not installed",
)
 CliRunner = typer_testing.CliRunner  # ← LEADING SPACE
```

**Required Fix**:
Remove the leading space from line 14:
```python
typer_testing = pytest.importorskip(
    "typer.testing",
    reason="Typer CLI dependencies not installed",
)
CliRunner = typer_testing.CliRunner
```

**Verification**:
```bash
# Check for leading whitespace issues
grep -n "^ [A-Z]" /home/user/riso/template/files/python/tests/test_cli.py.jinja
# Should return no matches after fix
```

---

### TASK-003: Fix Node.js health endpoint status mismatch

**Priority**: P0 (Critical)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Context**:
The Fastify health endpoint returns `status: 'healthy'` but the test expects `status: 'ok'`. This causes all Node.js API tests to fail.

**Files**:
- `/home/user/riso/template/files/node/apps/api-node/src/health.ts.jinja`
- `/home/user/riso/template/files/node/apps/api-node/tests/test_api_fastify.spec.ts.jinja`

**Option A - Fix implementation** (RECOMMENDED):
In `health.ts.jinja`, change the status value to match the test expectation:
```typescript
// Change from:
return { status: 'healthy', service: 'api-node' };
// To:
return { status: 'ok', service: 'api-node' };
```

**Option B - Fix test**:
In `test_api_fastify.spec.ts.jinja`, change the expected value:
```typescript
// Change from:
expect(JSON.parse(response.body)).toMatchObject({
  status: "ok",
// To:
expect(JSON.parse(response.body)).toMatchObject({
  status: "healthy",
```

**Verification**:
```bash
# After fix, grep both files to ensure consistency
grep -r "status.*healthy\|status.*ok" /home/user/riso/template/files/node/apps/api-node/
```

---

### TASK-004: Add missing Drizzle ORM imports

**Priority**: P0 (Critical)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Context**:
The SaaS API users route template uses `or` and `sql` functions from drizzle-orm but doesn't import them, causing TypeScript compilation errors when Drizzle ORM is selected.

**File**: `/home/user/riso/template/files/node/saas/app/api/examples/users/route.ts.jinja`

**Location**: Near line 23 (import section)

**Required Fix**:
Find the existing drizzle-orm import and add the missing functions:
```typescript
// Find this line (or similar):
import { eq, ilike } from 'drizzle-orm';

// Change to:
import { eq, ilike, or, sql } from 'drizzle-orm';
```

**Verification**:
```bash
# Check imports include or and sql
grep -n "import.*from 'drizzle-orm'" /home/user/riso/template/files/node/saas/app/api/examples/users/route.ts.jinja
# Verify or and sql are used later in the file
grep -n "\bor\b\|\bsql\b" /home/user/riso/template/files/node/saas/app/api/examples/users/route.ts.jinja
```

---

### TASK-005: Fix semantic-release tag format syntax

**Priority**: P0 (Critical)
**Estimated Effort**: 5 minutes
**Dependencies**: None

**Context**:
The semantic-release configuration uses shell variable syntax (`${name}`) instead of the correct lodash template syntax (`<%=name%>`), causing monorepo releases to fail.

**File**: `/home/user/riso/template/files/shared/.releaserc.yml.jinja`

**Location**: Lines 18-22

**Current Code** (BROKEN):
```yaml
{% if project_layout == "monorepo" %}
tagFormat: "${name}/v${version}"
{% else %}
tagFormat: "v${version}"
{% endif %}
```

**Required Fix**:
```yaml
{% if project_layout == "monorepo" %}
tagFormat: "<%=name%>/v<%=version%>"
{% else %}
tagFormat: "v<%=version%>"
{% endif %}
```

**Verification**:
```bash
# Render template and check output
grep -A2 "tagFormat" /home/user/riso/template/files/shared/.releaserc.yml.jinja
# Should show <%=name%> syntax
```

---

## P1: High Priority Issues

### TASK-006: Remove undefined job dependency in release workflow

**Priority**: P1 (High)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Context**:
The release workflow references a `quality` job in the `needs` array, but this job doesn't exist in the workflow file, causing workflow failures.

**File**: `/home/user/riso/template/files/shared/.github/workflows/riso-release.yml.jinja`

**Location**: Line 32

**Current Code** (BROKEN):
```yaml
jobs:
  release:
    name: Semantic Release
    runs-on: ubuntu-latest
    needs: [quality]  # ← 'quality' job doesn't exist
```

**Required Fix** (Option A - Remove dependency):
```yaml
jobs:
  release:
    name: Semantic Release
    runs-on: ubuntu-latest
    # Removed: needs: [quality]
```

**Required Fix** (Option B - Add quality job):
Add a quality job before the release job, or ensure this workflow is only called from another workflow that provides the quality job.

**Verification**:
```bash
# Check for undefined job references
grep -n "needs:" /home/user/riso/template/files/shared/.github/workflows/riso-release.yml.jinja
# Cross-reference with job definitions
grep -n "^  [a-z_-]*:" /home/user/riso/template/files/shared/.github/workflows/riso-release.yml.jinja
```

---

### TASK-007: Fix hardcoded CORS origins security issue

**Priority**: P1 (High - Security)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**Context**:
The API configuration template has `http://localhost:3000` as a default CORS origin, which is a security risk if deployed to production without modification.

**File**: `/home/user/riso/template/files/python/src/{{ package_name }}/api/config.py.jinja`

**Location**: Around line 81

**Current Code** (SECURITY RISK):
```python
cors_origins: list[str] = Field(
    default=["http://localhost:3000"],
    description="Allowed CORS origins",
)
```

**Required Fix**:
```python
cors_origins: list[str] = Field(
    default_factory=list,  # Empty by default for security
    description="Allowed CORS origins. Configure via CORS_ORIGINS env var.",
)
```

**Also add documentation comment above the field**:
```python
# SECURITY: CORS origins must be explicitly configured for production.
# Set CORS_ORIGINS environment variable with comma-separated origins.
# Example: CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

**Verification**:
```bash
# Ensure no hardcoded localhost in CORS config
grep -n "localhost" /home/user/riso/template/files/python/src/*/api/config.py.jinja
# Should not match CORS origins
```

---

### TASK-008: Remove ESLint configuration conflict

**Priority**: P1 (High)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**Context**:
The SaaS package.json includes both `eslint-config-next` and `@next/eslint-plugin-next`, which creates a dependency conflict for Next.js 15 projects.

**File**: `/home/user/riso/template/files/node/saas/package.json.jinja`

**Location**: Around line 206 in devDependencies

**Required Fix**:
Remove the `eslint-config-next` entry from devDependencies since Next.js 15 uses `@next/eslint-plugin-next` instead.

Find and remove:
```json
"eslint-config-next": "^15.0.0",
```

**Verification**:
```bash
# Check for duplicate eslint configs
grep -n "eslint.*next" /home/user/riso/template/files/node/saas/package.json.jinja
# Should only show @next/eslint-plugin-next
```

---

### TASK-009: Add SHA256 digests to Docker base images

**Priority**: P1 (High - Security)
**Estimated Effort**: 30 minutes
**Dependencies**: None

**Context**:
Docker base images use tag-only references without SHA256 digests, which can lead to non-reproducible builds and potential supply chain attacks.

**Files**:
- `/home/user/riso/template/files/shared/.docker/Dockerfile.jinja` (lines 23, 49, 97, 135)
- `/home/user/riso/template/files/shared/.docker/Dockerfile.dev.jinja`

**Current Code** (lines vary):
```dockerfile
FROM python:3.11-slim-bookworm AS builder-python
FROM node:20-alpine AS builder-node
```

**Required Fix**:
Add SHA256 digests (get current digests from Docker Hub):
```dockerfile
# Get latest digests:
# docker pull python:3.11-slim-bookworm && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim-bookworm
# docker pull node:20-alpine && docker inspect --format='{{index .RepoDigests 0}}' node:20-alpine

FROM python:3.11-slim-bookworm@sha256:<CURRENT_DIGEST> AS builder-python
FROM node:20-alpine@sha256:<CURRENT_DIGEST> AS builder-node
```

**Alternative**: Add template variable for easy updates:
```dockerfile
# Allow override via build arg, default to specific digest
ARG PYTHON_IMAGE_DIGEST=sha256:abc123...
FROM python:3.11-slim-bookworm@${PYTHON_IMAGE_DIGEST} AS builder-python
```

**Verification**:
```bash
# Check all FROM statements have @sha256
grep -n "^FROM" /home/user/riso/template/files/shared/.docker/Dockerfile.jinja
grep -n "^FROM" /home/user/riso/template/files/shared/.docker/Dockerfile.dev.jinja
# Each should include @sha256:
```

---

### TASK-010: Document or complete GraphQL authentication stubs

**Priority**: P1 (High)
**Estimated Effort**: 45 minutes
**Dependencies**: None

**Context**:
GraphQL authentication templates contain TODO comments for core functionality. These should either be completed or clearly documented as requiring user implementation.

**Files**:
- `/home/user/riso/template/files/python/graphql_api/auth.py.jinja`
- `/home/user/riso/template/files/python/graphql_api/main.py.jinja`
- `/home/user/riso/template/files/python/graphql_api/context.py.jinja`

**Option A - Add documentation** (RECOMMENDED):
Add a clear warning block at the top of each file:
```python
"""GraphQL Authentication Module.

⚠️  IMPORTANT: This module contains stub implementations that MUST be
completed before production use. The following require implementation:

1. Token validation logic in `validate_token()`
2. Database session dependency in `get_db_session()`
3. JWT validation in `verify_jwt_token()`

See docs/modules/graphql.md for implementation guidance.
"""
```

**Option B - Complete implementations**:
Implement the TODO items with working code using python-jose and SQLAlchemy.

**Verification**:
```bash
# List all TODOs in GraphQL templates
grep -rn "TODO" /home/user/riso/template/files/python/graphql_api/
# After fix, should have clear documentation instead of bare TODOs
```

---

## P2: Medium Priority Issues

### TASK-011: Increase coverage threshold to 90%

**Priority**: P2 (Medium)
**Estimated Effort**: 5 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/shared/quality/coverage.cfg.jinja`

**Location**: Line 15

**Current Code**:
```ini
fail_under = 85.0
```

**Required Fix**:
```ini
fail_under = 90.0
```

---

### TASK-012: Standardize Python version in workflows

**Priority**: P2 (Medium)
**Estimated Effort**: 20 minutes
**Dependencies**: None

**Context**:
Multiple workflow templates hardcode different Python versions instead of using a template variable.

**Files to update**:
- `/home/user/riso/template/files/shared/.github/workflows/riso-quality.yml.jinja`
- `/home/user/riso/template/files/shared/.github/workflows/quality-matrix.yml.jinja`

**Required Fix**:
Replace hardcoded Python versions with template variable:
```yaml
# Change from:
python-version: "3.11"
# To:
python-version: "{{ python_versions[0] }}"
```

---

### TASK-013: Fix trailing comma issue in container build workflow

**Priority**: P2 (Medium)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/shared/.github/workflows/riso-container-build.yml.jinja`

**Location**: Lines 175-178

**Context**:
Complex Jinja2 logic for the `needs` array can produce invalid YAML with trailing commas.

**Required Fix**:
Use Jinja2 list construction instead of string concatenation:
```yaml
{% set job_deps = [] %}
{% if api_tracks in ['python', 'python+node'] %}
  {% set _ = job_deps.append('build-python') %}
{% endif %}
{% if api_tracks in ['node', 'python+node'] %}
  {% set _ = job_deps.append('build-node') %}
{% endif %}
    needs: {{ job_deps | tojson }}
```

---

### TASK-014: Add correlation IDs to parallel publishing

**Priority**: P2 (Medium)
**Estimated Effort**: 20 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/shared/scripts/release/publish-artifacts.py.jinja`

**Required Fix**:
Add UUID-based correlation IDs to parallel execution logging for debugging.

---

### TASK-015: Add startup delays to docker-compose health checks

**Priority**: P2 (Medium)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/shared/docker-compose.yml.jinja`

**Required Fix**:
Add `start_period` to health check configuration:
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s  # ← Add this
```

---

### TASK-016: Update OpenAI model references

**Priority**: P2 (Medium)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**Context**:
Vision API references use outdated model names like `gpt-4-vision-preview`.

**Files**: Search for OpenAI client templates in `/home/user/riso/template/files/node/saas/integrations/ai/`

**Required Fix**:
Update to current model names:
```typescript
// Change from:
model: 'gpt-4-vision-preview'
// To:
model: 'gpt-4o'  // or 'gpt-4-turbo' depending on use case
```

---

### TASK-017: Complete R2 storage multipart upload

**Priority**: P2 (Medium)
**Estimated Effort**: 45 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/node/saas/integrations/storage/r2/client.ts.jinja`

**Location**: Around line 79

**Context**:
The `uploadLargeFile()` function for files >5MB is marked as incomplete and falls back to standard upload.

**Required Fix**:
Implement S3-compatible multipart upload using the AWS SDK.

---

### TASK-018: Complete Paddle webhook routing

**Priority**: P2 (Medium)
**Estimated Effort**: 30 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/node/saas/integrations/billing/service.ts.jinja`

**Location**: Around line 140

**Context**:
Paddle webhook event routing is marked for implementation.

**Required Fix**:
Implement event routing similar to Stripe webhook handling.

---

## P3: Low Priority Issues

### TASK-019: Add terminal fallback for emoji display

**Priority**: P3 (Low)
**Estimated Effort**: 10 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/shared/scripts/release/validate-commit.py.jinja`

**Required Fix**:
Add ASCII fallback for terminals that don't support Unicode emoji.

---

### TASK-020: Add thread-safety to WebSocket singleton

**Priority**: P3 (Low)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/python/src/{{ package_name }}/websocket/manager.py.jinja`

**Required Fix**:
Add `threading.Lock` to singleton pattern.

---

### TASK-021: Remove Python reference from Node workspace config

**Priority**: P3 (Low)
**Estimated Effort**: 5 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/node/pnpm-workspace.yaml.jinja`

**Required Fix**:
Remove or conditionally include the Python workspace reference.

---

### TASK-022: Update README.md feature status

**Priority**: P3 (Low)
**Estimated Effort**: 15 minutes
**Dependencies**: None

**File**: `/home/user/riso/README.md`

**Context**:
README references "Coming Next" features (004-007) that are already implemented.

**Required Fix**:
Update the feature list to reflect current implementation status (features 001-015 are complete).

---

### TASK-023: Remove redundant conditional logic in changelog docs

**Priority**: P3 (Low)
**Estimated Effort**: 5 minutes
**Dependencies**: None

**File**: `/home/user/riso/template/files/shared/docs/modules/changelog-release.md.jinja`

**Location**: Lines 1-5

**Current Code**:
```markdown
{% if changelog_module == "enabled" -%}
# Changelog & Release Management

> **Status**: `{{ 'enabled' if changelog_module == 'enabled' else 'disabled' }}`
```

**Required Fix**:
```markdown
{% if changelog_module == "enabled" -%}
# Changelog & Release Management

> **Status**: `enabled`
```

---

## Task Summary

| Priority | Count | Description |
|----------|-------|-------------|
| P0 (Critical) | 5 | Block release - syntax errors, test failures |
| P1 (High) | 5 | Security issues, workflow errors |
| P2 (Medium) | 8 | Quality improvements, completions |
| P3 (Low) | 5 | Minor fixes, documentation |
| **Total** | **23** | |

---

## Execution Order Recommendation

### Phase 1: Critical Fixes (P0)
Execute TASK-001 through TASK-005 in parallel (no dependencies).

### Phase 2: High Priority (P1)
Execute TASK-006 through TASK-010 in parallel after Phase 1.

### Phase 3: Medium Priority (P2)
Execute TASK-011 through TASK-018 based on available capacity.

### Phase 4: Low Priority (P3)
Execute TASK-019 through TASK-023 as time permits.

---

## Verification Script

After completing all P0 and P1 tasks, run:

```bash
#!/bin/bash
# Verify critical fixes

echo "=== Verifying P0 Fixes ==="

# TASK-001: Python syntax
python3 -m py_compile /dev/stdin <<< "
def _camel_case(s):
    if '_' not in s and '-' not in s:
        return s[0].lower() + s[1:] if len(s) > 1 else s
    parts = s.replace('-', '_').split('_')
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])
" && echo "✓ TASK-001: camel_case syntax OK"

# TASK-002: No leading spaces
! grep -q "^ [A-Z]" /home/user/riso/template/files/python/tests/test_cli.py.jinja && echo "✓ TASK-002: No leading spaces"

# TASK-003: Health status consistency
grep -q "status.*ok" /home/user/riso/template/files/node/apps/api-node/src/health.ts.jinja && echo "✓ TASK-003: Health status OK"

# TASK-004: Drizzle imports
grep -q "or.*sql" /home/user/riso/template/files/node/saas/app/api/examples/users/route.ts.jinja && echo "✓ TASK-004: Drizzle imports OK"

# TASK-005: Semantic release syntax
grep -q "<%=name%>" /home/user/riso/template/files/shared/.releaserc.yml.jinja && echo "✓ TASK-005: Tag format syntax OK"

echo "=== P0 Verification Complete ==="
```
