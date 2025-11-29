"""Pytest-benchmark tests for core Riso operations.

These benchmarks are run with pytest-benchmark to track performance
of key operations over time.

Run with:
    pytest tests/benchmarks/ --benchmark-only
    pytest tests/benchmarks/ --benchmark-autosave
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def sample_copier_answers():
    """Sample copier answers for testing."""
    return {
        "project_name": "Test Project",
        "project_slug": "test-project",
        "package_name": "test_project",
        "project_layout": "single-package",
        "quality_profile": "standard",
        "python_versions": ["3.11", "3.12", "3.13"],
        "cli_module": "enabled",
        "api_tracks": "python",
        "graphql_api_module": "disabled",
        "mcp_module": "disabled",
        "websocket_module": "disabled",
        "codegen_module": "disabled",
        "changelog_module": "disabled",
        "notebook_module": "disabled",
        "docs_site": "fumadocs",
        "shared_logic": "disabled",
        "ci_platform": "github-actions",
        "saas_starter_module": "disabled",
    }


def test_pydantic_validation(benchmark, sample_copier_answers):
    """Benchmark Pydantic model validation."""
    sys.path.insert(0, str(REPO_ROOT / "template"))
    from hooks.validation import validate_copier_answers

    def validate():
        return validate_copier_answers(sample_copier_answers)

    result = benchmark(validate)
    assert result is not None


def test_template_discovery(benchmark):
    """Benchmark template file discovery."""
    template_dir = REPO_ROOT / "template"

    def discover():
        jinja_files = list(template_dir.rglob("*.jinja"))
        py_files = list(template_dir.rglob("*.py"))
        yml_files = list(template_dir.rglob("*.yml"))
        return len(jinja_files), len(py_files), len(yml_files)

    result = benchmark(discover)
    assert all(count > 0 for count in result)


def test_hook_import(benchmark):
    """Benchmark hook module import."""
    def import_hooks():
        sys.path.insert(0, str(REPO_ROOT / "template"))
        from hooks import validation  # noqa: F401
        return True

    result = benchmark(import_hooks)
    assert result is True


def test_subprocess_security_import(benchmark):
    """Benchmark subprocess security module import."""
    def import_security():
        sys.path.insert(0, str(REPO_ROOT))
        from scripts.subprocess_security import run_command_safe, sanitize_path  # noqa: F401
        return True

    result = benchmark(import_security)
    assert result is True


def test_path_sanitization(benchmark):
    """Benchmark path sanitization."""
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.subprocess_security import sanitize_path

    test_path = Path("/tmp/test/file.txt")
    allowed_parent = Path("/tmp")

    result = benchmark(sanitize_path, test_path, allowed_parent)
    assert result == test_path.resolve()


def test_command_validation(benchmark):
    """Benchmark command validation."""
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.subprocess_security import validate_command

    test_command = ["ls", "-la", "/tmp"]
    allowed_commands = {"ls", "cat", "grep", "find"}

    # benchmark() automatically handles the call
    benchmark(validate_command, test_command, allowed_commands)


# Benchmark groups for reporting
pytest.mark.benchmark(group="validation")
pytest.mark.benchmark(group="discovery")
pytest.mark.benchmark(group="import")
pytest.mark.benchmark(group="security")
