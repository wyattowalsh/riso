"""Table tests for apply_removed_key_remaps operators."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from riso.core import (
    ANSWER_KEY_REMAPS,
    REMOVED_ANSWER_KEYS,
    RemapResult,
    apply_removed_key_remaps,
    reject_removed_answer_keys,
)
from riso.core.errors import ValidationFailedError

pytestmark = pytest.mark.unit

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "remap"


def _load_fixture(name: str) -> dict[str, Any]:
    raw = yaml.safe_load((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return raw


def _apply(answers: dict[str, Any]) -> RemapResult:
    return apply_removed_key_remaps(answers)


def _apply_then_reject(answers: dict[str, Any]) -> RemapResult:
    result = _apply(answers)
    reject_removed_answer_keys(result.answers)
    return result


@pytest.mark.parametrize(
    ("before", "expected_langs", "action"),
    [
        ("python", ["python"], "wrap-list"),
        ("node", ["node"], "wrap-list"),
        ("rust", ["rust"], "wrap-list"),
        ("go", ["go"], "wrap-list"),
        (["python"], ["python"], "wrap-list"),
        (["node", "go"], ["node", "go"], "wrap-list"),
    ],
)
def test_wrap_api_language(
    before: str | list[str], expected_langs: list[str], action: str
) -> None:
    result = _apply({"api_language": before})
    assert result.answers["api_languages"] == expected_langs
    assert "api_language" not in result.answers
    assert result.ops[0].action == action
    assert result.ops[0].old == "api_language"
    assert result.ops[0].new_keys == ("api_languages",)


@pytest.mark.parametrize(
    ("before", "expected_langs"),
    [
        ("python", ["python"]),
        ("typescript", ["typescript"]),
        ("rust", ["rust"]),
        ("go", ["go"]),
        ("node", ["typescript"]),
        ("js", ["typescript"]),
        (["python"], ["python"]),
        (["node", "go"], ["typescript", "go"]),
    ],
)
def test_wrap_mcp_language(before: str | list[str], expected_langs: list[str]) -> None:
    result = _apply({"mcp_language": before})
    assert result.answers["mcp_languages"] == expected_langs
    assert "mcp_language" not in result.answers
    assert result.ops[0].action == "wrap-list"
    assert result.ops[0].new_keys == ("mcp_languages",)


@pytest.mark.parametrize(
    ("before", "expected"),
    [
        ("", {"api_module": "disabled"}),
        ("none", {"api_module": "disabled"}),
        ("disabled", {"api_module": "disabled"}),
        ([], {"api_module": "disabled"}),
        ("python", {"api_module": "enabled", "api_languages": ["python"]}),
        ("python+node", {"api_module": "enabled", "api_languages": ["python", "node"]}),
        (
            "fastapi",
            {"api_module": "enabled", "api_languages": ["python"]},
        ),
        (
            "fastify",
            {"api_module": "enabled", "api_languages": ["node"]},
        ),
        (
            "actix",
            {"api_module": "enabled", "api_languages": ["rust"]},
        ),
        (
            ["python", "go"],
            {"api_module": "enabled", "api_languages": ["python", "go"]},
        ),
    ],
)
def test_derive_api_tracks(before: Any, expected: dict[str, Any]) -> None:
    result = _apply({"api_tracks": before})
    for key, value in expected.items():
        assert result.answers[key] == value
    assert "api_tracks" not in result.answers
    assert result.ops[0].action == "derive"
    assert result.ops[0].new_keys == ("api_module", "api_languages")


@pytest.mark.parametrize(
    ("before", "expected"),
    [
        ("none", {"docs_module": "disabled"}),
        ("false", {"docs_module": "disabled"}),
        ("disabled", {"docs_module": "disabled"}),
        ("off", {"docs_module": "disabled"}),
        (
            "sphinx",
            {"docs_module": "enabled", "docs_framework": "sphinx-shibuya"},
        ),
        (
            "sphinx-shibuya",
            {"docs_module": "enabled", "docs_framework": "sphinx-shibuya"},
        ),
        (
            "docusaurus",
            {"docs_module": "enabled", "docs_framework": "docusaurus"},
        ),
        (
            "fumadocs",
            {"docs_module": "enabled", "docs_framework": "fumadocs"},
        ),
    ],
)
def test_derive_docs_site(before: str, expected: dict[str, Any]) -> None:
    result = _apply({"docs_site": before})
    for key, value in expected.items():
        assert result.answers[key] == value
    assert "docs_site" not in result.answers
    assert result.ops[0].action == "derive"
    assert result.ops[0].new_keys == ("docs_module", "docs_framework")


@pytest.mark.parametrize(
    ("before", "expected"),
    [
        ("enabled", "enabled"),
        ("disabled", "disabled"),
        (True, "enabled"),
        (False, "disabled"),
    ],
)
def test_rename_saas_starter_module(before: Any, expected: str) -> None:
    result = _apply({"saas_starter_module": before})
    assert result.answers["saas_infra_module"] == expected
    assert "saas_starter_module" not in result.answers
    assert result.ops[0].action == "rename"
    assert result.ops[0].new_keys == ("saas_infra_module",)


@pytest.mark.parametrize(
    ("before", "expected"),
    [
        ("none", {"saas_auth_module": "disabled"}),
        ("disabled", {"saas_auth_module": "disabled"}),
        ("false", {"saas_auth_module": "disabled"}),
        ("off", {"saas_auth_module": "disabled"}),
        (
            "clerk",
            {"saas_auth_module": "enabled", "saas_auth_provider": "clerk"},
        ),
        (
            "authjs",
            {"saas_auth_module": "enabled", "saas_auth_provider": "authjs"},
        ),
    ],
)
def test_split_saas_auth(before: str, expected: dict[str, Any]) -> None:
    result = _apply({"saas_auth": before})
    for key, value in expected.items():
        assert result.answers[key] == value
    assert "saas_auth" not in result.answers
    assert result.ops[0].action == "split"
    assert result.ops[0].new_keys == ("saas_auth_module", "saas_auth_provider")


@pytest.mark.parametrize(
    ("before", "expected"),
    [
        ("none", {"saas_billing_module": "disabled"}),
        ("disabled", {"saas_billing_module": "disabled"}),
        ("false", {"saas_billing_module": "disabled"}),
        ("off", {"saas_billing_module": "disabled"}),
        (
            "stripe",
            {"saas_billing_module": "enabled", "saas_billing_provider": "stripe"},
        ),
        (
            "paddle",
            {"saas_billing_module": "enabled", "saas_billing_provider": "paddle"},
        ),
        (
            "lemonsqueezy",
            {
                "saas_billing_module": "enabled",
                "saas_billing_provider": "lemonsqueezy",
            },
        ),
    ],
)
def test_split_saas_billing(before: str, expected: dict[str, Any]) -> None:
    result = _apply({"saas_billing": before})
    for key, value in expected.items():
        assert result.answers[key] == value
    assert "saas_billing" not in result.answers
    assert result.ops[0].action == "split"
    assert result.ops[0].new_keys == (
        "saas_billing_module",
        "saas_billing_provider",
    )


@pytest.mark.parametrize(
    ("before", "expected"),
    [
        (True, True),
        (False, False),
        ("true", True),
        ("yes", True),
        ("false", False),
        ("off", False),
        (1, True),
        (0, False),
    ],
)
def test_rename_bool_include_admin(before: Any, expected: bool) -> None:
    result = _apply({"include_admin": before})
    assert result.answers["saas_admin_dashboard"] is expected
    assert "include_admin" not in result.answers
    assert result.ops[0].action == "rename-bool"
    assert result.ops[0].new_keys == ("saas_admin_dashboard",)


def test_remap_table_covers_removed_keys() -> None:
    assert set(ANSWER_KEY_REMAPS) == set(REMOVED_ANSWER_KEYS)
    assert len(ANSWER_KEY_REMAPS) == 8
    assert ANSWER_KEY_REMAPS["api_language"].action == "wrap-list"
    assert ANSWER_KEY_REMAPS["mcp_language"].action == "wrap-list"
    assert ANSWER_KEY_REMAPS["api_tracks"].action == "derive"
    assert ANSWER_KEY_REMAPS["docs_site"].action == "derive"
    assert ANSWER_KEY_REMAPS["saas_starter_module"].action == "rename"
    assert ANSWER_KEY_REMAPS["saas_auth"].action == "split"
    assert ANSWER_KEY_REMAPS["saas_billing"].action == "split"
    assert ANSWER_KEY_REMAPS["include_admin"].action == "rename-bool"


def test_apply_does_not_mutate_input() -> None:
    original = {"api_language": "python"}
    _apply(original)
    assert original == {"api_language": "python"}


def test_idempotent_second_apply_is_noop() -> None:
    first = _apply({"api_language": "python", "mcp_language": "node"})
    second = _apply(first.answers)
    assert second.answers == first.answers
    assert second.ops == ()


def test_wrap_api_language_unknown_sequence_token_fail_closed() -> None:
    result = _apply({"api_language": ["python", "fortran"]})
    assert result.ops == ()
    assert result.answers["api_language"] == ["python", "fortran"]
    with pytest.raises(ValidationFailedError):
        _apply_then_reject({"api_language": ["python", "fortran"]})


def test_do_not_overwrite_dest_wrap_list() -> None:
    result = _apply({"api_language": "python", "api_languages": ["go"]})
    assert result.answers["api_languages"] == ["go"]
    assert "api_language" not in result.answers


def test_lucia_saas_auth_fail_closes() -> None:
    from riso.core.answers import apply_then_reject_removed_keys
    from riso.core.errors import ValidationFailedError

    with pytest.raises(ValidationFailedError) as exc:
        apply_then_reject_removed_keys({"saas_auth": "lucia"})
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_do_not_overwrite_dest_split() -> None:
    result = _apply(
        {
            "saas_auth": "authjs",
            "saas_auth_module": "disabled",
            "saas_auth_provider": "clerk",
        }
    )
    assert result.answers["saas_auth_module"] == "disabled"
    assert result.answers["saas_auth_provider"] == "clerk"
    assert "saas_auth" not in result.answers


def test_do_not_overwrite_dest_derive() -> None:
    result = _apply(
        {
            "api_tracks": "node",
            "api_module": "disabled",
            "api_languages": ["rust"],
        }
    )
    assert result.answers["api_module"] == "disabled"
    assert result.answers["api_languages"] == ["rust"]
    assert "api_tracks" not in result.answers


def test_unmapped_value_left_for_reject() -> None:
    result = _apply({"saas_auth": "firebase"})
    assert result.answers["saas_auth"] == "firebase"
    assert result.ops == ()
    with pytest.raises(ValidationFailedError) as exc:
        reject_removed_answer_keys(result.answers)
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])
    assert any("saas_auth_module" in err for err in exc.value.data["errors"])


def test_unknown_leftover_raises_after_apply() -> None:
    leftover = _load_fixture("leftover.yml")
    with pytest.raises(ValidationFailedError) as exc:
        _apply_then_reject(leftover)
    assert exc.value.data is not None
    assert any("saas_auth" in err for err in exc.value.data["errors"])


def test_fixture_api_language() -> None:
    result = _apply_then_reject(_load_fixture("api_language.yml"))
    assert result.answers["api_languages"] == ["python"]
    assert "api_language" not in result.answers


def test_fixture_mcp_language_node_to_typescript() -> None:
    result = _apply_then_reject(_load_fixture("mcp_language.yml"))
    assert result.answers["mcp_languages"] == ["typescript"]
    assert "mcp_language" not in result.answers


def test_fixture_api_tracks() -> None:
    result = _apply_then_reject(_load_fixture("api_tracks.yml"))
    assert result.answers["api_module"] == "enabled"
    assert result.answers["api_languages"] == ["python", "node"]
    assert "api_tracks" not in result.answers


def test_fixture_docs_site() -> None:
    result = _apply_then_reject(_load_fixture("docs_site.yml"))
    assert result.answers["docs_module"] == "enabled"
    assert result.answers["docs_framework"] == "sphinx-shibuya"
    assert "docs_site" not in result.answers


def test_fixture_saas_starter_module() -> None:
    result = _apply_then_reject(_load_fixture("saas_starter_module.yml"))
    assert result.answers["saas_infra_module"] == "enabled"
    assert "saas_starter_module" not in result.answers


def test_fixture_saas_auth() -> None:
    result = _apply_then_reject(_load_fixture("saas_auth.yml"))
    assert result.answers["saas_auth_module"] == "enabled"
    assert result.answers["saas_auth_provider"] == "clerk"
    assert "saas_auth" not in result.answers


def test_fixture_saas_billing() -> None:
    result = _apply_then_reject(_load_fixture("saas_billing.yml"))
    assert result.answers["saas_billing_module"] == "enabled"
    assert result.answers["saas_billing_provider"] == "stripe"
    assert "saas_billing" not in result.answers


def test_fixture_include_admin() -> None:
    result = _apply_then_reject(_load_fixture("include_admin.yml"))
    assert result.answers["saas_admin_dashboard"] is True
    assert "include_admin" not in result.answers


def test_fixture_mixed() -> None:
    result = _apply_then_reject(_load_fixture("mixed.yml"))
    assert result.answers["api_module"] == "enabled"
    assert result.answers["api_languages"] == ["python", "go"]
    assert result.answers["mcp_languages"] == ["typescript"]
    assert result.answers["docs_module"] == "enabled"
    assert result.answers["docs_framework"] == "docusaurus"
    assert result.answers["saas_infra_module"] == "enabled"
    assert result.answers["saas_auth_module"] == "enabled"
    assert result.answers["saas_auth_provider"] == "authjs"
    assert result.answers["saas_billing_module"] == "enabled"
    assert result.answers["saas_billing_provider"] == "lemonsqueezy"
    assert result.answers["saas_admin_dashboard"] is False
    assert set(result.answers).isdisjoint(REMOVED_ANSWER_KEYS)


def test_fixture_already_canonical_is_noop() -> None:
    original = _load_fixture("already_canonical.yml")
    result = _apply_then_reject(original)
    assert result.answers == original
    assert result.ops == ()
