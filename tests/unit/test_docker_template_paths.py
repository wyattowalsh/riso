"""Generated container build paths, startup commands, and workspace dependencies."""

from __future__ import annotations

import json
import shlex
from pathlib import Path

import pytest
import yaml
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


def _assert_no_dest_root_copies(rendered: str) -> None:
    """Require an empty list of invalid COPY paths, with useful failure context."""
    illegal = _illegal_dest_root_copies(rendered)
    assert not illegal, f"Invalid destination-root COPY instructions: {illegal}"


def test_compose_without_service_tracks_emits_empty_mapping() -> None:
    """Desktop and stdio projects still produce a valid Compose document."""
    rendered = _render("docker-compose.yml.jinja", include_databases="no")

    assert yaml.safe_load(rendered)["services"] == {}


def test_python_api_copies_python_prefix_not_dest_root_src() -> None:
    """Python images copy the language track and install the API dependency group."""
    rendered = _render(
        ".docker/Dockerfile.jinja",
        api_module="enabled",
        api_languages=["python"],
    )
    assert "COPY python/pyproject.toml python/uv.lock ./" in rendered
    assert "COPY python/src/ ./src/" in rendered
    assert "uv sync --frozen --no-dev" in rendered
    assert "--group api_python" in rendered
    _assert_no_dest_root_copies(rendered)


def test_python_api_dev_dockerfile_uses_python_prefix() -> None:
    """Development images and mounts use the generated Python track paths."""
    rendered = _render(
        ".docker/Dockerfile.dev.jinja",
        api_module="enabled",
        api_languages=["python"],
    )
    assert "COPY --chown=1000:1000 python/pyproject.toml python/uv.lock ./" in rendered
    assert "./python/src:/app/src" in rendered
    assert "--group api_python" in rendered
    _assert_no_dest_root_copies(rendered)
    assert "./src:/app/src" not in rendered.replace("./python/src:/app/src", "")


def test_mcp_python_image_installs_and_launches_project_package() -> None:
    """MCP is installed in the copied venv, independently of the builder path."""
    rendered = _render(
        ".docker/Dockerfile.jinja",
        mcp_module="enabled",
        mcp_languages=["python"],
    )
    assert "COPY python/src/ ./src/" in rendered
    assert "COPY python/mcp/" not in rendered
    assert "/build/mcp /app/mcp" not in rendered
    assert "uv sync --frozen --no-dev --no-editable --group mcp" in rendered
    assert 'CMD ["python", "-m", "docker_path_test.mcp"]' in rendered
    assert "python -m docker_path_test.mcp --help" in rendered
    _assert_no_dest_root_copies(rendered)


def test_mcp_python_dev_image_uses_mounted_src_and_supported_command() -> None:
    """The MCP dev image launches mounted src with the existing log level setting."""
    rendered = _render(
        ".docker/Dockerfile.dev.jinja",
        mcp_module="enabled",
        mcp_languages=["python"],
    )
    assert "--group mcp --no-install-project" in rendered
    assert 'ENV PYTHONPATH="/app/src"' in rendered
    assert "ENV DOCKER_PATH_TEST_MCP_LOG_LEVEL=DEBUG" in rendered
    assert 'CMD ["python", "-m", "docker_path_test.mcp"]' in rendered
    assert "--log-level" not in rendered
    assert "./python/mcp:/app/mcp" not in rendered


