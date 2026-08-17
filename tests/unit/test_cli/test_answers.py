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
    with pytest.raises(ValidationFailedError) as exc:
        reject_removed_answer_keys({"api_tracks": "python"})
    assert exc.value.data is not None
    assert any("api_tracks" in err for err in exc.value.data["errors"])


def test_removed_keys_sync_count() -> None:
    assert len(REMOVED_ANSWER_KEYS) == 8


def test_prepare_copier_data_strips_empty_lists() -> None:
    cleaned = prepare_copier_data({"project_name": "x", "api_features": []})
    assert "api_features" not in cleaned
    assert cleaned["project_name"] == "x"


def test_apply_then_reject_remaps_known_key() -> None:
    result = apply_then_reject_removed_keys({"api_tracks": "python"})
    assert result.answers["api_module"] == "enabled"
    assert result.answers["api_languages"] == ["python"]
    assert "api_tracks" not in result.answers


def test_apply_then_reject_leftover_raises() -> None:
    with pytest.raises(ValidationFailedError) as exc:
        apply_then_reject_removed_keys({"saas_auth": "firebase"})
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])
