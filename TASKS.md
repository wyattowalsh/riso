# Riso Project Task List

> **Optimized for Claude Code Subagents**
>
> This task list is structured for autonomous execution by Claude Code agents.
> Each task includes context, file paths, expected outcomes, and verification steps.

---

## Task Categories

- [SECURITY] - Security vulnerabilities requiring immediate attention
- [TEST] - Test infrastructure and coverage improvements
- [REFACTOR] - Code quality and maintainability improvements
- [CI] - CI/CD workflow enhancements
- [DOCS] - Documentation improvements
- [CONFIG] - Configuration and dependency updates
- [FEATURE] - Missing functionality

---

## Priority Levels

- **P0** - Critical security/blocking issues (do immediately)
- **P1** - High priority (within 1 week)
- **P2** - Medium priority (within 1 month)
- **P3** - Low priority (backlog)

---

## SECURITY Tasks

### SEC-001: Validate COPIER_CMD environment variable [P0]

**Category:** SECURITY
**Files:** `scripts/render-samples.sh`
**Lines:** 287-291

**Problem:** The `COPIER_CMD` environment variable is passed directly to shell execution without validation, enabling command injection.

**Task:**
1. Read `scripts/render-samples.sh`
2. Add validation before line 287 to ensure COPIER_CMD is a valid executable name
3. Implement whitelist validation: only allow `copier` or absolute paths to copier binary
4. Add error message if validation fails

**Implementation:**
```bash
# Add before line 287
validate_copier_cmd() {
  local cmd="${COPIER_CMD:-copier}"
  if [[ "$cmd" == "copier" ]]; then
    return 0
  elif [[ "$cmd" =~ ^/.*copier$ ]] && [[ -x "$cmd" ]]; then
    return 0
  else
    echo "ERROR: Invalid COPIER_CMD: $cmd" >&2
    echo "Must be 'copier' or absolute path to copier binary" >&2
    return 1
  fi
}
validate_copier_cmd || exit 1
```

**Verification:**
- Test with `COPIER_CMD=copier` - should succeed
- Test with `COPIER_CMD="/usr/bin/copier"` - should succeed if file exists
- Test with `COPIER_CMD="copier; rm -rf /"` - should fail with error

---

### SEC-002: Pin Trivy action to semantic version [P0]

**Category:** SECURITY
**Files:** `template/files/node/saas/.github/workflows/ci.yml.jinja`
**Lines:** 213

**Problem:** Using `aquasecurity/trivy-action@master` tracks unstable branch, creating supply chain risk.

**Task:**
1. Read the workflow file
2. Replace `@master` with `@0.20.0` (or latest stable version)
3. Add comment explaining version pinning rationale

**Implementation:**
```yaml
# Change from:
- uses: aquasecurity/trivy-action@master

# Change to:
- uses: aquasecurity/trivy-action@0.20.0  # Pin to stable version for security
```

**Verification:**
- Validate YAML syntax with `actionlint` if available
- Confirm version exists at https://github.com/aquasecurity/trivy-action/releases

---

### SEC-003: Replace curl|sh with official uv action [P0]

**Category:** SECURITY
**Files:**
- `template/files/shared/.github/workflows/riso-quality.yml.jinja` (line 41)
- `template/files/shared/.github/workflows/riso-matrix.yml.jinja` (line 53)

**Problem:** `curl -LsSf https://astral.sh/uv/install.sh | sh` pattern is vulnerable to MITM attacks.

**Task:**
1. Read both workflow files
2. Replace curl installation with official `astral-sh/setup-uv@v3` action
3. Configure caching for efficiency

**Implementation:**
```yaml
# Replace curl command with:
- name: Set up uv
  uses: astral-sh/setup-uv@v3
  with:
    version: "latest"
    enable-cache: true
    cache-dependency-glob: "**/uv.lock"
```

**Verification:**
- Validate YAML syntax
- Check that UV_CACHE_DIR environment variable is still set if needed

---

### SEC-004: Add concurrency controls to all workflows [P0]

**Category:** SECURITY
**Files:**
- `.github/workflows/quality.yml`
- `template/files/shared/.github/workflows/riso-quality.yml.jinja`
- `template/files/shared/.github/workflows/riso-matrix.yml.jinja`
- `template/files/shared/.github/workflows/riso-container-build.yml.jinja`
- `template/files/shared/.github/workflows/riso-container-publish.yml.jinja`
- `template/files/shared/.github/workflows/riso-release.yml.jinja`
- `template/files/shared/.github/workflows/quality-matrix.yml.jinja`
- `template/files/shared/.github/workflows/template-ci.yml.jinja`
- `template/files/node/saas/.github/workflows/ci.yml.jinja`
- `template/files/node/saas/.github/workflows/database.yml.jinja`

**Problem:** No concurrency controls prevent overlapping workflow runs.

**Task:**
1. Read each workflow file
2. Add concurrency configuration after the `on:` trigger block
3. Use workflow name and ref for grouping

