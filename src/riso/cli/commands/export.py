"""Export command — emit copier CLI and YAML for humans."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from riso.cli.helpers import resolve_answers

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
    answers = resolve_answers(
        answers_file=answers_file,
        data_pairs=data_pairs,
        template_path=config.template_path,
    )
    if answers_file:
        cmd = (
            f"copier copy {config.template_path} {destination} "
            f"--answers-file {answers_file}"
        )
    else:
        data_args = " ".join(f'--data "{k}={v}"' for k, v in sorted(answers.items()))
        cmd = f"copier copy {config.template_path} {destination} {data_args}".strip()

    riso_cmd = (
        f"uv run riso copy {destination} "
        + (f"--answers-file {answers_file}" if answers_file else "")
        + (
            " " + " ".join(f"--data {k}={v}" for k, v in sorted(answers.items()))
            if not answers_file
            else ""
        )
    ).strip()

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
