"""Recopy command — regenerate project from template."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.cli.helpers import parse_data_pairs
from riso.core.answers import (
    apply_then_reject_removed_keys,
    prepare_copier_data,
    remap_answers_file,
)
from riso.core.diff import compute_diff
from riso.core.errors import (
    CopierOperationError,
    PathNotFoundError,
    ValidationFailedError,
)
from riso.core.generation_gates import validate_answers_for_generation
from riso.core.names import validate_identity_fields
from riso.core.paths import validate_destination
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
    dest_path = validate_destination(destination)
    if not dest_path.exists():
        raise PathNotFoundError(str(dest_path))

    provided = parse_data_pairs(data_pairs)
    if answers_file:
        from riso.cli.helpers import load_answers_file

        provided = {**load_answers_file(answers_file), **provided}
    provided = apply_then_reject_removed_keys(provided).answers
    identity_errors = validate_identity_fields(provided)
    if identity_errors:
        raise ValidationFailedError(identity_errors)

    dest_answers = dest_path / ".copier-answers.yml"
    dest_remapped: dict = {}
    if dest_answers.exists():
        dest_remapped = remap_answers_file(dest_answers, write=not dry_run).answers

    merged = apply_then_reject_removed_keys({**dest_remapped, **provided}).answers
    gate = validate_answers_for_generation(merged)
    if not gate.ok:
        raise ValidationFailedError(list(gate.errors))

    if dry_run:
        final_answers = prepare_copier_data(merged)
        diff = compute_diff(
            answers=final_answers,
            destination=dest_path,
            template_path=config.template_path,
            operation="recopy",
            timeout=config.timeout,
            force_unsafe=config.force_unsafe,
        )
        return diff.to_dict()

    try:
        result = template_run_recopy(
            destination=dest_path,
            data=provided or None,
            template_path=config.template_path,
            force_unsafe=config.force_unsafe,
            timeout=config.timeout,
            skip_post_gen=config.skip_post_gen,
        )
    except Exception as exc:
        raise CopierOperationError("recopy", str(exc)) from exc

    return result.to_dict()