**Implementation:**
```yaml
# Add after 'on:' block in each workflow:
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Verification:**
- Validate YAML syntax for each file
- Confirm concurrency block is at correct indentation level

---

### SEC-005: Fix JSON parsing from environment without validation [P1]

**Category:** SECURITY
**Files:** `template/hooks/pre_gen_project.py`
**Lines:** 57-121

**Problem:** Functions `_load_docs_site()`, `_load_ci_platform()`, and `_load_copier_context()` parse JSON from environment variables without schema validation.

**Task:**
1. Read the pre_gen_project.py file
2. Create a schema validation function for copier context
3. Add validation after JSON parsing
4. Ensure only expected keys and value types are accepted

**Implementation:**
```python
VALID_DOCS_SITES = {"fumadocs", "sphinx-shibuya", "docusaurus", "none"}
VALID_CI_PLATFORMS = {"github-actions", "none"}

def _validate_string_value(value: str, allowed: set[str], field: str) -> str:
    """Validate string value against allowed set."""
    if value not in allowed:
        raise ValueError(f"Invalid {field}: {value}. Must be one of: {allowed}")
    return value
```

**Verification:**
- Test with valid values - should pass
- Test with invalid values - should raise ValueError
- Ensure error messages are actionable

---

### SEC-006: Replace manual YAML parsing with yaml.safe_load [P1]

**Category:** SECURITY
**Files:** `template/hooks/post_gen_project.py`
**Lines:** 43-54

**Problem:** Manual YAML parsing with string splitting is fragile and doesn't handle edge cases.

**Task:**
1. Read post_gen_project.py
2. Import yaml module (already available via pyyaml)
3. Replace manual parsing with `yaml.safe_load()`
4. Handle potential YAML parsing errors

**Implementation:**
```python
import yaml

def _load_answers(answers_path: Path) -> dict[str, str]:
    """Load answers from YAML file safely."""
    if not answers_path.exists():
        return {}
    try:
        with answers_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except yaml.YAMLError as e:
        sys.stderr.write(f"Warning: Failed to parse answers file: {e}\n")
        return {}
```

**Verification:**
- Test with valid YAML file
- Test with malformed YAML - should not crash
- Test with nested structures - should handle correctly

---

### SEC-007: Fix Docker hadolint resource leak [P1]

**Category:** SECURITY
**Files:** `scripts/ci/render_matrix.py`
**Lines:** 96-108

**Problem:** File opened for stdin without context manager, causing potential resource leak.

**Task:**
1. Read render_matrix.py
2. Wrap file open in context manager
3. Ensure proper cleanup on success and failure

**Implementation:**
```python
# Replace lines 96-108 with:
try:
    with docker_file.open("rb") as f:
        hadolint_result = subprocess.run(
            ["docker", "run", "--rm", "-i", "hadolint/hadolint"],
            stdin=f,
            capture_output=True,
            timeout=30,
        )
    # Process result...
except (subprocess.TimeoutExpired, FileNotFoundError):
    pass  # hadolint not available or timeout
```

**Verification:**
- Run with valid Dockerfile - should complete without resource warnings
- Run with timeout - should clean up properly

---

### SEC-008: Add URL validation in render_client.py [P1]

**Category:** SECURITY
**Files:** `scripts/automation/render_client.py`
**Lines:** 76-78

**Problem:** Variant name passed to URL construction with minimal validation.

**Task:**
1. Read render_client.py
2. Add validation function for variant names
3. Validate before URL construction
4. Reject suspicious patterns

**Implementation:**
```python
import re

VALID_VARIANT_PATTERN = re.compile(r'^[a-z0-9][a-z0-9_-]*$')

def _validate_variant_name(name: str) -> str:
    """Validate variant name is safe for URL construction."""
    if not VALID_VARIANT_PATTERN.match(name):
        raise ValueError(f"Invalid variant name: {name}. Must match pattern: {VALID_VARIANT_PATTERN.pattern}")
    if len(name) > 64:
        raise ValueError(f"Variant name too long: {len(name)} > 64 chars")
    return name
```

**Verification:**
- Test with valid names like "default", "api-python" - should pass
- Test with "../escape" - should fail
- Test with very long names - should fail

---

## TEST Tasks

### TEST-001: Create pytest configuration [P1]

**Category:** TEST
**Files:** `pyproject.toml`

**Problem:** No pytest configuration exists for the project.

**Task:**
1. Read current pyproject.toml
2. Add comprehensive pytest configuration
3. Configure coverage settings
4. Set up test markers

**Implementation:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
    "--cov=scripts",
    "--cov=template/hooks",
    "--cov-report=term-missing",
    "--cov-report=xml:coverage.xml",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
branch = true
source = ["scripts", "template/hooks"]
omit = ["*/__pycache__/*", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

**Verification:**
- Run `uv run pytest --collect-only` - should discover tests
- Run `uv run pytest --help` - should show custom markers

---

### TEST-002: Create test directory structure [P1]

**Category:** TEST
**Files:** Create new files

**Problem:** No organized test directory structure exists.

**Task:**
1. Create directory structure
2. Add __init__.py files
3. Create conftest.py with shared fixtures

**Files to create:**
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── ci/
│   │   ├── __init__.py
│   │   └── (test files go here)
│   └── hooks/
│       ├── __init__.py
│       └── (test files go here)
├── integration/
│   ├── __init__.py
│   └── (integration test files)
└── fixtures/
    ├── __init__.py
    ├── yaml_samples/
    │   ├── valid_copier_answers.yml
    │   ├── invalid_copier_answers.yml
    │   └── empty.yml
    └── json_samples/
        ├── valid_smoke_results.json
        └── invalid_smoke_results.json
```

