"""Integration-style tests for riso update worker payload (mocked Copier)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from riso.core.paths import resolve_template_path
from riso.template import run_recopy, run_update


def test_update_worker_payload_includes_src_path_and_skip_tasks(tmp_path: Path) -> None:
    """Ensure update dispatches skip_tasks, overwrite, and remapped answers."""
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "cli_module: enabled\ncli_languages: [python]\n",
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
        captured["op"] = op
        captured["payload"] = payload
        captured["timeout"] = timeout

    template = tmp_path / "template-root"
    template.mkdir()
    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_update(
            destination=dest,
            template_path=template,
            skip_post_gen=True,
        )

    assert captured["op"] == "update"
    assert captured["payload"]["skip_tasks"] is True
    assert captured["payload"]["overwrite"] is True
    assert captured["payload"]["unsafe"] is False
    data = captured["payload"]["data"]
    assert data["_src_path"] == str(template)
    assert data["cli_module"] == "enabled"
    assert data["cli_languages"] == ["python"]


def test_update_worker_payload_bundled_sets_unsafe(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "cli_module: enabled\ncli_languages: [python]\n",
        encoding="utf-8",
    )
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
        captured["payload"] = payload

    bundled = resolve_template_path()
    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_update(destination=dest, template_path=bundled, skip_post_gen=True)

    assert captured["payload"]["unsafe"] is True
    assert captured["payload"]["skip_tasks"] is True
    assert captured["payload"]["overwrite"] is True
    assert captured["payload"]["data"]["_src_path"] == str(bundled)


def test_recopy_worker_payload_overwrite_defaults_skip_answered(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    captured: dict[str, Any] = {}

    def fake_worker(op: str, payload: dict[str, Any], timeout: int | None) -> None:
        captured["op"] = op
        captured["payload"] = payload

    template = tmp_path / "template-root"
    template.mkdir()
    with (
        patch("riso.template._run_copier_worker", side_effect=fake_worker),
        patch("riso.template._maybe_run_post_gen"),
    ):
        run_recopy(
            destination=dest,
            data={"project_name": "Demo"},
            template_path=template,
            skip_post_gen=True,
        )

    assert captured["op"] == "recopy"
    payload = captured["payload"]
    assert payload["skip_tasks"] is True
    assert payload["overwrite"] is True
    assert payload["defaults"] is True
    assert payload["skip_answered"] is True
    assert payload["unsafe"] is False
    assert payload["data"]["_src_path"] == str(template)
