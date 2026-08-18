"""Tests for doctor command."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from riso.cli.commands.doctor import meets_min_copier, run_doctor
from riso.cli.config import CliConfig

pytestmark = pytest.mark.unit


def test_meets_min_copier_compares_numeric_prefixes() -> None:
    assert meets_min_copier("9.1", "9.1.0") is True
    assert meets_min_copier("9.0.9", "9.1.0") is False
    assert meets_min_copier("copier 9.16.0", "9.1.0") is True
    assert meets_min_copier(None, "9.1.0") is False
    assert meets_min_copier("9.1.0", None) is True


def test_doctor_returns_copier_config_valid_when_template_exists() -> None:
    config = CliConfig.from_options()
    result = run_doctor(config=config)

    checks = result["checks"]
    assert checks["template_exists"] is True
    assert checks["copier_config_valid"] is True


def test_doctor_ready_uses_copier_import_not_only_which(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_which(name: str) -> str | None:
        if name in {"uv", "git"}:
            return f"/usr/bin/{name}"
        return None

    monkeypatch.setattr("riso.cli.commands.doctor.shutil.which", fake_which)
    monkeypatch.setattr(
        "riso.cli.commands.doctor.importlib.util.find_spec",
        lambda name: object() if name == "copier" else None,
    )
    config = CliConfig.from_options()
    result = run_doctor(config=config)

    assert result["checks"]["copier"]["available"] is True
    assert result["ready"] is True


def test_doctor_not_ready_when_uv_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    real_which = shutil.which

    def fake_which(name: str) -> str | None:
        if name == "uv":
            return None
        return real_which(name)

    monkeypatch.setattr("riso.cli.commands.doctor.shutil.which", fake_which)
    config = CliConfig.from_options()
    result = run_doctor(config=config)
    assert result["ready"] is False
    assert result["checks"]["uv"]["available"] is False


def test_doctor_not_ready_when_git_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    real_which = shutil.which

    def fake_which(name: str) -> str | None:
        if name == "git":
            return None
        return real_which(name)

    monkeypatch.setattr("riso.cli.commands.doctor.shutil.which", fake_which)
    config = CliConfig.from_options()
    result = run_doctor(config=config)
    assert result["ready"] is False
    assert result["checks"]["git"]["available"] is False


def test_doctor_reports_bundled_update_unsafe_policy() -> None:
    config = CliConfig.from_options()
    result = run_doctor(config=config)
    policy = result["checks"]["bundled_update_unsafe"]
    assert policy["applies"] is True
    assert policy["unsafe"] is True
    assert "skip_tasks" in policy["policy"]
    assert "unsafe" in policy["policy"].lower()
    assert result["checks"]["template_has_tasks"] is True
    assert result["checks"]["update_sets_unsafe"] is True
    assert result["checks"]["copier"]["meets_min"] is True
    assert any("unsafe" in warning.lower() for warning in result["warnings"])


def test_doctor_not_ready_when_template_path_missing(tmp_path: Path) -> None:
    missing = tmp_path / "no-template-here"
    config = CliConfig.from_options(template_path=missing)
    result = run_doctor(config=config)

    assert result["ready"] is False
    assert result["checks"]["template_exists"] is False
    assert result["checks"]["template_path"] is None
    assert result["checks"].get("template_error")


def test_doctor_ready_requires_min_copier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "riso.cli.commands.doctor._copier_package_version",
        lambda: "9.0.0",
    )
    config = CliConfig.from_options()
    result = run_doctor(config=config)
    assert result["checks"]["min_copier_version"] == "9.1.0"
    assert result["checks"]["copier"]["meets_min"] is False
    assert result["ready"] is False


def test_doctor_reports_min_copier_when_ready() -> None:
    config = CliConfig.from_options()
    result = run_doctor(config=config)
    assert result["checks"]["min_copier_version"] == "9.1.0"
    assert result["checks"]["copier"]["meets_min"] is True
    assert result["checks"]["git"]["available"] is True
    assert result["ready"] is True


def test_doctor_result_includes_envelope_friendly_top_level_keys() -> None:
    config = CliConfig.from_options()
    result = run_doctor(config=config)

    assert "ready" in result
    assert "checks" in result
    assert isinstance(result["checks"], dict)
    assert isinstance(result["warnings"], list)
