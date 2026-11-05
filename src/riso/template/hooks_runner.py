"""Run the bundled Riso post-generation hook in an isolated subprocess."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

from riso.core.errors import CopierOperationError, OperationTimeoutError
from riso.core.paths import bundled_template_path


def _candidate_post_gen_paths(template_hint: Path | None = None) -> list[Path]:
    """Only select the hook belonging to Riso's bundled template."""
    bundled = bundled_template_path()
    if template_hint is not None and template_hint.resolve() != bundled:
        return []
    script = bundled / "hooks" / "post_gen_project.py"
    if script.resolve().parent != bundled / "hooks":
        return []
    return [script]


def find_post_gen_script(template_hint: Path | None = None) -> Path | None:
    """Return the bundled hook, never one from an external template."""
    for path in _candidate_post_gen_paths(template_hint):
        if path.is_file():
            return path
    return None


def run_post_gen(
    destination: Path,
    *,
    template_hint: Path | None = None,
    extra_env: Mapping[str, str] | None = None,
    timeout: int | None = None,
) -> None:
    """Run the bundled hook with child-only environment, argv, and cwd."""
    dest = destination.resolve()
    if not dest.is_dir():
        raise FileNotFoundError(dest)

    script = find_post_gen_script(template_hint)
    if script is None:
        raise CopierOperationError(
            "post_gen", "Trusted Riso post-generation hook not found"
        )

    from riso.template._copier_worker import run_argv_with_timeout

    child_env = os.environ.copy()
    if extra_env:
        child_env.update({str(key): str(value) for key, value in extra_env.items()})
    try:
        completed = run_argv_with_timeout(
            [sys.executable, str(script)],
            timeout=timeout,
            cwd=dest,
            env=child_env,
        )
    except subprocess.TimeoutExpired as exc:
        raise OperationTimeoutError(
            operation="post_gen",
            timeout_seconds=int(timeout or 0),
            details=f"post_gen exceeded {timeout}s timeout",
        ) from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise CopierOperationError(
            "post_gen", detail or f"post_gen exited with code {completed.returncode}"
        )


def should_skip_post_gen(
    *,
    skip_flag: bool = False,
    env: Mapping[str, str] | None = None,
) -> bool:
    """Return True when post-gen should be skipped (tests / agent escape hatch)."""
    if skip_flag:
        return True
    environ = env if env is not None else os.environ
    value = str(environ.get("RISO_SKIP_POST_GEN", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


__all__ = ["find_post_gen_script", "run_post_gen", "should_skip_post_gen"]
