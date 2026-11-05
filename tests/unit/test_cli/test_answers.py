"""Tests for removed answer key enforcement."""

from __future__ import annotations

import pytest

from riso.core.answers import (
    REMOVED_ANSWER_KEYS,
    apply_then_reject_removed_keys,
    prepare_copier_data,
    reject_removed_answer_keys,
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
