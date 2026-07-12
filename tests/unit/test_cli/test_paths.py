"""Tests for path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.errors import PermissionDeniedError, TemplateNotFoundError
from riso.core.paths import resolve_template_path, validate_destination


def test_resolve_template_from_checkout() -> None:
    path = resolve_template_path()
    assert path.name == "template"
    assert (path / "copier.yml").exists()


def test_resolve_template_explicit(tmp_path: Path) -> None:
    with pytest.raises(TemplateNotFoundError):
        resolve_template_path(tmp_path / "missing")


def test_validate_destination_blocks_etc() -> None:
    with pytest.raises(PermissionDeniedError):
        validate_destination("/etc/passwd")


def test_validate_destination_blocks_dollar_home(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOME", "/etc")
    with pytest.raises(PermissionDeniedError):
        validate_destination("$HOME/passwd")


def test_validate_destination_blocks_home_secret_dirs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_home = tmp_path / "userhome"
    fake_home.mkdir()
    for name in (".ssh", ".gnupg", ".aws"):
        (fake_home / name).mkdir()
    monkeypatch.setattr("riso.core.paths.Path.home", lambda: fake_home)

    for name in (".ssh", ".gnupg", ".aws"):
        with pytest.raises(PermissionDeniedError):
            validate_destination(str(fake_home / name / "credentials"))


def test_validate_destination_allows_projects_under_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_home = tmp_path / "userhome"
    fake_home.mkdir()
    project = fake_home / "dev" / "my-app"
    monkeypatch.setattr("riso.core.paths.Path.home", lambda: fake_home)

    resolved = validate_destination(str(project))
    assert resolved == project.resolve()
