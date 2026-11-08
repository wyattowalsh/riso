"""Tests for riso check-update."""

from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

import pytest
from typer.testing import CliRunner

from riso.cli.app import app
from riso.cli.commands.check_update import run_check_update
from riso.cli.config import CliConfig
from riso.core.errors import CopierOperationError, PathNotFoundError

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("returncode", [0, 1, 2])
def test_check_update_rejects_empty_output_instead_of_reporting_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, returncode: int
) -> None:
    """Missing JSON cannot be mistaken for an up-to-date project."""
    monkeypatch.setattr(
        "riso.cli.commands.check_update.shutil.which", lambda _name: "/usr/bin/copier"
    )
    monkeypatch.setattr(
        "riso.cli.commands.check_update.subprocess.run",
        lambda *_args, **_kwargs: CompletedProcess(
            ["copier"], returncode, stdout="", stderr="lookup failed"
        ),
    )
    with pytest.raises(CopierOperationError):
        run_check_update(config=CliConfig.from_options(), destination=str(tmp_path))


def test_check_update_cli_reports_operational_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An operational Copier failure produces a nonzero, failed JSON envelope."""
    monkeypatch.setattr(
        "riso.cli.commands.check_update.shutil.which", lambda _name: "/usr/bin/copier"
    )
    monkeypatch.setattr(
        "riso.cli.commands.check_update.subprocess.run",
        lambda *_args, **_kwargs: CompletedProcess(
            ["copier"], 1, stdout="", stderr="lookup failed"
        ),
    )
    result = CliRunner().invoke(app, ["--json", "check-update", str(tmp_path)])
    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "lookup failed" in payload["errors"][0]


def test_check_update_missing_dest(tmp_path: Path) -> None:
    """A missing project fails before invoking Copier."""
    config = CliConfig.from_options()
    with pytest.raises(PathNotFoundError):
        run_check_update(config=config, destination=str(tmp_path / "missing"))


def test_check_update_parses_copier_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Structured Copier results retain availability, versions, and exit status."""
    dest = tmp_path / "proj"
    dest.mkdir()
    payload = {
        "update_available": True,
        "current_version": "1.2.11",
        "latest_version": "2.0.0",
    }

    def fake_run(*_args: Any, **_kwargs: Any) -> CompletedProcess[str]:
        return CompletedProcess(
            args=["copier"],
            returncode=2,
            stdout=json.dumps(payload),
            stderr="",
        )

    monkeypatch.setattr(
        "riso.cli.commands.check_update.shutil.which",
        lambda _name: "/usr/bin/copier",
    )
    monkeypatch.setattr("riso.cli.commands.check_update.subprocess.run", fake_run)
    config = CliConfig.from_options()
    result = run_check_update(config=config, destination=str(dest))
    assert result["update_available"] is True
    assert result["latest_version"] == "2.0.0"
    assert result["destination"] == str(dest)
    assert result["returncode"] == 2


def test_check_update_requires_copier_on_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing Copier produces an operational error instead of an update result."""
    dest = tmp_path / "proj"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.cli.commands.check_update.shutil.which", lambda _name: None
    )
    config = CliConfig.from_options()
    with pytest.raises(CopierOperationError):
        run_check_update(config=config, destination=str(dest))