**conftest.py content:**
```python
"""Shared pytest fixtures for riso tests."""
import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_copier_answers() -> dict:
    """Sample copier answers for testing."""
    return {
        "project_name": "Test Project",
        "project_slug": "test-project",
        "package_name": "test_project",
        "project_layout": "single-package",
        "quality_profile": "standard",
        "python_versions": ["3.11", "3.12", "3.13"],
        "cli_module": "disabled",
        "api_tracks": "none",
        "docs_site": "fumadocs",
    }


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess.run for testing."""
    results = []

    def mock_run(*args, **kwargs):
        from unittest.mock import MagicMock
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        results.append((args, kwargs))
        return result

    monkeypatch.setattr("subprocess.run", mock_run)
    return results
```

**Verification:**
- Run `uv run pytest --collect-only` - should show test structure
- Import conftest fixtures in a test file - should work

---

### TEST-003: Add unit tests for validate_release_configs.py [P1]

**Category:** TEST
**Files:** Create `tests/unit/ci/test_validate_release_configs.py`
**Depends on:** TEST-001, TEST-002

**Problem:** 286 lines of validation logic with zero test coverage.

**Task:**
1. Create comprehensive unit tests for all validation functions
2. Test valid configurations
3. Test invalid configurations with specific error messages
4. Test edge cases (empty files, malformed YAML)

**Test cases to implement:**
```python
"""Unit tests for validate_release_configs.py"""
import pytest
from pathlib import Path

# Import module under test
import sys
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "ci"))
from validate_release_configs import (
    validate_commitlint_config,
    validate_releaserc_config,
    validate_release_workflow,
)


class TestValidateCommitlintConfig:
    """Tests for commitlint configuration validation."""

    def test_valid_config(self, temp_dir):
        """Valid commitlint config should pass validation."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
extends:
  - "@commitlint/config-conventional"
rules:
  type-enum:
    - 2
    - always
    - [feat, fix, docs, style, refactor, test, chore]
""")
        valid, errors = validate_commitlint_config(temp_dir)
        assert valid is True
        assert len(errors) == 0

    def test_missing_extends(self, temp_dir):
        """Missing extends field should fail."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("rules: {}")
        valid, errors = validate_commitlint_config(temp_dir)
        assert valid is False
        assert any("extends" in e for e in errors)

    def test_missing_rules(self, temp_dir):
        """Missing rules field should fail."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("extends: ['@commitlint/config-conventional']")
        valid, errors = validate_commitlint_config(temp_dir)
        assert valid is False
        assert any("rules" in e for e in errors)

    def test_malformed_yaml(self, temp_dir):
        """Malformed YAML should fail gracefully."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("extends: [unclosed")
        valid, errors = validate_commitlint_config(temp_dir)
        assert valid is False
        assert any("YAML" in e or "parsing" in e.lower() for e in errors)

    def test_missing_file(self, temp_dir):
        """Missing config file should fail."""
        valid, errors = validate_commitlint_config(temp_dir)
        assert valid is False
        assert any("not found" in e.lower() for e in errors)


class TestValidateReleasercConfig:
    """Tests for .releaserc.yml validation."""

    def test_valid_config(self, temp_dir):
        """Valid releaserc config should pass."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
  - "@semantic-release/github"
""")
        valid, errors = validate_releaserc_config(temp_dir)
        assert valid is True

    def test_missing_required_plugins(self, temp_dir):
        """Missing required plugins should fail."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
""")
        valid, errors = validate_releaserc_config(temp_dir)
        assert valid is False
        assert any("plugin" in e.lower() for e in errors)


class TestValidateReleaseWorkflow:
    """Tests for release workflow validation."""

    def test_valid_workflow(self, temp_dir):
        """Valid release workflow should pass."""
        workflows_dir = temp_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        workflow = workflows_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Release
        run: npx semantic-release
""")
        valid, errors = validate_release_workflow(temp_dir)
        assert valid is True

    def test_missing_workflow(self, temp_dir):
        """Missing workflow should fail."""
        valid, errors = validate_release_workflow(temp_dir)
        assert valid is False
```

**Verification:**
- Run `uv run pytest tests/unit/ci/test_validate_release_configs.py -v`
- All tests should pass
- Coverage should increase

---

### TEST-004: Add unit tests for pre_gen_project.py [P1]

**Category:** TEST
**Files:** Create `tests/unit/hooks/test_pre_gen_project.py`
**Depends on:** TEST-001, TEST-002

**Problem:** Critical hook with 364 lines has no tests.

**Task:**
1. Test environment variable loading functions
2. Test SaaS validation logic
3. Test tool provisioning logic
4. Mock subprocess calls

