"""Tests for path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.errors import TemplateNotFoundError
from riso.core.paths import resolve_template_path, validate_destination


def test_resolve_template_from_checkout() -> None:
    path = resolve_template_path()
    assert path.name == "template"
    assert (path / "copier.yml").exists()


def test_resolve_template_explicit(tmp_path: Path) -> None:
    with pytest.raises(TemplateNotFoundError):
        resolve_template_path(tmp_path / "missing")


def test_validate_destination_blocks_etc() -> None:
    with pytest.raises(Exception):
        validate_destination("/etc/passwd")
