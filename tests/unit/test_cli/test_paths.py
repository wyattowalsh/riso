"""Tests for path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.errors import PermissionDeniedError, TemplateNotFoundError
from riso.core.paths import (
    bundled_template_path,
    is_bundled_template,
    packaged_template_path,
    resolve_template_path,
    validate_destination,
)


def test_is_bundled_template_matches_checkout() -> None:
    path = resolve_template_path()
    assert is_bundled_template(path) is True
    assert path.name == "template"
    assert (path / "copier.yml").exists()


def test_is_bundled_template_rejects_other_path(tmp_path: Path) -> None:
    assert is_bundled_template(tmp_path) is False


def test_resolve_template_from_packaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packaged = tmp_path / "copier_template"
    packaged.mkdir()
    (packaged / "copier.yml").write_text("_min_copier_version: '9.1.0'\n")
    monkeypatch.delenv("RISO_TEMPLATE_PATH", raising=False)
    monkeypatch.setattr("riso.core.paths.checkout_root", lambda: None)
    monkeypatch.setattr(
        "riso.core.paths.packaged_template_path", lambda: packaged.resolve()
    )

    path = resolve_template_path()
    assert path == packaged.resolve()
    assert is_bundled_template(path) is True
    assert bundled_template_path() == packaged.resolve()


def test_resolve_template_missing_without_checkout_or_wheel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("RISO_TEMPLATE_PATH", raising=False)
    monkeypatch.setattr("riso.core.paths.checkout_root", lambda: None)
    monkeypatch.setattr("riso.core.paths.packaged_template_path", lambda: None)
    monkeypatch.setattr("riso.core.paths.repo_root", lambda: tmp_path)

    with pytest.raises(TemplateNotFoundError):
        resolve_template_path()


def test_packaged_template_path_none_in_src_checkout() -> None:
    # Editable/src layout does not ship ``riso/copier_template``; checkout wins.
    assert packaged_template_path() is None


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
