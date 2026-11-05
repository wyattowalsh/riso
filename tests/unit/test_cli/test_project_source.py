"""Saved Copier source selection, safety, and real worker boundary checks."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml
from copier import run_copy

from riso.cli.commands.recopy import run_recopy as cli_recopy
from riso.cli.commands.update import run_update as cli_update
from riso.cli.config import CliConfig
from riso.core.errors import CopierOperationError
from riso.template import run_recopy, run_update
from riso.template._copier_worker import _run_update


@pytest.mark.parametrize("operation", ["update", "recopy"])
def test_cli_default_does_not_override_saved_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    """The implicit bundled default cannot replace a project's saved source."""
    monkeypatch.delenv("RISO_TEMPLATE_PATH", raising=False)
    dest = tmp_path / "project"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        f"_src_path: {tmp_path / 'external'}\nproject_name: Demo\n"
    )
    fake = SimpleNamespace(to_dict=lambda: {"success": True})
    config = CliConfig.from_options()
    with patch(
        f"riso.cli.commands.{operation}.template_run_{operation}", return_value=fake
    ) as worker:
        if operation == "update":
            cli_update(config, destination=str(dest))
        else:
            cli_recopy(
                config, destination=str(dest), answers_file=None, data_pairs=None
            )
    assert worker.call_args.kwargs["template_path"] is None


@pytest.mark.parametrize("operation", ["update", "recopy"])
@pytest.mark.parametrize("override_kind", ["explicit", "data"])
def test_conflicting_source_is_rejected_without_mutation(
    tmp_path: Path, operation: str, override_kind: str
) -> None:
    """Conflicting flag/data sources fail before workers or answer writes."""
    dest = tmp_path / "project"
    dest.mkdir()
    answers_file = dest / ".copier-answers.yml"
    answers_file.write_text(f"_src_path: {tmp_path / 'saved'}\nproject_name: Demo\n")
    original = answers_file.read_bytes()
    explicit = tmp_path / "different" if override_kind == "explicit" else None
    supplied = (
        {"_src_path": str(tmp_path / "different")} if override_kind == "data" else None
    )
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(CopierOperationError, match="conflicts"):
            if operation == "update":
                run_update(destination=dest, template_path=explicit, answers=supplied)
            else:
                run_recopy(destination=dest, template_path=explicit, data=supplied)
    worker.assert_not_called()
    assert answers_file.read_bytes() == original


@pytest.mark.parametrize("operation", ["update", "recopy"])
def test_remote_saved_source_never_inherits_bundled_hook_or_unsafe_permission(
    tmp_path: Path, operation: str
) -> None:
    """Remote saved sources gain neither bundled hook execution nor unsafe mode."""
    dest = tmp_path / "project"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "_src_path: https://example.invalid/template.git\nproject_name: Demo\n"
    )
    with (
        patch("riso.template._run_copier_worker") as worker,
        patch("riso.template.run_post_gen") as post,
    ):
        if operation == "update":
            run_update(destination=dest)
        else:
            run_recopy(destination=dest, data=None)
    assert worker.call_args.args[1]["unsafe"] is False
    assert "_src_path" not in worker.call_args.args[1]["data"]
    post.assert_not_called()


def test_update_worker_enables_required_overwrite_without_enabling_unsafe(
    tmp_path: Path,
) -> None:
    """Copier updates receive required overwrite without additional trust."""
    with patch("riso.template._copier_worker.run_update") as copier_update:
        _run_update({"destination": str(tmp_path)})
    assert copier_update.call_args.kwargs["overwrite"] is True
    assert copier_update.call_args.kwargs["unsafe"] is False
    assert copier_update.call_args.kwargs["skip_tasks"] is True


def test_real_recopy_uses_saved_template_without_config_default(tmp_path: Path) -> None:
    """A real Copier recopy selects its persisted external template by default."""
    template = tmp_path / "external"
    template.mkdir()
    (template / "copier.yml").write_text(
        "project_name:\n  type: str\n  default: Demo\n"
    )
    (template / ".copier-answers.yml.jinja").write_text(
        "{{ _copier_answers | to_nice_yaml }}\n"
    )
    (template / "message.txt.jinja").write_text("Original {{ project_name }}\n")
    dest = tmp_path / "project"
    run_copy(str(template), str(dest), defaults=True, skip_tasks=True)

    # Recopy the real persisted source without changing any existing file, so
    # this verifies source resolution independently of overwrite UX.
    result = run_recopy(destination=dest, data=None, timeout=10)

    assert result.success
    assert (dest / "message.txt").read_text() == "Original Demo\n"
    assert yaml.safe_load((dest / ".copier-answers.yml").read_text())[
        "_src_path"
    ] == str(template)
