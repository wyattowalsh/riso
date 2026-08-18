"""Tests for diff command apply-then-reject wiring."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from riso.cli.commands.diff import run_diff
from riso.cli.config import CliConfig
from riso.core.errors import ValidationFailedError
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "remap"


def _config() -> CliConfig:
    return CliConfig.from_options(template_path=resolve_template_path())


def test_diff_copy_remaps_answers_file(tmp_path: Path) -> None:
    answers = tmp_path / "answers.yml"
    answers.write_text((FIXTURE_DIR / "api_language.yml").read_text(encoding="utf-8"))
    fake_diff = SimpleNamespace(to_dict=lambda: {"operation": "copy", "files": []})

    with patch(
        "riso.cli.commands.diff.compute_diff", return_value=fake_diff
    ) as compute:
        run_diff(
            _config(),
            destination=str(tmp_path / "out"),
            answers_file=answers,
            data_pairs=None,
            operation="copy",
        )

    remapped = compute.call_args.kwargs["answers"]
    assert remapped["api_languages"] == ["python"]
    assert "api_language" not in remapped


def test_diff_update_remaps_existing_answers(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        (FIXTURE_DIR / "mixed.yml").read_text(encoding="utf-8")
    )
    fake_diff = SimpleNamespace(to_dict=lambda: {"operation": "update", "files": []})

    with patch(
        "riso.cli.commands.diff.compute_diff", return_value=fake_diff
    ) as compute:
        run_diff(
            _config(),
            destination=str(dest),
            answers_file=None,
            data_pairs=None,
            operation="update",
        )

    remapped = compute.call_args.kwargs["answers"]
    assert remapped["api_module"] == "enabled"
    assert remapped["saas_auth_provider"] == "authjs"
    assert "api_tracks" not in remapped
    assert "saas_auth" not in remapped


def test_compute_diff_update_does_not_remerge_removed_keys(tmp_path: Path) -> None:
    from riso.core.diff import compute_diff
    from riso.core.paths import resolve_template_path

    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: Demo\napi_language: python\napi_languages:\n  - python\n",
        encoding="utf-8",
    )
    captured: dict = {}

    def fake_worker(op: str, payload: dict, timeout: int | None) -> None:
        captured["data"] = payload.get("data")
        Path(payload["destination"]).mkdir(parents=True, exist_ok=True)

    with patch("riso.template._run_copier_worker", side_effect=fake_worker):
        compute_diff(
            answers={"project_name": "Demo", "api_languages": ["python"]},
            destination=dest,
            template_path=resolve_template_path(),
            operation="update",
        )

    assert captured["data"] is not None
    assert "api_language" not in captured["data"]
    assert captured["data"]["api_languages"] == ["python"]


def test_diff_rejects_leftover(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        (FIXTURE_DIR / "leftover.yml").read_text(encoding="utf-8")
    )

    with pytest.raises(ValidationFailedError) as exc:
        run_diff(
            _config(),
            destination=str(dest),
            answers_file=None,
            data_pairs=None,
            operation="update",
        )
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])
