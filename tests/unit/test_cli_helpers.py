"""Unit tests for riso.cli.helpers."""

from __future__ import annotations

import pytest

from riso.cli.helpers import parse_data_pairs

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("pairs, expected", [(None, {}), ([], {})])
def test_parse_data_pairs_empty(
    pairs: list[str] | None, expected: dict[str, object]
) -> None:
    """Treat absent or empty CLI data overrides as an empty mapping."""
    assert parse_data_pairs(pairs) == expected


def test_parse_data_pairs_basic() -> None:
    """Parse named CLI overrides and coerce numeric values."""
    result = parse_data_pairs(["project_name=demo", "count=3"])
    assert result == {"project_name": "demo", "count": 3}


def test_parse_data_pairs_coerces_bool_and_int() -> None:
    """Coerce YAML boolean, integer, and floating-point override values."""
    result = parse_data_pairs(["flag=true", "enabled=no", "size=42", "ratio=1.5"])
    assert result["flag"] is True
    assert result["enabled"] is False
    assert result["size"] == 42
    assert result["ratio"] == 1.5


def test_parse_data_pairs_yaml_lists() -> None:
    """Parse list-valued language overrides without splitting their items."""
    result = parse_data_pairs(
        ["api_languages=[python]", "mcp_languages=['typescript', 'go']"]
    )
    assert result["api_languages"] == ["python"]
    assert result["mcp_languages"] == ["typescript", "go"]


def test_parse_data_pairs_rejects_invalid_pair() -> None:
    """Reject overrides without an assignment or with an empty key."""
    with pytest.raises(ValueError, match="expected key=value"):
        parse_data_pairs(["not-a-pair"])

    with pytest.raises(ValueError, match="empty key"):
        parse_data_pairs(["=value"])
