"""Directory arguments must expand to *.jinja files for the official ladder argv."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from validate_jinja_templates import _expand_jinja_paths, main

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


def test_expand_directory_walks_nested_jinja(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    jinja = nested / "ok.jinja"
    jinja.write_text("{{ x }}\n", encoding="utf-8")
    (tmp_path / "skip.txt").write_text("nope\n", encoding="utf-8")

    assert _expand_jinja_paths([tmp_path]) == [jinja]


def test_expand_keeps_explicit_files(tmp_path: Path) -> None:
    jinja = tmp_path / "ok.jinja"
    jinja.write_text("{% if true %}ok{% endif %}\n", encoding="utf-8")
    missing = tmp_path / "missing.jinja"

    assert _expand_jinja_paths([jinja, missing]) == [jinja, missing]


def test_main_accepts_directory_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "ok.jinja").write_text("{% if true %}ok{% endif %}\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["validate_jinja_templates.py", str(tmp_path)])

    assert main() == 0
    captured = capsys.readouterr()
    assert "1 Jinja template(s): all OK" in captured.out
    assert "Not a file" not in captured.err
