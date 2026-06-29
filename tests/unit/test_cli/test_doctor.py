"""Tests for doctor command."""

from __future__ import annotations

import pytest

from riso.cli.commands.doctor import run_doctor
from riso.cli.config import CliConfig

pytestmark = pytest.mark.unit


def test_doctor_returns_copier_config_valid_when_template_exists() -> None:
    config = CliConfig.from_options()
    result = run_doctor(config=config)

    checks = result["checks"]
    assert checks["template_exists"] is True
    assert checks["copier_config_valid"] is True
