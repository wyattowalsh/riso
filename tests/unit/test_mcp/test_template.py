"""Tests for riso.template helpers."""

from __future__ import annotations

import pytest

pytest.importorskip("yaml")


def test_get_template_path_exists():
    from riso.template import get_template_path

    path = get_template_path()
    assert path.exists()
    assert (path / "copier.yml").exists()


def test_load_copier_config_contains_defaults():
    from riso.template import load_copier_config, get_template_path

    config = load_copier_config(get_template_path())
    assert "_defaults" in config  # Copier uses underscore prefix for internal keys
    # Check for some expected prompt keys (not "_prompts" since prompts are inlined)
    assert "project_name" in config


def test_get_defaults_computes_slug_and_package():
    from riso.template import get_defaults, get_template_path

    defaults = get_defaults(get_template_path(), project_name="My Project")
    assert defaults["project_name"] == "My Project"
    assert defaults["project_slug"] == "my-project"
    assert defaults["package_name"] == "my_project"


def test_validate_answers_reports_invalid_choice():
    from riso.template import validate_answers, get_template_path

    result = validate_answers({"project_layout": "unknown"}, get_template_path())
    assert result.valid is False
    assert any("project_layout" in err for err in result.errors)


def test_validate_answers_unknown_key_warning():
    from riso.template import validate_answers, get_template_path

    result = validate_answers({"unknown_key": "value"}, get_template_path())
    assert result.valid is True
    assert any("unknown_key" in warn for warn in result.warnings)


def test_list_sample_variants_has_default():
    from riso.template import list_sample_variants, get_samples_path

    variants = list_sample_variants(get_samples_path())
    names = {item["name"] for item in variants}
    assert "default" in names


def test_load_sample_answers_default():
    from riso.template import load_sample_answers, get_samples_path

    answers = load_sample_answers(samples_path=get_samples_path(), variant="default")
    assert isinstance(answers, dict)
    assert "project_name" in answers