@pytest.mark.parametrize("shared_logic", ["disabled", "enabled"])
def test_node_api_container_launches_the_deployed_package_entry(
    shared_logic: str,
) -> None:
    """The build context and runtime entry must match the emitted app package."""
    choices = {
        "api_module": "enabled",
        "api_languages": ["node"],
        "shared_logic": shared_logic,
    }
    rendered = _render(".docker/Dockerfile.jinja", **choices)
    dev = _render(".docker/Dockerfile.dev.jinja", **choices)
    package = json.loads(_render("node/apps/api-node/package.json.jinja", **choices))
    workspace = json.loads(_render("package.json.jinja", **choices))
    assert "COPY node/apps/api-node/package.json ./node/apps/api-node/" in rendered
    assert "COPY node/apps/ ./node/apps/" in rendered
    assert ("COPY node/shared-config/ ./node/shared-config/" in rendered) == (
        shared_logic == "enabled"
    )
    assert "COPY tsconfig.json ./" not in rendered
    assert "--prod deploy /out/api-node" in rendered
    assert "/out/api-node ./node/apps/api-node" in rendered
    assert f'CMD ["node", "node/apps/api-node/{package["main"]}"]' in rendered
    assert "COPY --chown=1000:1000 node/apps/api-node/ ./node/apps/api-node/" in dev
    assert (
        "COPY --chown=1000:1000 node/shared-config/ ./node/shared-config/" in dev
    ) == (shared_logic == "enabled")
    assert 'CMD ["pnpm", "--filter", "api-node", "dev"]' in dev
    assert "pnpm add -g" not in dev
    for image in (rendered, dev):
        assert f"corepack prepare {workspace['packageManager']} --activate" in image
        assert "USER 1000:1000" in image
        assert "addgroup -g 1000" not in image
    assert "**/node_modules/" in _render(".dockerignore.jinja", **choices).splitlines()
    _assert_no_dest_root_copies(rendered)
    _assert_no_dest_root_copies(dev)


@pytest.mark.parametrize(
    ("framework", "output_dir", "port", "single_page"),
    [("fumadocs", "out", "3001", []), ("docusaurus", "build", "3002", ["-s"])],
)
def test_docs_static_output_has_its_own_command_in_combined_compose(
    framework: str, output_dir: str, port: str, single_page: list[str]
) -> None:
    """Serve the generated docs assets when Fastify shares the same image."""
    docs = {
        "docs_module": "enabled",
        "docs_framework": framework,
        "docusaurus_openapi": "enabled",
    }
    output = f"node/docs/{framework}/{output_dir}"
    command = ["serve", *single_page, output, "-l", port]
    healthcheck = f"curl -f http://localhost:{port}/ || exit 1"
    runtime = _render(".docker/Dockerfile.jinja", **docs).split("AS runtime-node", 1)[1]
    assert f"/build/{output} ./{output}" in runtime
    assert f"CMD {json.dumps(command)}" in runtime
    assert healthcheck in runtime
    assert runtime.index("npm install -g serve@14.2.6") < runtime.index(
        "USER 1000:1000"
    )

    combined = {**docs, "api_module": "enabled", "api_languages": ["node"]}
    rendered = _render(".docker/Dockerfile.jinja", **combined)
    dev = _render(".docker/Dockerfile.dev.jinja", **combined)
    assert f"/build/{output}" in rendered
    assert "COPY node/docs/" in rendered
    assert f"node/docs/{framework}/ ./node/docs/{framework}/" in dev
    for image in (rendered, dev):
        assert ("--config.side-effects-cache=false" in image) == (
            framework == "docusaurus"
        )
    compose = yaml.safe_load(_render("docker-compose.yml.jinja", **combined))
    service = compose["services"][f"docs-{framework}"]
    assert service["build"]["target"] == "runtime-node"
    assert compose["services"]["api-node"]["build"]["target"] == "runtime-node"
    assert service["command"] == command
    assert service["healthcheck"]["test"] == ["CMD-SHELL", healthcheck]
    _assert_no_dest_root_copies(rendered)


def test_websocket_and_graphql_groups_when_enabled() -> None:
    """Include all dependency groups required by enabled Python modules."""
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


