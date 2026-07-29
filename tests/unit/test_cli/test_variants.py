"""Tests for variants command (shipped run_variants_* entrypoints)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

import pytest

from riso.cli.commands.variants import run_variants_list, run_variants_show
from riso.cli.config import CliConfig
from riso.core.errors import PathNotFoundError

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
