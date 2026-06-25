"""Update command — apply template updates to existing project."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.core.diff import compute_diff
from riso.core.errors import CopierOperationError, PathNotFoundError
from riso.template import run_update as template_run_update

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_update(
    config: CliConfig,
    *,
    destination: str,
    skip_answered: bool = True,
    dry_run: bool = False,
) -> dict:
    """Update an existing Copier project."""
    dest_path = Path(destination).expanduser().resolve()
    if not dest_path.exists():
        raise PathNotFoundError(str(dest_path))

    answers_file = dest_path / ".copier-answers.yml"
    if not answers_file.exists():
        raise CopierOperationError(
            "update",
            f"No .copier-answers.yml found at {dest_path}",
        )

    if dry_run:
        import yaml

        from riso.core.answers import reject_removed_answer_keys

        answers = yaml.safe_load(answers_file.read_text(encoding="utf-8")) or {}
        reject_removed_answer_keys(answers)
        diff = compute_diff(
            answers=answers,
            destination=dest_path,
            template_path=config.template_path,
            operation="update",
        )
        return diff.to_dict()

    try:
        result = template_run_update(
            destination=dest_path,
            template_path=config.template_path,
            skip_answered=skip_answered,
            timeout=config.timeout,
        )
    except Exception as exc:
        raise CopierOperationError("update", str(exc)) from exc

    return result.to_dict()
