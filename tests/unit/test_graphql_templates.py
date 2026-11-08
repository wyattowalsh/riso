"""GraphQL template contracts for imports and schema validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

pytestmark = pytest.mark.unit

TEMPLATE_FILES = Path(__file__).resolve().parents[2] / "template" / "files"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_FILES),
        keep_trailing_newline=True,
    )


def _graphql_context() -> dict[str, object]:
    return {
        "project_name": "GraphQL Test",
        "project_slug": "graphql-test",
        "package_name": "graphql_test",
        "api_module": "enabled",
        "api_languages": ["python"],
        "api_features": ["graphql"],
        "graphql_api_module": "enabled",
        "websocket_module": "disabled",
    }


def test_graphql_runtime_does_not_import_sqlalchemy() -> None:
    """SQLAlchemy session wiring is deferred until spec 017."""
    files = (
        "python/src/{{ package_name }}/graphql_api/main.py.jinja",
        "python/src/{{ package_name }}/graphql_api/dataloaders.py.jinja",
        "python/src/{{ package_name }}/graphql_api/context.py.jinja",
    )
    env = _env()
    ctx = _graphql_context()
    for rel in files:
        text = (TEMPLATE_FILES / rel).read_text(encoding="utf-8")
        assert "sqlalchemy" not in text.lower()
        rendered = env.get_template(rel).render(**ctx)
        assert "sqlalchemy" not in rendered.lower()
        compile(rendered, rel, "exec")


def test_schema_attaches_complexity_validators() -> None:
    """Attach both query depth and complexity validation extensions."""
    rendered = (
        _env()
        .get_template("python/src/{{ package_name }}/graphql_api/schema.py.jinja")
        .render(**_graphql_context())
    )
    assert "AddValidationRules" in rendered
    assert "QueryLimitsValidator" in rendered
    assert "extensions=" in rendered
