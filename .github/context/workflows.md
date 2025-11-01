# GitHub Actions Workflows Context

This document provides extension patterns and context for GitHub Actions CI/CD workflows in the Riso template.

## Workflow Architecture

The template provides two core workflows:

1. **riso-quality.yml** – Main quality validation workflow
   - Python quality checks (ruff, mypy, pylint, pytest)
   - Optional Node.js quality checks (ESLint, TypeScript, Vitest)
   - Conditional CLI and MCP module tests
   - Retry logic with exponential backoff
   - Artifact uploads with 90-day retention

2. **riso-matrix.yml** – Matrix testing across Python versions
   - Tests against Python 3.11, 3.12, 3.13
   - Independent cache keys per version
   - Fail-fast disabled for comprehensive testing
   - Matrix summary job blocks merge on any failure

## Extension Patterns

### Adding Custom Workflow Steps

**Before quality checks:**
```yaml
- name: Custom preparation step
  run: |
    # Your custom logic
    echo "Preparing environment..."
```

**After quality checks:**
```yaml
- name: Custom validation step
  run: |
    # Your custom logic
    uv run python scripts/custom_checks.py
```

### Adding New Jobs

**Parallel job pattern:**
```yaml
custom-checks:
  name: Custom Checks
  runs-on: ubuntu-latest
  timeout-minutes: 10
  
  steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Run custom checks
      run: |
        # Your custom logic
```

**Dependent job pattern:**
```yaml
custom-checks:
  name: Custom Checks
  runs-on: ubuntu-latest
  needs: [python-quality, node-quality]  # Wait for other jobs
  
  steps:
    # Your steps
```

### Customizing Cache Keys

**Add custom paths to Python cache:**
```yaml
- name: Cache Python dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      ~/.cache/pip
      .custom-cache/  # Add your custom path
    key: ${{ runner.os }}-py-${{ hashFiles('**/uv.lock', 'custom-deps.lock') }}
```

**Add custom restore keys:**
```yaml
restore-keys: |
  ${{ runner.os }}-py3.11-
  ${{ runner.os }}-py-
  ${{ runner.os }}-custom-
```

### Artifact Upload Patterns

**Upload custom artifacts:**
```yaml
- name: Upload custom artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: custom-results-${{ github.run_id }}
    path: |
      custom-results/
      custom-logs/
    retention-days: 90
```

### Environment Variable Customization

**Project-level environment:**
```yaml
env:
  QUALITY_PROFILE: strict
  PACKAGE_NAME: my_package
  CUSTOM_VAR: custom_value  # Add your custom variables
```

**Job-level environment:**
```yaml
python-quality:
  env:
    PYTEST_ARGS: "-vv --tb=short"
    MYPY_CACHE_DIR: ".mypy_cache"
```

**Step-level environment:**
```yaml
- name: Run tests
  env:
    DATABASE_URL: "sqlite:///test.db"
  run: uv run pytest
```

### Conditional Execution Patterns

**Run step only on specific branches:**
```yaml
- name: Deploy to staging
  if: github.ref == 'refs/heads/develop'
  run: |
    # Deployment logic
```

**Run step only on PR:**
```yaml
- name: Comment on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: 'Quality checks passed! ✅'
      })
```

**Run step only on failure:**
```yaml
- name: Send failure notification
  if: failure()
  run: |
    # Notification logic
```

### Matrix Expansion

**Add custom matrix dimensions:**
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']
    os: [ubuntu-latest, windows-latest, macos-latest]  # Add OS matrix
    # or
    database: [sqlite, postgres, mysql]  # Add database matrix
```

**Use matrix values in steps:**
```yaml
- name: Test with ${{ matrix.database }}
  env:
    DB_TYPE: ${{ matrix.database }}
  run: uv run pytest
```

### Retry Logic Customization

**Adjust retry parameters:**
```yaml
- name: Run quality checks with retry
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 20  # Increase timeout
    max_attempts: 5      # More attempts
    retry_wait_seconds: 60  # Longer wait
    exponential_backoff: true
    command: |
      QUALITY_PROFILE=strict uv run task quality
```

**Retry specific commands only:**
```yaml
- name: Install flaky dependency
  uses: nick-fields/retry@v3
  with:
    max_attempts: 3
    command: uv pip install some-flaky-package
```

## Integration with External Services

### Code Coverage Services

**Codecov integration:**
```yaml
- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

**Coveralls integration:**
```yaml
- name: Upload to Coveralls
  uses: coverallsapp/github-action@v2
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    path-to-lcov: ./coverage.lcov
```

### Notification Services

**Slack notifications:**
```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "CI run ${{ job.status }}"
      }
```

### Security Scanning

**Snyk security scan:**
```yaml
- name: Run Snyk security scan
  uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## Performance Optimization

### Free Tier Optimization

**Reduce workflow triggers:**
```yaml
on:
  pull_request:
    branches: [main]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
      # Exclude docs-only changes
```

**Use concurrency limits:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel old runs on new push
```

**Aggressive caching:**
```yaml
- name: Cache everything
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/uv
      ~/.cache/pip
      ~/.cache/pypoetry
      node_modules
      .venv
    key: mega-cache-${{ hashFiles('**/*.lock', '**/pyproject.toml') }}
```

## Troubleshooting

### Workflow Not Triggering

1. Check trigger conditions in `on:` section
2. Verify branch protection rules don't block workflow
3. Check if workflow file has syntax errors (run `actionlint`)

### Cache Not Hitting

1. Check cache key generation logic
2. Verify lock files haven't changed
3. Check cache size limits (10GB per repository)
4. Review cache hit/miss logs in workflow output

### Job Timeouts

1. Increase `timeout-minutes` in job definition
2. Use `needs:` to ensure jobs run in correct order
3. Check for hanging processes or network issues
4. Consider splitting long jobs into multiple jobs

### Artifact Upload Failures

1. Check artifact size (500MB limit per file)
2. Verify paths exist before upload
3. Use `if-no-files-found: warn` for optional artifacts
4. Check retention-days is within limits (1-90 days)

## References

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [actionlint](https://github.com/rhysd/actionlint) – Workflow linter
- [actions/cache](https://github.com/actions/cache) – Caching action
- [actions/upload-artifact](https://github.com/actions/upload-artifact) – Artifact uploads
- [nick-fields/retry](https://github.com/nick-fields/retry) – Retry logic
