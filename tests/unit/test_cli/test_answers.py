"""Tests for removed answer key enforcement."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.answers import (
    REMOVED_ANSWER_KEYS,
    apply_then_reject_removed_keys,
    dump_answers_file,
    load_answers_file,
    persist_remapped_answers,
    prepare_copier_data,
    reject_removed_answer_keys,
    strip_empty_lists_for_copier,
)
from riso.core.errors import ValidationFailedError


def test_reject_removed_keys() -> None:
    """Leftover removed keys are rejected by the fail-closed boundary."""
    with pytest.raises(ValidationFailedError) as exc:
        reject_removed_answer_keys({"api_tracks": "python"})
    assert exc.value.data is not None
    assert any("api_tracks" in err for err in exc.value.data["errors"])


def test_removed_keys_sync_count() -> None:
    """The migration contract contains exactly the eight reviewed old keys."""
    assert len(REMOVED_ANSWER_KEYS) == 8


def test_prepare_copier_data_preserves_explicit_empty_lists_for_validation() -> None:
    """Explicit empty lists reach validation instead of selecting defaults."""
    cleaned = prepare_copier_data({"project_name": "x", "api_features": []})
    assert isinstance(cleaned["api_features"], list)
    assert not cleaned["api_features"]
    assert cleaned["project_name"] == "x"


def test_apply_then_reject_remaps_known_key() -> None:
    """A known old API key becomes canonical fields before rejection."""
    result = apply_then_reject_removed_keys({"api_tracks": "python"})
    assert result.answers["api_module"] == "enabled"
    assert result.answers["api_languages"] == ["python"]
    assert "api_tracks" not in result.answers


def test_apply_then_reject_leftover_raises() -> None:
    """An unsupported historical auth value remains rejected after remapping."""
    with pytest.raises(ValidationFailedError) as exc:
        apply_then_reject_removed_keys({"saas_auth": "firebase"})
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_strip_empty_lists_for_copier() -> None:
    """Only the final Copier boundary removes unsupported empty overrides."""
    stripped = strip_empty_lists_for_copier({"project_name": "x", "api_features": []})
    assert "api_features" not in stripped
    assert stripped["project_name"] == "x"


def test_prepare_copier_data_enables_modules_from_api_features() -> None:
    """Feature strings become token-safe lists and derived module switches."""
    prepared = prepare_copier_data({"api_features": "graphql,websocket"})
    assert prepared["graphql_api_module"] == "enabled"
    assert prepared["websocket_module"] == "enabled"
    assert prepared["api_features"] == ["graphql", "websocket"]


def test_prepare_copier_data_explicit_enabled_wins() -> None:
    """Explicit enabled module switches survive an otherwise empty token list."""
    prepared = prepare_copier_data(
        {"api_features": "none", "websocket_module": "enabled"}
    )
    assert prepared["websocket_module"] == "enabled"
    assert prepared["graphql_api_module"] == "disabled"


def test_persist_remapped_answers_merges_and_drops_removed_keys(
    tmp_path: Path,
) -> None:
    """Post-operation persistence preserves metadata while dropping removed keys."""
    dest = tmp_path / ".copier-answers.yml"
    dump_answers_file(
        dest,
        {
            "_src_path": "/tmp/template",
            "project_name": "Demo",
            "api_language": "python",
        },
    )
    persist_remapped_answers(
        dest,
        {"project_name": "Demo", "api_languages": ["python"]},
    )
    written = load_answers_file(dest)
    assert written["_src_path"] == "/tmp/template"
    assert written["api_languages"] == ["python"]
    assert "api_language" not in written
