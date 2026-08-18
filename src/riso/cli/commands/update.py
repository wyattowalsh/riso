"""Update command — apply template updates to existing project."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from riso.core.answers import (
    persist_remapped_answers,
    prepare_copier_data,
    remap_answers_file,
    serialize_remap_ops,
)
from riso.core.errors import (
    CopierOperationError,
    PathNotFoundError,
    RisoError,
    ValidationFailedError,
)
from riso.core.generation_gates import validate_answers_for_generation
from riso.core.paths import validate_destination
from riso.template import run_update as template_run_update

if TYPE_CHECKING:
    from riso.cli.config import CliConfig
    from riso.core.answers import RemapResult


def build_update_preview(
    *,
    operation: str,
    destination: Path,
    answers: dict[str, Any],
    remap: RemapResult | None,
    dest_answers_path: Path | None,
) -> dict[str, Any]:
    """Answers-only dry-run preview. Never runs Copier."""
    return {
        "operation": operation,
        "dry_run": True,
        "destination": str(destination),
        "preview_engine": "answers",
        "summary": ("dry-run: remapped answers and generation gates (no Copier copy)"),
        "answers": prepare_copier_data(answers),
        "remap": {
            "answers_file": str(dest_answers_path) if dest_answers_path else None,
            "changed": bool(remap.ops) if remap is not None else False,
            "written": False,
            "ops": serialize_remap_ops(remap.ops) if remap is not None else [],
        },
    }


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

    remapped = remap_answers_file(answers_file, write=False)
    remap_payload = {
        "answers_file": str(answers_file),
        "changed": bool(remapped.ops),
        "written": False,
        "ops": serialize_remap_ops(remapped.ops),
    }

    if dry_run:
        gate = validate_answers_for_generation(remapped.answers)
        if not gate.ok:
            raise ValidationFailedError(list(gate.errors))
        return build_update_preview(
            operation="update",
            destination=dest_path,
            answers=remapped.answers,
            remap=remapped,
            dest_answers_path=answers_file,
        )

    try:
        result = template_run_update(
            destination=dest_path,
            template_path=config.template_path,
            skip_answered=skip_answered,
            force_unsafe=config.force_unsafe,
            timeout=config.timeout,
            skip_post_gen=config.skip_post_gen,
            answers=remapped.answers,
        )
    except ValidationFailedError:
        raise
    except RisoError:
        raise
    except Exception as exc:
        raise CopierOperationError("update", str(exc)) from exc

    persist_remapped_answers(answers_file, remapped.answers)
    remap_payload["written"] = bool(remapped.ops)

    payload = result.to_dict()
    payload["remap"] = remap_payload
    return payload