@pytest.mark.parametrize(
    ("runtime", "orm", "artifacts", "health"),
    [
        (
            "nextjs-16",
            "prisma",
            ["runtime/nextjs/.next", "runtime/nextjs/public"],
            "/api/health",
        ),
        (
            "remix-2",
            "drizzle",
            ["runtime/remix/build", "runtime/remix/public/build"],
            "/comparison",
        ),
    ],
)
def test_saas_image_carries_the_selected_build_and_launches_its_server(
    runtime: str, orm: str, artifacts: list[str], health: str
) -> None:
    """The runtime has the selected app's CLI, artifacts, and probe."""
    saas = {
        "saas_infra_module": "enabled",
        "saas_runtime": runtime,
        "saas_orm": orm,
        "saas_ui_framework": "shadcn-ui" if runtime == "nextjs-16" else "headless-ui",
    }
    rendered = _render(".docker/Dockerfile.jinja", **saas)
    package = json.loads(_render("node/saas/package.json.jinja", **saas))
    start = shlex.split(package["scripts"]["start"])
    start[0] = f"./node_modules/.bin/{start[0]}"

    assert "COPY node/saas/package.json ./node/saas/" in rendered
    assert "COPY node/saas/ ./node/saas/" in rendered
    assert "RUN pnpm --dir node/saas run build" in rendered
    assert "pnpm prune --prod" not in rendered
    assert "/build/node_modules ./node_modules" in rendered
    assert "/build/node/saas/node_modules ./node/saas/node_modules" in rendered
    assert "WORKDIR /app/node/saas" in rendered
    assert f"CMD {json.dumps(start)}" in rendered
    assert f"curl -f http://localhost:3000{health} || exit 1" in rendered
    for artifact in artifacts:
        assert f"/build/node/saas/{artifact} ./node/saas/{artifact}" in rendered

    schema = "COPY node/saas/integrations/orm/prisma/schema.prisma "
    remix_config = _render("node/saas/remix.config.js.jinja", **saas)
    if runtime == "nextjs-16":
        assert package["scripts"]["build"] == "next build runtime/nextjs"
        assert rendered.index(schema) < rendered.index("install --frozen-lockfile")
        assert "RUN mkdir -p node/saas/runtime/nextjs/public" in rendered
        assert "runtime/nextjs/next.config.js ./node/saas/runtime/nextjs/" in rendered
        assert "/build/node/saas/runtime/remix/" not in rendered
        assert remix_config == ""
        assert "isbot" not in package["dependencies"]
    else:
        assert package["scripts"]["build"] == "remix build"
        assert "isbot" in package["dependencies"]
        assert "appDirectory: 'runtime/remix/app'" in remix_config
        assert "serverBuildPath: 'runtime/remix/build/index.js'" in remix_config
        assert "assetsBuildDirectory: 'runtime/remix/public/build'" in remix_config
        assert schema not in rendered
        assert "/build/node/saas/runtime/nextjs/" not in rendered
    _assert_no_dest_root_copies(rendered)


@pytest.mark.parametrize("runtime", ["nextjs-16", "remix-2"])
@pytest.mark.parametrize("has_node_api", [False, True])
def test_saas_compose_starts_independently_of_docs_and_api(
    runtime: str, has_node_api: bool
) -> None:
    """Shared images run separate service commands with distinct host ports."""
    choices = {
        "saas_infra_module": "enabled",
        "saas_runtime": runtime,
        "saas_orm": "drizzle",
        "saas_auth_module": "enabled",
        "docs_module": "enabled",
        "docs_framework": "fumadocs",
        "api_module": "enabled" if has_node_api else "disabled",
        "api_languages": ["node"] if has_node_api else [],
    }
    services = yaml.safe_load(_render("docker-compose.yml.jinja", **choices))[
        "services"
    ]
    dockerfile = _render(".docker/Dockerfile.jinja", **choices)
    saas = services["saas"]
    docs = services["docs-fumadocs"]
    command = (
        ["./node_modules/.bin/next", "start", "runtime/nextjs"]
        if runtime == "nextjs-16"
        else ["./node_modules/.bin/remix-serve", "runtime/remix/build/index.js"]
    )
    health = "/api/health" if runtime == "nextjs-16" else "/comparison"
    host_port = 3003 if has_node_api else 3000
    assert saas["build"]["target"] == docs["build"]["target"] == "runtime-node"
    assert saas["working_dir"] == "/app/node/saas"
    assert saas["command"] == command
    assert saas["ports"] == [f"{host_port}:3000"]
    assert f"AUTH_URL=http://localhost:{host_port}" in saas["environment"]
    assert saas["healthcheck"]["test"] == [
        "CMD-SHELL",
        f"curl -f http://localhost:3000{health} || exit 1",
    ]
    assert docs["command"] == ["serve", "node/docs/fumadocs/out", "-l", "3001"]
    assert docs["ports"] == ["3001:3001"]
    if has_node_api:
        assert services["api-node"]["ports"] == ["3000:3000"]
        assert 'CMD ["node", "node/apps/api-node/dist/main.js"]' in dockerfile
    else:
        assert f"CMD {json.dumps(docs['command'])}" in dockerfile
