"""Shared pytest fixtures for rendered Python projects."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _ensure_cli_commands_registered() -> None:
    """Ensure Typer commands are registered before CLI tests run."""
    from changelog_python.cli.__main__ import register_commands  # noqa: PLC0415

    register_commands()
