"""Diff command — preview Copier operation changes."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

import yaml

from riso.cli.helpers import resolve_answers
from riso.core.answers import reject_removed_answer_keys
from riso.core.diff import compute_diff
from riso.core.errors import PathNotFoundError

if TYPE_CHECKING:
    from riso.cli.config import CliConfig

Operation = Literal["copy", "update", "recopy"]


def run_diff(
    config: CliConfig,
    *,
    destination: str,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    operation: Operation = "copy",
) -> dict:
    """Compute diff for a Copier operation."""
    dest_path = Path(destination).expanduser().resolve()

    if operation in ("update", "recopy") and not dest_path.exists():
        raise PathNotFoundError(str(dest_path))

    if operation == "copy":
        final_answers = resolve_answers(
            answers_file=answers_file,
            data_pairs=data_pairs,
            template_path=config.template_path,
        )
    else:
        existing: dict = {}
        answers_path = dest_path / ".copier-answers.yml"
        if answers_path.exists():
            existing = yaml.safe_load(answers_path.read_text(encoding="utf-8")) or {}
        provided = {}
        if answers_file:
            from riso.cli.helpers import load_answers_file

            provided.update(load_answers_file(answers_file))
        from riso.cli.helpers import parse_data_pairs

        provided.update(parse_data_pairs(data_pairs))
        reject_removed_answer_keys(existing)
        reject_removed_answer_keys(provided)
        final_answers = {**existing, **provided}

    diff = compute_diff(
        answers=final_answers,
        destination=dest_path,
        template_path=config.template_path,
        operation=operation,
    )
    return diff.to_dict()
