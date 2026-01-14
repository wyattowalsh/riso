"""Shared pytest fixtures for riso tests."""
import sys
import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Add project root to path for scripts module imports
# This is needed because scripts use `from scripts.lib.logger import ...`
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# MCP-specific fixtures
@pytest.fixture
def mcp_server():
    """Provide the MCP server instance for testing."""
    from riso.mcp.server import mcp
    return mcp


@pytest.fixture
def session_manager():
    """Provide a fresh session manager for testing."""
    from riso.mcp.session import SessionManager
    return SessionManager(ttl_minutes=60)


@pytest.fixture
def sample_prompts():
    """Sample prompts for wizard testing."""
    return [
        {"name": "project_name", "type": "str", "help": "Project name"},
        {"name": "package_name", "type": "str", "help": "Package name"},
        {"name": "cli_module", "type": "str", "choices": ["enabled", "disabled"]},
    ]


@pytest.fixture
def caplog(caplog):
    """Enhance caplog to capture loguru logs.

    This fixture intercepts loguru's output and makes it available
    through pytest's caplog mechanism.
    """
    from loguru import logger
    import logging

    class PropagateHandler(logging.Handler):
        """Handler that propagates loguru records to Python logging."""

        def emit(self, record):
            """Emit a log record to standard logging."""
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)


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
    from unittest.mock import MagicMock

    results = []

    def mock_run(*args, **kwargs):
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        results.append((args, kwargs))
        return result

    monkeypatch.setattr("subprocess.run", mock_run)
    return results


@pytest.fixture
def ci_scripts_path(monkeypatch):
    """Add CI scripts to Python path for imports."""
    scripts_path = Path(__file__).parent.parent / "scripts" / "ci"
    monkeypatch.syspath_prepend(str(scripts_path))
    return scripts_path


@pytest.fixture
def hooks_path(monkeypatch):
    """Add template hooks to Python path for imports."""
    hooks_path = Path(__file__).parent.parent / "template" / "hooks"
    monkeypatch.syspath_prepend(str(hooks_path))
    return hooks_path


@pytest.fixture
def scripts_hooks_path(monkeypatch):
    """Add scripts/hooks to Python path for imports."""
    scripts_hooks_path = Path(__file__).parent.parent / "scripts" / "hooks"
    monkeypatch.syspath_prepend(str(scripts_hooks_path))
    return scripts_hooks_path


@pytest.fixture
def lib_path(monkeypatch):
    """Add scripts/lib to Python path for imports."""
    lib_path = Path(__file__).parent.parent / "scripts" / "lib"
    monkeypatch.syspath_prepend(str(lib_path))
    return lib_path


@pytest.fixture
def sample_dockerfile(tmp_path):
    """Create a sample valid Dockerfile.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Returns:
        Path: Path to the created Dockerfile
    """
    dockerfile = tmp_path / 'Dockerfile'
    dockerfile.write_text('FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\n')
    return dockerfile


@pytest.fixture
def sample_workflow(tmp_path):
    """Create a sample GitHub Actions workflow.

    Creates a basic workflow file in .github/workflows/ with a simple
    test job that checks out the repository.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Returns:
        Path: Path to the created workflow file
    """
    workflow_dir = tmp_path / '.github' / 'workflows'
    workflow_dir.mkdir(parents=True)
    workflow = workflow_dir / 'test.yml'
    workflow.write_text('''name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
''')
    return workflow


@pytest.fixture
def sample_pyproject(tmp_path):
    """Create a sample pyproject.toml file.

    Creates a minimal pyproject.toml with project name and version.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Returns:
        Path: Path to the created pyproject.toml file
    """
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text('''[project]
name = "test-project"
version = "0.1.0"
''')
    return pyproject


@pytest.fixture
def sample_copier_context():
    """Provide a sample copier context dictionary.

    Contains typical copier template variables for testing template
    rendering and project generation workflows.

    Returns:
        dict: Dictionary of copier context variables
    """
    return {
        'project_name': 'test-project',
        'project_type': 'python',
        'python_version': '3.11',
        'use_docker': True,
        'ci_platform': 'github',
        'docs_site': 'sphinx',
    }
