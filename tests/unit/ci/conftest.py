"""Fixtures for CI script tests."""
import sys
from pathlib import Path

import pytest

# Add scripts/ci directory to path for imports at module load time
# This allows test files to import directly: from check_quality_parity import ...
_ci_scripts_path = Path(__file__).parents[3] / "scripts" / "ci"
if str(_ci_scripts_path) not in sys.path:
    sys.path.insert(0, str(_ci_scripts_path))


@pytest.fixture
def ci_scripts_dir():
    """Return the CI scripts directory path."""
    return _ci_scripts_path
