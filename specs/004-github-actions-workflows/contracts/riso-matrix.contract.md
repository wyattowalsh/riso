# Workflow Template Contract: riso-matrix.yml

**Purpose**: Matrix testing workflow that executes quality checks across multiple Python versions (3.11, 3.12, 3.13) in parallel, with all jobs required to pass.

**Template Path**: `template/files/shared/.github/workflows/riso-matrix.yml.jinja`

**Rendered Path**: `.github/workflows/riso-matrix.yml`

## Input Contract (Copier Answers)

### Required Inputs

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `package_name` | string | `myproject` | Python package name for module execution |
| `quality_profile` | enum | `standard` or `strict` | Quality check strictness level |
| `python_versions` | list[string] | `['3.11', '3.12', '3.13']` | Python versions for matrix (default from constitution) |

### Optional Inputs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `matrix_fail_fast` | bool | `false` | Whether to cancel other jobs on first failure (always false per research) |
| `matrix_max_parallel` | int | `3` | Maximum concurrent matrix jobs |

## Output Contract (Generated Workflow)

### Workflow Structure

```yaml
name: Matrix Testing
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

env:
  QUALITY_PROFILE: {{ quality_profile }}
  PACKAGE_NAME: {{ package_name }}

jobs:
  matrix-test:
    name: Python ${{ matrix.python-version }} Quality
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    strategy:
      fail-fast: false
      max-parallel: 3
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/uv
            ~/.cache/pip
          key: ${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('**/uv.lock') }}
          restore-keys: |
            ${{ runner.os }}-py${{ matrix.python-version }}-
            ${{ runner.os }}-
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests with retry
        uses: nick-fields/retry@v3
        with:
          timeout_minutes: 12
          max_attempts: 3
          retry_wait_seconds: 30
          exponential_backoff: true
          command: |
            uv run pytest --tb=short
      
      - name: Run type checking
        run: uv run mypy .
      
      - name: Run linting
        run: uv run ruff check .
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: matrix-results-py${{ matrix.python-version }}-${{ github.run_id }}
          path: |
            test-results.xml
            .coverage
          retention-days: 90
      
      - name: Report matrix status
        if: failure()
        run: |
          echo "::error::Python ${{ matrix.python-version }} checks failed"
          echo "This failure blocks PR merge per matrix policy"

  matrix-summary:
    name: Matrix Summary
    needs: matrix-test
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Check matrix results
        run: |
          if [ "${{ needs.matrix-test.result }}" != "success" ]; then
            echo "::error::Matrix testing failed - not all Python versions passed"
            echo "All Python versions (3.11, 3.12, 3.13) must pass for merge"
            exit 1
          fi
          echo "✅ All Python versions passed quality checks"
```

### Success Criteria

- All matrix jobs complete in <8 minutes (SC-003)
- Each individual job respects 15-minute timeout
- If any matrix job fails, overall workflow fails (per clarifications)
- Matrix summary job aggregates results clearly
- Artifacts uploaded for each Python version independently

### Matrix Reporting

**Job Naming Convention**: `Python {version} Quality` - appears as separate required check in GitHub UI

**Status Aggregation**: `matrix-summary` job marked as required check; depends on all matrix jobs

**Failure Display**:

```
❌ Python 3.13 Quality - Failed
  Error: Type error in new f-string syntax (Python 3.13+)
  Duration: 4m 32s
  Logs: [link]

✅ Python 3.11 Quality - Passed
  Duration: 3m 12s

✅ Python 3.12 Quality - Passed
  Duration: 3m 18s

❌ Matrix Summary - Failed
  Message: Not all Python versions passed - merge blocked
```

## Validation Rules

### Matrix Configuration

1. `fail-fast` must be `false` (show all failures)
2. `python-version` must include exactly 3.11, 3.12, 3.13
3. Each matrix job must be marked as required check
4. Matrix summary job must depend on all matrix jobs

### Cache Strategy

1. Each Python version gets independent cache key
2. Cache key includes Python version to prevent cross-version corruption
3. Restore keys allow fallback to same OS without version match

### Artifact Naming

1. Must include Python version: `matrix-results-py{version}-{run_id}`
2. Run ID ensures uniqueness across workflow runs
3. 90-day retention enforced

## Error Scenarios

| Scenario | Behavior | Recovery |
|----------|----------|----------|
| Python 3.13 fails, others pass | All jobs complete, summary fails | Fix 3.13-specific issue, re-run |
| Cache corruption | Fallback to fresh install | Monitor cache hit rate metrics |
| All versions fail | Summary shows aggregate failure | Check for fundamental code issue |
| Service outage | Retry 3x per job independently | Wait for service recovery |
| Timeout on one version | That job fails, others continue | Investigate performance regression |

## Testing Strategy

### Unit Tests

```python
def test_matrix_workflow_generation():
    """Verify matrix workflow generates with correct strategy"""
    answers = {'package_name': 'testpkg', 'quality_profile': 'standard'}
    workflow = render_template('riso-matrix.yml.jinja', answers)
    
    assert 'fail-fast: false' in workflow
    assert "'3.11', '3.12', '3.13'" in workflow
    assert 'matrix-summary:' in workflow
    assert 'needs: matrix-test' in workflow

def test_matrix_cache_keys():
    """Verify each Python version gets unique cache key"""
    workflow = render_template('riso-matrix.yml.jinja', {...})
    
    assert 'py${{ matrix.python-version }}' in workflow
    assert 'hashFiles' in workflow
```

### Integration Tests

```bash
# Test matrix with simulated Python 3.13 failure
cd /tmp/test-project
echo "# Intentional Python 3.13 syntax" >> src/test.py
git commit -am "Test matrix failure"
act pull_request -W .github/workflows/riso-matrix.yml

# Verify failure display
gh pr checks --json name,conclusion --jq '.[] | select(.name | startswith("Python"))'
```

### Performance Tests

Monitor against SC-003: matrix builds must complete in <8 minutes

```python
# In smoke test
matrix_start = record_time()
run_matrix_workflow()
matrix_duration = record_time() - matrix_start

assert matrix_duration < 480, f"Matrix took {matrix_duration}s, expected <480s"
```

## Maintenance Notes

### Adding Python Versions

To support Python 3.14 in future:

1. Update constitution to include 3.14 in supported range
2. Add `'3.14'` to matrix in template
3. Update timeout if needed (more versions = longer total time)
4. Test backward compatibility with 3.11-3.13

### Branch Protection Configuration

Required checks for matrix workflow:

```
- Python 3.11 Quality
- Python 3.12 Quality
- Python 3.13 Quality
- Matrix Summary
```

All four must pass for PR merge to proceed.

### Debugging Matrix Failures

1. Check individual job logs for specific Python version
2. Download version-specific artifacts for local reproduction
3. Compare passing vs failing versions to isolate compatibility issue
4. Use matrix summary output for aggregate view

---

**Contract Version**: 1.0  
**Last Updated**: 2025-10-30  
**Status**: Complete
