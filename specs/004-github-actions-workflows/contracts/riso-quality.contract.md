# Workflow Template Contract: riso-quality.yml

**Purpose**: Main quality workflow that executes linting, type checking, static analysis, and testing on PR/push events.

**Template Path**: `template/files/shared/.github/workflows/riso-quality.yml.jinja`

**Rendered Path**: `.github/workflows/riso-quality.yml`

## Input Contract (Copier Answers)

### Required Inputs

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `package_name` | string | `myproject` | Python package name for module execution |
| `quality_profile` | enum | `standard` or `strict` | Quality check strictness level |
| `api_tracks` | list[string] | `['python']` or `['python', 'node']` | Enabled API frameworks |
| `cli_module` | enum | `enabled` or `disabled` | Whether CLI module is enabled |
| `mcp_module` | enum | `enabled` or `disabled` | Whether MCP module is enabled |
| `docs_site` | enum | `none`, `sphinx`, `fumadocs`, `docusaurus` | Documentation framework |
| `shared_logic` | enum | `enabled` or `disabled` | Whether shared logic module enabled |

### Optional Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ci_platform` | enum | `github-actions` | CI platform (future: GitLab, CircleCI) |
| `python_versions` | list[string] | `['3.11', '3.12', '3.13']` | Python versions to test |

## Output Contract (Generated Workflow)

### Workflow Structure

```yaml
name: Quality Checks
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

env:
  QUALITY_PROFILE: {{ quality_profile }}
  PACKAGE_NAME: {{ package_name }}

jobs:
  python-quality:
    name: Python Quality Checks
    runs-on: ubuntu-latest
    timeout-minutes: {% if quality_profile == 'strict' %}20{% else %}10{% endif %}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/uv
            ~/.cache/pip
          key: ${{ runner.os }}-py3.11-${{ hashFiles('**/uv.lock') }}
          restore-keys: |
            ${{ runner.os }}-py3.11-
            ${{ runner.os }}-
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run quality checks with retry
        uses: nick-fields/retry@v3
        with:
          timeout_minutes: {% if quality_profile == 'strict' %}18{% else %}8{% endif %}
          max_attempts: 3
          retry_wait_seconds: 30
          exponential_backoff: true
          command: |
            uv run task quality
      
      {% if cli_module == 'enabled' %}
      - name: Test CLI module
        run: uv run pytest tests/test_cli.py -v
      {% endif %}
      
      {% if mcp_module == 'enabled' %}
      - name: Test MCP module
        run: uv run pytest tests/test_mcp.py -v
      {% endif %}
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-py3.11-${{ github.run_id }}
          path: |
            test-results.xml
            htmlcov/
            .coverage
          retention-days: 90
      
      - name: Upload quality logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-logs-py3.11-${{ github.run_id }}
          path: |
            ruff-output.txt
            mypy-output.txt
            pylint-output.txt
          retention-days: 90

  {% if 'node' in api_tracks %}
  node-quality:
    name: Node.js Quality Checks
    runs-on: ubuntu-latest
    timeout-minutes: {% if quality_profile == 'strict' %}20{% else %}10{% endif %}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Enable corepack
        run: corepack enable
      
      - name: Cache pnpm dependencies
        uses: actions/cache@v4
        with:
          path: |
            node_modules
            .pnpm-store
          key: ${{ runner.os }}-node-${{ hashFiles('**/pnpm-lock.yaml') }}
          restore-keys: |
            ${{ runner.os }}-node-
      
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
      
      - name: Run ESLint
        run: pnpm run lint
      
      - name: Run TypeScript check
        run: pnpm run type-check
      
      - name: Run tests
        run: pnpm test
      
      - name: Upload Node.js test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: node-test-results-${{ github.run_id }}
          path: coverage/
          retention-days: 90
  {% endif %}
```

### Success Criteria

- Workflow validates via actionlint with zero errors
- Jobs execute within timeout (10 min standard, 20 min strict)
- Cache restoration completes in <10 seconds on hits
- All required jobs pass for PR merge to proceed
- Artifacts upload successfully with 90-day retention

### Error Handling

