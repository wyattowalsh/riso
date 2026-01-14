"""Fixtures for automation tests."""
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_path = Path(__file__).parents[3] / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))


@pytest.fixture
def scripts_dir():
    """Return the scripts directory path."""
    return scripts_path


@pytest.fixture
def automation_dir(scripts_dir):
    """Return the automation directory path."""
    return scripts_dir / "automation"
