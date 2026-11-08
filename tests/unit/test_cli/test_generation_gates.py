"""Unit tests for generation_gates."""

from __future__ import annotations

import pytest

from riso.core.generation_gates import (
    _collect_saas_selected,
    normalize_api_features,
    validate_answers_for_generation,
)


def test_removed_keys_block() -> None:
    """Unmapped historical answers remain blocking after remapping."""
    result = validate_answers_for_generation({"saas_auth": "firebase"})
    assert result.ok is False
    assert any("saas_auth" in e for e in result.errors)


def test_remappable_keys_do_not_block() -> None:
    """Known API keys become accepted canonical answers before gating."""
    result = validate_answers_for_generation({"api_tracks": "python"})
    assert result.ok is True
    assert result.errors == ()


def test_saas_neon_supabase_storage_error() -> None:
    """Selected database and storage providers must be compatible."""
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
    """Supabase Realtime requires its matching database provider."""
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
    """Explicitly empty CLI language selections fail closed."""
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
    """A supported nonempty CLI language selection passes."""
    result = validate_answers_for_generation(
        {"cli_module": "enabled", "cli_languages": ["python"]}
    )
    assert result.ok is True
    assert result.errors == ()


def test_docs_module_does_not_require_docs_languages() -> None:
    """Docs frameworks do not require an unrelated language selection."""
    result = validate_answers_for_generation(
        {"docs_module": "enabled", "docs_languages": []}
    )
    assert result.ok is True


@pytest.mark.parametrize(
    ("overrides", "blocked"),
    [
        ({"package_name": "mcp", "mcp_languages": ["python"]}, True),
        ({"project_name": "MCP"}, True),
        ({"project_slug": "mcp", "mcp_languages": ["go", "python"]}, True),
        ({"project_name": "MCP", "package_name": "example_service"}, False),
        ({"package_name": "mcp", "mcp_languages": ["go"]}, False),
        ({"package_name": "mcp", "mcp_module": "disabled"}, False),
    ],
)
def test_python_mcp_rejects_names_that_shadow_its_sdk(overrides, blocked) -> None:
    """Explicit and derived names conflict only when the Python SDK is selected."""
    result = validate_answers_for_generation({"mcp_module": "enabled", **overrides})
    assert result.ok is not blocked
    assert (
        any("reserved by the Python MCP SDK" in error for error in result.errors)
        is blocked
    )


def test_saas_billing_requires_auth_module() -> None:
    """Billing cannot be enabled without authentication."""
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
    """The application module requires both authentication and billing."""
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
    """Enabled Auth.js rejects its unsupported Remix runtime."""
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_runtime": "remix-2",
            "saas_auth_provider": "authjs",
            "saas_auth_module": "enabled",
        }
    )
    assert result.ok is False
    assert any("Remix" in e or "Auth.js" in e for e in result.errors)


def test_remix_ignores_dormant_authjs_provider_when_auth_is_disabled() -> None:
    """A disabled auth module does not activate its remembered provider choice."""
    result = validate_answers_for_generation(
        {
            "saas_infra_module": "enabled",
            "saas_runtime": "remix-2",
            "saas_auth_module": "disabled",
            "saas_auth_provider": "authjs",
        }
    )
    assert result.ok


@pytest.mark.parametrize(
    ("infra", "auth", "runtime", "valid"),
    [
        ("enabled", "enabled", "nextjs-16", True),
        ("enabled", "disabled", "nextjs-16", False),
        ("enabled", "enabled", "remix-2", False),
        ("enabled", "disabled", "remix-2", False),
        ("disabled", "disabled", "remix-2", True),
    ],
)
def test_uploadthing_requires_authenticated_nextjs_runtime(
    infra: str, auth: str, runtime: str, valid: bool
) -> None:
    """Only active Uploadthing selections enforce their implemented prerequisites."""
    result = validate_answers_for_generation(
        {
            "saas_infra_module": infra,
            "saas_file_upload": "uploadthing",
            "saas_auth_module": auth,
            "saas_runtime": runtime,
            "saas_auth_provider": "clerk",
        }
    )
    assert result.ok is valid
    if not valid:
        assert any("Uploadthing" in message for message in result.errors)


def test_collect_saas_selected_does_not_read_saas_auth() -> None:
    """SaaS selection discovery reads canonical auth fields only."""
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
    """An unsupported historical auth provider retains the removed-key error."""
    result = validate_answers_for_generation({"saas_auth": "firebase"})
    assert result.ok is False
    assert any("saas_auth" in e for e in result.errors)


def test_mapped_saas_auth_does_not_fail_closed() -> None:
    """The known Clerk auth remap remains accepted."""
    result = validate_answers_for_generation({"saas_auth": "clerk"})
    assert result.ok is True
    assert result.errors == ()


def test_saas_starter_module_remap_feeds_combo_gates() -> None:
    """Starter-module remaps still participate in provider combination checks."""
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
    """Feature parsing compares whole tokens and recognizes disabled values."""
    assert normalize_api_features("none") == frozenset()
    assert normalize_api_features([]) == frozenset()
    assert normalize_api_features("graphql") == frozenset({"graphql"})
    assert normalize_api_features(["graphql", "websocket"]) == frozenset(
        {"graphql", "websocket"}
    )
    # Whole-token, not substring: "not-graphql" is its own token
    assert "graphql" not in normalize_api_features("not-graphql")