| Error Type | Behavior | User-Facing Message |
|------------|----------|---------------------|
| Syntax error | actionlint fails during render | "Workflow validation failed: {error details}" |
| Timeout exceeded | Job cancels after limit | "Quality checks exceeded {timeout} minute limit" |
| Tool failure | Retry up to 3 attempts | "Retrying after transient failure (attempt {N}/3)" |
| Service outage | Display after 3 failures | "⚠️ Service Issue - GitHub Actions may be experiencing problems" |
| Cache miss | Continue with full install | "Cache miss - installing dependencies (this may take 5-6 minutes)" |

## Validation Rules

### Pre-Generation (Template)

1. All Jinja2 variables must have defaults or be required in `copier.yml`
2. Conditional blocks must check existence of variables before use
3. Action versions must be pinned (e.g., `@v4`, not `@latest`)
4. Timeout values must respect profile constraints

### Post-Generation (Rendered)

1. Workflow YAML must be valid per GitHub Actions schema
2. All referenced actions must exist in GitHub marketplace
3. Cache keys must include hash of lock files
4. Artifact retention must be exactly 90 days
5. Job names must be unique within workflow
6. Required jobs must be specified in branch protection

## Dependencies

### GitHub Actions

- `actions/checkout@v4` - Repository checkout
- `actions/setup-python@v5` - Python environment setup
- `actions/setup-node@v4` - Node.js environment setup (conditional)
- `actions/cache@v4` - Dependency caching
- `actions/upload-artifact@v4` - Artifact uploads
- `nick-fields/retry@v3` - Retry logic for transient failures

### External Tools

- `uv` - Python package management and execution
- `corepack` - Node.js package manager enablement
- `pnpm` - Node.js package management (when Node track enabled)
- `actionlint` - Workflow validation (host tool, not in workflow)

## Testing Strategy

### Unit Tests (Template)

```python
def test_quality_workflow_generation():
    """Verify riso-quality.yml generates correctly"""
    answers = {
        'package_name': 'testpkg',
        'quality_profile': 'standard',
        'api_tracks': ['python'],
        'cli_module': 'enabled'
    }
    workflow = render_template('riso-quality.yml.jinja', answers)
    
    assert 'name: Quality Checks' in workflow
    assert 'timeout-minutes: 10' in workflow
    assert 'Test CLI module' in workflow
    assert 'node-quality:' not in workflow  # Node disabled

def test_strict_profile_timeout():
    """Verify strict profile uses 20-minute timeout"""
    answers = {'quality_profile': 'strict', ...}
    workflow = render_template('riso-quality.yml.jinja', answers)
    
    assert 'timeout-minutes: 20' in workflow
```

### Integration Tests (Rendered)

```bash
# Render sample project
copier copy . /tmp/test-project -d quality_profile=standard

# Validate workflow
actionlint /tmp/test-project/.github/workflows/riso-quality.yml

# Simulate workflow execution (local act)
cd /tmp/test-project
act pull_request -W .github/workflows/riso-quality.yml
```

### Smoke Tests

1. Render default sample with standard profile
2. Render full-stack sample with strict profile + Node track
3. Verify workflow files exist at expected paths
4. Run actionlint on all generated workflows
5. Check `smoke-results.json` for workflow validation status

## Maintenance Notes

### Updating Action Versions

When updating GitHub Actions versions (e.g., `actions/checkout@v4` → `@v5`):

1. Update all workflow templates consistently
2. Test with sample renders
3. Document breaking changes in upgrade guide
4. Consider copier update compatibility

### Adding New Module Checks

To add validation for a new optional module:

1. Add module flag to input contract
2. Add conditional step block in workflow
3. Update data model with new module field
4. Add smoke test for new module path
5. Update quickstart docs

### Performance Optimization

Monitor `MatrixBuildResult.duration_seconds` and `CacheManifest` hit rates:

- If cache hit rate < 70%, investigate cache key stability
- If duration > 6 minutes on cache miss, review dependency bloat
- If duration > 3 minutes on cache hit, check for unnecessary re-installs

---

**Contract Version**: 1.0  
**Last Updated**: 2025-10-30  
**Status**: Complete
