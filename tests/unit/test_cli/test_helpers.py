"""Tests for CLI helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.cli.helpers import load_answers_file
from riso.core.errors import ValidationFailedError

pytestmark = pytest.mark.unit


def test_load_answers_file_rejects_non_mapping(tmp_path: Path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text("- item\n", encoding="utf-8")
    with pytest.raises(ValidationFailedError) as exc:
        load_answers_file(path)
    assert exc.value.data is not None
    assert any("mapping" in err for err in exc.value.data["errors"])


def test_load_answers_file_loads_mapping(tmp_path: Path) -> None:
    path = tmp_path / "answers.yml"
    path.write_text("project_name: demo\n", encoding="utf-8")
    assert load_answers_file(path) == {"project_name": "demo"}


def test_load_answers_file_rejects_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text("project_name: [unterminated\n", encoding="utf-8")
    with pytest.raises(ValidationFailedError) as exc:
        load_answers_file(path)
    assert exc.value.data is not None
    assert any(
        "YAML" in err or "yaml" in err.lower() for err in exc.value.data["errors"]
    )


def test_load_answers_file_empty_returns_empty_dict(tmp_path: Path) -> None:
    path = tmp_path / "empty.yml"
    path.write_text("", encoding="utf-8")
    assert load_answers_file(path) == {}
