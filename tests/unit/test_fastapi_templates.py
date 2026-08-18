"""FastAPI template contracts: in-memory HTTP rate-limit middleware."""

from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

pytestmark = pytest.mark.unit

TEMPLATE_FILES = Path(__file__).resolve().parents[2] / "template" / "files"

RATE_LIMIT_REL = "python/src/{{ package_name }}/api/middleware/rate_limit.py.jinja"
API_TEMPLATE_RELS = (
    RATE_LIMIT_REL,
    "python/src/{{ package_name }}/api/middleware/__init__.py.jinja",
    "python/src/{{ package_name }}/api/main.py.jinja",
    "python/src/{{ package_name }}/api/config.py.jinja",
    "python/tests/api/test_rate_limit.py.jinja",
)


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_FILES),
        keep_trailing_newline=True,
    )


def _api_context(**overrides: object) -> dict[str, object]:
    ctx: dict[str, object] = {
        "project_name": "API Test",
        "project_slug": "api-test",
        "package_name": "api_test",
        "api_module": "enabled",
        "api_languages": ["python"],
        "api_features": [],
        "graphql_api_module": "disabled",
        "websocket_module": "disabled",
    }
    ctx.update(overrides)
    return ctx


def test_rate_limit_jinja_contains_http_contracts() -> None:
    text = (TEMPLATE_FILES / RATE_LIMIT_REL).read_text(encoding="utf-8")
    assert "RateLimitMiddleware" in text
    assert "429" in text
    assert "X-RateLimit-Limit" in text


def test_fastapi_rate_limit_templates_compile() -> None:
    env = _env()
    ctx = _api_context()
    for rel in API_TEMPLATE_RELS:
        rendered = env.get_template(rel).render(**ctx)
        compile(rendered, rel, "exec")


def test_rate_limit_disabled_render_compiles() -> None:
    rendered = (
        _env()
        .get_template(RATE_LIMIT_REL)
        .render(**_api_context(api_module="disabled", api_languages=[]))
    )
    compile(rendered, RATE_LIMIT_REL, "exec")
    assert "RateLimitMiddleware" not in rendered