**Test cases to implement:**
```python
"""Unit tests for pre_gen_project.py hook."""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parents[3] / "template" / "hooks"))
from pre_gen_project import (
    _load_docs_site,
    _load_ci_platform,
    _load_copier_context,
    _validate_saas_starter,
    _attempt_install,
    ProvisionResult,
)


class TestLoadDocsSite:
    """Tests for _load_docs_site function."""

    def test_default_value(self, monkeypatch):
        """Should return default when no env vars set."""
        monkeypatch.delenv("COPIER_ANSWERS", raising=False)
        monkeypatch.delenv("COPIER_JINJA2_CONTEXT", raising=False)
        monkeypatch.delenv("COPIER_RENDER_CONTEXT", raising=False)
        result = _load_docs_site()
        assert result == "fumadocs"

    def test_custom_default(self, monkeypatch):
        """Should return custom default when specified."""
        monkeypatch.delenv("COPIER_ANSWERS", raising=False)
        result = _load_docs_site(default="sphinx-shibuya")
        assert result == "sphinx-shibuya"

    def test_loads_from_copier_answers(self, monkeypatch):
        """Should load docs_site from COPIER_ANSWERS."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps({"docs_site": "docusaurus"}))
        result = _load_docs_site()
        assert result == "docusaurus"

    def test_invalid_json_fallback(self, monkeypatch):
        """Should fallback to default on invalid JSON."""
        monkeypatch.setenv("COPIER_ANSWERS", "not valid json")
        result = _load_docs_site()
        assert result == "fumadocs"

    def test_non_dict_fallback(self, monkeypatch):
        """Should fallback when JSON is not a dict."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps(["list", "not", "dict"]))
        result = _load_docs_site()
        assert result == "fumadocs"


class TestValidateSaasStarter:
    """Tests for SaaS starter validation."""

    def test_disabled_module_returns_empty(self):
        """Disabled SaaS module should return no issues."""
        context = {"saas_starter_module": "disabled"}
        issues = _validate_saas_starter(context)
        assert issues == []

    def test_incompatible_neon_supabase_storage(self):
        """Neon + Supabase Storage should be error."""
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "supabase-storage",
        }
        issues = _validate_saas_starter(context)
        errors = [i for i in issues if i["severity"] == "error"]
        assert len(errors) == 1
        assert "Neon" in errors[0]["message"]

    def test_cloudflare_prisma_warning(self):
        """Cloudflare + Prisma should be warning."""
        context = {
            "saas_starter_module": "enabled",
            "saas_hosting": "cloudflare",
            "saas_orm": "prisma",
        }
        issues = _validate_saas_starter(context)
        warnings = [i for i in issues if i["severity"] == "warning"]
        assert len(warnings) >= 1
        assert any("Prisma" in w["message"] for w in warnings)

    def test_supabase_clerk_info(self):
        """Supabase + Clerk should be info notice."""
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "supabase",
            "saas_auth": "clerk",
        }
        issues = _validate_saas_starter(context)
        infos = [i for i in issues if i["severity"] == "info"]
        assert len(infos) >= 1


class TestProvisionResult:
    """Tests for ProvisionResult dataclass."""

    def test_minimal_creation(self):
        """Should create with required fields only."""
        result = ProvisionResult(
            tool_name="uv",
            version_requested="0.4",
            status="installed",
        )
        assert result["tool_name"] == "uv"
        assert result["status"] == "installed"
        assert "timestamp" in result

    def test_with_optional_fields(self):
        """Should include optional fields when provided."""
        result = ProvisionResult(
            tool_name="node",
            version_requested="20",
            status="failed",
            stderr="Error message",
            next_steps="Install manually",
            retry_command="mise install node@20",
        )
        assert result["stderr"] == "Error message"
        assert result["next_steps"] == "Install manually"
        assert result["retry_command"] == "mise install node@20"


class TestAttemptInstall:
    """Tests for _attempt_install function."""

    def test_already_present(self, monkeypatch):
        """Should return already_present when tool exists."""
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/" + x)
        result = _attempt_install("uv", "0.4", "uv@0.4")
        assert result["status"] == "already_present"

    def test_mise_install_success(self, monkeypatch, mock_subprocess):
        """Should return installed on successful mise install."""
        calls = []
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/mise" if x == "mise" else None)

        def mock_which_after_install(x):
            if x == "uv" and len(calls) > 0:
                return "/usr/bin/uv"
            if x == "mise":
                return "/usr/bin/mise"
            return None

        # This test would need more sophisticated mocking
        # Simplified version:
        result = _attempt_install("nonexistent", "1.0", None)
        assert result["status"] == "failed"
```

**Verification:**
- Run `uv run pytest tests/unit/hooks/test_pre_gen_project.py -v`
- All tests should pass

---

### TEST-005: Add unit tests for record_module_success.py [P1]

**Category:** TEST
**Files:** Create `tests/unit/ci/test_record_module_success.py`
**Depends on:** TEST-001, TEST-002

**Problem:** Module success tracking logic untested, including potential division by zero.

**Task:**
1. Test ModuleStats class
2. Test success rate calculation
3. Test edge cases (zero totals)
4. Test JSON serialization

