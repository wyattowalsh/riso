"""Recopy command — regenerate project from template."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.cli.commands.update import build_update_preview
from riso.cli.helpers import load_answers_file, parse_data_pairs
from riso.core.answers import (
    apply_then_reject_removed_keys,
    persist_remapped_answers,
    remap_answers_file,
)
from riso.core.errors import (
    CopierOperationError,
    PathNotFoundError,
    RisoError,
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
        provided = {**load_answers_file(answers_file), **provided}
    provided = apply_then_reject_removed_keys(provided).answers
    identity_errors = validate_identity_fields(provided)
    if identity_errors:
        raise ValidationFailedError(identity_errors)

    dest_answers = dest_path / ".copier-answers.yml"
    dest_remap = (
        remap_answers_file(dest_answers, write=False) if dest_answers.exists() else None
    )
    merged = apply_then_reject_removed_keys(
        {**(dest_remap.answers if dest_remap else {}), **provided}
    ).answers
    gate = validate_answers_for_generation(merged)
    if not gate.ok:
        raise ValidationFailedError(list(gate.errors))

    if dry_run:
        return build_update_preview(
            operation="recopy",
            destination=dest_path,
            answers=merged,
            remap=dest_remap,
            dest_answers_path=dest_answers if dest_answers.exists() else None,
        )

    try:
        result = template_run_recopy(
            destination=dest_path,
            data=merged,
            template_path=config.template_path,
            force_unsafe=config.force_unsafe,
            timeout=config.timeout,
            skip_post_gen=config.skip_post_gen,
        )
    except ValidationFailedError:
        raise
    except RisoError:
        raise
    except Exception as exc:
        raise CopierOperationError("recopy", str(exc)) from exc

    if dest_remap is not None and dest_answers.exists():
        persist_remapped_answers(dest_answers, dest_remap.answers)

    return result.to_dict()
