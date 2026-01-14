"""Fixtures for CI script tests."""

from pathlib import Path

import pytest

# NOTE: sys.path setup is handled by the main tests/conftest.py
# This file only provides CI-specific fixtures

_project_root = Path(__file__).parents[3]
_ci_scripts_path = _project_root / "scripts" / "ci"


@pytest.fixture
def ci_scripts_dir():
    """Return the CI scripts directory path."""
    return _ci_scripts_path