**Test cases:**
```python
"""Unit tests for record_module_success.py"""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "ci"))
from record_module_success import ModuleStats, ModuleSuccessRecorder


class TestModuleStats:
    """Tests for ModuleStats dataclass."""

    def test_initial_state(self):
        """New ModuleStats should have zero counts."""
        stats = ModuleStats()
        assert stats.passed == 0
        assert stats.failed == 0
        assert stats.errored == 0
        assert stats.skipped == 0

    def test_total_calculation(self):
        """Total should sum all counts."""
        stats = ModuleStats(passed=5, failed=2, errored=1, skipped=3)
        assert stats.total() == 11

    def test_success_rate_normal(self):
        """Success rate should be passed/total."""
        stats = ModuleStats(passed=8, failed=2)
        assert stats.success_rate() == 0.8

    def test_success_rate_zero_total(self):
        """Success rate should be 0.0 when total is 0."""
        stats = ModuleStats()
        assert stats.success_rate() == 0.0

    def test_success_rate_all_passed(self):
        """Success rate should be 1.0 when all passed."""
        stats = ModuleStats(passed=10)
        assert stats.success_rate() == 1.0

    def test_success_rate_all_failed(self):
        """Success rate should be 0.0 when all failed."""
        stats = ModuleStats(failed=10)
        assert stats.success_rate() == 0.0

    def test_to_dict(self):
        """to_dict should include all fields plus computed values."""
        stats = ModuleStats(passed=5, failed=2, errored=1, skipped=2)
        d = stats.to_dict()
        assert d["passed"] == 5
        assert d["failed"] == 2
        assert d["total"] == 10
        assert d["success_rate"] == 0.5


class TestModuleSuccessRecorder:
    """Tests for ModuleSuccessRecorder class."""

    def test_empty_recorder(self):
        """Empty recorder should have no modules."""
        recorder = ModuleSuccessRecorder()
        assert len(recorder.modules) == 0

    def test_record_result(self):
        """Should record module results correctly."""
        recorder = ModuleSuccessRecorder()
        recorder.record("cli", "passed", "default")
        assert "cli" in recorder.modules
        assert recorder.modules["cli"].passed == 1

    def test_record_multiple_variants(self):
        """Should accumulate across variants."""
        recorder = ModuleSuccessRecorder()
        recorder.record("api", "passed", "variant1")
        recorder.record("api", "passed", "variant2")
        recorder.record("api", "failed", "variant3")
        assert recorder.modules["api"].passed == 2
        assert recorder.modules["api"].failed == 1

    def test_write_and_load(self, temp_dir):
        """Should serialize to JSON and back."""
        recorder = ModuleSuccessRecorder()
        recorder.record("test_module", "passed", "v1")

        output_path = temp_dir / "success.json"
        recorder.write(output_path)

        assert output_path.exists()
        import json
        data = json.loads(output_path.read_text())
        assert "test_module" in data
```

**Verification:**
- Run `uv run pytest tests/unit/ci/test_record_module_success.py -v`
- Check coverage includes edge cases

---

### TEST-006: Add unit tests for validate_dockerfiles.py [P2]

**Category:** TEST
**Files:** Create `tests/unit/ci/test_validate_dockerfiles.py`
**Depends on:** TEST-001, TEST-002

**Task:** Test Dockerfile discovery, hadolint output parsing, and error categorization.

---

### TEST-007: Add unit tests for validate_workflows.py [P2]

**Category:** TEST
**Files:** Create `tests/unit/ci/test_validate_workflows.py`
**Depends on:** TEST-001, TEST-002

**Task:** Test actionlint integration, JSON parsing, and error reporting.

---

### TEST-008: Add unit tests for render_matrix.py [P2]

**Category:** TEST
**Files:** Create `tests/unit/ci/test_render_matrix.py`
**Depends on:** TEST-001, TEST-002

**Task:** Test variant discovery, smoke results parsing, and metadata handling.

---

### TEST-009: Add unit tests for quality_tool_check.py [P2]

**Category:** TEST
**Files:** Create `tests/unit/hooks/test_quality_tool_check.py`
**Depends on:** TEST-001, TEST-002

**Task:** Test tool checking and provisioning logic with mocked subprocess.

---

### TEST-010: Add integration tests for template rendering [P2]

**Category:** TEST
**Files:** Create `tests/integration/test_template_rendering.py`
**Depends on:** TEST-001, TEST-002

**Task:** Test that template renders correctly for each sample configuration.

---

### TEST-011: Create test fixtures directory with sample data [P1]

**Category:** TEST
**Files:** Create files in `tests/fixtures/`

**Task:**
1. Create valid YAML samples
2. Create invalid YAML samples
3. Create JSON samples for smoke results
4. Create mock subprocess outputs

**Files to create:**
- `tests/fixtures/yaml_samples/valid_commitlint.yml`
- `tests/fixtures/yaml_samples/valid_releaserc.yml`
- `tests/fixtures/yaml_samples/invalid_missing_extends.yml`
- `tests/fixtures/json_samples/smoke_results_all_pass.json`
- `tests/fixtures/json_samples/smoke_results_with_failures.json`
- `tests/fixtures/hadolint_output/valid_dockerfile.json`
- `tests/fixtures/hadolint_output/errors_and_warnings.json`

