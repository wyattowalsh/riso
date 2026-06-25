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
        for key, value in data.items():
            if key == "message":
                print(value)
            elif key == "summary":
                print(value)


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
    if isinstance(exc, SystemExit):
        raise
    if isinstance(exc, KeyboardInterrupt):
        emit_error(
            ctx,
            "Interrupted",
            exit_code=ExitCode.INTERRUPTED,
        )
    emit_error(ctx, str(exc))
