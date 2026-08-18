"""Tests for variants command (shipped run_variants_* entrypoints)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path

import pytest

from riso.cli.commands.variants import run_variants_list, run_variants_show
from riso.cli.config import CliConfig
from riso.core.errors import PathNotFoundError
from riso.template import list_sample_variants

pytestmark = pytest.mark.unit


def test_variants_list_returns_count_matching_variants() -> None:
    config = CliConfig.from_options()
    result = run_variants_list(config)

    assert isinstance(result["variants"], list)
    assert result["count"] == len(result["variants"])
    assert result["count"] >= 1
    names = [v["name"] for v in result["variants"]]
    assert len(names) == len(set(names))
    for item in result["variants"]:
        assert "name" in item
        assert "path" in item
        assert "has_answers" in item


def test_variants_show_known_variant_includes_answers() -> None:
    config = CliConfig.from_options()
    listed = run_variants_list(config)
    name = listed["variants"][0]["name"]

    result = run_variants_show(config, name)

    assert result["name"] == name
    assert "answers" in result
    assert isinstance(result["answers"], dict)


def test_variants_show_unknown_raises_path_not_found() -> None:
    config = CliConfig.from_options()
    with pytest.raises(PathNotFoundError):
        run_variants_show(config, "__no_such_variant__")


def test_list_sample_variants_includes_nested_answers(tmp_path: Path) -> None:
    nested = tmp_path / "saas-starter" / "nested"
    nested.mkdir(parents=True)
    (nested / "copier-answers.yml").write_text("project_name: Nested\n")
    skipped = tmp_path / "render" / "ignored"
    skipped.mkdir(parents=True)
    (skipped / "copier-answers.yml").write_text("project_name: Skip\n")
    (tmp_path / "metadata").mkdir()
    (tmp_path / "default").mkdir()
    (tmp_path / "default" / "copier-answers.yml").write_text("project_name: Default\n")

    variants = list_sample_variants(tmp_path)
    names = [item["name"] for item in variants]
    assert "saas-starter/nested" in names
    assert "default" in names
    assert "render" not in names
    assert "render/ignored" not in names
    assert all("/" not in name or name == "saas-starter/nested" for name in names)
    nested_item = next(
        item for item in variants if item["name"] == "saas-starter/nested"
    )
    assert nested_item["answers"]["project_name"] == "Nested"
