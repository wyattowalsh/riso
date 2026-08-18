"""Unit tests for generation_gates."""

from __future__ import annotations

from riso.core.generation_gates import (
    _collect_saas_selected,
    normalize_api_features,
    validate_answers_for_generation,
)


def test_removed_keys_block() -> None:
    result = validate_answers_for_generation({"saas_auth": "firebase"})
    assert result.ok is False
    assert any("saas_auth" in e for e in result.errors)


def test_remappable_keys_do_not_block() -> None:
    result = validate_answers_for_generation({"api_tracks": "python"})
    assert result.ok is True
    assert result.errors == ()


def test_saas_neon_supabase_storage_error() -> None:
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "supabase-storage",
        }
    )
    assert result.ok is False
    assert any("Neon" in e or "neon" in e.lower() for e in result.errors)


def test_saas_realtime_requires_supabase_db() -> None:
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_database": "neon",
            "saas_realtime": "supabase-realtime",
        }
    )
    assert result.ok is False
    assert any("Realtime" in e or "realtime" in e.lower() for e in result.errors)


def test_cli_module_empty_languages_errors() -> None:
    result = validate_answers_for_generation(
        {"cli_module": "enabled", "cli_languages": []}
    )
    assert result.ok is False
    assert any("cli_languages" in e for e in result.errors)


def test_cli_module_missing_languages_ok() -> None:
    """Absent languages key is non-blocking (defaults may apply later)."""
    result = validate_answers_for_generation({"cli_module": "enabled"})
    assert result.ok is True


def test_ok_when_languages_present() -> None:
    result = validate_answers_for_generation(
        {"cli_module": "enabled", "cli_languages": ["python"]}
    )
    assert result.ok is True
    assert result.errors == ()


def test_docs_module_does_not_require_docs_languages() -> None:
    result = validate_answers_for_generation(
        {"docs_module": "enabled", "docs_languages": []}
    )
    assert result.ok is True


def test_saas_billing_requires_auth_module() -> None:
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_billing_module": "enabled",
            "saas_auth_module": "disabled",
        }
    )
    assert result.ok is False
    assert any("saas_auth_module" in e for e in result.errors)


def test_saas_app_requires_auth_and_billing() -> None:
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_app_module": "enabled",
            "saas_auth_module": "enabled",
            "saas_billing_module": "disabled",
        }
    )
    assert result.ok is False
    assert any("saas_app_module" in e for e in result.errors)


def test_remix_authjs_is_illegal_combo() -> None:
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_runtime": "remix-2",
            "saas_auth_provider": "authjs",
        }
    )
    assert result.ok is False
    assert any("Remix" in e or "Auth.js" in e for e in result.errors)


def test_collect_saas_selected_does_not_read_saas_auth() -> None:
    selected = _collect_saas_selected(
        {
            "saas_auth": "SENTINEL_AUTH",
            "saas_auth_module": "enabled",
            "saas_auth_provider": "clerk",
        }
    )
    assert "SENTINEL_AUTH" not in selected
    assert "enabled" in selected
    assert "clerk" in selected


def test_leftover_saas_auth_still_rejected_as_removed_key() -> None:
    result = validate_answers_for_generation({"saas_auth": "firebase"})
    assert result.ok is False
    assert any("saas_auth" in e for e in result.errors)


def test_mapped_saas_auth_does_not_fail_closed() -> None:
    result = validate_answers_for_generation({"saas_auth": "clerk"})
    assert result.ok is True
    assert result.errors == ()


def test_saas_starter_module_remap_feeds_combo_gates() -> None:
    result = validate_answers_for_generation(
        {
            "saas_starter_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "supabase-storage",
        }
    )
    assert result.ok is False
    assert any("Neon" in e or "neon" in e.lower() for e in result.errors)


def test_normalize_api_features() -> None:
    assert normalize_api_features("none") == frozenset()
    assert normalize_api_features([]) == frozenset()
    assert normalize_api_features("graphql") == frozenset({"graphql"})
    assert normalize_api_features(["graphql", "websocket"]) == frozenset(
        {"graphql", "websocket"}
    )
    # Whole-token, not substring: "not-graphql" is its own token
    assert "graphql" not in normalize_api_features("not-graphql")
