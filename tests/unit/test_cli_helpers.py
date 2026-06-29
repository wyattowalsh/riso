"""Unit tests for riso.cli.helpers."""

from __future__ import annotations

import pytest

from riso.cli.helpers import parse_data_pairs

pytestmark = pytest.mark.unit


def test_parse_data_pairs_empty() -> None:
    assert parse_data_pairs(None) == {}
    assert parse_data_pairs([]) == {}


def test_parse_data_pairs_basic() -> None:
    result = parse_data_pairs(["project_name=demo", "count=3"])
    assert result == {"project_name": "demo", "count": 3}


def test_parse_data_pairs_coerces_bool_and_int() -> None:
    result = parse_data_pairs(["flag=true", "enabled=no", "size=42", "ratio=1.5"])
    assert result["flag"] is True
    assert result["enabled"] is False
    assert result["size"] == 42
    assert result["ratio"] == 1.5


def test_parse_data_pairs_rejects_invalid_pair() -> None:
    with pytest.raises(ValueError, match="expected key=value"):
        parse_data_pairs(["not-a-pair"])

    with pytest.raises(ValueError, match="empty key"):
        parse_data_pairs(["=value"])
