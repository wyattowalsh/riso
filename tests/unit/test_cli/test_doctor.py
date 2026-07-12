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


def test_doctor_ready_uses_copier_import_not_only_which(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("riso.cli.commands.doctor.shutil.which", lambda _name: None)
    monkeypatch.setattr(
        "riso.cli.commands.doctor.importlib.util.find_spec",
        lambda name: object() if name == "copier" else None,
    )
    config = CliConfig.from_options()
    result = run_doctor(config=config)

    assert result["checks"]["copier"]["available"] is True
    assert result["ready"] is True
