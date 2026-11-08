"""Run trusted bundled generation hooks in isolated subprocesses.

The CLI runs post-gen only. Pre-gen is an explicit operator helper because it
may provision tooling.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

from riso.core.answers import load_answers_file
from riso.core.errors import CopierOperationError, OperationTimeoutError
from riso.core.paths import bundled_template_path

_PRE_GEN_FILENAME = "pre_gen_project.py"
_POST_GEN_FILENAME = "post_gen_project.py"


def _bundled_hook_script(filename: str) -> Path:
    return bundled_template_path() / "hooks" / filename


def _candidate_hook_paths(
    filename: str, template_hint: Path | None = None
) -> list[Path]:
    """Select only the exact bundled hook, rejecting external hints and symlinks."""
    bundled = bundled_template_path()
    if template_hint is not None and template_hint.resolve() != bundled:
        return []
    script = _bundled_hook_script(filename)
    if script.resolve().parent != bundled / "hooks":
        return []
    return [script]


def _find_hook_script(filename: str, template_hint: Path | None = None) -> Path | None:
    for path in _candidate_hook_paths(filename, template_hint):
        if path.is_file():
            return path
    return None


def find_pre_gen_script(template_hint: Path | None = None) -> Path | None:
    """Return first existing pre_gen script path, or None."""
    return _find_hook_script(_PRE_GEN_FILENAME, template_hint)


def find_post_gen_script(template_hint: Path | None = None) -> Path | None:
    """Return first existing post_gen script path, or None."""
    return _find_hook_script(_POST_GEN_FILENAME, template_hint)


def _copier_answers_json(destination: Path) -> str | None:
    """Serialize dest ``.copier-answers.yml`` like Copier ``_tasks`` pre_gen."""
    answers_file = destination / ".copier-answers.yml"
    if not answers_file.is_file():
        return None
    return json.dumps(load_answers_file(answers_file))


def _hook_env(
    extra_env: Mapping[str, str] | None,
    destination: Path,
    *,
    inject_copier_answers: bool,
) -> dict[str, str]:
    env = os.environ.copy()
    if extra_env:
        env.update({str(k): str(v) for k, v in extra_env.items()})
    if inject_copier_answers and not env.get("COPIER_ANSWERS"):
        payload = _copier_answers_json(destination)
        if payload is not None:
            env["COPIER_ANSWERS"] = payload
    return env


def _run_hook_script(
    *,
    operation: str,
    destination: Path,
    script: Path | None,
    extra_env: Mapping[str, str] | None,
    timeout: int | None,
    missing_message: str,
    inject_copier_answers: bool = False,
) -> None:
    dest = destination.resolve()
    if not dest.is_dir():
        raise FileNotFoundError(dest)

    if script is None:
        raise CopierOperationError(operation, missing_message)

    env = _hook_env(
        extra_env,
        dest,
        inject_copier_answers=inject_copier_answers,
    )

    # Defer the worker's Copier imports until a hook operation actually runs.
    from riso.template._copier_worker import run_argv_with_timeout  # pylint: disable=import-outside-toplevel

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
            operation=operation,
            timeout_seconds=int(timeout or 0),
            details=f"{operation} exceeded {timeout}s timeout",
        ) from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise CopierOperationError(
            operation,
            detail or f"{operation} exited with code {completed.returncode}",
        )


def run_pre_gen(
    destination: Path,
    *,
    template_hint: Path | None = None,
    extra_env: Mapping[str, str] | None = None,
    timeout: int | None = None,
) -> None:
    """Execute pre_gen_project.py with ``cwd=destination`` via subprocess.

    Mirrors Copier ``_tasks``: when dest ``.copier-answers.yml`` exists and
    ``COPIER_ANSWERS`` is unset, load it with ``yaml.safe_load`` and set
    ``COPIER_ANSWERS`` to ``json.dumps`` of the mapping.

    Raises:
        CopierOperationError: if the script is missing or exits non-zero.
        OperationTimeoutError: if the hook exceeds *timeout*.
        FileNotFoundError: if destination does not exist.
    """
    _run_hook_script(
        operation="pre_gen",
        destination=destination,
        script=find_pre_gen_script(template_hint),
        extra_env=extra_env,
        timeout=timeout,
        missing_message="Trusted Riso pre-generation hook not found",
        inject_copier_answers=True,
    )


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
    _run_hook_script(
        operation="post_gen",
        destination=destination,
        script=find_post_gen_script(template_hint),
        extra_env=extra_env,
        timeout=timeout,
        missing_message="Trusted Riso post-generation hook not found",
    )


def should_skip_hooks(
    *,
    skip_flag: bool = False,
    env: Mapping[str, str] | None = None,
) -> bool:
    """Return True when pre_gen and post_gen should both be skipped.

    ``RISO_SKIP_POST_GEN`` is the shared escape hatch for both hooks.
    """
    if skip_flag:
        return True
    environ = env if env is not None else os.environ
    value = str(environ.get("RISO_SKIP_POST_GEN", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def should_skip_post_gen(
    *,
    skip_flag: bool = False,
    env: Mapping[str, str] | None = None,
) -> bool:
    """Alias for :func:`should_skip_hooks` (same ``RISO_SKIP_POST_GEN`` hatch)."""
    return should_skip_hooks(skip_flag=skip_flag, env=env)


__all__ = [
    "find_pre_gen_script",
    "find_post_gen_script",
    "run_pre_gen",
    "run_post_gen",
    "should_skip_hooks",
    "should_skip_post_gen",
]
