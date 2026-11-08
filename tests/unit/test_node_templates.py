"""Tests for Node template contracts (docs + api-node)."""

# pylint: disable=redefined-outer-name,import-outside-toplevel,too-few-public-methods

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("jinja2")

pytestmark = pytest.mark.unit

NAMED_MERMAID_EXPORT = "export { mermaidThemeByColorMode }"
SIDEBAR_JS_REQUIRE = "require('./docs/api-reference/sidebar.js')"
STATIC_EXPORT = "output: 'export' as const"
FORCE_STATIC = "export const dynamic = 'force-static'"
NO_REVALIDATE = "export const revalidate = false"
FUMADOCS_ESLINT_FILENAME = (
    "{% if docs_module == 'enabled' and docs_framework == 'fumadocs' %}"
    "eslint.config.mjs{% endif %}.jinja"
)


@pytest.fixture
def template_dir() -> Path:
    """Get the template directory."""
    return Path(__file__).parents[2] / "template"


@pytest.fixture
def files_dir(template_dir: Path) -> Path:
    """Get the Copier files root (dest-root templates)."""
    return template_dir / "files"


@pytest.fixture
def node_files_dir(template_dir: Path) -> Path:
    """Get the Node template files directory."""
    return template_dir / "files" / "node"


def _read(path: Path) -> str:
    """Read a template file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def _render(template_path: Path, **context: object) -> str:
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    return env.get_template(template_path.name).render(**context)


def _jinja_hits(root: Path, needle: str) -> list[str]:
    """Return jinja paths under root whose text contains needle."""
    hits: list[str] = []
    for path in root.rglob("*.jinja"):
        if needle in _read(path):
            hits.append(str(path.relative_to(root)))
    return hits


def _dest_root_context(**overrides: object) -> dict[str, object]:
    """Minimal Copier context for dest-root package.json and CI templates."""
    ctx: dict[str, object] = {
        "project_slug": "test-project",
        "project_name": "Test Project",
        "package_name": "test_project",
        "project_layout": "monorepo",
        "quality_profile": "standard",
        "task_runner": "just",
        "ci_platform": "github-actions",
        "api_module": "disabled",
        "api_languages": [],
        "docs_module": "disabled",
        "docs_framework": "none",
        "mcp_module": "disabled",
        "mcp_languages": [],
        "saas_infra_module": "disabled",
        "desktop_module": "disabled",
        "changelog_module": "disabled",
        "cli_module": "disabled",
        "cli_languages": [],
    }
    ctx.update(overrides)
    return ctx


def _dest_root_scripts(files_dir: Path, **overrides: object) -> dict[str, str]:
    """Render dest-root package.json and return its scripts map."""
    rendered = _render(
        files_dir / "package.json.jinja",
        **_dest_root_context(**overrides),
    )
    data = json.loads(rendered)
    scripts = data["scripts"]
    assert isinstance(scripts, dict)
    return {str(key): str(value) for key, value in scripts.items()}


def _node_engine_major(spec: str) -> int:
    match = re.search(r">=\s*(\d+)", spec)
    assert match is not None, f"expected node engines >=N, got {spec!r}"
    return int(match.group(1))


class TestDocusaurusMermaidNamedExport:
    """Docusaurus mermaid token bag stays file-local (no named export)."""

    def test_docusaurus_config_exists(self, node_files_dir: Path) -> None:
        """docusaurus.config.ts.jinja should exist."""
        config = node_files_dir / "docs" / "docusaurus" / "docusaurus.config.ts.jinja"
        assert config.is_file()

    def test_mermaid_theme_bag_is_file_local(self, node_files_dir: Path) -> None:
        """mermaidThemeByColorMode is a file-local const, not a named export."""
        config = node_files_dir / "docs" / "docusaurus" / "docusaurus.config.ts.jinja"
        text = _read(config)
        assert "const mermaidThemeByColorMode =" in text
        assert NAMED_MERMAID_EXPORT not in text

    def test_named_mermaid_export_absent_from_docusaurus_templates(
        self, node_files_dir: Path
    ) -> None:
        """No docusaurus jinja file named-exports mermaidThemeByColorMode."""
        docusaurus_dir = node_files_dir / "docs" / "docusaurus"
        assert not _jinja_hits(docusaurus_dir, NAMED_MERMAID_EXPORT)

    def test_rendered_config_keeps_mermaid_bag_local(
        self, node_files_dir: Path
    ) -> None:
        """Rendered docusaurus config still has the bag and no named export."""
        config = node_files_dir / "docs" / "docusaurus" / "docusaurus.config.ts.jinja"
        rendered = _render(
            config,
            docs_module="enabled",
            docs_framework="docusaurus",
            docusaurus_mermaid="enabled",
            project_name="Test Project",
            project_slug="test-project",
        )
        assert "const mermaidThemeByColorMode =" in rendered
        assert NAMED_MERMAID_EXPORT not in rendered
        assert "export default config" in rendered


class TestDocusaurusSidebarJs:
    """OpenAPI sidebar.js require must stay deleted."""

    def test_sidebars_template_exists(self, node_files_dir: Path) -> None:
        """sidebars.ts.jinja should exist."""
        sidebars = node_files_dir / "docs" / "docusaurus" / "sidebars.ts.jinja"
        assert sidebars.is_file()

    def test_sidebar_js_require_absent_from_sidebars(
        self, node_files_dir: Path
    ) -> None:
        """sidebars.ts.jinja must not require the v4 sidebar.js path."""
        sidebars = node_files_dir / "docs" / "docusaurus" / "sidebars.ts.jinja"
        text = _read(sidebars)
        assert SIDEBAR_JS_REQUIRE not in text
        assert "dirName: 'api-reference'" in text

    def test_sidebar_js_require_absent_from_docusaurus_templates(
        self, node_files_dir: Path
    ) -> None:
        """No leftover sidebar.js require under docusaurus jinja."""
        docusaurus_dir = node_files_dir / "docs" / "docusaurus"
        assert not _jinja_hits(docusaurus_dir, SIDEBAR_JS_REQUIRE)

    def test_rendered_sidebars_omit_sidebar_js_require(
        self, node_files_dir: Path
    ) -> None:
        """Rendered sidebars keep the autogenerated api-reference category."""
        sidebars = node_files_dir / "docs" / "docusaurus" / "sidebars.ts.jinja"
        rendered = _render(
            sidebars,
            docs_module="enabled",
            docs_framework="docusaurus",
            docusaurus_openapi="enabled",
            api_module="enabled",
            api_languages=["node"],
            api_features=[],
            cli_module="disabled",
            graphql_api_module="disabled",
            websocket_module="disabled",
            mcp_module="disabled",
            project_name="Test Project",
            project_slug="test-project",
        )
        assert SIDEBAR_JS_REQUIRE not in rendered
        assert "dirName: 'api-reference'" in rendered


class TestDocusaurusTooling:
    """The generated Docusaurus commands have their required config files."""

    def test_typecheck_declares_shared_tsconfig(self, node_files_dir: Path) -> None:
        """The package declares the base settings referenced by its tsconfig."""
        docs = node_files_dir / "docs" / "docusaurus"
        context = _dest_root_context(docs_module="enabled", docs_framework="docusaurus")
        package = json.loads(_render(docs / "package.json.jinja", **context))
        config = json.loads(_render(docs / "tsconfig.json.jinja", **context))
        assert config["extends"] in package["devDependencies"]

    def test_flat_config_replaces_legacy_file(self, node_files_dir: Path) -> None:
        """The enabled docs package gets an ESLint 9 flat config filename."""
        from jinja2 import Environment

        docs = node_files_dir / "docs" / "docusaurus"
        assert not (docs / ".eslintrc.js.jinja").exists()
        configs = list(docs.glob("*eslint.config.mjs*.jinja"))
        assert len(configs) == 1
        name = Environment().from_string(configs[0].stem)
        assert name.render(docs_module="enabled", docs_framework="docusaurus") == (
            "eslint.config.mjs"
        )
        assert not name.render(docs_module="disabled", docs_framework="docusaurus")


class TestFumadocsLint:
    """Next 16 uses the ESLint CLI and a config emitted only for Fumadocs."""

    def test_package_uses_eslint_cli(self, node_files_dir: Path) -> None:
        """The lint script invokes the installed CLI instead of removed next lint."""
        rendered = _render(
            node_files_dir / "docs" / "fumadocs" / "package.json.jinja",
            **_dest_root_context(docs_module="enabled", docs_framework="fumadocs"),
        )
        package = json.loads(rendered)
        assert package["scripts"]["lint"] == "eslint ."
        assert "eslint" in package["devDependencies"]
        assert "eslint-config-next" in package["devDependencies"]

    @pytest.mark.parametrize(
        ("module", "framework", "expected"),
        [
            ("enabled", "fumadocs", "eslint.config.mjs"),
            ("disabled", "fumadocs", ""),
            ("enabled", "docusaurus", ""),
        ],
    )
    def test_flat_config_filename_omits_inactive_docs(
        self, node_files_dir: Path, module: str, framework: str, expected: str
    ) -> None:
        """Copier's empty-filename contract prevents inactive config artifacts."""
        from jinja2 import Environment

        path = node_files_dir / "docs" / "fumadocs" / FUMADOCS_ESLINT_FILENAME
        assert path.is_file()
        rendered_name = (
            Environment()
            .from_string(path.stem)
            .render(docs_module=module, docs_framework=framework)
        )
        assert rendered_name == expected

    def test_banner_store_preserves_ssr_and_dismissal(
        self, node_files_dir: Path
    ) -> None:
        """Banner storage stays hidden on SSR and cleans up dismissal listeners."""
        node = shutil.which("node")
        repository = node_files_dir.parents[2]
        compilers = [
            repository / "web/node_modules/typescript",
            repository
            / "samples/docs-fumadocs-full/render/node/docs/fumadocs/node_modules/typescript",
            repository
            / "samples/default/render/node/docs/fumadocs/node_modules/typescript",
        ]
        compiler = next((path for path in compilers if path.is_dir()), None)
        if node is None or compiler is None:
            pytest.skip("Node and an existing local TypeScript compiler are required")
        source = _render(
            node_files_dir / "docs/fumadocs/components/banner/index.tsx.jinja",
            docs_module="enabled",
            docs_framework="fumadocs",
            fumadocs_banner="enabled",
        )
        program = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require(process.argv[1]);
