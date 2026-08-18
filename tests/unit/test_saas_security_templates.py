"""Banned-pattern and security contracts for node/saas templates."""

# pylint: disable=too-few-public-methods

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("jinja2")

pytestmark = pytest.mark.unit

SAAS_ROOT = Path(__file__).parents[2] / "template" / "files" / "node" / "saas"


def _read(path: Path) -> str:
    """Read a template file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def _jinja_hits(root: Path, needle: str) -> list[str]:
    """Return jinja paths under root whose text contains needle."""
    hits: list[str] = []
    for path in root.rglob("*.jinja"):
        if needle in _read(path):
            hits.append(str(path.relative_to(root)))
    return hits


class TestSaasMultiTenancyVariable:
    """Enterprise isolation uses saas_multi_tenancy_level, not saas_multi_tenancy."""

    def test_no_legacy_saas_multi_tenancy_equals(self) -> None:
        """Owned tree must not compare saas_multi_tenancy ==."""
        assert _jinja_hits(SAAS_ROOT, "saas_multi_tenancy ==") == []

    def test_enterprise_gate_uses_level(self) -> None:
        """Multi-tenant files gate on saas_multi_tenancy_level == 'enterprise'."""
        isolation = SAAS_ROOT / "lib" / "multi-tenant" / "isolation.ts.jinja"
        tenants = (
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "admin"
            / "tenants"
            / "page.tsx.jinja"
        )
        assert "saas_multi_tenancy_level == 'enterprise'" in _read(isolation)
        assert "saas_multi_tenancy_level == 'enterprise'" in _read(tenants)


class TestSaasTenantQueryNoSqlConcat:
    """buildTenantQuery must not interpolate tenant IDs into SQL strings."""

    def test_no_tenant_id_sql_interpolation(self) -> None:
        """Forbidden tenant.id SQL interpolation is gone."""
        isolation = SAAS_ROOT / "lib" / "multi-tenant" / "isolation.ts.jinja"
        text = _read(isolation)
        assert "'${tenant.id}'" not in text
        assert '"${tenant.id}"' not in text

    def test_build_tenant_query_returns_params(self) -> None:
        """Replacement helper returns field/value for parameterized queries."""
        isolation = SAAS_ROOT / "lib" / "multi-tenant" / "isolation.ts.jinja"
        text = _read(isolation)
        assert "export function buildTenantQuery(" in text
        assert "field: string; value: string" in text


class TestSaasAdminAuthz:
    """Admin pages throw on missing admin role; they never treat it as a boolean."""

    def test_require_admin_role_is_throw_only(self) -> None:
        """requireAdminRole is annotated Promise<void> and does not return boolean."""
        helpers = SAAS_ROOT / "integrations" / "auth" / "helpers.ts.jinja"
        text = _read(helpers)
        assert "export async function requireAdminRole(): Promise<void>" in text
        assert "return allowed" not in text
        assert "hasRole('org:admin')" in text
        assert "hasRole('admin')" in text

    def test_admin_pages_await_require_admin_role(self) -> None:
        """Admin pages call await requireAdminRole() without capturing a boolean."""
        pages = [
            SAAS_ROOT / "runtime" / "nextjs" / "app" / "admin" / "page.tsx.jinja",
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "admin"
            / "users"
            / "page.tsx.jinja",
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "admin"
            / "subscriptions"
            / "page.tsx.jinja",
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "admin"
            / "tenants"
            / "page.tsx.jinja",
        ]
        for page in pages:
            text = _read(page)
            assert "await requireUserId();" in text
            assert "await requireAdminRole();" in text
            assert "const isAdmin = await requireAdminRole()" not in text

    def test_users_admin_splits_server_page_and_client(self) -> None:
        """Users admin auth stays on the server page; UI is a client module."""
        users_dir = SAAS_ROOT / "runtime" / "nextjs" / "app" / "admin" / "users"
        page = _read(users_dir / "page.tsx.jinja")
        client = _read(users_dir / "client.tsx.jinja")

        assert "'use client'" not in page
        assert "import UsersClient from './client'" in page
        assert "await requireUserId();" in page
        assert "await requireAdminRole();" in page
        assert "return <UsersClient />;" in page

        assert client.lstrip().startswith("{% if saas_infra_module")
        assert "'use client'" in client
        assert client.find("'use client'") < client.find(
            "export default function UsersClient"
        )
        assert "requireUserId" not in client
        assert "requireAdminRole" not in client
        assert "@/lib/auth/helpers" not in client
        assert "fetch(`/api/admin/users/${userId}`" in client
        assert "fetch(`/api/admin/users/${userToDelete.id}`" in client


class TestSaasClerkMiddleware:
    """Clerk ^5.5.0 uses clerkMiddleware, not deprecated authMiddleware."""

    def test_no_auth_middleware(self) -> None:
        """authMiddleware must not appear in owned jinja."""
        assert _jinja_hits(SAAS_ROOT, "authMiddleware") == []

    def test_middleware_uses_clerk_middleware(self) -> None:
        """Next middleware imports clerkMiddleware from @clerk/nextjs/server."""
        middleware = SAAS_ROOT / "runtime" / "nextjs" / "middleware.ts.jinja"
        text = _read(middleware)
        assert "clerkMiddleware" in text
        assert "from '@clerk/nextjs/server'" in text


class TestSaasNextConfigNoStaticExport:
    """Cloudflare hosting must not set Next output to static export."""

    def test_saas_next_config_has_no_output_export(self) -> None:
        """runtime/nextjs/next.config.js.jinja has no output: 'export'."""
        config = SAAS_ROOT / "runtime" / "nextjs" / "next.config.js.jinja"
        text = _read(config)
        assert "output: 'export'" not in text
        assert 'output: "export"' not in text


class TestSaasRateLimitNoClientUserHeader:
    """Rate limit identity comes from session or trusted IP, never x-user-id."""

    def test_no_x_user_id_header(self) -> None:
        """x-user-id must not be used as a rate-limit identifier."""
        rate_limit = SAAS_ROOT / "integrations" / "security" / "rate-limit.ts.jinja"
        text = _read(rate_limit)
        assert "x-user-id" not in text
        assert "getUserId" in text
        assert "x-forwarded-for" in text


class TestSaasB2cOrgFieldsGated:
    """Organization FKs after the Organization model are gated on b2b-teams."""

    def test_prisma_subscription_org_gated(self) -> None:
        """Prisma Subscription organization fields sit inside b2b-teams."""
        schema = SAAS_ROOT / "integrations" / "orm" / "prisma" / "schema.prisma.jinja"
        text = _read(schema)
        assert 'saas_tenancy_model == "b2b-teams"' in text
        assert "model Subscription" in text
        assert (
            '{% if saas_tenancy_model == "b2b-teams" %}\n  organizationId String?'
        ) in text

    def test_drizzle_subscription_org_gated(self) -> None:
        """Drizzle subscriptions.organizationId is inside b2b-teams."""
        schema = SAAS_ROOT / "integrations" / "orm" / "drizzle" / "schema.ts.jinja"
        text = _read(schema)
        assert (
            '{% if saas_tenancy_model == "b2b-teams" %}\n'
            "  organizationId: text('organization_id').unique()"
            ".references(() => organizations.id"
        ) in text

    def test_lemonsqueezy_orm_columns(self) -> None:
        """Prisma and Drizzle add LemonSqueezy columns via elif lemonsqueezy."""
        prisma = _read(
            SAAS_ROOT / "integrations" / "orm" / "prisma" / "schema.prisma.jinja"
        )
        drizzle = _read(
            SAAS_ROOT / "integrations" / "orm" / "drizzle" / "schema.ts.jinja"
        )
        for text in (prisma, drizzle):
            assert 'saas_billing_provider == "lemonsqueezy"' in text
            assert "lemonSqueezySubscriptionId" in text
            assert "lemonSqueezyCustomerId" in text


class TestSaasWebhooksAndCron:
    """Billing webhook routes call processWebhook; cron routes require a secret."""

    def test_webhook_routes_exist(self) -> None:
        """Stripe, Paddle, and LemonSqueezy webhook routes exist under runtime/nextjs."""
        base = SAAS_ROOT / "runtime" / "nextjs" / "app" / "api" / "webhooks"
        for provider in ("stripe", "paddle", "lemonsqueezy"):
            route = base / provider / "route.ts.jinja"
            text = _read(route)
            assert route.is_file()
            assert "processWebhook" in text
            assert f'saas_billing_provider == "{provider}"' in text

    def test_paddle_service_dispatches(self) -> None:
        """Paddle processWebhook in the billing service dispatches to handlers."""
        service = _read(SAAS_ROOT / "integrations" / "billing" / "service.ts.jinja")
        assert "processPaddleWebhook" in service
        assert "JSON.parse(payload)" not in service

    def test_cron_routes_require_secret(self) -> None:
        """Vercel cron paths authorize with Bearer CRON_SECRET."""
        for job in ("cleanup", "reports"):
            route = (
                SAAS_ROOT
                / "runtime"
                / "nextjs"
                / "app"
                / "api"
                / "cron"
                / job
                / "route.ts.jinja"
            )
            text = _read(route)
            assert "CRON_SECRET" in text
            assert "Unauthorized" in text


class TestSaasUploadthingAndExamples:
    """UploadThing API lives under runtime/nextjs; example APIs moved with it."""

    def test_uploadthing_core_and_route(self) -> None:
        """UploadThing core/route are gated on saas_file_upload == uploadthing."""
        core = (
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "api"
            / "uploadthing"
            / "core.ts.jinja"
        )
        route = (
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "api"
            / "uploadthing"
            / "route.ts.jinja"
        )
        assert core.is_file()
        assert route.is_file()
        assert 'saas_file_upload == "uploadthing"' in _read(core)
        assert "ourFileRouter" in _read(core)
        assert "createRouteHandler" in _read(route)

    def test_examples_moved_out_of_saas_app_root(self) -> None:
        """Example API routes live under runtime/nextjs, not node/saas/app."""
        assert not (SAAS_ROOT / "app" / "api" / "examples").exists()
        users = (
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "api"
            / "examples"
            / "users"
            / "route.ts.jinja"
        )
        subs = (
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "api"
            / "examples"
            / "subscriptions"
            / "[id]"
            / "route.ts.jinja"
        )
        assert users.is_file()
        assert subs.is_file()


class TestSaasAuthSecretAndValidateEnv:
    """Auth.js v5 AUTH_SECRET/AUTH_URL are documented; validate-env script exists."""

    def test_auth_secret_in_owned_docs(self) -> None:
        """Owned docs mention AUTH_SECRET and AUTH_URL."""
        readme = _read(SAAS_ROOT / "README.md.jinja")
        env_ts = _read(SAAS_ROOT / "config" / "env.ts.jinja")
        assert "AUTH_SECRET" in readme
        assert "AUTH_URL" in readme
        assert "AUTH_SECRET: z.string().min(32)" in env_ts
        assert "AUTH_URL:" in env_ts

    def test_validate_env_script_exists(self) -> None:
        """package.json validate:env has a matching scripts/validate-env.ts.jinja."""
        script = SAAS_ROOT / "scripts" / "validate-env.ts.jinja"
        package = _read(SAAS_ROOT / "package.json.jinja")
        assert script.is_file()
        assert "validate:env" in package
        assert "from '../config/env'" in _read(script)

    def test_env_example_uses_auth_js_v5_names(self) -> None:
        """.env.example documents AUTH_SECRET/AUTH_URL and omits NEXTAUTH_*."""
        env_example = _read(SAAS_ROOT / ".env.example.jinja")
        assert "AUTH_SECRET" in env_example
        assert "AUTH_URL" in env_example
        assert "NEXTAUTH_SECRET" not in env_example
        assert "NEXTAUTH_URL" not in env_example

    def test_authjs_app_router_route_exports_handlers(self) -> None:
        """Next App Router catch-all re-exports Auth.js GET/POST handlers."""
        route = (
            SAAS_ROOT
            / "runtime"
            / "nextjs"
            / "app"
            / "api"
            / "auth"
            / "[...nextauth]"
            / "route.ts.jinja"
        )
        assert route.is_file()
        text = _read(route)
        assert "import { handlers } from '@/lib/auth'" in text
        assert "export const { GET, POST } = handlers" in text
        assert 'saas_auth_provider == "authjs"' in text
        assert 'saas_runtime == "nextjs-16"' in text


class TestSaasLemonSqueezyHealthProbe:
    """Health probe uses the same LEMONSQUEEZY_API_KEY name as env.ts."""

    def test_health_probe_env_key_matches_canonical(self) -> None:
        """LemonSqueezy health check must not use LEMON_SQUEEZY_API_KEY."""
        health = _read(
            SAAS_ROOT / "runtime" / "nextjs" / "lib" / "health.ts.jinja"
        )
        assert "LEMONSQUEEZY_API_KEY" in health
        assert "LEMON_SQUEEZY_API_KEY" not in health


class TestSaasPackageNameDisambiguated:
    """Workspace package name must not collide with dest-root project_slug."""

    def test_saas_package_name_suffix(self) -> None:
        """SaaS package.json uses {{ project_slug }}-saas."""
        package = _read(SAAS_ROOT / "package.json.jinja")
        assert '"name": "{{ project_slug }}-saas"' in package
        assert '"name": "{{ project_slug }}"' not in package


class TestSaasGdprDrizzleExtensionPoint:
    """Drizzle GDPR paths fail closed with a named extension-point error."""

    def test_no_pending_drizzle_throw(self) -> None:
        """Owned GDPR jinja must not throw a generic pending Error."""
        export = _read(SAAS_ROOT / "compliance" / "gdpr" / "data-export.ts.jinja")
        deletion = _read(
            SAAS_ROOT / "compliance" / "gdpr" / "data-deletion.ts.jinja"
        )
        assert "Drizzle implementation pending" not in export
        assert "Drizzle implementation pending" not in deletion
        assert "GdprDrizzleNotImplementedError" in export
        assert "GdprDrizzleNotImplementedError" in deletion
        assert "EXTENSION POINT" in export
        assert "EXTENSION POINT" in deletion


class TestSaasImpersonationGated:
    """Impersonation tables are not always-on."""

    def test_prisma_impersonation_gated(self) -> None:
        """Prisma ImpersonationSession is behind saas_user_impersonation."""
        schema = _read(
            SAAS_ROOT / "integrations" / "orm" / "prisma" / "schema.prisma.jinja"
        )
        assert "{% if saas_user_impersonation %}" in schema
        assert "model ImpersonationSession" in schema

    def test_drizzle_impersonation_gated(self) -> None:
        """Drizzle impersonationSessions is behind saas_user_impersonation."""
        schema = _read(
            SAAS_ROOT / "integrations" / "orm" / "drizzle" / "schema.ts.jinja"
        )
        assert "{% if saas_user_impersonation %}" in schema
        assert "impersonationSessions" in schema


class TestSaasLemonSqueezyWebhookSecret:
    """LemonSqueezy webhook secret is required when LS is the billing provider."""

    def test_env_webhook_secret_required(self) -> None:
        """config/env.ts requires LEMONSQUEEZY_WEBHOOK_SECRET (not optional)."""
        env_ts = _read(SAAS_ROOT / "config" / "env.ts.jinja")
        assert "LEMONSQUEEZY_WEBHOOK_SECRET: z.string().min(1)" in env_ts
        assert "LEMONSQUEEZY_WEBHOOK_SECRET: z.string().min(1).optional()" not in env_ts

    def test_csp_includes_lemonsqueezy(self) -> None:
        """CSP has a three-way Stripe / Paddle / LemonSqueezy branch."""
        csp = _read(SAAS_ROOT / "config" / "security-headers.ts.jinja")
        assert "lemonsqueezy.com" in csp
        assert "saas_billing_provider == 'lemonsqueezy'" in csp


class TestSaasSqlInjectionBoundWhere:
    """Dynamic WHERE clauses must bind values; never sql.raw(whereClause)."""

    def test_no_sql_raw_where_clause_in_saas_jinja(self) -> None:
        """Owned jinja must not inject concatenated WHERE via sql.raw."""
        assert _jinja_hits(SAAS_ROOT, "sql.raw(whereClause)") == []

    def test_token_tracking_no_interpolated_dates_or_operation(self) -> None:
        """token-tracking must not interpolate dates or operation into SQL."""
        text = _read(SAAS_ROOT / "lib" / "ai" / "token-tracking.ts.jinja")
        assert "created_at >= '${" not in text
        assert "operation = '${" not in text

    def test_token_tracking_operation_allowlist(self) -> None:
        """operation is validated against a frozen embedding/generation/rerank list."""
        text = _read(SAAS_ROOT / "lib" / "ai" / "token-tracking.ts.jinja")
        assert "Object.freeze" in text
        assert "assertTokenOperation" in text
        assert "'embedding'" in text
        assert "'generation'" in text
        assert "'rerank'" in text

    def test_vector_store_no_raw_where_interpolation(self) -> None:
        """vector-store must not inject whereClause via sql.raw or prisma."""
        text = _read(
            SAAS_ROOT / "integrations" / "ai" / "rag" / "vector-store.ts.jinja"
        )
        assert "${sql.raw(whereClause)}" not in text
        assert "${whereClause}" not in text
        assert "user_id = '${filter.userId}'" not in text
        assert "organization_id = '${filter.organizationId}'" not in text
