"""Tests for scripts/ci/check_removed_key_ssot.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from check_removed_key_ssot import (
    CANONICAL_OPS,
    EXPECTED_KEYS,
    check_answer_schema_removed_keys,
    check_surface,
    check_v2_remap_ssot,
    compare_three_way,
    load_answer_schema_forbidden_keys,
    load_core,
    load_scripts_fallback,
    load_ts,
    load_v2,
    parse_v2_remap_keys,
    scan_sample_answers_for_removed_keys,
)


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


def test_repository_three_way_ssot_is_valid() -> None:
    core_keys, core_ops = load_core()
    lib_keys, lib_ops = load_scripts_fallback()
    ts_keys, ts_ops = load_ts()
    assert check_surface("core", core_keys, core_ops) == []
    assert check_surface("scripts.lib", lib_keys, lib_ops) == []
    assert check_surface("web TS", ts_keys, ts_ops) == []
    assert (
        compare_three_way(core_keys, core_ops, lib_keys, lib_ops, ts_keys, ts_ops) == []
    )
    assert tuple(core_keys) == EXPECTED_KEYS or set(core_keys) == set(EXPECTED_KEYS)
    assert dict(core_ops) == CANONICAL_OPS


def test_check_surface_reports_fixture_drift() -> None:
    keys = {key: "x" for key in EXPECTED_KEYS}
    keys.pop("include_admin")
    keys["extra_key"] = "nope"
    ops = dict(CANONICAL_OPS)
    errors = check_surface("fixture", keys, ops)
    assert errors
    assert any("missing" in item or "drift" in item for item in errors)


def test_sample_answers_have_no_removed_keys() -> None:
    assert scan_sample_answers_for_removed_keys() == []


def test_answer_schema_forbids_all_eight_removed_keys() -> None:
    keys = load_answer_schema_forbidden_keys()
    assert set(keys) == set(EXPECTED_KEYS)
    assert check_answer_schema_removed_keys() == []


def test_check_answer_schema_removed_keys_reports_drift() -> None:
    incomplete = [key for key in EXPECTED_KEYS if key != "include_admin"]
    errors = check_answer_schema_removed_keys(incomplete)
    assert errors
    assert any("include_admin" in item for item in errors)


def test_sample_scan_detects_leftover_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys

    samples = tmp_path / "samples"
    leftover = samples / "legacy" / "copier-answers.yml"
    leftover.parent.mkdir(parents=True)
    leftover.write_text("project_name: Demo\napi_tracks: python\n", encoding="utf-8")
    scripts_dir = str(Path(__file__).resolve().parents[3] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import lib.paths as lib_paths

    monkeypatch.setattr(lib_paths, "samples_dir", lambda: samples)
    errors = scan_sample_answers_for_removed_keys()
    assert any("api_tracks" in item for item in errors)
    assert (
        yaml.safe_load(leftover.read_text(encoding="utf-8"))["api_tracks"] == "python"
    )


def test_repository_v2_remap_keys_match_removed_answer_keys() -> None:
    core_keys, _core_ops = load_core()
    v2_ops = load_v2()
    assert check_v2_remap_ssot(v2_ops, core_keys) == []
    assert set(v2_ops) == set(EXPECTED_KEYS)
    assert dict(v2_ops) == CANONICAL_OPS


def test_parse_v2_remap_keys_normalizes_string_and_list_dest() -> None:
    text = """
remap:
  copier_migrations: false
  keys:
    api_language:
      operator: wrap-list
      dest: api_languages
    api_tracks:
      operator: derive
      dest: [api_module, api_languages]
"""
    parsed = parse_v2_remap_keys(text)
    assert parsed["api_language"] == (
        "api_language",
        ("api_languages",),
        "wrap-list",
    )
    assert parsed["api_tracks"] == (
        "api_tracks",
        ("api_module", "api_languages"),
        "derive",
    )


def test_parse_v2_remap_keys_strips_jinja_before_yaml() -> None:
    text = """
{# comment #}
remap:
  keys:
    include_admin:
      operator: rename-bool
      dest: saas_admin_dashboard
"""
    parsed = parse_v2_remap_keys(text)
    assert parsed["include_admin"][2] == "rename-bool"


def test_check_v2_remap_ssot_reports_key_drift() -> None:
    keys = {key: "x" for key in EXPECTED_KEYS}
    ops = dict(CANONICAL_OPS)
    ops.pop("include_admin")
    errors = check_v2_remap_ssot(ops, keys)
    assert errors
    assert any("missing" in item or "remap.keys" in item for item in errors)


def test_parse_v2_remap_keys_rejects_missing_operator() -> None:
    snippet = "remap:\n  keys:\n    api_language:\n      dest: api_languages\n"
    with pytest.raises(ValueError, match="operator"):
        parse_v2_remap_keys(snippet)
