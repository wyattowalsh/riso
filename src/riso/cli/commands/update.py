"""Update command — apply template updates to existing project."""

from __future__ import annotations

from typing import TYPE_CHECKING

from riso.core.answers import remap_answers_file, serialize_remap_ops
from riso.core.diff import compute_diff
from riso.core.errors import (
    CopierOperationError,
    PathNotFoundError,
    ValidationFailedError,
)
from riso.core.generation_gates import validate_answers_for_generation
from riso.core.paths import validate_destination
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
    dest_path = validate_destination(destination)
    if not dest_path.exists():
        raise PathNotFoundError(str(dest_path))

    answers_file = dest_path / ".copier-answers.yml"
    if not answers_file.exists():
        raise CopierOperationError(
            "update",
            f"No .copier-answers.yml found at {dest_path}",
        )

    remapped = remap_answers_file(answers_file, write=not dry_run)
    remap_payload = {
        "answers_file": str(answers_file),
        "changed": bool(remapped.ops),
        "written": bool(remapped.ops) and not dry_run,
        "ops": serialize_remap_ops(remapped.ops),
    }

    if dry_run:
        gate = validate_answers_for_generation(remapped.answers)
        if not gate.ok:
            raise ValidationFailedError(list(gate.errors))
        diff = compute_diff(
            answers=remapped.answers,
            destination=dest_path,
            template_path=config.template_path,
            operation="update",
            timeout=config.timeout,
            force_unsafe=config.force_unsafe,
        )
        payload = diff.to_dict()
        payload["remap"] = remap_payload
        return payload

    try:
        result = template_run_update(
            destination=dest_path,
            template_path=config.template_path,
            skip_answered=skip_answered,
            force_unsafe=config.force_unsafe,
            timeout=config.timeout,
            skip_post_gen=config.skip_post_gen,
        )
    except Exception as exc:
        raise CopierOperationError("update", str(exc)) from exc

    payload = result.to_dict()
    payload["remap"] = remap_payload
    return payload
