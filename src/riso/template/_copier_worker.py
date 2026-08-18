"""Subprocess worker for Copier operations (timeout-killable).

Invoked as::

    python -m riso.template._copier_worker copy --json-args '...'

Keeps Copier calls out-of-process so the parent can terminate on timeout
without relying on ThreadPoolExecutor (which cannot abort in-flight work).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

# Copier is optional until the worker process runs an operation.
from copier import run_copy, run_recopy, run_update  # pylint: disable=import-error


def run_argv_with_timeout(
    argv: list[str],
    *,
    timeout: int | None,
    cwd: str | os.PathLike[str] | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run argv in a new session; kill the process group on timeout.

    Returns a CompletedProcess. Callers map returncode to domain errors.
    """
    run_kwargs: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "start_new_session": True,
    }
    if cwd is not None:
        run_kwargs["cwd"] = os.fspath(cwd)
    if env is not None:
        run_kwargs["env"] = env

    # start_new_session=True => child is session/process group leader (pgid == pid).
    try:
        # pylint: disable-next=consider-using-with
        proc = subprocess.Popen(argv, **run_kwargs)
    except (TypeError, ValueError, OSError):
        # Extremely old platforms: fall back to plain run (no group kill).
        fallback: dict[str, Any] = {
            "check": False,
            "capture_output": True,
            "text": True,
            "timeout": timeout if timeout is not None and timeout > 0 else None,
        }
        if cwd is not None:
            fallback["cwd"] = os.fspath(cwd)
        if env is not None:
            fallback["env"] = env
        return subprocess.run(argv, **fallback)

    try:
        stdout, stderr = proc.communicate(
            timeout=timeout if timeout is not None and timeout > 0 else None
        )
    except subprocess.TimeoutExpired as exc:
        _kill_process_group(proc)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except (OSError, subprocess.SubprocessError, TimeoutError):
            stdout, stderr = "", ""
        raise subprocess.TimeoutExpired(
            cmd=argv,
            timeout=exc.timeout,
            output=stdout,
            stderr=stderr,
        ) from exc

    return subprocess.CompletedProcess(
        args=argv,
        returncode=proc.returncode if proc.returncode is not None else -1,
        stdout=stdout or "",
        stderr=stderr or "",
    )


def _kill_process_group(proc: subprocess.Popen[str]) -> None:
    """Best-effort terminate then kill the child's process group."""
    if proc.pid is None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except OSError:
            return
        return
    try:
        proc.wait(timeout=2)
        return
    except (OSError, subprocess.SubprocessError, TimeoutError):
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except OSError:
            pass


def _run_copy(args: dict[str, Any]) -> None:
    """Execute Copier copy with worker payload."""
    run_copy(
        str(args["template_path"]),
        str(args["destination"]),
        data=args.get("data") or {},
        vcs_ref=args.get("vcs_ref"),
        overwrite=bool(args.get("overwrite", False)),
        unsafe=bool(args.get("unsafe", False)),
        skip_tasks=bool(args.get("skip_tasks", True)),
        defaults=bool(args.get("defaults", False)),
    )


def _run_update(args: dict[str, Any]) -> None:
    """Execute Copier update with worker payload."""
    kwargs: dict[str, Any] = {
        "skip_answered": bool(args.get("skip_answered", True)),
        "unsafe": bool(args.get("unsafe", False)),
        "skip_tasks": bool(args.get("skip_tasks", True)),
        # Copier 9.16 run_update hard-fails without overwrite=True.
        "overwrite": bool(args.get("overwrite", True)),
    }
    data = args.get("data")
    if data:
        kwargs["data"] = data
    if "defaults" in args:
        kwargs["defaults"] = bool(args["defaults"])
    run_update(str(args["destination"]), **kwargs)


def _run_recopy(args: dict[str, Any]) -> None:
    """Execute Copier recopy with worker payload."""
    kwargs: dict[str, Any] = {
        "unsafe": bool(args.get("unsafe", False)),
        "skip_tasks": bool(args.get("skip_tasks", True)),
        "overwrite": bool(args.get("overwrite", True)),
        "defaults": bool(args.get("defaults", True)),
        "skip_answered": bool(args.get("skip_answered", True)),
    }
    data = args.get("data")
    if data:
        kwargs["data"] = data
    run_recopy(str(args["destination"]), **kwargs)


_HANDLERS = {
    "copy": _run_copy,
    "update": _run_update,
    "recopy": _run_recopy,
}


def main(argv: list[str] | None = None) -> int:
    """CLI entry for the Copier worker process."""
    parser = argparse.ArgumentParser(prog="riso.template._copier_worker")
    parser.add_argument("operation", choices=sorted(_HANDLERS))
    parser.add_argument(
        "--json-args",
        required=True,
        help="JSON object with operation arguments",
    )
    ns = parser.parse_args(argv)
    try:
        payload = json.loads(ns.json_args)
    except json.JSONDecodeError as exc:
        print(f"invalid --json-args: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("--json-args must be a JSON object", file=sys.stderr)
        return 2

    for key in ("template_path", "destination"):
        if key in payload and payload[key] is not None:
            payload[key] = str(Path(payload[key]).expanduser())

    try:
        _HANDLERS[ns.operation](payload)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Surface any Copier failure to the parent as stderr + exit 1.
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
