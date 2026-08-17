"""Tests for CLI helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.cli.helpers import load_answers_file, resolve_answers, validate_and_raise
from riso.core.errors import ValidationFailedError
from riso.core.paths import resolve_template_path

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "remap"


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


def test_resolve_answers_applies_then_rejects_remappable_keys(tmp_path: Path) -> None:
    path = tmp_path / "answers.yml"
    path.write_text((FIXTURE_DIR / "api_language.yml").read_text(encoding="utf-8"))
    answers = resolve_answers(
        answers_file=path,
        data_pairs=None,
        template_path=resolve_template_path(),
    )
    assert answers["api_languages"] == ["python"]
    assert "api_language" not in answers
    assert "api_tracks" not in answers


def test_resolve_answers_rejects_leftover_removed_keys(tmp_path: Path) -> None:
    path = tmp_path / "answers.yml"
    path.write_text((FIXTURE_DIR / "leftover.yml").read_text(encoding="utf-8"))
    with pytest.raises(ValidationFailedError) as exc:
        resolve_answers(
            answers_file=path,
            data_pairs=None,
            template_path=resolve_template_path(),
        )
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_validate_and_raise_remaps_then_validates() -> None:
    answers = {"project_name": "Demo App", "api_tracks": "python"}
    result = validate_and_raise(answers, resolve_template_path())
    assert result["valid"] is True
    assert answers["api_module"] == "enabled"
    assert answers["api_languages"] == ["python"]
    assert "api_tracks" not in answers


def test_validate_and_raise_rejects_leftover() -> None:
    answers = {"project_name": "Demo App", "saas_auth": "firebase"}
    with pytest.raises(ValidationFailedError) as exc:
        validate_and_raise(answers, resolve_template_path())
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])
