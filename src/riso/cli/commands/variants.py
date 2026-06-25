"""Variants command — list and show sample configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from riso.core.errors import PathNotFoundError
from riso.template import list_sample_variants, load_sample_answers

if TYPE_CHECKING:
    from riso.cli.config import CliConfig


def run_variants_list(config: CliConfig) -> dict:
    """List sample variants."""
    variants = list_sample_variants(config.samples_path)
    return {"variants": variants, "count": len(variants)}


def run_variants_show(config: CliConfig, name: str) -> dict:
    """Show a single sample variant."""
    variants = list_sample_variants(config.samples_path)
    match = next((v for v in variants if v["name"] == name), None)
    if match is None:
        raise PathNotFoundError(f"Variant not found: {name}")

    answers = load_sample_answers(samples_path=config.samples_path, variant=name)
    return {**match, "answers": answers}
