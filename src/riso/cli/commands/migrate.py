"""Migrate command — remap removed Copier answer keys in an answers file."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from riso.core.answers import remap_answers_file, serialize_remap_ops
from riso.core.errors import CopierOperationError, PathNotFoundError
from riso.core.paths import validate_destination

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_migrate(
    config: CliConfig,
    *,
    destination: str | None,
    answers_file: Path | None,
    dry_run: bool = False,
) -> dict:
    """Remap removed keys in DEST/.copier-answers.yml or --answers-file."""
    dest_given = bool(destination)
    file_given = answers_file is not None
    if dest_given == file_given:
        raise ValueError("Provide DEST or --answers-file (exactly one)")

    if answers_file is not None:
        path = Path(answers_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(path)
    else:
        dest_path = validate_destination(str(destination))
        if not dest_path.exists():
            raise PathNotFoundError(str(dest_path))
        path = dest_path / ".copier-answers.yml"
        if not path.exists():
            raise CopierOperationError(
                "migrate",
                f"No .copier-answers.yml found at {dest_path}",
            )

    remapped = remap_answers_file(path, write=not dry_run)
    changed = bool(remapped.ops)
    return {
        "answers_file": str(path),
        "changed": changed,
        "written": changed and not dry_run,
        "dry_run": dry_run,
        "ops": serialize_remap_ops(remapped.ops),
        "answers": remapped.answers,
        "template_path": str(config.template_path),
        "message": (
            f"Remapped {len(remapped.ops)} key(s)" if changed else "Already canonical"
        ),
    }