---

## REFACTOR Tasks

### REF-001: Extract common environment loading logic [P2]

**Category:** REFACTOR
**Files:** `template/hooks/pre_gen_project.py`
**Lines:** 57-121

**Problem:** Three nearly identical functions load values from the same environment variables.

**Task:**
1. Create generic `_load_from_env(key: str, default: T) -> T` function
2. Refactor `_load_docs_site`, `_load_ci_platform`, `_load_copier_context` to use it
3. Reduce code duplication

**Implementation:**
```python
def _load_from_env(key: str, default: str, candidates: tuple[str, ...] = None) -> str:
    """Load a string value from copier environment variables."""
    if candidates is None:
        candidates = ("COPIER_ANSWERS", "COPIER_JINJA2_CONTEXT", "COPIER_RENDER_CONTEXT")

    for env_key in candidates:
        raw = os.environ.get(env_key)
        if not raw:
            continue
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                value = data.get(key)
                if isinstance(value, str) and value:
                    return value
        except json.JSONDecodeError:
            continue
    return default


def _load_docs_site(default: str = "fumadocs") -> str:
    return _load_from_env("docs_site", default)


def _load_ci_platform(default: str = "github-actions") -> str:
    return _load_from_env("ci_platform", default)
```

**Verification:**
- All existing functionality should work identically
- Run any existing tests

---

### REF-002: Standardize exception handling patterns [P2]

**Category:** REFACTOR
**Files:** Multiple scripts in `scripts/ci/`

**Problem:** Inconsistent use of broad `except Exception` vs specific exceptions.

**Task:**
1. Audit all `except Exception` usages
2. Replace with specific exception types
3. Add proper logging for caught exceptions
4. Ensure errors are not silently swallowed

**Files to update:**
- `scripts/ci/render_matrix.py`
- `scripts/ci/validate_release_configs.py`
- `scripts/ci/record_module_success.py`
- `scripts/automation/render_client.py`

**Pattern to follow:**
```python
# Instead of:
except Exception:
    pass

# Use:
except (json.JSONDecodeError, KeyError) as e:
    logger.warning(f"Failed to parse JSON: {e}")
    # Handle gracefully or re-raise
```

---

### REF-003: Normalize type hints to modern Python style [P2]

**Category:** REFACTOR
**Files:** All Python files in `scripts/` and `template/hooks/`

**Problem:** Mix of `Dict`/`dict`, `List`/`list`, `Optional`/`| None` styles.

**Task:**
1. Replace `Dict[K, V]` with `dict[K, V]`
2. Replace `List[T]` with `list[T]`
3. Replace `Optional[T]` with `T | None`
4. Remove unused imports from `typing` module

**Example changes:**
```python
# Before:
from typing import Dict, List, Optional
def func(data: Dict[str, List[int]], default: Optional[str] = None) -> List[str]:

# After:
def func(data: dict[str, list[int]], default: str | None = None) -> list[str]:
```

---

### REF-004: Create TypedDict for complex structures [P2]

**Category:** REFACTOR
**Files:**
- `scripts/ci/record_module_success.py`
- `scripts/ci/render_matrix.py`
- `scripts/automation/render_client.py`

**Problem:** Using `dict[str, Any]` loses type safety.

**Task:**
1. Define TypedDict for smoke results
2. Define TypedDict for module stats
3. Define TypedDict for API responses
4. Update function signatures

**Implementation:**
```python
from typing import TypedDict

class SmokeResult(TypedDict):
    module: str
    status: str  # "passed" | "failed" | "errored" | "skipped"
    duration: float
    error: str | None

class ModuleStatsDict(TypedDict):
    passed: int
    failed: int
    errored: int
    skipped: int
    total: int
    success_rate: float
```

---

### REF-005: Extract validation utilities into shared module [P2]

**Category:** REFACTOR
**Files:** Create `scripts/lib/validation.py`

**Problem:** Similar validation patterns repeated across multiple files.

**Task:**
1. Create shared validation utilities module
2. Extract common patterns (YAML loading, schema validation, path validation)
3. Update callers to use shared utilities

---

### REF-006: Add docstrings to all functions [P3]

**Category:** REFACTOR
**Files:** All Python files in `scripts/` and `template/hooks/`

**Problem:** 40% of functions lack docstrings.

**Task:**
1. Audit all functions for missing docstrings
2. Add Google-style docstrings
3. Include Args, Returns, Raises sections

---

### REF-007: Remove code duplication in validation scripts [P3]

**Category:** REFACTOR
**Files:** `scripts/ci/validate_*.py`

**Problem:** Similar YAML loading and error handling patterns repeated.

**Task:**
1. Identify common patterns
2. Extract into shared utilities
3. Update all validation scripts

---

## CI Tasks

### CI-001: Update GitHub Actions versions [P1]

**Category:** CI
**Files:** `.github/workflows/quality.yml`
**Lines:** 14, 31, 34

**Problem:** Using outdated action versions (checkout@v3, setup-python@v4).

