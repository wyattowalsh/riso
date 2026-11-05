"""Unit tests for scripts/ci/verify_version_sync.py parsers and comparison."""

from __future__ import annotations

from pathlib import Path

import pytest

from verify_version_sync import (
    VersionSource,
    compare_versions,
    normalize_version,
    parse_mise_toml,
    parse_pre_gen_project,
    parse_pyproject_jinja,
    parse_versions_sh,
    parse_package_json,
    versions_compatible,
    main,
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.parametrize(
    ("required", "configured", "tool", "expected"),
    [
        ("22.13.0", "22.23.1", "node", True),
        ("22.13.0", "22.1.0", "node", False),
        ("22.14.0", "^22.14.0 || >=24.10.0", "node", True),
        ("20.0.0", "^22.14.0 || >=24.10.0", "node", False),
        ("20", ">=20.0.0", "node", True),
        ("20", "22.23.1", "node", False),
        ("0.4.30", "0.11.26", "uv", False),
        ("11.11.0", "9.15.0", "pnpm", False),
    ],
)
def test_distinct_runtime_floors_stay_checked(required, configured, tool, expected):
    """Verify distinct runtime floors stay checked."""
    assert versions_compatible(required, configured, tool) is expected


def test_repository_versions_agree_within_scopes():
    """Verify repository versions agree within scopes."""
    assert main() == 0


def test_package_parser_reads_jinja_wrapped_prompts(tmp_path):
    """Verify package parser reads jinja wrapped prompts."""
    path = tmp_path / "package.json.jinja"
    path.write_text(
        '{% if node_enabled %}\n{"engines":{"node":">=20.0.0"},'
        '"packageManager":"pnpm@9.15.0"}\n{% endif %}',
        encoding="utf-8",
    )
    assert parse_package_json(path) == {"node": ">=20.0.0", "pnpm": "9.15.0"}


@pytest.mark.unit
class TestNormalizeVersion:  # pylint: disable=too-few-public-methods
    """Test Normalize Version cases."""

    def test_strips_whitespace(self) -> None:
        """Verify strips whitespace."""
        assert normalize_version("  0.14.2  ") == "0.14.2"


@pytest.mark.unit
class TestParseVersionsSh:  # pylint: disable=too-few-public-methods
    """Test Parse Versions Sh cases."""

    def test_extracts_export_constants(self, tmp_path: Path) -> None:
        """Verify extracts export constants."""
        path = tmp_path / "versions.sh"
        path.write_text(
            '\nexport PYTHON_MIN_VERSION="3.11"\nexport UV_MIN_VERSION="0.4"\n',
            encoding="utf-8",
        )
        versions = parse_versions_sh(path)
        assert versions["python"] == "3.11"
        assert versions["uv"] == "0.4"


@pytest.mark.unit
class TestParsePreGen:  # pylint: disable=too-few-public-methods
    """Test Parse Pre Gen cases."""

    def test_extracts_tool_matrix_tuples(self, tmp_path: Path) -> None:
        """Verify extracts tool matrix tuples."""
        path = tmp_path / "pre_gen.py"
        path.write_text(
            'tool_matrix = [\n    ("uv", "0.4", "uv@0.4"),\n    ("node", "20", "node@20"),\n]\n',
            encoding="utf-8",
        )
        versions = parse_pre_gen_project(path)
        assert versions["uv"] == "0.4"
        assert versions["node"] == "20"


@pytest.mark.unit
class TestParsePyprojectJinja:  # pylint: disable=too-few-public-methods
    """Test Parse Pyproject Jinja cases."""

    def test_extracts_quality_deps(self, tmp_path: Path) -> None:
        """Verify extracts quality deps."""
        path = tmp_path / "pyproject.toml.jinja"
        path.write_text(
            "[dependency-groups]\n"
            "quality = [\n"
            '  "ruff>=0.14.2",\n'
            '  "ty>=0.0.1",\n'
            '  "pylint>=3.0",\n'
            '  "coverage>=7.0",\n'
            '  "pre-commit>=3.0",\n'
            "]\n",
            encoding="utf-8",
        )
        versions = parse_pyproject_jinja(path)
        assert versions["ruff"] == "0.14.2"
        assert versions["ty"] == "0.0.1"
        assert versions["pylint"] == "3.0"


@pytest.mark.unit
class TestParseMise:  # pylint: disable=too-few-public-methods
    """Test Parse Mise cases."""

    def test_extracts_tool_pins(self, tmp_path: Path) -> None:
        """Verify extracts tool pins."""
        path = tmp_path / ".mise.toml.jinja"
        path.write_text(
            '[tools]\npython = "3.12"\nnode = "20"\nuv = "0.4"\n',
            encoding="utf-8",
        )
        versions = parse_mise_toml(path)
        assert versions["python"] == "3.12"
        assert versions["node"] == "20"
        assert versions["uv"] == "0.4"


@pytest.mark.unit
class TestCompareVersions:
    """Test Compare Versions cases."""

    def test_mismatch_reports_error(self, tmp_path: Path) -> None:
        """Verify mismatch reports error."""
        source = VersionSource(file=tmp_path / "versions.sh", versions={"uv": "0.4"})
        other = VersionSource(file=tmp_path / "other.py", versions={"uv": "0.5"})
        errors = compare_versions(source, [other], "uv")
        assert len(errors) == 1
        assert "0.4" in errors[0]
        assert "0.5" in errors[0]

    def test_missing_on_other_is_skipped(self, tmp_path: Path) -> None:
        """Verify missing on other is skipped."""
        source = VersionSource(file=tmp_path / "versions.sh", versions={"uv": "0.4"})
        other = VersionSource(file=tmp_path / "other.py", versions={})
        assert compare_versions(source, [other], "uv") == []

    def test_match_is_clean(self, tmp_path: Path) -> None:
        """Verify match is clean."""
        source = VersionSource(file=tmp_path / "versions.sh", versions={"uv": "0.4"})
        other = VersionSource(file=tmp_path / "other.py", versions={"uv": "0.4"})
        assert compare_versions(source, [other], "uv") == []
