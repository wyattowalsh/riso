"""Tests for CLI JSON envelope."""

from __future__ import annotations

import json

import pytest

from riso.cli.output import CliContext, emit_success
from riso.core.errors import ValidationFailedError


def test_emit_success_json(capsys: pytest.CaptureFixture[str]) -> None:
    ctx = CliContext(json_mode=True, command_name="riso doctor")
    emit_success(ctx, data={"ready": True})
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["ok"] is True
    assert payload["command"] == "riso doctor"
    assert payload["data"]["ready"] is True


def test_validation_error_exit_code() -> None:
    err = ValidationFailedError(["project_name: required"])
    assert err.exit_code == 2


def test_emit_success_json_includes_warnings(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=True, command_name="riso validate")
    emit_success(
        ctx,
        data={"valid": True, "errors": [], "warnings": ["foo: unknown answer key"]},
        warnings=["foo: unknown answer key"],
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["warnings"] == ["foo: unknown answer key"]
    assert payload["data"]["warnings"] == ["foo: unknown answer key"]
