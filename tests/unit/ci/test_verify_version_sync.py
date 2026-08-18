"""Unit tests for scripts/ci/verify_version_sync.py parsers and comparison."""

from __future__ import annotations

from pathlib import Path

import pytest

from verify_version_sync import (
    VersionSource,
    compare_lane,
    compare_versions,
    main,
    normalize_version,
    parse_mise_toml,
    parse_package_json,
    parse_pre_gen_project,
    parse_versions_sh,
    versions_compatible,
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestNormalizeVersion:
    def test_strips_whitespace(self) -> None:
        assert normalize_version("  0.14.2  ") == "0.14.2"

    def test_strips_ge_operator(self) -> None:
        assert normalize_version(">=22.13.0") == "22.13.0"

    def test_strips_package_manager_prefix(self) -> None:
        assert normalize_version("pnpm@11.11.0") == "11.11.0"


@pytest.mark.unit
class TestVersionsCompatible:
    def test_node_major_prefix_matches_patch_pins(self) -> None:
        assert versions_compatible("22", "22.13.0", "node")
        assert versions_compatible("22.13.0", "22.23.1", "node")
        assert versions_compatible(">=22.13.0", "22.23.1", "node")

    def test_generated_node_20_is_not_maintainer_22(self) -> None:
        assert not versions_compatible("20", "22", "node")
        assert not versions_compatible("20.0.0", "22.13.0", "node")

    def test_dotted_prefix_for_uv(self) -> None:
        assert versions_compatible("0.11", "0.11.26", "uv")
        assert not versions_compatible("0.4.30", "0.11.26", "uv")


@pytest.mark.unit
class TestParseVersionsSh:
    def test_extracts_export_constants(self, tmp_path: Path) -> None:
        path = tmp_path / "versions.sh"
        path.write_text(
            '\nexport PYTHON_MIN_VERSION="3.11"\nexport UV_MIN_VERSION="0.11.26"\n',
            encoding="utf-8",
        )
        versions = parse_versions_sh(path)
        assert versions["python"] == "3.11"
        assert versions["uv"] == "0.11.26"


@pytest.mark.unit
class TestParsePreGen:
    def test_extracts_tool_matrix_tuples(self, tmp_path: Path) -> None:
        path = tmp_path / "pre_gen.py"
        path.write_text(
            'tool_matrix = [\n    ("uv", "0.11.26", "uv@0.11.26"),\n    ("node", "22", "node@22"),\n]\n',
            encoding="utf-8",
        )
        versions = parse_pre_gen_project(path)
        assert versions["uv"] == "0.11.26"
        assert versions["node"] == "22"

    def test_ignores_unrelated_string_tuples(self, tmp_path: Path) -> None:
        path = tmp_path / "pre_gen.py"
        path.write_text(
            'for key in ("COPIER_ANSWERS", "COPIER_JINJA2_CONTEXT"):\n    pass\n',
            encoding="utf-8",
        )
        assert parse_pre_gen_project(path) == {}


@pytest.mark.unit
class TestParseMise:
    def test_extracts_tool_pins_from_mise_toml_jinja(self, tmp_path: Path) -> None:
        path = tmp_path / "mise.toml.jinja"
        path.write_text(
            '[tools]\npython = "3.11"\nnode = "20"\nuv = "0.4.30"\n',
            encoding="utf-8",
        )
        versions = parse_mise_toml(path)
        assert versions["python"] == "3.11"
        assert versions["node"] == "20"
        assert versions["uv"] == "0.4.30"


@pytest.mark.unit
class TestParsePackageJson:
    def test_extracts_engines_and_package_manager(self, tmp_path: Path) -> None:
        path = tmp_path / "package.json"
        path.write_text(
            '{"engines":{"node":">=22.13.0","pnpm":">=11.11.0"},'
            '"packageManager":"pnpm@11.11.0"}',
            encoding="utf-8",
        )
        versions = parse_package_json(path)
        assert versions["node"] == ">=22.13.0"
        assert versions["pnpm"] == "11.11.0"

    def test_parses_jinja_wrapped_generated_package_json(self, tmp_path: Path) -> None:
        path = tmp_path / "package.json.jinja"
        path.write_text(
            '{% if true %}\n{\n  "engines": {\n    "node": ">=20.0.0",\n'
            '    "pnpm": ">=9.0.0"\n  },\n  "packageManager": "pnpm@9.15.0"\n}\n{% endif %}\n',
            encoding="utf-8",
        )
        versions = parse_package_json(path)
        assert versions["node"] == ">=20.0.0"
        assert versions["pnpm"] == "9.15.0"


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

    def test_node_major_prefix_is_clean(self, tmp_path: Path) -> None:
        source = VersionSource(
            file=tmp_path / "versions.sh", versions={"node": "22.13.0"}
        )
        other = VersionSource(
            file=tmp_path / ".mise.toml", versions={"node": "22.23.1"}
        )
        assert compare_versions(source, [other], "node") == []


@pytest.mark.unit
class TestCompareLane:
    def test_does_not_cross_compare_generated_and_maintainer_node(
        self, tmp_path: Path
    ) -> None:
        maintainer = [
            VersionSource(file=tmp_path / "versions.sh", versions={"node": "22.13.0"}),
            VersionSource(file=tmp_path / ".mise.toml", versions={"node": "22.23.1"}),
        ]
        generated = [
            VersionSource(file=tmp_path / "mise.toml.jinja", versions={"node": "20"}),
            VersionSource(
                file=tmp_path / "package.json.jinja", versions={"node": ">=20.0.0"}
            ),
        ]
        assert compare_lane("maintainer", maintainer) == []
        assert compare_lane("generated", generated) == []
        crossed = compare_versions(maintainer[0], generated, "node")
        assert crossed


@pytest.mark.unit
class TestMainRepoLanes:
    def test_repo_dual_lane_sync_exits_zero(self) -> None:
        assert main() == 0
