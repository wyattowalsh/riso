"""Tests for scripts/ci/check_removed_key_ssot.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from check_removed_key_ssot import (
    CANONICAL_OPS,
    EXPECTED_KEYS,
    check_surface,
    compare_three_way,
    load_core,
    load_scripts_fallback,
    load_ts,
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
