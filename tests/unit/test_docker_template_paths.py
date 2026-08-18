"""Dest-layout COPY paths, uv groups, and Docusaurus serve-before-USER in Dockerfiles."""

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


def _base_context(**overrides: object) -> dict[str, object]:
    context: dict[str, object] = {
        "project_name": "Docker Path Test",
        "project_slug": "docker-path-test",
        "package_name": "docker_path_test",
        "project_layout": "monorepo",
        "ci_platform": "github-actions",
        "cli_module": "disabled",
        "cli_languages": [],
        "api_module": "disabled",
        "api_languages": [],
        "api_features": [],
        "mcp_module": "disabled",
        "mcp_languages": [],
        "docs_module": "disabled",
        "docs_framework": "none",
        "saas_infra_module": "disabled",
        "codegen_module": "disabled",
        "graphql_api_module": "disabled",
        "websocket_module": "disabled",
        "shared_logic": "disabled",
    }
    context.update(overrides)
    return context


def _render(name: str, **overrides: object) -> str:
    return _env().get_template(name).render(**_base_context(**overrides))


def _illegal_dest_root_copies(rendered: str) -> list[str]:
    """COPY instructions that pull dest-root src/ or apps/ (not python/src or node/apps)."""
    illegal: list[str] = []
    for line in rendered.splitlines():
        stripped = line.strip()
        if stripped.startswith("COPY src/") or stripped.startswith("COPY apps/"):
            illegal.append(stripped)
        if stripped.startswith("COPY --chown=1000:1000 src/") or stripped.startswith(
            "COPY --chown=1000:1000 apps/"
        ):
            illegal.append(stripped)
    return illegal


def test_python_api_copies_python_prefix_not_dest_root_src() -> None:
    rendered = _render(
        ".docker/Dockerfile.jinja",
        api_module="enabled",
        api_languages=["python"],
    )
    assert "COPY python/pyproject.toml python/uv.lock ./" in rendered
    assert "COPY python/src/ ./src/" in rendered
    assert "uv sync --frozen --no-dev" in rendered
    assert "--group api_python" in rendered
    assert _illegal_dest_root_copies(rendered) == []


def test_python_api_dev_dockerfile_uses_python_prefix() -> None:
    rendered = _render(
        ".docker/Dockerfile.dev.jinja",
        api_module="enabled",
        api_languages=["python"],
    )
    assert "COPY --chown=1000:1000 python/pyproject.toml python/uv.lock ./" in rendered
    assert "./python/src:/app/src" in rendered
    assert "--group api_python" in rendered
    assert _illegal_dest_root_copies(rendered) == []
    assert "./src:/app/src" not in rendered.replace("./python/src:/app/src", "")


def test_mcp_python_copies_mcp_package_and_uses_python_m_mcp() -> None:
    rendered = _render(
        ".docker/Dockerfile.jinja",
        mcp_module="enabled",
        mcp_languages=["python"],
    )
    assert "COPY python/mcp/ ./mcp/" in rendered
    assert 'CMD ["python", "-m", "mcp"]' in rendered
    assert "--group mcp" in rendered
    assert "docker_path_test.mcp" not in rendered
    assert _illegal_dest_root_copies(rendered) == []


def test_node_api_copies_node_apps_not_dest_root_apps() -> None:
    rendered = _render(
        ".docker/Dockerfile.jinja",
        api_module="enabled",
        api_languages=["node"],
        project_layout="monorepo",
    )
    assert "COPY node/apps/api-node/package.json ./node/apps/api-node/" in rendered
    assert "COPY node/apps/ ./node/apps/" in rendered
    assert 'CMD ["node", "node/apps/api-node/dist/main.js"]' in rendered
    assert _illegal_dest_root_copies(rendered) == []


def test_docusaurus_installs_serve_before_user() -> None:
    rendered = _render(
        ".docker/Dockerfile.jinja",
        docs_module="enabled",
        docs_framework="docusaurus",
    )
    assert "AS runtime-node" in rendered
    node_runtime = rendered.split("AS runtime-node", 1)[1]
    serve_at = node_runtime.find("npm install -g serve")
    user_at = node_runtime.find("USER 1000:1000")
    assert serve_at >= 0
    assert user_at >= 0
    assert serve_at < user_at
    assert 'CMD ["serve", "-s", "node/docs/docusaurus/build", "-l", "3002"]' in rendered
    assert "COPY node/docs/" in rendered
    assert _illegal_dest_root_copies(rendered) == []


def test_websocket_and_graphql_groups_when_enabled() -> None:
    rendered = _render(
        ".docker/Dockerfile.jinja",
        api_module="enabled",
        api_languages=["python"],
        api_features=["websocket", "graphql"],
        websocket_module="enabled",
        graphql_api_module="enabled",
        cli_module="enabled",
        cli_languages=["python"],
        codegen_module="enabled",
    )
    assert "--group api_python" in rendered
    assert "--group websocket" in rendered
    assert "--group graphql_api" in rendered
    assert "--group cli" in rendered
    assert "--group codegen" in rendered


def test_saas_copies_node_saas_not_apps_saas() -> None:
    rendered = _render(
        ".docker/Dockerfile.jinja",
        saas_infra_module="enabled",
    )
    assert "COPY node/saas/package.json ./node/saas/" in rendered
    assert "COPY node/saas/ ./node/saas/" in rendered
    assert _illegal_dest_root_copies(rendered) == []
