"""Unit tests for scripts/hooks/quality_tool_check.py env hardening."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
def test_subprocess_env_trusts_cwd_for_mise(tmp_path: Path, monkeypatch) -> None:
    """Generated sample .mise.toml must be trusted for uv tool probes."""
    # Import via scripts path layout used by post_gen hooks.
    scripts = Path(__file__).resolve().parents[3] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    # Clear cached import
    import sys

    for name in list(sys.modules):
        if name == "hooks" or name.startswith("hooks."):
            del sys.modules[name]

    os.chdir(tmp_path)
    from hooks.quality_tool_check import (  # pylint: disable=import-error,no-name-in-module
        _subprocess_env,
    )

    monkeypatch.setenv("MISE_TRUSTED_CONFIG_PATHS", "/already/trusted")
    env = _subprocess_env()
    trusted = env["MISE_TRUSTED_CONFIG_PATHS"]
    assert "/already/trusted" in trusted
    assert str(tmp_path.resolve()) in trusted
    assert str(tmp_path.resolve().parent) in trusted
