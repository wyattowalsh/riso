"""Tests for SaaS template clients, analytics providers, and dest contracts."""

# pylint: disable=redefined-outer-name,import-outside-toplevel,too-few-public-methods

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytest.importorskip("jinja2")

pytestmark = pytest.mark.unit


@pytest.fixture
def saas_files_dir() -> Path:
    """Get the nested SaaS template directory."""
    return Path(__file__).parents[2] / "template" / "files" / "node" / "saas"


def _read(path: Path) -> str:
    """Read a template file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def _render(template_path: Path, **context: object) -> str:
    """Render a jinja template with the given context."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    return env.get_template(template_path.name).render(**context)


def _exports_symbol(text: str, name: str) -> bool:
    """Return True if TypeScript source has a named export of ``name``."""
    compact = "".join(text.split())
    return (
        f"export function {name}" in text
        or f"export const {name}" in text
        or f"export class {name}" in text
        or f"export{{{name}" in compact
    )


def _function_source(module_path: Path, name: str) -> str:
    """Return source text for a top-level function in a Python module."""
    text = _read(module_path)
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            segment = ast.get_source_segment(text, node)
            assert segment is not None, f"no source segment for {name}"
            return segment
    raise AssertionError(f"{name} not found in {module_path}")


class TestSaasDatabaseClient:
    """lib/database/client.ts.jinja is the import target for health/admin."""

    def test_client_template_exists(self, saas_files_dir: Path) -> None:
        """client.ts.jinja must exist under lib/database."""
        client = saas_files_dir / "lib" / "database" / "client.ts.jinja"
        assert client.is_file()

    def test_source_exports_db_or_prisma(self, saas_files_dir: Path) -> None:
        """Source template exports prisma and/or db."""
        text = _read(saas_files_dir / "lib" / "database" / "client.ts.jinja")
        assert "export { prisma }" in text or "export const prisma" in text
        assert "export const db" in text

    def test_prisma_render_exports_prisma(self, saas_files_dir: Path) -> None:
        """Prisma render exports prisma (db may alias it)."""
        rendered = _render(
            saas_files_dir / "lib" / "database" / "client.ts.jinja",
            saas_infra_module="enabled",
            saas_orm="prisma",
        )
        assert "export { prisma }" in rendered
        assert "PrismaClient" in rendered

    def test_drizzle_render_exports_db(self, saas_files_dir: Path) -> None:
        """Drizzle render exports db against the live schema path."""
        rendered = _render(
            saas_files_dir / "lib" / "database" / "client.ts.jinja",
            saas_infra_module="enabled",
            saas_orm="drizzle",
            saas_database="neon",
        )
        assert "export const db" in rendered
        assert "@/integrations/orm/drizzle/schema" in rendered
        assert "export { prisma }" not in rendered


class TestSaasAuthHelpers:
    """lib/auth/helpers.ts.jinja re-exports integrations/auth/helpers."""

    def test_helpers_template_exists(self, saas_files_dir: Path) -> None:
        """helpers.ts.jinja must exist under lib/auth."""
        helpers = saas_files_dir / "lib" / "auth" / "helpers.ts.jinja"
        assert helpers.is_file()

    def test_reexports_integrations_auth_helpers(self, saas_files_dir: Path) -> None:
        """Source re-exports the integrations auth helper barrel."""
        text = _read(saas_files_dir / "lib" / "auth" / "helpers.ts.jinja")
        assert "export * from '@/integrations/auth/helpers'" in text

    def test_rendered_reexport(self, saas_files_dir: Path) -> None:
        """Rendered helpers file is a barrel re-export."""
        rendered = _render(
            saas_files_dir / "lib" / "auth" / "helpers.ts.jinja",
            saas_infra_module="enabled",
            saas_auth_module="enabled",
        )
        assert "export * from '@/integrations/auth/helpers'" in rendered


