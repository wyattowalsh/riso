"""JSON envelope and human output for Riso CLI."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any

from riso.core.errors import ExitCode, RisoError


@dataclass
class CliContext:
    """Runtime CLI context shared across commands."""

    json_mode: bool = False
    quiet: bool = False
    verbose: bool = False
    command_name: str = "riso"


@dataclass
class Envelope:
    """Stable JSON response envelope for agents."""

    ok: bool
    command: str
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "command": self.command,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def emit_success(
    ctx: CliContext,
    *,
    data: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> None:
    """Emit successful output."""
    if ctx.json_mode:
        envelope = Envelope(
            ok=True,
            command=ctx.command_name,
            data=data or {},
            warnings=warnings or [],
        )
        print(json.dumps(envelope.to_dict(), indent=2))
        return

    if not ctx.quiet and data:
        if _emit_human_command_output(data):
            return
        for key, value in data.items():
            if key == "message":
                print(value)
            elif key == "summary":
                print(value)


def _emit_human_command_output(data: dict[str, Any]) -> bool:
    """Print structured command results in human mode. Return True if handled."""
    if "yaml" in data and isinstance(data.get("yaml"), str):
        yaml_text = data["yaml"]
        end = "" if yaml_text.endswith("\n") else "\n"
        print(yaml_text, end=end)
        return True

    if "copier_command" in data:
        print(data["copier_command"])
        if riso_cmd := data.get("riso_command"):
            print(riso_cmd)
        return True

    if "valid" in data:
        status = "valid" if data.get("valid") else "invalid"
        print(f"validation: {status}")
        for err in data.get("errors") or []:
            print(f"  error: {err}")
        for warn in data.get("warnings") or []:
            print(f"  warning: {warn}")
        return True

    if "checks" in data and "ready" in data:
        ready = data.get("ready")
        print(f"ready: {ready}")
        checks = data.get("checks")
        if isinstance(checks, dict):
            if checks.get("template_path"):
                print(f"template_path: {checks['template_path']}")
            copier = checks.get("copier")
            if isinstance(copier, dict):
                print(
                    f"copier: {'available' if copier.get('available') else 'missing'}"
                )
            if checks.get("riso_version"):
                print(f"riso_version: {checks['riso_version']}")
        for warn in data.get("warnings") or []:
            print(f"warning: {warn}")
        return True

    remap_only = "ops" in data and "answers_file" in data
    remap_payload = data.get("remap") if isinstance(data.get("remap"), dict) else None
    if remap_only or remap_payload is not None:
        _emit_remap_preview(data, remap_payload)
        if remap_only:
            return True
        if "summary" in data:
            print(data["summary"])
            return True
        if "message" in data:
            print(data["message"])
            return True
        return True

    return False


def _emit_remap_preview(
    data: dict[str, Any],
    remap_payload: dict[str, Any] | None,
) -> None:
    """Print apply-then-reject remap preview rows."""
    payload = remap_payload or data
    answers_file = payload.get("answers_file") or data.get("answers_file")
    if answers_file:
        print(f"answers_file: {answers_file}")
    ops = payload.get("ops") or []
    if not ops:
        print("remap: already canonical")
    else:
        print(f"remap: {len(ops)} key(s)")
        for op in ops:
            dests = ", ".join(str(key) for key in (op.get("new_keys") or []))
            print(f"  {op.get('old')} -> {dests} ({op.get('action')})")
    if payload.get("written"):
        print("wrote: true")
    if data.get("dry_run"):
        print("dry_run: true")
    if data.get("message") and "ops" in data:
        print(data["message"])


def emit_error(
    ctx: CliContext,
    message: str,
    *,
    errors: list[str] | None = None,
    exit_code: ExitCode = ExitCode.OPERATIONAL_FAILURE,
) -> None:
    """Emit error and exit."""
    error_list = errors or [message]
    if ctx.json_mode:
        envelope = Envelope(
            ok=False,
            command=ctx.command_name,
            errors=error_list,
        )
        print(json.dumps(envelope.to_dict(), indent=2), file=sys.stderr)
    else:
        for err in error_list:
            print(f"error: {err}", file=sys.stderr)
    raise SystemExit(int(exit_code))


def _error_messages(exc: RisoError) -> list[str]:
    if exc.data and isinstance(exc.data.get("errors"), list):
        return [str(item) for item in exc.data["errors"]]
    return [exc.message]


def handle_exception(ctx: CliContext, exc: BaseException) -> None:
    """Map exceptions to CLI exit codes."""
    if isinstance(exc, RisoError):
        emit_error(
            ctx,
            exc.message,
            errors=_error_messages(exc),
            exit_code=exc.exit_code,
        )
    if isinstance(exc, FileExistsError):
        emit_error(
            ctx,
            str(exc),
            exit_code=ExitCode.USAGE_OR_VALIDATION,
        )
    if isinstance(exc, (ValueError, FileNotFoundError)):
        emit_error(
            ctx,
            str(exc),
            exit_code=ExitCode.USAGE_OR_VALIDATION,
        )
    if isinstance(exc, SystemExit):
        raise exc
    if isinstance(exc, KeyboardInterrupt):
        emit_error(
            ctx,
            "Interrupted",
            exit_code=ExitCode.INTERRUPTED,
        )
    emit_error(ctx, str(exc))
