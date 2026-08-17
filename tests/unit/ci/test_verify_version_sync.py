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
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestNormalizeVersion:
    def test_strips_whitespace(self) -> None:
        assert normalize_version("  0.14.2  ") == "0.14.2"


@pytest.mark.unit
class TestParseVersionsSh:
    def test_extracts_export_constants(self, tmp_path: Path) -> None:
        path = tmp_path / "versions.sh"
        path.write_text(
            '\nexport PYTHON_MIN_VERSION="3.11"\nexport UV_MIN_VERSION="0.4"\n',
            encoding="utf-8",
        )
        versions = parse_versions_sh(path)
        assert versions["python"] == "3.11"
        assert versions["uv"] == "0.4"


@pytest.mark.unit
class TestParsePreGen:
    def test_extracts_tool_matrix_tuples(self, tmp_path: Path) -> None:
        path = tmp_path / "pre_gen.py"
        path.write_text(
            'tool_matrix = [\n    ("uv", "0.4", "uv@0.4"),\n    ("node", "20", "node@20"),\n]\n',
            encoding="utf-8",
        )
        versions = parse_pre_gen_project(path)
        assert versions["uv"] == "0.4"
        assert versions["node"] == "20"


@pytest.mark.unit
class TestParsePyprojectJinja:
    def test_extracts_quality_deps(self, tmp_path: Path) -> None:
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
class TestParseMise:
    def test_extracts_tool_pins(self, tmp_path: Path) -> None:
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
    def test_mismatch_reports_error(self, tmp_path: Path) -> None:
        source = VersionSource(file=tmp_path / "versions.sh", versions={"uv": "0.4"})
        other = VersionSource(file=tmp_path / "other.py", versions={"uv": "0.5"})
        errors = compare_versions(source, [other], "uv")
        assert len(errors) == 1
        assert "0.4" in errors[0]
        assert "0.5" in errors[0]

    def test_missing_on_other_is_skipped(self, tmp_path: Path) -> None:
        source = VersionSource(file=tmp_path / "versions.sh", versions={"uv": "0.4"})
        other = VersionSource(file=tmp_path / "other.py", versions={})
        assert compare_versions(source, [other], "uv") == []

    def test_match_is_clean(self, tmp_path: Path) -> None:
        source = VersionSource(file=tmp_path / "versions.sh", versions={"uv": "0.4"})
        other = VersionSource(file=tmp_path / "other.py", versions={"uv": "0.4"})
        assert compare_versions(source, [other], "uv") == []
