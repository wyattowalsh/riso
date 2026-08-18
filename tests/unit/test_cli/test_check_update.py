"""Tests for riso check-update."""

from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

import pytest

from riso.cli.commands.check_update import run_check_update
from riso.cli.config import CliConfig
from riso.core.errors import CopierOperationError, PathNotFoundError

pytestmark = pytest.mark.unit


def test_check_update_missing_dest(tmp_path: Path) -> None:
    config = CliConfig.from_options()
    with pytest.raises(PathNotFoundError):
        run_check_update(config=config, destination=str(tmp_path / "missing"))


def test_check_update_parses_copier_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    dest = tmp_path / "proj"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.cli.commands.check_update.shutil.which", lambda _name: None
    )
    config = CliConfig.from_options()
    with pytest.raises(CopierOperationError):
        run_check_update(config=config, destination=str(dest))
