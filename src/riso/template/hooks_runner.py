"""Run Riso post-generation hooks outside Copier ``_tasks``."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

from riso.core.errors import CopierOperationError, OperationTimeoutError
from riso.core.paths import is_bundled_template


def _bundled_post_gen_script() -> Path:
    pkg_root = Path(__file__).resolve().parents[3]
    return pkg_root / "template" / "hooks" / "post_gen_project.py"


def _candidate_post_gen_paths(template_hint: Path | None = None) -> list[Path]:
    """Resolve possible post_gen_project.py locations.

    Untrusted external ``template_hint`` paths are ignored; only the bundled
    template hook is eligible unless the hint itself is the bundled template.
    """
    candidates: list[Path] = []
    if template_hint is not None and is_bundled_template(template_hint):
        root = template_hint.resolve()
        candidates.extend(
            [
                root / "hooks" / "post_gen_project.py",
                root / "template" / "hooks" / "post_gen_project.py",
                root.parent / "hooks" / "post_gen_project.py",
            ]
        )
    candidates.append(_bundled_post_gen_script())
    return candidates


def find_post_gen_script(template_hint: Path | None = None) -> Path | None:
    """Return first existing post_gen script path, or None."""
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
    """Execute post_gen_project.py with ``cwd=destination`` via subprocess.

    Raises:
        CopierOperationError: if the script is missing or exits non-zero.
        OperationTimeoutError: if the hook exceeds *timeout*.
        FileNotFoundError: if destination does not exist.
    """
    dest = destination.resolve()
    if not dest.is_dir():
        raise FileNotFoundError(dest)

    script = find_post_gen_script(template_hint)
    if script is None:
        raise CopierOperationError(
            "post_gen",
            "Riso post-generation hook not found",
        )

    env = os.environ.copy()
    if extra_env:
        env.update({str(k): str(v) for k, v in extra_env.items()})

    from riso.template._copier_worker import run_argv_with_timeout

    argv = [sys.executable, str(script)]
    try:
        completed = run_argv_with_timeout(
            argv,
            timeout=timeout,
            cwd=dest,
            env=env,
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
            "post_gen",
            detail or f"post_gen exited with code {completed.returncode}",
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


__all__ = [
    "find_post_gen_script",
    "run_post_gen",
    "should_skip_post_gen",
]
