"""Integration-specific pytest fixtures for riso."""
import pytest
from pathlib import Path


@pytest.fixture(scope='module')
def rendered_project(tmp_path_factory):
    """Render a full project for integration testing.

    This fixture creates a minimal but complete project structure that can be
    used for integration tests. It is module-scoped to improve test efficiency
    by reusing the same rendered project across multiple tests in a module.

    Args:
        tmp_path_factory: pytest's built-in factory for creating temporary directories

    Returns:
        Path: Path to the rendered project directory

    Example:
        def test_project_has_pyproject(rendered_project):
            pyproject = rendered_project / 'pyproject.toml'
            assert pyproject.exists()
    """
    render_dir = tmp_path_factory.mktemp('render')

    # Create minimal project structure
    (render_dir / 'pyproject.toml').write_text(
        '[project]\nname = "test"\nversion = "0.1.0"\n'
    )
    (render_dir / 'src').mkdir()
    (render_dir / 'tests').mkdir()

    return render_dir


@pytest.fixture
def copier_answers():
    """Default answers for copier rendering.

    This fixture provides a standard set of copier template answers that can
    be used for integration tests. Tests can override specific values as needed.

    Returns:
        dict: Dictionary of copier template answers

    Example:
        def test_with_custom_answers(copier_answers):
            copier_answers['project_name'] = 'my-custom-project'
            # Use modified answers...
    """
    return {
        'project_name': 'integration-test',
        'project_type': 'python',
        'python_version': '3.11',
        'use_docker': False,
        'ci_platform': 'github',
        'docs_site': 'none',
    }


@pytest.fixture
def clean_environment(monkeypatch):
    """Ensure clean environment for integration tests.

    This fixture removes common environment variables that could interfere with
    integration tests, such as virtual environment paths and Python path settings.
    This ensures tests run in a predictable, isolated environment.

    Args:
        monkeypatch: pytest's monkeypatch fixture for modifying environment

    Example:
        def test_in_clean_env(clean_environment):
            # Test runs without VIRTUAL_ENV, CONDA_PREFIX, or PYTHONPATH set
            assert 'VIRTUAL_ENV' not in os.environ
    """
    monkeypatch.delenv('VIRTUAL_ENV', raising=False)
    monkeypatch.delenv('CONDA_PREFIX', raising=False)
    monkeypatch.delenv('PYTHONPATH', raising=False)
