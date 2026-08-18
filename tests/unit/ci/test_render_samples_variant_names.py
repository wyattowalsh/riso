"""Nested variant names must be accepted by render-samples.sh."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

RENDER_SAMPLES = Path(__file__).resolve().parents[3] / "scripts" / "render-samples.sh"


def test_render_samples_accepts_nested_saas_variant_name() -> None:
    """Accept nested saas-starter variant names and reject absolute paths."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert "^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$" in text
    pattern = re.compile(r"^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$")
    assert pattern.match("saas-starter/vercel-starter")
    assert pattern.match("default")
    assert not pattern.match("/abs/path")
    assert not pattern.match("saas-starter//vercel")


def test_render_samples_exports_copier_answers_json() -> None:
    """Official render must export COPIER_ANSWERS JSON for pre_gen."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert "export COPIER_ANSWERS" in text
    assert "json.dumps(yaml.safe_load" in text


def test_render_samples_trusts_dest_mise_toml() -> None:
    """Official dest writer must trust generated mise.toml before bootstrap."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert 'mise trust "${destination}/mise.toml"' in text
    assert 'mise trust "${destination}"' in text


def test_render_samples_syncs_api_python_quality_groups() -> None:
    """Python dest bootstrap must isolate uv groups from the parent venv."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert "--group api_python --group api_python_test" in text
    assert "env -u VIRTUAL_ENV uv sync" in text
    assert 'child_env.pop("VIRTUAL_ENV", None)' in text


def test_render_samples_fails_variant_on_bootstrap_error() -> None:
    """Bootstrap failure must fail the variant instead of continuing."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert (
        'if ! bootstrap_render_dependencies "${destination}" "${answers_file}"; then'
        in text
    )
    assert "ERROR: bootstrap failed for variant" in text
    assert "failed=1" in text
    assert 'return "${failed}"' in text or 'return "${failed}"' in text
