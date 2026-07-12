"""Tests for CLI JSON envelope."""

from __future__ import annotations

import json

import pytest

from riso.cli.output import CliContext, emit_success, handle_exception
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


def test_handle_exception_value_error_usage_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=False)
    with pytest.raises(SystemExit) as exc:
        handle_exception(ctx, ValueError("bad input"))
    assert exc.value.code == int(ExitCode.USAGE_OR_VALIDATION)


def test_handle_exception_file_not_found_usage_exit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ctx = CliContext(json_mode=False)
    with pytest.raises(SystemExit) as exc:
        handle_exception(ctx, FileNotFoundError("/missing.yml"))
    assert exc.value.code == int(ExitCode.USAGE_OR_VALIDATION)