const source = fs.readFileSync(0, 'utf8');
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    jsx: ts.JsxEmit.ReactJSX,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText;
const exportsObject = {};
const storage = new Map();
let server = true;
let hook;
const react = {
  useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot) {
    hook = { subscribe, getSnapshot, getServerSnapshot };
    return server ? getServerSnapshot() : getSnapshot();
  },
};
const element = (type, props) => ({ type, props });
vm.runInNewContext(compiled, {
  exports: exportsObject,
  require(name) {
    if (name === 'react') return react;
    if (name === 'react/jsx-runtime') return { jsx: element, jsxs: element };
    throw new Error(`Unexpected import: ${name}`);
  },
  localStorage: {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
  },
});
const render = (id) => exportsObject.Banner({ id, children: 'Release' });
assert.equal(render('first'), null);
assert.equal(hook.getServerSnapshot(), true);
server = false;
const shown = render('first');
assert.notEqual(shown, null);
assert.equal(hook.getSnapshot(), false);
let notifications = 0;
const unsubscribe = hook.subscribe(() => { notifications += 1; });
shown.props.children[1].props.onClick();
assert.equal(storage.get('banner-first'), 'dismissed');
assert.equal(notifications, 1);
assert.equal(render('first'), null);
assert.notEqual(render('second'), null);
unsubscribe();
render('second').props.children[1].props.onClick();
assert.equal(notifications, 1);
"""
        result = subprocess.run(
            [node, "-e", program, str(compiler)],
            input=source,
            cwd=repository,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
            env={**os.environ, "MISE_AUTO_INSTALL": "false"},
        )
        assert result.returncode == 0, result.stderr or result.stdout


class TestFumadocsStaticExport:
    """Fumadocs static-export contracts (no middleware / rewrite path)."""

    def test_middleware_template_deleted(self, node_files_dir: Path) -> None:
        """fumadocs middleware.ts.jinja must not exist."""
        middleware = node_files_dir / "docs" / "fumadocs" / "middleware.ts.jinja"
        assert not middleware.exists()

    def test_next_config_output_export_as_const(self, node_files_dir: Path) -> None:
        """next.config.ts.jinja pins static export with `as const`."""
        next_config = node_files_dir / "docs" / "fumadocs" / "next.config.ts.jinja"
        text = _read(next_config)
        assert STATIC_EXPORT in text

    def test_rendered_next_config_output_export_as_const(
        self, node_files_dir: Path
    ) -> None:
        """Rendered Next config keeps `output: 'export' as const`."""
        next_config = node_files_dir / "docs" / "fumadocs" / "next.config.ts.jinja"
        rendered = _render(
            next_config,
            docs_module="enabled",
            docs_framework="fumadocs",
        )
        assert STATIC_EXPORT in rendered

    @pytest.mark.parametrize(
        "relative",
        [
            "docs/fumadocs/app/sitemap.ts.jinja",
            "docs/fumadocs/app/robots.ts.jinja",
        ],
    )
    def test_static_route_flags(self, node_files_dir: Path, relative: str) -> None:
        """sitemap and robots stay force-static with revalidate disabled."""
        text = _read(node_files_dir / relative)
        assert FORCE_STATIC in text
        assert NO_REVALIDATE in text

    @pytest.mark.parametrize(
        "relative",
        [
            "docs/fumadocs/app/sitemap.ts.jinja",
            "docs/fumadocs/app/robots.ts.jinja",
        ],
    )
    def test_rendered_static_route_flags(
        self, node_files_dir: Path, relative: str
    ) -> None:
        """Rendered sitemap and robots keep the static-export flags."""
        rendered = _render(
            node_files_dir / relative,
            docs_module="enabled",
            docs_framework="fumadocs",
            project_slug="test-project",
        )
        assert FORCE_STATIC in rendered
        assert NO_REVALIDATE in rendered

    def test_search_route_uses_requestless_static_get(
        self, node_files_dir: Path
    ) -> None:
        """Static export must not bind GET to a Request-reading handler."""
        text = _read(
            node_files_dir
            / "docs"
            / "fumadocs"
            / "app"
            / "api"
            / "search"
            / "route.ts.jinja"
        )
        assert "export const GET = search.staticGET" not in text
        assert "export async function GET()" in text
        assert "return staticGET()" in text


class TestApiNodePackage:
    """api-node package.json.jinja name, engines, and test/runtime deps."""

    def test_package_json_exists(self, node_files_dir: Path) -> None:
        """api-node package.json.jinja should exist."""
        package_json = node_files_dir / "apps" / "api-node" / "package.json.jinja"
        assert package_json.is_file()

    def test_package_json_name_engines_fastify_vitest(
        self, node_files_dir: Path
    ) -> None:
        """Rendered api-node package is named, node>=22, with fastify and vitest."""
        package_json = node_files_dir / "apps" / "api-node" / "package.json.jinja"
        rendered = _render(
            package_json,
            api_module="enabled",
            api_languages=["node"],
            project_name="Test Project",
        )
        data = json.loads(rendered)
        assert data["name"] == "api-node"
        node_engine = data["engines"]["node"]
        assert _node_engine_major(node_engine) >= 22
        assert "fastify" in data["dependencies"]
        assert "vitest" in data["devDependencies"]


class TestDocusaurusTailwindDeleted:
    """Docusaurus Tailwind v4 is CSS-first; the TS config must stay gone."""

    def test_tailwind_config_template_absent(self, node_files_dir: Path) -> None:
        """docs/docusaurus/tailwind.config.ts.jinja must not exist."""
        tailwind = node_files_dir / "docs" / "docusaurus" / "tailwind.config.ts.jinja"
        assert not tailwind.exists()


_API_NODE_TYPECHECK = "pnpm --filter api-node run typecheck"
_DEST_ROOT_TYPECHECK = "pnpm run typecheck"


class TestDestRootNodeTypecheckAliases:
    """Dest-root type-check / typecheck aliases delegate to api-node."""

    def test_node_api_scripts_alias_filter_api_node(self, files_dir: Path) -> None:
        """When Node API is on, both dest-root aliases filter api-node."""
        scripts = _dest_root_scripts(
            files_dir,
            api_module="enabled",
            api_languages=["node"],
        )
        assert scripts["type-check"] == _API_NODE_TYPECHECK
        assert scripts["typecheck"] == _API_NODE_TYPECHECK

    def test_docs_only_omits_dest_root_typecheck_aliases(self, files_dir: Path) -> None:
        """Docs-only dest-root package.json has no typecheck aliases."""
        scripts = _dest_root_scripts(
            files_dir,
            docs_module="enabled",
            docs_framework="fumadocs",
        )
        assert "type-check" not in scripts
        assert "typecheck" not in scripts


class TestRisoQualityNodeFilter:
    """GHA node-quality uses --filter api-node, not dest-root type-check."""

    def test_node_quality_source_uses_api_node_filter(self, files_dir: Path) -> None:
        """node-quality lint / typecheck / test must filter api-node."""
        text = _read(files_dir / ".github" / "workflows" / "riso-quality.yml.jinja")
        match = re.search(
            r"^  node-quality:.*?(?=^  \{\%)",
            text,
            re.M | re.S,
        )
        assert match is not None, "node-quality job missing"
        block = match.group(0)
        assert "pnpm --filter api-node run lint" in block
        assert "pnpm --filter api-node run typecheck" in block
        assert "pnpm --filter api-node test" in block
        assert "pnpm run type-check" not in block
        assert "pnpm run lint" not in block
        assert "pnpm test" not in block

    def test_rendered_node_quality_uses_api_node_filter(self, files_dir: Path) -> None:
        """Rendered node-quality job keeps the api-node filter commands."""
        rendered = _render(
            files_dir / ".github" / "workflows" / "riso-quality.yml.jinja",
            **_dest_root_context(
                ci_platform="github-actions",
                api_module="enabled",
                api_languages=["node"],
            ),
        )
        assert "pnpm --filter api-node run lint" in rendered
        assert "pnpm --filter api-node run typecheck" in rendered
        assert "pnpm --filter api-node test" in rendered
        assert "pnpm run type-check" not in rendered


class TestGitLabNodeTypecheckFilters:
    """GitLab Node jobs must not call dest-root typecheck unconditionally."""

    def test_source_omits_dest_root_typecheck(self, files_dir: Path) -> None:
        """gitlab-ci.yml.jinja must not invoke dest-root pnpm run typecheck."""
        text = _read(files_dir / ".gitlab" / ".gitlab-ci.yml.jinja")
        assert _DEST_ROOT_TYPECHECK not in text

    def test_fumadocs_only_does_not_call_dest_root_typecheck(
        self, files_dir: Path
    ) -> None:
        """Docs-only GitLab CI typechecks fumadocs, not dest-root scripts."""
        rendered = _render(
            files_dir / ".gitlab" / ".gitlab-ci.yml.jinja",
            **_dest_root_context(
                ci_platform="gitlab-ci",
                docs_module="enabled",
                docs_framework="fumadocs",
            ),
        )
        assert _DEST_ROOT_TYPECHECK not in rendered
        assert "pnpm --filter docs-fumadocs run typecheck" in rendered
        assert "pnpm --filter api-node" not in rendered

    def test_node_api_uses_api_node_typecheck_filter(self, files_dir: Path) -> None:
        """Node API GitLab lint uses --filter api-node typecheck."""
        rendered = _render(
            files_dir / ".gitlab" / ".gitlab-ci.yml.jinja",
            **_dest_root_context(
                ci_platform="gitlab-ci",
                api_module="enabled",
                api_languages=["node"],
            ),
        )
        assert _DEST_ROOT_TYPECHECK not in rendered
        assert "pnpm --filter api-node run typecheck" in rendered

    def test_saas_only_does_not_call_dest_root_typecheck(self, files_dir: Path) -> None:
        """SaaS-only GitLab CI typechecks node/saas, not dest-root scripts."""
        rendered = _render(
            files_dir / ".gitlab" / ".gitlab-ci.yml.jinja",
            **_dest_root_context(
                ci_platform="gitlab-ci",
                saas_infra_module="enabled",
            ),
        )
        assert _DEST_ROOT_TYPECHECK not in rendered
        assert "pnpm --dir node/saas run typecheck" in rendered
        assert "pnpm --filter api-node" not in rendered


class TestDestRootWorkspaces:
    """Dest-root package.json / pnpm-workspace list electron, tauri, saas."""

    def test_saas_listed_in_package_json_workspaces(self, files_dir: Path) -> None:
        """SaaS-enabled dest-root package.json includes node/saas."""
        rendered = _render(
            files_dir / "package.json.jinja",
            **_dest_root_context(saas_infra_module="enabled"),
        )
        data = json.loads(rendered)
        assert "node/saas" in data["workspaces"]

    def test_electron_listed_when_desktop_electron(self, files_dir: Path) -> None:
        """Electron desktop is a workspace member, not implied under node/*."""
        rendered = _render(
            files_dir / "package.json.jinja",
            **_dest_root_context(
                desktop_module="enabled",
                desktop_framework="electron-vite",
            ),
        )
        data = json.loads(rendered)
        assert "electron" in data["workspaces"]
        assert "tauri" not in data["workspaces"]

    def test_tauri_listed_when_desktop_tauri(self, files_dir: Path) -> None:
        """Tauri desktop is a workspace member at dest-root tauri/."""
        rendered = _render(
            files_dir / "package.json.jinja",
            **_dest_root_context(
                desktop_module="enabled",
                desktop_framework="tauri",
            ),
        )
        data = json.loads(rendered)
        assert "tauri" in data["workspaces"]
        assert "electron" not in data["workspaces"]

    def test_pnpm_workspace_includes_desktop_and_saas(self, files_dir: Path) -> None:
        """pnpm-workspace.yaml keeps node/saas and adds electron when enabled."""
        rendered = _render(
            files_dir / "pnpm-workspace.yaml.jinja",
            mcp_module="enabled",
            mcp_languages=["typescript"],
            saas_infra_module="enabled",
            desktop_module="enabled",
            desktop_framework="electron-vite",
        )
        assert '  - "node/saas"' in rendered
        assert '  - "electron"' in rendered
        assert '  - "tauri"' not in rendered


class TestDestLayoutDockerAndMise:
    """Dest layout prefixes (python/, node/, rust/) and canonical mise.toml."""

    def test_dockerfile_copies_track_prefixes(self, files_dir: Path) -> None:
        """Production Dockerfile copies python/, node/{apps,docs,saas}, rust/."""
        text = _read(files_dir / ".docker" / "Dockerfile.jinja")
        assert "COPY python/pyproject.toml python/uv.lock ./" in text
        assert "COPY python/src/" in text
        assert "COPY node/apps/" in text
        assert "COPY node/docs/" in text
        assert "COPY node/saas/" in text
        assert "COPY rust/src/" in text
        copy_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("COPY ") and "COPY --from=" not in line
        ]
        assert not any(line.startswith("COPY src/") for line in copy_lines)
        assert not any(line.startswith("COPY apps/") for line in copy_lines)

    def test_canonical_mise_toml_not_dotted(self, files_dir: Path) -> None:
        """Dest mise config is mise.toml.jinja with Node 22; .mise.toml.jinja is gone."""
        assert not (files_dir / ".mise.toml.jinja").exists()
        mise = files_dir / "mise.toml.jinja"
        assert mise.is_file()
        text = _read(mise)
        assert 'node = "22"' in text

    def test_generated_docs_state_node_22_floor(self, files_dir: Path) -> None:
        """Live generated prose must not still claim a Node 20 floor."""
        agents = _read(files_dir / "AGENTS.md.jinja")
        assert "Node **22**" in agents
        assert "Node **20**" not in agents
        assert "Node.js**: 22 LTS" in agents
        design = _read(files_dir / "DESIGN.md.jinja")
        assert "Node **22**" in design
        assert "Node **20**" not in design
        prompt_ref = _read(files_dir / "docs" / "modules" / "prompt-reference.md.jinja")
        assert "Node **22**" in prompt_ref
        assert "Node **20**" not in prompt_ref
        upgrade = _read(files_dir / "docs" / "upgrade-guide.md.jinja")
        assert "| Node | `22` |" in upgrade
        assert "Generated Node floor is **22**" in upgrade
        dockerfile = _read(files_dir / ".docker" / "Dockerfile.jinja")
        assert "FROM node:22-alpine" in dockerfile
        assert "FROM node:20-alpine" not in dockerfile
        versions = _read(files_dir / "scripts" / "setup" / "lib" / "versions.sh.jinja")
        assert 'NODE_MIN_VERSION="22"' in versions


class TestNodeMcpHttpPolicy:
    """HTTP example emission retains HTTPS-only, manual-redirect defaults."""

    def test_example_http_tools_require_https_and_manual_redirects(
        self, node_files_dir: Path
    ) -> None:
        """The emitted client disallows HTTP and automatic redirect following."""
        rendered = _render(
            node_files_dir / "mcp" / "src" / "tools" / "http-fetch.ts.jinja",
            mcp_module="enabled",
            mcp_languages=["typescript"],
            mcp_example_tools=True,
        )
        assert "only https:// URLs are allowed" in rendered
        assert 'redirect: "manual"' in rendered
