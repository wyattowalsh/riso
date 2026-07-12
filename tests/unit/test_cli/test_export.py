"""Tests for export command."""

from __future__ import annotations

import shlex
from pathlib import Path

import pytest

from riso.cli.commands.export import run_export_cli, run_export_yaml
from riso.cli.config import CliConfig
from riso.core.errors import PermissionDeniedError
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit


def test_run_export_cli_quotes_paths_with_spaces(tmp_path: Path) -> None:
    real_template = resolve_template_path()
    spaced_parent = tmp_path / "my templates"
    spaced_parent.mkdir()
    template_link = spaced_parent / "template"
    template_link.symlink_to(real_template, target_is_directory=True)

    config = CliConfig.from_options(template_path=template_link)
    destination = str(tmp_path / "out dir" / "my project")

    result = run_export_cli(
        config,
        answers_file=None,
        data_pairs=["project_name=Demo App"],
        destination=destination,
    )

    template_quoted = shlex.quote(str(config.template_path))
    dest_quoted = shlex.quote(destination)

    assert template_quoted in result["copier_command"]
    assert dest_quoted in result["copier_command"]
    assert dest_quoted in result["riso_command"]


def test_run_export_cli_rejects_dangerous_destination(tmp_path: Path) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    with pytest.raises(PermissionDeniedError):
        run_export_cli(
            config,
            answers_file=None,
            data_pairs=["project_name=demo"],
            destination="/etc/foo",
        )


def test_run_export_cli_includes_data_overrides_with_answers_file(
    tmp_path: Path,
) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    answers_file = tmp_path / "copier-answers.yml"
    answers_file.write_text("project_name: Base\n", encoding="utf-8")

    result = run_export_cli(
        config,
        answers_file=answers_file,
        data_pairs=["project_name=Override"],
        destination=str(tmp_path / "out"),
    )

    assert "--answers-file" in result["copier_command"]
    assert "project_name=Override" in result["copier_command"]
    assert "--data" in result["riso_command"]
    assert "project_name=Override" in result["riso_command"]


def test_run_export_yaml_does_not_write_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = CliConfig.from_options(template_path=resolve_template_path())
    run_export_yaml(
        config,
        answers_file=None,
        data_pairs=["project_name=StdoutFree"],
    )
    assert capsys.readouterr().out == ""
