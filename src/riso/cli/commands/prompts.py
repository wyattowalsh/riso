"""Prompts command — introspect copier.yml questions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from riso.core.errors import ValidationFailedError
from riso.template import get_defaults, get_prompts, load_copier_config

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_prompts_list(config: CliConfig) -> dict:
    """Return all template prompts."""
    full_config = load_copier_config(config.template_path)
    return {
        "prompts": get_prompts(config.template_path),
        "defaults": get_defaults(config.template_path),
        "metadata": full_config.get("metadata", {}),
    }


def run_prompts_show(config: CliConfig, key: str) -> dict:
    """Return a single prompt definition."""
    prompts = get_prompts(config.template_path)
    if key not in prompts:
        raise ValidationFailedError([f"Unknown prompt key: {key}"])
    defaults = get_defaults(config.template_path)
    return {
        "key": key,
        "prompt": prompts[key],
        "default": defaults.get(key),
    }