class TestSaasNestedCiGone:
    """SaaS GHA lives at dest-root; nested workflow jinja is gone."""

    def test_nested_saas_workflows_are_gone(self, saas_files_dir: Path) -> None:
        """ci/database/e2e jinja must not ship under node/saas/.github."""
        workflows = saas_files_dir / ".github" / "workflows"
        assert not (workflows / "ci.yml.jinja").is_file()
        assert not (workflows / "database.yml.jinja").is_file()
        assert not (workflows / "e2e.yml.jinja").is_file()

    def test_auth_barrel_exists(self, saas_files_dir: Path) -> None:
        """Auth.js middleware imports @/lib/auth from lib/auth/index.ts."""
        barrel = saas_files_dir / "lib" / "auth" / "index.ts.jinja"
        assert barrel.is_file()
        text = _read(barrel)
        assert "@/integrations/auth/authjs/auth.config" in text


class TestSaasPosthogProvider:
    """lib/analytics/posthog-provider.tsx.jinja is the layout import target."""

    def test_provider_template_exists(self, saas_files_dir: Path) -> None:
        """posthog-provider.tsx.jinja must exist under lib/analytics."""
        provider = saas_files_dir / "lib" / "analytics" / "posthog-provider.tsx.jinja"
        assert provider.is_file()

    def test_source_exports_posthog_provider(self, saas_files_dir: Path) -> None:
        """Source template exports PostHogProvider."""
        text = _read(
            saas_files_dir / "lib" / "analytics" / "posthog-provider.tsx.jinja"
        )
        assert _exports_symbol(text, "PostHogProvider")

    def test_gated_on_posthog(self, saas_files_dir: Path) -> None:
        """Provider is Jinja-gated on saas_analytics == posthog."""
        path = saas_files_dir / "lib" / "analytics" / "posthog-provider.tsx.jinja"
        text = _read(path)
        assert (
            'saas_analytics == "posthog"' in text
            or "saas_analytics == 'posthog'" in text
        )
        enabled = _render(
            path,
            saas_infra_module="enabled",
            saas_runtime="nextjs-16",
            saas_app_module="enabled",
            saas_analytics="posthog",
        )
        assert _exports_symbol(enabled, "PostHogProvider")
        assert "posthog-js/react" in enabled
        app_off = _render(
            path,
            saas_infra_module="enabled",
            saas_runtime="nextjs-16",
            saas_app_module="disabled",
            saas_analytics="posthog",
        )
        assert _exports_symbol(app_off, "PostHogProvider")
        assert "posthog-js" not in app_off
        disabled = _render(
            path,
            saas_infra_module="enabled",
            saas_runtime="nextjs-16",
            saas_app_module="enabled",
            saas_analytics="amplitude",
        )
        assert "PostHogProvider" not in disabled


class TestSaasAmplitudeProvider:
    """lib/analytics/amplitude-provider.ts.jinja is the layout import target."""

    def test_provider_template_exists(self, saas_files_dir: Path) -> None:
        """amplitude-provider.ts.jinja must exist under lib/analytics."""
        provider = saas_files_dir / "lib" / "analytics" / "amplitude-provider.ts.jinja"
        assert provider.is_file()

    def test_source_exports_amplitude_provider(self, saas_files_dir: Path) -> None:
        """Source template exports AmplitudeProvider."""
        text = _read(
            saas_files_dir / "lib" / "analytics" / "amplitude-provider.ts.jinja"
        )
        assert _exports_symbol(text, "AmplitudeProvider")


class TestSaasThemeToggle:
    """components/theme-toggle.tsx.jinja is the dashboard import target."""

    def test_theme_toggle_template_exists(self, saas_files_dir: Path) -> None:
        """theme-toggle.tsx.jinja must exist under components."""
        toggle = saas_files_dir / "components" / "theme-toggle.tsx.jinja"
        assert toggle.is_file()

    def test_source_exports_theme_toggle(self, saas_files_dir: Path) -> None:
        """Source template exports ThemeToggle."""
        text = _read(saas_files_dir / "components" / "theme-toggle.tsx.jinja")
        assert _exports_symbol(text, "ThemeToggle")