**Task:**
1. Update `actions/checkout@v3` to `@v4`
2. Update `actions/setup-python@v4` to `@v5`
3. Verify compatibility

**Verification:**
- Validate YAML syntax
- CI should still pass

---

### CI-002: Add if-no-files-found to artifact uploads [P1]

**Category:** CI
**Files:**
- `.github/workflows/quality.yml` (line 62)
- `template/files/shared/.github/workflows/riso-matrix.yml.jinja` (line 90)

**Problem:** Artifact upload fails if files don't exist.

**Task:**
1. Add `if-no-files-found: warn` to artifact upload steps
2. Prevents CI failure when optional artifacts are missing

**Implementation:**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: results/
    if-no-files-found: warn  # Add this line
    retention-days: 90
```

---

### CI-003: Fix ephemeral UV cache [P1]

**Category:** CI
**Files:** `template/files/shared/.github/workflows/quality-matrix.yml.jinja`
**Lines:** 13

**Problem:** `UV_CACHE_DIR` set to `runner.temp` which is not persisted.

**Task:**
1. Change UV_CACHE_DIR to standard location `~/.cache/uv`
2. Or add explicit cache action to persist the temp location

**Implementation:**
```yaml
# Option 1: Use standard location
env:
  UV_CACHE_DIR: ~/.cache/uv

