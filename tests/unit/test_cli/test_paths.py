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
from riso.template import get_template_path


def test_is_bundled_template_matches_checkout() -> None:
    """Trust checks recognize only the resolved checkout template."""
    assert is_bundled_template(resolve_template_path())


def test_is_bundled_template_rejects_other_path(tmp_path: Path) -> None:
    """An arbitrary local directory does not acquire bundled-template trust."""
    assert not is_bundled_template(tmp_path)


def test_resolve_template_from_packaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Wheel discovery remains available when there is no source checkout."""
    packaged = tmp_path / "copier_template"
    packaged.mkdir()
    (packaged / "copier.yml").write_text("_min_copier_version: '9.1.0'\n")
    monkeypatch.delenv("RISO_TEMPLATE_PATH", raising=False)
    monkeypatch.setattr("riso.core.paths.checkout_root", lambda: None)
    monkeypatch.setattr("riso.core.paths.packaged_template_path", lambda: packaged)
    assert resolve_template_path() == packaged
    assert bundled_template_path() == packaged
    assert is_bundled_template(packaged)


def test_resolve_template_missing_without_checkout_or_wheel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing wheel payload is reported rather than guessed from another path."""
    monkeypatch.delenv("RISO_TEMPLATE_PATH", raising=False)
    monkeypatch.setattr("riso.core.paths.checkout_root", lambda: None)
    monkeypatch.setattr("riso.core.paths.packaged_template_path", lambda: None)
    monkeypatch.setattr("riso.core.paths.repo_root", lambda: tmp_path)
    with pytest.raises(TemplateNotFoundError):
        resolve_template_path()


def test_packaged_template_path_none_in_src_checkout() -> None:
    """Editable source installs use the checkout instead of a wheel data directory."""
    assert packaged_template_path() is None


def test_resolve_template_from_checkout() -> None:
    """A source checkout resolves its checked-in Copier template."""
    path = resolve_template_path()
    assert path.name == "template"
    assert (path / "copier.yml").exists()


def test_resolve_template_explicit(tmp_path: Path) -> None:
    """An explicit missing template raises a path-resolution error."""
    with pytest.raises(TemplateNotFoundError):
        resolve_template_path(tmp_path / "missing")


def test_installed_template_resolution_without_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Installed CLI helpers agree on the bundled wheel payload location."""
    packaged = tmp_path / "site-packages" / "riso" / "copier_template"
    packaged.mkdir(parents=True)
    (packaged / "copier.yml").write_text("project_name: Demo\n", encoding="utf-8")
    monkeypatch.delenv("RISO_TEMPLATE_PATH", raising=False)
    monkeypatch.setattr("riso.core.paths.repo_root", lambda: tmp_path / "absent")
    monkeypatch.setattr("riso.core.paths.packaged_template_path", lambda: packaged)

    assert resolve_template_path() == packaged
    assert bundled_template_path() == packaged
    assert is_bundled_template(packaged)
    assert not is_bundled_template(tmp_path / "external")

    assert get_template_path() == packaged


def test_validate_destination_blocks_etc() -> None:
    """System configuration directories cannot become generated destinations."""
    with pytest.raises(PermissionDeniedError):
        validate_destination("/etc/passwd")


def test_validate_destination_blocks_dollar_home(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Environment expansion cannot bypass the system-directory guard."""
    monkeypatch.setenv("HOME", "/etc")
    with pytest.raises(PermissionDeniedError):
        validate_destination("$HOME/passwd")


def test_validate_destination_blocks_home_secret_dirs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Private credential directories remain forbidden under the user's home."""
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
    """Ordinary project directories under home remain valid destinations."""
    fake_home = tmp_path / "userhome"
    fake_home.mkdir()
    project = fake_home / "dev" / "my-app"
    monkeypatch.setattr("riso.core.paths.Path.home", lambda: fake_home)

    resolved = validate_destination(str(project))
    assert resolved == project.resolve()
