"""Copy command — generate new project from template."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.cli.helpers import resolve_answers, validate_and_raise
from riso.core.diff import compute_diff
from riso.core.errors import CopierOperationError
from riso.core.paths import validate_destination
from riso.template import run_generator

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_copy(
    config: CliConfig,
    *,
    destination: str,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    force: bool = False,
    dry_run: bool = False,
    vcs_ref: str | None = None,
) -> dict:
    """Copy template to destination."""
    dest_path = validate_destination(destination)
    answers = resolve_answers(
        answers_file=answers_file,
        data_pairs=data_pairs,
        template_path=config.template_path,
    )
    validate_and_raise(answers, config.template_path)

    if dry_run:
        diff = compute_diff(
            answers=answers,
            destination=dest_path,
            template_path=config.template_path,
            operation="copy",
        )
        return diff.to_dict()

    try:
        result = run_generator(
            destination=dest_path,
            data=answers,
            template_path=config.template_path,
            force=force,
            vcs_ref=vcs_ref,
            timeout=config.timeout,
        )
    except Exception as exc:
        raise CopierOperationError("copy", str(exc)) from exc

    return result.to_dict()