_PRISMA_BASE = {
    "saas_infra_module": "enabled",
    "saas_orm": "prisma",
    "saas_database": "neon",
    "saas_billing_provider": "stripe",
    "saas_auth_provider": "authjs",
    "saas_api_access": "public-api",
    "saas_notifications": "none",
    "saas_onboarding": "none",
    "saas_enterprise_bridge": "none",
    "saas_rbac_system": "custom-permissions",
    "saas_waitlist": False,
    "saas_user_impersonation": False,
}


class TestSaasMultiTenancyLevelGate:
    """Enterprise isolation uses saas_multi_tenancy_level, not a second prompt."""

    def test_multi_tenant_and_admin_use_level_key(self, saas_files_dir: Path) -> None:
        """Jinja gates must use saas_multi_tenancy_level == enterprise."""
        roots = [
            saas_files_dir / "lib" / "multi-tenant",
            saas_files_dir / "runtime" / "nextjs" / "app" / "admin" / "tenants",
        ]
        jinja_files: list[Path] = []
        for root in roots:
            jinja_files.extend(root.glob("*.jinja"))
        assert jinja_files
        for path in jinja_files:
            text = _read(path)
            assert "saas_multi_tenancy ==" not in text, path
            assert "saas_multi_tenancy_level == 'enterprise'" in text, path


class TestPrismaOrgRelationsGated:
    """Organization FKs on SaaS models exist only for b2b-teams."""

    def test_b2c_omits_organization_fks(self, saas_files_dir: Path) -> None:
        """B2C schema has no Organization model or organizationId columns."""
        rendered = _render(
            saas_files_dir / "integrations" / "orm" / "prisma" / "schema.prisma.jinja",
            saas_tenancy_model="b2c-users",
            **_PRISMA_BASE,
        )
        assert "model Organization " not in rendered
        assert "organizationId" not in rendered
        assert "model Subscription" in rendered
        assert "model ApiKey" in rendered
        assert "model Role" in rendered

    def test_b2b_keeps_organization_fks(self, saas_files_dir: Path) -> None:
        """B2B schema keeps org FKs on Subscription, ApiKey, webhooks, audit, Role."""
        rendered = _render(
            saas_files_dir / "integrations" / "orm" / "prisma" / "schema.prisma.jinja",
            saas_tenancy_model="b2b-teams",
            **_PRISMA_BASE,
        )
        assert "model Organization " in rendered
        for model in ("Subscription", "ApiKey", "WebhookEndpoint", "AuditLog", "Role"):
            assert f"model {model}" in rendered
        assert "organizationId String?" in rendered


class TestSaasCloudflareNextConfig:
    """SaaS Next config must not static-export on Cloudflare."""

    def test_cloudflare_omits_static_export(self, saas_files_dir: Path) -> None:
        """Cloudflare render comments adapter requirement, no output export key."""
        rendered = _render(
            saas_files_dir / "runtime" / "nextjs" / "next.config.js.jinja",
            saas_infra_module="enabled",
            saas_runtime="nextjs-16",
            saas_hosting="cloudflare",
            saas_observability_sentry=False,
            saas_observability_otel=False,
            saas_auth_provider="clerk",
            saas_storage="none",
        )
        code_lines = [
            line for line in rendered.splitlines() if not line.strip().startswith("//")
        ]
        assert not any("output: 'export'" in line for line in code_lines)
        assert "Node or edge adapter" in rendered
        assert "static" in rendered.lower()
        assert "module.exports = nextConfig" in rendered


class TestRecopyIntegrationDest:
    """Recopy dry-run integration must preview official dest without Copier."""

    def test_recopy_dry_run_uses_official_dest_answers_preview(self) -> None:
        """test_recopy_dry_run_json stays on default dest and asserts answers preview."""
        module = Path(__file__).parents[1] / "integration" / "test_riso_cli.py"
        src = _function_source(module, "test_recopy_dry_run_json")
        assert "samples/default/render" in src
        assert 'preview_engine"] == "answers"' in src
        assert "timeout=60" in src
