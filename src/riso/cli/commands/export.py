"""Export command — emit copier CLI and YAML for humans."""

from __future__ import annotations

import shlex
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from riso.cli.helpers import resolve_answers
from riso.core.paths import validate_destination

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_export_cli(
    config: CliConfig,
    *,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    destination: str = "./my-project",
) -> dict:
    """Export a human-readable copier copy command."""
    validate_destination(destination)
    answers = resolve_answers(
        answers_file=answers_file,
        data_pairs=data_pairs,
        template_path=config.template_path,
    )
    template_q = shlex.quote(str(config.template_path))
    dest_q = shlex.quote(destination)
    if answers_file:
        answers_q = shlex.quote(str(answers_file))
        cmd = f"copier copy {template_q} {dest_q} --answers-file {answers_q}"
    else:
        data_args = " ".join(
            f"--data {shlex.quote(f'{k}={v}')}" for k, v in sorted(answers.items())
        )
        cmd = f"copier copy {template_q} {dest_q} {data_args}".strip()

    riso_parts = ["uv", "run", "riso", "copy", dest_q]
    if answers_file:
        riso_parts.extend(["--answers-file", shlex.quote(str(answers_file))])
    else:
        for key, value in sorted(answers.items()):
            riso_parts.extend(["--data", shlex.quote(f"{key}={value}")])
    riso_cmd = " ".join(riso_parts)

    return {
        "copier_command": cmd,
        "riso_command": riso_cmd,
        "destination": destination,
        "template_path": str(config.template_path),
    }


def run_export_yaml(
    config: CliConfig,
    *,
    answers_file: Path | None,
    data_pairs: list[str] | None,
    to_stdout: bool = True,
) -> dict:
    """Export copier-answers.yml content."""
    answers = resolve_answers(
        answers_file=answers_file,
        data_pairs=data_pairs,
        template_path=config.template_path,
    )
    yaml_text = yaml.safe_dump(answers, sort_keys=False, default_flow_style=False)
    if to_stdout and not answers_file:
        sys.stdout.write(yaml_text)
    return {"yaml": yaml_text, "answers": answers}
