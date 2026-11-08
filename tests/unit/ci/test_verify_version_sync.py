"""Unit tests for scripts/ci/verify_version_sync.py parsers and comparison."""

from __future__ import annotations

from pathlib import Path

import pytest

from verify_version_sync import (
    VersionSource,
    compare_versions,
    compare_lane,
    generated_package_profiles,
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
    """Check the selected value and do not read engines from a disabled branch."""
    path = tmp_path / "package.json.jinja"
    path.write_text(
        '{% if node_enabled %}\n{"engines":{"node":"{{ node_range }}"},'
        '"packageManager":"pnpm@9.15.0"}\n{% endif %}',
        encoding="utf-8",
    )
    assert parse_package_json(
        path, context={"node_enabled": True, "node_range": "^22.22.0 || >=24.0.0"}
    ) == {"node": "^22.22.0 || >=24.0.0", "pnpm": "9.15.0"}
    assert parse_package_json(path, context={"node_enabled": False}) == {}


def test_generated_version_check_rejects_missing_engine_in_one_profile(tmp_path):
    """A valid first branch must not mask a broken generated desktop profile."""
    path = tmp_path / "package.json.jinja"
    path.write_text(
        '{"packageManager":"pnpm@9.15.0"'
        '{% if desktop_module == "disabled" %},"engines":{"node":">=22.0.0"}'
        "{% endif %}}",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing runtime declarations"):
        generated_package_profiles(path)


@pytest.mark.unit
class TestNormalizeVersion:  # pylint: disable=too-few-public-methods
    """Test Normalize Version cases."""

    def test_strips_whitespace(self) -> None:
        """Verify strips whitespace."""
        assert normalize_version("  0.14.2  ") == "0.14.2"

    def test_strips_ge_operator(self) -> None:
        """Verify strips ge operator."""
        assert normalize_version(">=22.13.0") == "22.13.0"

    def test_strips_package_manager_prefix(self) -> None:
        """Verify strips package manager prefix."""
        assert normalize_version("pnpm@11.11.0") == "11.11.0"


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

    def test_ignores_unrelated_string_tuples(self, tmp_path: Path) -> None:
        """Verify ignores unrelated string tuples."""
        path = tmp_path / "pre_gen.py"
        path.write_text(
            'for key in ("COPIER_ANSWERS", "COPIER_JINJA2_CONTEXT"):\n    pass\n',
            encoding="utf-8",
        )
        assert parse_pre_gen_project(path) == {}


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

    def test_extracts_tool_pins_from_mise_toml_jinja(self, tmp_path: Path) -> None:
        """Verify extracts tool pins from mise toml jinja."""
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

    def test_node_major_prefix_is_clean(self, tmp_path: Path) -> None:
        """Verify node major prefix is clean."""
        source = VersionSource(
            file=tmp_path / "versions.sh", versions={"node": "22.13.0"}
        )
        other = VersionSource(
            file=tmp_path / ".mise.toml", versions={"node": "22.23.1"}
        )
        assert compare_versions(source, [other], "node") == []


@pytest.mark.unit
class TestVersionsCompatible:
    """Verify Test Versions Compatible."""

    def test_node_major_prefix_matches_patch_pins(self) -> None:
        """Verify node major prefix matches patch pins."""
        assert versions_compatible("22", "22.13.0", "node")
        assert versions_compatible("22.13.0", "22.23.1", "node")
        assert versions_compatible(">=22.13.0", "22.23.1", "node")

    def test_generated_node_20_is_not_maintainer_22(self) -> None:
        """Verify generated node 20 is not maintainer 22."""
        assert not versions_compatible("20", "22", "node")
        assert not versions_compatible("20.0.0", "22.13.0", "node")

    def test_dotted_prefix_for_uv(self) -> None:
        """Verify dotted prefix for uv."""
        assert versions_compatible("0.11", "0.11.26", "uv")
        assert not versions_compatible("0.4.30", "0.11.26", "uv")


@pytest.mark.unit
class TestParsePackageJson:
    """Verify Test Parse Package Json."""

    def test_extracts_engines_and_package_manager(self, tmp_path: Path) -> None:
        """Verify extracts engines and package manager."""
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
        """Verify parses jinja wrapped generated package json."""
        path = tmp_path / "package.json.jinja"
        path.write_text(
            '{% if true %}\n{\n  "engines": {\n    "node": ">=20.0.0",\n'
            '    "pnpm": ">=9.0.0"\n  },\n  "packageManager": "pnpm@9.15.0"\n}\n{% endif %}\n',
            encoding="utf-8",
        )
        versions = parse_package_json(path)
        assert versions["node"] == ">=20.0.0"
        assert versions["pnpm"] == "9.15.0"


# Pytest groups this behavior in a focused test class.
@pytest.mark.unit
class TestCompareLane:  # pylint: disable=too-few-public-methods
    """Verify Test Compare Lane."""

    def test_does_not_cross_compare_generated_and_maintainer_node(
        self, tmp_path: Path
    ) -> None:
        """Verify does not cross compare generated and maintainer node."""
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


# Pytest groups this behavior in a focused test class.
@pytest.mark.unit
class TestMainRepoLanes:  # pylint: disable=too-few-public-methods
    """Verify Test Main Repo Lanes."""

    def test_repo_dual_lane_sync_exits_zero(self) -> None:
        """Verify repo dual lane sync exits zero."""
        assert main() == 0
