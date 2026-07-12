"""Integration-style tests for riso update worker payload (mocked Copier)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

from riso.template import run_update


def test_update_worker_payload_includes_src_path_and_skip_tasks(tmp_path: Path) -> None:
    """Ensure update dispatches skip_tasks and template path via data."""
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
    assert captured["payload"]["data"] == {"_src_path": str(template)}
