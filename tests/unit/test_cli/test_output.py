"""Tests for CLI JSON envelope."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

import json

import pytest

from riso.cli.output import CliContext, emit_error, emit_success, handle_exception
from riso.core.errors import ExitCode, ValidationFailedError


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


def test_emit_success_json_export_yaml_single_envelope(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=True, command_name="riso export yaml")
    emit_success(
        ctx,
        data={"yaml": "project_name: demo\n", "answers": {"project_name": "demo"}},
    )
    captured = capsys.readouterr()
    assert captured.out.strip().startswith("{")
    payload = json.loads(captured.out)
    assert payload["data"]["yaml"] == "project_name: demo\n"


def test_emit_success_human_doctor(capsys: pytest.CaptureFixture[str]) -> None:
    ctx = CliContext(json_mode=False, command_name="riso doctor")
    emit_success(
        ctx,
        data={
            "ready": True,
            "checks": {
                "template_path": "/tmp/template",
                "copier": {"available": True},
                "riso_version": "1.0.0",
            },
        },
    )
    out = capsys.readouterr().out
    assert "ready: True" in out
    assert "template_path: /tmp/template" in out
    assert "copier: available" in out


def test_emit_success_human_validate(capsys: pytest.CaptureFixture[str]) -> None:
    ctx = CliContext(json_mode=False, command_name="riso validate")
    emit_success(
        ctx,
        data={
            "valid": False,
            "errors": ["project_name: required"],
            "warnings": ["extra: unknown"],
        },
    )
    out = capsys.readouterr().out
    assert "validation: invalid" in out
    assert "project_name: required" in out
    assert "extra: unknown" in out


def test_handle_exception_value_error_usage_exit() -> None:
    ctx = CliContext(json_mode=False)
    with pytest.raises(SystemExit) as exc:
        handle_exception(ctx, ValueError("bad input"))
    assert exc.value.code == int(ExitCode.USAGE_OR_VALIDATION)


def test_handle_exception_file_not_found_usage_exit() -> None:
    ctx = CliContext(json_mode=False)
    with pytest.raises(SystemExit) as exc:
        handle_exception(ctx, FileNotFoundError("/missing.yml"))
    assert exc.value.code == int(ExitCode.USAGE_OR_VALIDATION)


def test_emit_error_json_writes_envelope_to_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=True, command_name="riso validate")
    with pytest.raises(SystemExit) as exc:
        emit_error(
            ctx,
            "Validation failed",
            errors=["project_name: required"],
            exit_code=ExitCode.USAGE_OR_VALIDATION,
        )
    assert exc.value.code == int(ExitCode.USAGE_OR_VALIDATION)
    captured = capsys.readouterr()
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["ok"] is False
    assert payload["command"] == "riso validate"
    assert payload["errors"] == ["project_name: required"]
    assert payload["data"] == {}
    assert payload["warnings"] == []


def test_handle_exception_riso_error_json_uses_exit_code(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=True, command_name="riso copy")
    with pytest.raises(SystemExit) as exc:
        handle_exception(ctx, ValidationFailedError(["api_tracks: removed"]))
    assert exc.value.code == int(ExitCode.USAGE_OR_VALIDATION)
    payload = json.loads(capsys.readouterr().err)
    assert payload["ok"] is False
    assert any("api_tracks" in e for e in payload["errors"])


def test_emit_success_quiet_suppresses_human_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=False, quiet=True, command_name="riso doctor")
    emit_success(ctx, data={"ready": True, "message": "should stay quiet"})
    captured = capsys.readouterr()
    assert captured.out == ""
