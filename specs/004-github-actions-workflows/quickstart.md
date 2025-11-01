# Quickstart: GitHub Actions CI/CD Workflows

**Feature**: 004-github-actions-workflows  
**Target Audience**: Template maintainers and downstream project developers  
**Prerequisites**: Completed features 001-003, GitHub repository with Actions enabled

## For Template Maintainers

### 1. Implement Workflow Templates (10 minutes)

Create workflow Jinja2 templates in `template/files/shared/.github/workflows/`:

```bash
cd template/files/shared
mkdir -p .github/workflows

# Create main quality workflow
touch .github/workflows/riso-quality.yml.jinja

# Create matrix testing workflow
touch .github/workflows/riso-matrix.yml.jinja
```

Key template patterns:

```jinja
{# Conditional Node.js jobs #}
{% if 'node' in api_tracks %}
  node-quality:
    name: Node.js Quality Checks
    ...
{% endif %}

{# Profile-based timeouts #}
timeout-minutes: {% if quality_profile == 'strict' %}20{% else %}10{% endif %}

{# Module-conditional steps #}
{% if cli_module == 'enabled' %}
- name: Test CLI module
  run: uv run pytest tests/test_cli.py
{% endif %}
```

### 2. Add Workflow Validation (5 minutes)

Update `template/hooks/post_gen_project.py` to validate generated workflows:

```python
import subprocess
import sys
from pathlib import Path

def validate_workflows():
    """Validate generated workflow YAML files"""
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print("⚠️  No workflows directory found")
        return
    
    workflow_files = list(workflows_dir.glob("riso-*.yml"))
    
    if not workflow_files:
        print("✅ No template workflows generated (expected for minimal configs)")
        return
    
    # Attempt actionlint validation
    try:
        result = subprocess.run(
            ["actionlint"] + [str(f) for f in workflow_files],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Validated {len(workflow_files)} workflow(s)")
        else:
            print(f"❌ Workflow validation failed:\n{result.stderr}")
            print("\nℹ️  Run 'actionlint .github/workflows/*.yml' to see details")
            # Don't fail render - workflows may still work
            
    except FileNotFoundError:
        print("⚠️  actionlint not found - skipping workflow validation")
        print("   Install: brew install actionlint (macOS) or see https://github.com/rhysd/actionlint")
    except subprocess.TimeoutExpired:
        print("⚠️  Workflow validation timed out")

# Call in post-generation
validate_workflows()
```

### 3. Test with Sample Renders (15 minutes)

```bash
# Render default sample (Python-only)
./scripts/render-samples.sh --variant default

# Verify workflows generated
ls -la samples/default/render/.github/workflows/
# Expected: riso-quality.yml, riso-matrix.yml

# Validate workflows
cd samples/default/render
actionlint .github/workflows/*.yml

# Render full-stack sample (Python + Node)
cd ../../../
./scripts/render-samples.sh --variant full-stack

# Verify Node.js jobs included
grep -A 10 "node-quality:" samples/full-stack/render/.github/workflows/riso-quality.yml
```

### 4. Update Documentation (10 minutes)

Update `docs/quickstart.md.jinja` with CI instructions:

```markdown
## Viewing CI Status

After pushing your first commit:

1. Navigate to your GitHub repository
2. Click the "Actions" tab
3. View workflow runs and job status

### Required Checks

The following checks must pass before PR merge:

- **Quality Checks** (`riso-quality.yml`) - Linting, type checking, testing
- **Python 3.11 Quality** (`riso-matrix.yml`) - Matrix job for Python 3.11
- **Python 3.12 Quality** (`riso-matrix.yml`) - Matrix job for Python 3.12
- **Python 3.13 Quality** (`riso-matrix.yml`) - Matrix job for Python 3.13
- **Matrix Summary** (`riso-matrix.yml`) - Aggregate matrix status

### Downloading Artifacts

1. Click on a completed workflow run
2. Scroll to "Artifacts" section
3. Download test results, coverage reports, or quality logs
4. Artifacts expire after 90 days

### Debugging Failures

1. Click on failed job to view logs
2. Download artifacts for local reproduction
3. Check cache hit status - misses add 3-4 minutes
4. For matrix failures, compare passing vs failing Python versions
```

### 5. Configure Branch Protection (GitHub UI)

Enable branch protection rules in rendered project repository:

1. Go to Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Check "Require status checks to pass before merging"
4. Search and select required checks:
   - `Quality Checks`
   - `Python 3.11 Quality`
   - `Python 3.12 Quality`
   - `Python 3.13 Quality`
   - `Matrix Summary`
5. Check "Require branches to be up to date"
6. Save changes

---

## For Downstream Developers

### First-Time Setup (5 minutes)

Your project comes with pre-configured GitHub Actions workflows. No manual setup required!

**What's included**:

- ✅ Automatic quality checks on every PR
- ✅ Testing across Python 3.11, 3.12, 3.13
- ✅ Dependency caching for fast builds
- ✅ Test results and coverage artifacts

### Viewing Workflow Status

After opening a PR or pushing to `main`:

1. Visit the "Actions" tab in your GitHub repository
2. Click on the most recent workflow run
3. View individual job status and execution times

**Expected timeline**:

- First run (cache miss): ~5-6 minutes
- Subsequent runs (cache hit): ~2-3 minutes
- Matrix builds: ~8 minutes total (parallel execution)

### Understanding Check Failures

#### Linting Failure

```
❌ Quality Checks > Run quality checks with retry > ruff check
Error: Ruff found 3 issue(s)

src/main.py:15:5: F841 Local variable `unused_var` is assigned but never used
```

**Fix**: Address the reported linting issues and push again.

#### Type Checking Failure

```
❌ Python 3.12 Quality > Run type checking
Error: mypy found 1 error

src/api.py:42: error: Argument 1 to "process" has incompatible type "str"; expected "int"
```

**Fix**: Correct the type mismatch and verify locally with `uv run mypy .`

#### Matrix Version Failure

```
✅ Python 3.11 Quality - Passed
✅ Python 3.12 Quality - Passed
❌ Python 3.13 Quality - Failed
  SyntaxError: invalid syntax (new f-string feature)

❌ Matrix Summary - Failed
  Message: Not all Python versions passed
```

**Fix**: The code uses a Python 3.13-specific feature not supported in earlier versions, OR there's a breaking change in 3.13. Check the specific job logs for details.

### Cache Debugging

If CI is consistently slow:

1. Check cache hit status in workflow logs:
   ```
   Cache restored from key: ubuntu-latest-py3.11-abc123def456
   ```
   vs
   ```
   Cache miss - no matching cache key found
   ```

2. Verify `uv.lock` is committed (required for cache key stability)

3. If cache thrashing occurs, manually clear via Actions UI:
   - Settings → Actions → Caches → Delete old caches

### Customizing Workflows

**Do NOT edit workflow files directly** - they may be overwritten on template updates.

Instead, customize via environment variables:

```yaml
# In your PR, temporarily override Python versions for testing
env:
  PYTHON_VERSIONS: "3.11,3.12"  # Skip 3.13 for debugging
```

Or create a custom workflow:

```yaml
# .github/workflows/custom-checks.yml
name: Custom Checks
on: [pull_request]

jobs:
  custom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run custom validation
        run: ./scripts/custom-validation.sh
```

Template workflows (`riso-*.yml`) and custom workflows coexist safely due to distinctive naming.

### Quality Profiles

Your project's quality profile determines CI behavior:

**Standard Profile** (default):

- 10-minute timeout
- Core checks (ruff, mypy, pytest)
- Faster feedback, suitable for development

**Strict Profile**:

- 20-minute timeout
- Extended checks (pylint with high threshold, strict coverage)
- Slower but more thorough, suitable for production releases

Check your profile in `copier-answers.yml`:

```yaml
quality_profile: standard
```

To upgrade to strict profile, re-run copier update:

```bash
copier update
# Select "strict" when prompted for quality_profile
```

---

## Troubleshooting

### Workflow Not Triggering

**Symptom**: Pushed commit but no Actions run appears

**Solutions**:

1. Verify Actions enabled: Settings → Actions → General → "Allow all actions"
2. Check `.github/workflows/` directory exists in repository root
3. Ensure workflows have `.yml` extension (not `.yml.jinja`)
4. Check workflow `on:` triggers match your branch/event

### All Jobs Failing Immediately

**Symptom**: Every job fails within seconds

**Solutions**:

1. Check GitHub Actions service status: https://www.githubstatus.com/
2. Verify `uv` installation step succeeds (check logs)
3. Ensure `pyproject.toml` and `uv.lock` are present in repository

### Matrix Summary Always Fails

**Symptom**: All Python version jobs pass, but summary fails

**Solutions**:

1. Check branch protection settings - all matrix jobs must be required checks
2. Verify no syntax errors in matrix summary job definition
3. Check for race conditions - ensure `needs: matrix-test` is present

### Artifacts Not Uploading

**Symptom**: Workflows pass but no artifacts appear

**Solutions**:

1. Verify artifact paths exist before upload:
   ```yaml
   - name: Debug artifact paths
     run: |
       ls -la test-results.xml
       ls -la htmlcov/
   ```
2. Check artifact size limits (500MB per artifact, 2GB total)
3. Ensure `if: always()` is set so artifacts upload even on failure

### Cache Never Hits

**Symptom**: Every run shows "Cache miss"

**Solutions**:

1. Verify `uv.lock` is committed and tracked by git
2. Check cache key matches: `runner.os` and `matrix.python-version` must be consistent
3. Inspect cache key hash - if `uv.lock` changes frequently, cache won't hit
4. Ensure previous run completed successfully (incomplete runs don't save cache)

---

## Next Steps

- **Phase 2**: Proceed to `/speckit.tasks` to decompose implementation into tasks
- **Testing**: Execute smoke tests with rendered samples
- **Documentation**: Update upgrade guide with workflow migration instructions
- **Governance**: Update context files and module success tracking

**Quickstart Complete**: 2025-10-30  
**Estimated Onboarding Time**: 40 minutes (maintainers), 10 minutes (downstream devs)
