"""Recopy command — regenerate project from template."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from riso.cli.helpers import parse_data_pairs
from riso.core.answers import prepare_copier_data, reject_removed_answer_keys
from riso.core.diff import compute_diff
from riso.core.errors import CopierOperationError, PathNotFoundError
from riso.template import run_recopy as template_run_recopy

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_recopy(
    config: CliConfig,
    *,
    destination: str,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    dry_run: bool = False,
) -> dict:
    """Recopy an existing Copier project."""
    dest_path = Path(destination).expanduser().resolve()
    if not dest_path.exists():
        raise PathNotFoundError(str(dest_path))

    provided = parse_data_pairs(data_pairs)
    if answers_file:
        from riso.cli.helpers import load_answers_file

        provided = {**load_answers_file(answers_file), **provided}
    reject_removed_answer_keys(provided)

    if dry_run:
        existing: dict = {}
        answers_path = dest_path / ".copier-answers.yml"
        if answers_path.exists():
            existing = yaml.safe_load(answers_path.read_text(encoding="utf-8")) or {}
        reject_removed_answer_keys(existing)
        final_answers = prepare_copier_data({**existing, **provided})
        diff = compute_diff(
            answers=final_answers,
            destination=dest_path,
            template_path=config.template_path,
            operation="recopy",
        )
        return diff.to_dict()

    try:
        result = template_run_recopy(
            destination=dest_path,
            data=provided or None,
            template_path=config.template_path,
            timeout=config.timeout,
        )
    except Exception as exc:
        raise CopierOperationError("recopy", str(exc)) from exc

    return result.to_dict()
