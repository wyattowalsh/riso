"""Check-update command — wrap Copier template update detection."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TYPE_CHECKING, Any

from riso.core.errors import CopierOperationError, PathNotFoundError
from riso.core.paths import validate_destination

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_check_update(*, config: CliConfig, destination: str) -> dict[str, Any]:
    """Run ``copier check-update --output-format json`` in DEST."""
    dest_path = validate_destination(destination)
    if not dest_path.exists():
        raise PathNotFoundError(str(dest_path))

    copier_path = shutil.which("copier")
    if copier_path is None:
        raise CopierOperationError(
            "check-update",
            "copier is not on PATH; install Copier or use `uv run copier`",
        )

    try:
        proc = subprocess.run(
            [copier_path, "check-update", "--output-format", "json"],
            cwd=dest_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=config.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise CopierOperationError(
            "check-update",
            f"copier check-update exceeded {config.timeout}s timeout",
        ) from exc
    except OSError as exc:
        raise CopierOperationError("check-update", str(exc)) from exc

    stdout = (proc.stdout or "").strip()
    if proc.returncode not in {0, 2}:
        detail = (proc.stderr or "").strip() or f"exit {proc.returncode}"
        raise CopierOperationError("check-update", detail)
    if not stdout:
        raise CopierOperationError(
            "check-update", "copier check-update returned no JSON result"
        )
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        detail = stdout or (proc.stderr or "").strip() or str(exc)
        raise CopierOperationError(
            "check-update",
            f"copier check-update returned non-JSON output: {detail}",
        ) from exc

    if not isinstance(payload, dict):
        raise CopierOperationError(
            "check-update",
            "copier check-update JSON root must be an object",
        )

    if not isinstance(payload.get("update_available"), bool):
        raise CopierOperationError(
            "check-update",
            "copier check-update result lacks a boolean update_available",
        )
    payload["destination"] = str(dest_path)
    payload["returncode"] = proc.returncode
    if proc.stderr:
        payload["stderr"] = proc.stderr.strip()
    return payload