# Option 2: Add cache step
- uses: actions/cache@v4
  with:
    path: ${{ runner.temp }}/uv-cache
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
```

---

### CI-004: Add actionlint validation step [P2]

**Category:** CI
**Files:** `.github/workflows/quality.yml`

**Problem:** Workflow YAML syntax errors not caught until runtime.

**Task:**
1. Add actionlint step to validate workflow files
2. Run on all `.github/workflows/*.yml` files

**Implementation:**
```yaml
lint-workflows:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install actionlint
      run: |
        bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
    - name: Lint workflows
      run: ./actionlint -color
```

---

### CI-005: Add Dependabot configuration [P2]

**Category:** CI
**Files:** Create `.github/dependabot.yml`

**Problem:** No automated dependency updates configured.

**Task:**
1. Create Dependabot configuration
2. Configure for Python, Node.js, and GitHub Actions

**Implementation:**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      python-deps:
        patterns:
          - "*"

  - package-ecosystem: "npm"
    directory: "/template/files/node"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      actions:
        patterns:
          - "*"
```

---

### CI-006: Add pip-audit to CI pipeline [P2]

**Category:** CI
**Files:** `.github/workflows/quality.yml`

**Problem:** No security scanning for Python dependencies.

**Task:**
1. Add pip-audit step to quality workflow
2. Fail on HIGH/CRITICAL vulnerabilities

**Implementation:**
```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - name: Install pip-audit
      run: pip install pip-audit
    - name: Run pip-audit
      run: pip-audit --strict --vulnerability-service osv
```

---

## DOCS Tasks

### DOC-001: Expand README.md with installation and usage [P1]

**Category:** DOCS
**Files:** `README.md`

**Problem:** README is only 24 lines, missing essential information.

**Task:**
1. Add installation instructions
2. Add usage examples with copier
3. Add module configuration guide
4. Add contributing section
5. Add license information

**Sections to add:**
- Prerequisites
- Quick Start
- Module Reference (table)
- Configuration Options
- Sample Projects
- Contributing
- License

---

### DOC-002: Complete constitution placeholders [P1]

**Category:** DOCS
**Files:** `.specify/memory/constitution.md`

**Problem:** Constitution contains only template markers like `[PRINCIPLE_N_NAME]`.

**Task:**
1. Define actual governance principles for riso
2. Fill in all placeholder sections
3. Add ratification date

---

### DOC-003: Update README feature completion status [P1]

**Category:** DOCS
**Files:** `README.md`

**Problem:** README shows only 001-003 as complete, but specs/ has implementations through 015.

**Task:**
1. Review all specs/ directories for completion status
2. Update README with accurate completed features list
3. Align with roadmap.md

---

### DOC-004: Add API documentation for scripts [P2]

**Category:** DOCS
**Files:** Create `docs/api/scripts.md`

**Problem:** 18 Python scripts lack API documentation.

**Task:**
1. Document each script's purpose
2. Document CLI arguments
3. Document exit codes
4. Document dependencies

---

### DOC-005: Create CONTRIBUTING.md [P2]

**Category:** DOCS
**Files:** Create `CONTRIBUTING.md`

**Task:**
1. Define contribution workflow
2. Document code style requirements
3. Document testing requirements
4. Document PR process

---

### DOC-006: Add inline documentation to complex functions [P3]

**Category:** DOCS
**Files:** `template/hooks/pre_gen_project.py`, `scripts/ci/render_matrix.py`

**Task:**
1. Add explanatory comments to complex logic
2. Document non-obvious design decisions
3. Link to relevant specifications

---

## CONFIG Tasks

### CFG-001: Fix placeholder in pyproject.toml [P1]

**Category:** CONFIG
**Files:** `pyproject.toml`

**Problem:** Description is placeholder "Add your description here".

**Task:**
1. Update description to accurate project description
2. Add project URLs (homepage, documentation, repository)
3. Add classifiers

**Implementation:**
```toml
[project]
name = "riso"
version = "0.1.0"
description = "Modular Copier-based project template for Python and Node.js applications"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Riso Template Working Group"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[project.urls]
Homepage = "https://github.com/wyattowalsh/riso"
Documentation = "https://github.com/wyattowalsh/riso/tree/main/docs"
Repository = "https://github.com/wyattowalsh/riso"
```

---

### CFG-002: Reconsider Python 3.13 minimum requirement [P2]

**Category:** CONFIG
**Files:** `pyproject.toml`

**Problem:** Python 3.13 is bleeding edge; most users have 3.11 or 3.12.

**Task:**
1. Change `requires-python = ">=3.13"` to `">=3.11"`
2. Ensure all code is compatible with 3.11
3. Update CI matrix if needed

---

### CFG-003: Add development dependencies group [P2]

**Category:** CONFIG
**Files:** `pyproject.toml`

**Problem:** No dev dependencies defined (testing, linting tools).

**Task:**
1. Add `[project.optional-dependencies]` section
2. Define dev, test, docs groups

**Implementation:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.4",
    "mypy>=1.0",
    "pylint>=3.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.0",
]
docs = [
    "sphinx>=7.0",
    "shibuya>=2024.0",
]
```

---

## FEATURE Tasks

### FEAT-001: Generate smoke-results.json for samples [P1]

**Category:** FEATURE
**Files:** `scripts/render-samples.sh`

**Problem:** Documentation claims smoke-results.json should be generated but none exist.

**Task:**
1. Ensure smoke tests run during sample rendering
2. Write results to `samples/<variant>/smoke-results.json`
3. Aggregate to `samples/metadata/module_success.json`

---

### FEAT-002: Add sample validation to CI [P2]

**Category:** FEATURE
**Files:** `.github/workflows/quality.yml`

**Problem:** Samples are not validated in CI.

**Task:**
1. Add job to render all samples
2. Run smoke tests on each
3. Fail if any sample fails

---

### FEAT-003: Implement validate_saas_combinations.py validation [P2]

**Category:** FEATURE
**Files:** `scripts/ci/validate_saas_combinations.py`
**Lines:** 121-127

**Problem:** Core validation logic is not implemented - all tests marked as "skipped".

**Task:**
1. Implement actual template rendering for combinations
2. Run smoke tests on rendered output
3. Report results instead of skipping

---

---

## Task Dependencies Graph

```
TEST-001 (pytest config)
   └── TEST-002 (test structure)
         ├── TEST-003 (validate_release_configs tests)
         ├── TEST-004 (pre_gen_project tests)
         ├── TEST-005 (record_module_success tests)
         ├── TEST-006 (validate_dockerfiles tests)
         ├── TEST-007 (validate_workflows tests)
         ├── TEST-008 (render_matrix tests)
         ├── TEST-009 (quality_tool_check tests)
         └── TEST-010 (integration tests)

SEC-001 through SEC-004 (P0 security) - No dependencies, do first

CI-001 through CI-003 (P1 CI fixes) - No dependencies

DOC-001, DOC-002, DOC-003 - No dependencies

CFG-001, CFG-002 - No dependencies

REF-001 through REF-007 - Should follow test infrastructure
```

---

## Execution Order Recommendation

### Sprint 1: Security & Foundation
1. SEC-001, SEC-002, SEC-003, SEC-004 (P0 security)
2. CI-001, CI-002, CI-003 (P1 CI fixes)
3. TEST-001, TEST-002 (test infrastructure)
4. CFG-001 (pyproject placeholder)

### Sprint 2: Test Coverage
1. TEST-003, TEST-004, TEST-005 (high-priority tests)
2. TEST-011 (fixtures)
3. SEC-005, SEC-006, SEC-007, SEC-008 (P1 security)
4. DOC-001, DOC-002, DOC-003 (documentation)

### Sprint 3: Quality & Refinement
1. TEST-006, TEST-007, TEST-008, TEST-009 (remaining tests)
2. REF-001, REF-002, REF-003, REF-004 (refactoring)
3. CI-004, CI-005, CI-006 (CI enhancements)
4. FEAT-001 (smoke results)

### Sprint 4: Polish
1. TEST-010 (integration tests)
2. REF-005, REF-006, REF-007 (remaining refactoring)
3. DOC-004, DOC-005, DOC-006 (remaining docs)
4. FEAT-002, FEAT-003 (remaining features)
5. CFG-002, CFG-003 (config polish)

---

## Agent Instructions

When working on these tasks:

1. **Read the file(s) first** before making changes
2. **Run tests** after each change if test infrastructure exists
3. **Commit incrementally** with descriptive messages
4. **Update this file** to mark tasks as completed
5. **Note any blockers** or new issues discovered

### Task Status Tracking

Mark tasks with:
- `[ ]` - Not started
- `[~]` - In progress
- `[x]` - Completed
- `[!]` - Blocked (add reason)

---

*Last updated: 2025-12-23*
*Generated from comprehensive E2E audit*
