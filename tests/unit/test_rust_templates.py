"""Tests for Rust API template security contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("jinja2")

pytestmark = pytest.mark.unit


def _render(relative: str, **context: object) -> str:
    from jinja2 import Environment, FileSystemLoader

    path = Path(__file__).parents[2] / "template" / "files" / "rust" / relative
    env = Environment(loader=FileSystemLoader(str(path.parent)))
    return env.get_template(path.name).render(**context)


class TestRustApiCors:
    """Production CORS must use CORS_ORIGINS, never allow_any_origin."""

    def test_main_has_no_allow_any_origin(self) -> None:
        """actix-cors must not call allow_any_origin."""
        rendered = _render(
            "api/main.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
            project_name="Test API",
        )
        assert ".allow_any_origin(" not in rendered
        assert "CORS_ORIGINS" in rendered or "cors_origins" in rendered
        assert "allowed_origin" in rendered
        assert "is_production" in rendered

    def test_config_parses_cors_origins_env(self) -> None:
        """Config reads comma-separated CORS_ORIGINS and rejects *."""
        rendered = _render(
            "api/config.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
        )
        assert 'env::var("CORS_ORIGINS")' in rendered
        assert "parse_cors_origins" in rendered
        assert '*origin != "*"' in rendered
        assert "cors_origins: Vec<String>" in rendered


class TestRustPayloadHonesty:
    """Dest CI must not go green on empty API tests; uptime 0 is a labeled stub."""

    def test_api_integration_has_no_dummy_pass_or_todo_macro(self) -> None:
        """Integration tests are ignored EXTENSION POINTs, not assert!(true)."""
        rendered = _render(
            "tests/api_integration_test.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
            package_name="test_api",
        )
        assert "EXTENSION POINT" in rendered
        assert "#[ignore" in rendered
        code_lines = [line.split("//", 1)[0] for line in rendered.splitlines()]
        joined = "\n".join(code_lines)
        assert "assert!(true)" not in joined
        assert "todo!()" not in joined

    def test_health_uptime_stub_is_extension_point(self) -> None:
        """Health uptime stays 0 and is labeled EXTENSION POINT, not todo!()."""
        rendered = _render(
            "api/models/health.rs.jinja",
            api_module="enabled",
            api_languages=["rust"],
        )
        assert "uptime: 0" in rendered
        assert "EXTENSION POINT" in rendered
        assert "TODO:" not in rendered
        code_lines = [line.split("//", 1)[0] for line in rendered.splitlines()]
        assert "todo!()" not in "\n".join(code_lines)
