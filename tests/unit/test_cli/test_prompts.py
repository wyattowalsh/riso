"""Tests for prompts command (shipped run_prompts_* entrypoints)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

import pytest

from riso.cli.commands.prompts import run_prompts_list, run_prompts_show
from riso.cli.config import CliConfig
from riso.core.errors import ValidationFailedError

pytestmark = pytest.mark.unit


def test_prompts_list_includes_prompts_and_defaults() -> None:
    config = CliConfig.from_options()
    result = run_prompts_list(config)

    assert isinstance(result["prompts"], dict)
    assert isinstance(result["defaults"], dict)
    assert "project_name" in result["prompts"]
    assert "project_name" in result["defaults"]
    assert "metadata" in result


def test_prompts_show_returns_key_prompt_and_default() -> None:
    config = CliConfig.from_options()
    result = run_prompts_show(config, "project_name")

    assert result["key"] == "project_name"
    assert isinstance(result["prompt"], dict)
    assert "default" in result


def test_prompts_show_unknown_key_raises_validation_failed() -> None:
    config = CliConfig.from_options()
    with pytest.raises(ValidationFailedError) as exc_info:
        run_prompts_show(config, "__no_such_prompt_key__")

    assert any(
        "Unknown prompt key" in err
        for err in (exc_info.value.data or {}).get("errors", [])
    )
