"""Tests for riso migrate (remap answers file, dry-run, leftover fail-closed)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from riso.cli.app import app
from riso.cli.commands.migrate import run_migrate
from riso.cli.config import CliConfig
from riso.core.errors import PathNotFoundError, ValidationFailedError
from riso.core.paths import resolve_template_path
from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "remap"
EXPECTED_FIXTURES = {
    "api_language.yml",
    "api_tracks.yml",
    "docs_site.yml",
    "include_admin.yml",
    "mcp_language.yml",
    "saas_auth.yml",
    "saas_billing.yml",
    "saas_starter_module.yml",
    "mixed.yml",
    "already_canonical.yml",
    "leftover.yml",
}


def _config() -> CliConfig:
    return CliConfig.from_options(template_path=resolve_template_path())


def test_remap_fixtures_cover_eight_keys_mixed_and_leftover() -> None:
    names = {path.name for path in FIXTURE_DIR.glob("*.yml")}
    assert EXPECTED_FIXTURES <= names
    assert set(REMOVED_ANSWER_KEYS) == {
        "api_tracks",
        "api_language",
        "docs_site",
        "mcp_language",
        "saas_starter_module",
        "saas_auth",
        "saas_billing",
        "include_admin",
    }


@pytest.mark.parametrize(
    ("fixture", "old_key", "dest_check"),
    [
        (
            "api_language.yml",
            "api_language",
            lambda a: a["api_languages"] == ["python"],
        ),
        (
            "mcp_language.yml",
            "mcp_language",
            lambda a: a["mcp_languages"] == ["typescript"],
        ),
        ("api_tracks.yml", "api_tracks", lambda a: a["api_module"] == "enabled"),
        (
            "docs_site.yml",
            "docs_site",
            lambda a: a["docs_framework"] == "sphinx-shibuya",
        ),
        (
            "saas_starter_module.yml",
            "saas_starter_module",
            lambda a: a["saas_infra_module"] == "enabled",
        ),
        ("saas_auth.yml", "saas_auth", lambda a: a["saas_auth_provider"] == "clerk"),
        (
            "saas_billing.yml",
            "saas_billing",
            lambda a: a["saas_billing_provider"] == "stripe",
        ),
        (
            "include_admin.yml",
            "include_admin",
            lambda a: a["saas_admin_dashboard"] is True,
        ),
    ],
)
def test_migrate_dry_run_loads_fixture(
    tmp_path: Path,
    fixture: str,
    old_key: str,
    dest_check,
) -> None:
    answers = tmp_path / fixture
    answers.write_text((FIXTURE_DIR / fixture).read_text(encoding="utf-8"))
    original = answers.read_text(encoding="utf-8")

    result = run_migrate(
        _config(),
        destination=None,
        answers_file=answers,
        dry_run=True,
    )

    assert result["changed"] is True
    assert result["written"] is False
    assert result["dry_run"] is True
    assert answers.read_text(encoding="utf-8") == original
    assert old_key not in result["answers"]
    assert dest_check(result["answers"])
    assert any(op["old"] == old_key for op in result["ops"])


def test_migrate_mixed_fixture_then_idempotent_second_pass(tmp_path: Path) -> None:
    answers = tmp_path / "mixed.yml"
    answers.write_text((FIXTURE_DIR / "mixed.yml").read_text(encoding="utf-8"))

    first = run_migrate(
        _config(),
        destination=None,
        answers_file=answers,
        dry_run=False,
    )
    assert first["written"] is True
    written = yaml.safe_load(answers.read_text(encoding="utf-8"))
    assert set(written).isdisjoint(REMOVED_ANSWER_KEYS)
    assert written["api_languages"] == ["python", "go"]
    assert written["mcp_languages"] == ["typescript"]

    second = run_migrate(
        _config(),
        destination=None,
        answers_file=answers,
        dry_run=False,
    )
    assert second["changed"] is False
    assert second["written"] is False
    assert second["ops"] == []
    assert second["message"] == "Already canonical"


def test_migrate_leftover_fails_closed(tmp_path: Path) -> None:
    answers = tmp_path / "leftover.yml"
    answers.write_text((FIXTURE_DIR / "leftover.yml").read_text(encoding="utf-8"))
    original = answers.read_text(encoding="utf-8")

    with pytest.raises(ValidationFailedError) as exc:
        run_migrate(_config(), destination=None, answers_file=answers, dry_run=False)

    assert answers.read_text(encoding="utf-8") == original
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_migrate_dest_uses_copier_answers(tmp_path: Path) -> None:
    dest = tmp_path / "proj"
    dest.mkdir()
    answers = dest / ".copier-answers.yml"
    answers.write_text((FIXTURE_DIR / "already_canonical.yml").read_text())

    result = run_migrate(
        _config(),
        destination=str(dest),
        answers_file=None,
        dry_run=True,
    )
    assert result["changed"] is False
    assert Path(result["answers_file"]) == answers


def test_migrate_requires_exactly_one_target() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        run_migrate(_config(), destination=None, answers_file=None)
    with pytest.raises(ValueError, match="exactly one"):
        run_migrate(
            _config(),
            destination=".",
            answers_file=Path("x.yml"),
        )


def test_migrate_missing_dest_raises(tmp_path: Path) -> None:
    with pytest.raises(PathNotFoundError):
        run_migrate(
            _config(),
            destination=str(tmp_path / "nope"),
            answers_file=None,
        )


def test_migrate_help_lists_flags() -> None:
    from typer.testing import CliRunner

    result = CliRunner().invoke(app, ["migrate", "--help"])
    assert result.exit_code == 0
    assert "--dry-run" in result.stdout
    assert "--answers-file" in result.stdout
    assert "--json" not in result.stdout or "json" in result.stdout.lower()
