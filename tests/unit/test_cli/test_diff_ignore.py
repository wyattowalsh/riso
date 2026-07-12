"""Tests for diff ignore path rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.diff import _should_ignore

pytestmark = pytest.mark.unit


def test_should_ignore_git_requires_path_part() -> None:
    assert _should_ignore(Path("project.gitconfig")) is False
    assert _should_ignore(Path(".git/config")) is True
    assert _should_ignore(Path("nested/.git/HEAD")) is True
