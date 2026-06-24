"""Shared fixtures for hooks unit tests."""

import json
import pytest
from unittest.mock import MagicMock


# ============================================================================
# Subprocess Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_subprocess_success(mocker):
    """Mock all subprocess calls to succeed.

    Returns a mock subprocess.run that returns success (returncode=0).
    """
    mock = mocker.patch("subprocess.run")
    mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
    return mock


@pytest.fixture
def mock_subprocess_failure(mocker):
    """Mock subprocess calls to fail.

    Returns a mock subprocess.run that returns failure (returncode=1).
    """
    mock = mocker.patch("subprocess.run")
    mock.return_value = MagicMock(returncode=1, stdout="", stderr="error")
    return mock


# ============================================================================
# Shutil Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_shutil_which_found(mocker):
    """Mock shutil.which to find tools.

    Returns a mock that simulates all tools being available.
    """
    return mocker.patch("shutil.which", return_value="/usr/bin/tool")


@pytest.fixture
def mock_shutil_which_missing(mocker):
    """Mock shutil.which to not find tools.

    Returns a mock that simulates all tools being missing.
    """
    return mocker.patch("shutil.which", return_value=None)


# ============================================================================
# Context Fixtures
# ============================================================================


@pytest.fixture
def sample_python_context():
    """Sample context for Python projects.

    Provides a realistic configuration for Python-based projects
    with common settings.
    """
    return {
        "project_name": "test-project",
        "project_type": "python",
        "python_version": "3.11",
        "use_docker": True,
        "ci_platform": "github-actions",
        "docs_framework": "sphinx-shibuya",
        "saas_infra_module": "disabled",
    }


@pytest.fixture
def sample_node_context():
    """Sample context for Node.js projects.

    Provides a realistic configuration for Node.js-based projects
    with common settings.
    """
    return {
        "project_name": "test-project",
        "project_type": "node",
        "node_version": "20",
        "use_docker": True,
        "ci_platform": "github-actions",
        "docs_framework": "fumadocs",
        "saas_infra_module": "disabled",
    }


@pytest.fixture
def sample_saas_context():
    """Sample context for SaaS starter projects.

    Provides a realistic configuration for projects with SaaS
    starter module enabled.
    """
    return {
        "project_name": "test-saas-project",
        "project_type": "python",
        "python_version": "3.11",
        "use_docker": True,
        "ci_platform": "github-actions",
        "docs_framework": "fumadocs",
        "saas_infra_module": "enabled",
        "saas_database": "neon",
        "saas_storage": "r2",
        "saas_hosting": "vercel",
        "saas_orm": "prisma",
        "saas_auth_provider": "clerk",
    }


# ============================================================================
# Environment Variable Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_copier_answers(monkeypatch):
    """Factory fixture for mocking COPIER_ANSWERS environment variable.

    Returns a function that can be called with a dict to set the
    COPIER_ANSWERS environment variable with JSON content.

    Example:
        def test_something(mock_copier_answers):
            mock_copier_answers({'docs_framework': 'fumadocs'})
            # Now COPIER_ANSWERS env var is set
    """

    def _set_copier_answers(answers: dict):
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps(answers))

    return _set_copier_answers


@pytest.fixture
def clear_copier_env(monkeypatch):
    """Clear all Copier-related environment variables.

    Removes COPIER_ANSWERS, COPIER_JINJA2_CONTEXT, and
    COPIER_RENDER_CONTEXT to ensure clean test state.
    """
    monkeypatch.delenv("COPIER_ANSWERS", raising=False)
    monkeypatch.delenv("COPIER_JINJA2_CONTEXT", raising=False)
    monkeypatch.delenv("COPIER_RENDER_CONTEXT", raising=False)


# ============================================================================
# Tool Check Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_tool_check_success(mocker):
    """Mock ToolCheck class to return successful tool checks.

    Returns a mock that simulates all tools being present and working.
    """
    from pre_gen_project import ToolCheck

    def _create_success_checks(*args, **kwargs):
        return [
            ToolCheck(name="ruff", status="present", command="uv tool run"),
            ToolCheck(name="mypy", status="present", command="uv tool run"),
        ]

    return mocker.patch(
        "pre_gen_project.ensure_python_quality_tools",
        side_effect=_create_success_checks,
    )


@pytest.fixture
def mock_tool_check_failure(mocker):
    """Mock ToolCheck class to return failed tool checks.

    Returns a mock that simulates tools being missing or failing.
    """
    from pre_gen_project import ToolCheck

    def _create_failed_checks(*args, **kwargs):
        return [
            ToolCheck(name="ruff", status="present", command="uv tool run"),
            ToolCheck(
                name="mypy",
                status="failed",
                command="uv tool install",
                stderr="Installation failed",
            ),
        ]

    return mocker.patch(
        "pre_gen_project.ensure_python_quality_tools", side_effect=_create_failed_checks
    )


# ============================================================================
# Path Fixtures
# ============================================================================


@pytest.fixture
def temp_project_dir(tmp_path, monkeypatch):
    """Create a temporary project directory and change to it.

    Sets up a clean temporary directory for tests that need to work
    with the filesystem. Automatically changes to this directory and
    cleans up after the test.
    """
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture
def mock_log_dir(tmp_path, monkeypatch):
    """Create a temporary .riso log directory.

    Sets up the expected log directory structure that pre_gen_project.py
    uses for toolchain provisioning logs.
    """
    log_dir = tmp_path / ".riso"
    log_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    return log_dir
