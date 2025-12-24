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
