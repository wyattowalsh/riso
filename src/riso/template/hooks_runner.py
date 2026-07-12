"""Run Riso post-generation hooks outside Copier ``_tasks``."""

from __future__ import annotations

import os
import runpy
from collections.abc import Mapping
from pathlib import Path

from riso.core.errors import CopierOperationError


def _candidate_post_gen_paths(template_hint: Path | None = None) -> list[Path]:
    """Resolve possible post_gen_project.py locations."""
    candidates: list[Path] = []
    if template_hint is not None:
        root = template_hint.resolve()
        candidates.extend(
            [
                root / "hooks" / "post_gen_project.py",
                root / "template" / "hooks" / "post_gen_project.py",
                root.parent / "hooks" / "post_gen_project.py",
            ]
        )
    # Bundled relative to this package: repo template/hooks when developing.
    pkg_root = Path(__file__).resolve().parents[3]
    candidates.append(pkg_root / "template" / "hooks" / "post_gen_project.py")
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
) -> None:
    """Execute post_gen_project.py with ``cwd=destination``.

    Raises:
        CopierOperationError: if the script is missing or exits non-zero.
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

    env_backup = os.environ.copy()
    cwd_backup = Path.cwd()
    try:
        if extra_env:
            os.environ.update({str(k): str(v) for k, v in extra_env.items()})
        os.chdir(dest)
        try:
            runpy.run_path(str(script), run_name="__main__")
        except SystemExit as exc:
            code = exc.code
            if code in (None, 0):
                return
            if isinstance(code, int) and code == 0:
                return
            raise CopierOperationError(
                "post_gen",
                f"post_gen exited with code {code}",
            ) from exc
    finally:
        os.chdir(cwd_backup)
        os.environ.clear()
        os.environ.update(env_backup)


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
