"""Tests for export command."""

from __future__ import annotations

import shlex
from pathlib import Path

import pytest

from riso.cli.commands.export import run_export_cli
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
