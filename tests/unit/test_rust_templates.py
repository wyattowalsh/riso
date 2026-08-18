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
