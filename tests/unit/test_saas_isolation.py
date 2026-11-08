"""Runtime regressions for rendered SaaS tenant isolation and auth middleware."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

pytestmark = pytest.mark.unit
SAAS = Path(__file__).parents[2] / "template" / "files" / "node" / "saas"


def _render(relative: str, **overrides: object) -> str:
    """Render one SaaS payload using enabled defaults and explicit overrides."""
    context = {
        "saas_infra_module": "enabled",
        "saas_auth_module": "enabled",
        "saas_auth_provider": "clerk",
        "saas_runtime": "nextjs-16",
        "saas_multi_tenancy_level": "enterprise",
        "saas_admin_dashboard": True,
        "saas_billing_module": "enabled",
        "saas_billing_provider": "stripe",
        "saas_ui_framework": "shadcn-ui",
        "saas_orm": "prisma",
        "saas_i18n": False,
        "saas_observability_otel": False,
        "saas_observability_structured_logging": False,
    }
    context.update(overrides)
    return (
        Environment(loader=FileSystemLoader(str(SAAS)))
        .get_template(relative)
        .render(**context)
    )


def _node(source: str, assertions: str) -> None:
    """Execute the rendered TypeScript; only erase type syntax, not behavior."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js 22.13+ is needed for rendered TypeScript regressions")
    script = f"""
import assert from 'node:assert/strict';
import {{ stripTypeScriptTypes }} from 'node:module';
const source = {json.dumps(source)};
const javascript = stripTypeScriptTypes(source);
const mod = await import(
  'data:text/javascript;base64,' + Buffer.from(javascript).toString('base64')
);
{assertions}
"""
    result = subprocess.run(
        [node, "--no-warnings", "--input-type=module"],
        input=script,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    if "does not provide an export named 'stripTypeScriptTypes'" in result.stderr:
        pytest.skip("Node.js 22.13+ is needed for rendered TypeScript regressions")
    assert result.returncode == 0, result.stderr


def test_concurrent_tenants_and_nested_exceptions_do_not_leak() -> None:
    """Keep concurrent scopes separate and restore parents after exceptions."""
    _node(
        _render("lib/multi-tenant/isolation.ts.jinja"),
        """
const { withTenant, requireTenant, getCurrentTenant, setCurrentTenant } = mod;
const a = { id: 'tenant-A' }, b = { id: 'tenant-B' };
let enterB, releaseB;
const bEntered = new Promise(resolve => { enterB = resolve; });
const bReleased = new Promise(resolve => { releaseB = resolve; });
const observed = await Promise.all([
  withTenant(a, async () => {
    await bEntered;
    const id = requireTenant().id;
    releaseB();
    return id;
  }),
  withTenant(b, async () => {
    enterB();
    await bReleased;
    return requireTenant().id;
  }),
]);
assert.deepEqual(observed, ['tenant-A', 'tenant-B']);
assert.equal(getCurrentTenant(), null);
await withTenant(a, async () => {
  await assert.rejects(withTenant(b, async () => {
    assert.equal(requireTenant().id, 'tenant-B');
    throw new Error('nested failure');
  }), /nested failure/);
  assert.equal(requireTenant().id, 'tenant-A');
  setCurrentTenant(b);
  await Promise.resolve();
  assert.equal(requireTenant().id, 'tenant-B');
});
assert.equal(getCurrentTenant(), null);
assert.throws(() => setCurrentTenant(a), /request-scoped/);
for (const invalid of [null, {}, { id: '' }, { id: ' ' }, { id: 42 }]) {
  await assert.rejects(withTenant(invalid, async () => {
    throw new Error('Invalid scope callback must never run');
  }), /non-empty tenant ID/);
}
""",
    )


def test_prisma_operations_fail_closed_and_scope_mutations() -> None:
    """Reject missing tenants and prevent cross-tenant model mutations."""
    _node(
        _render("lib/multi-tenant/isolation.ts.jinja"),
        """
const extension = mod.createPrismaExtension({ $extends: extension => extension });
const execute = extension.query.$allModels.$allOperations;
let calls = 0;
const query = async args => { calls++; return args; };
const operations = ['findMany', 'findFirstOrThrow', 'findUnique', 'findUniqueOrThrow',
  'create', 'createMany', 'update', 'updateMany', 'delete', 'deleteMany',
  'upsert', 'aggregate', 'count', 'groupBy'];
for (const operation of operations) {
  await assert.rejects(execute({ model: 'Invoice', operation, args: {}, query }), /Tenant context/);
}
assert.equal(calls, 0);
assert.deepEqual(await execute({ model: 'User', operation: 'findMany', args: {}, query }), {});
await assert.rejects(
  execute({ model: 'users', operation: 'findMany', args: {}, query }),
  /Tenant context/
);
await mod.withTenant({ id: 'tenant-A' }, async () => {
  const find = await execute({ model: 'Invoice', operation: 'findUnique',
    args: { where: { id: 'invoice-B', tenantId: 'tenant-B' }, select: { id: true } }, query });
  assert.deepEqual(find.where, { id: 'invoice-B', tenantId: 'tenant-A' });
  assert.deepEqual(find.select, { id: true });
  const update = await execute({ model: 'Invoice', operation: 'update',
    args: {
      where: { id: 'invoice-B' },
      data: { tenantId: { set: 'tenant-B' }, title: 'new' },
    }, query });
  assert.equal(update.where.tenantId, 'tenant-A');
  assert.equal(update.data.tenantId, 'tenant-A');
  const upsert = await execute({ model: 'Invoice', operation: 'upsert',
    args: {
      where: { id: 'x' },
      create: { tenantId: 'tenant-B' },
      update: { tenantId: 'tenant-B' },
    }, query });
  assert.equal(upsert.where.tenantId, 'tenant-A');
  assert.equal(upsert.create.tenantId, 'tenant-A');
  assert.equal(upsert.update.tenantId, 'tenant-A');
  const create = await execute({ model: 'Invoice', operation: 'createMany',
    args: { data: [{ title: 'a' }, { tenantId: 'tenant-B' }] }, query });
  assert.deepEqual(create.data.map(row => row.tenantId), ['tenant-A', 'tenant-A']);
  await assert.rejects(
    execute({ model: 'Invoice', operation: 'findRaw', args: {}, query }),
    /Unsupported/
  );
});
""",
    )


def test_non_strict_prisma_mode_is_explicit_and_drizzle_still_requires_context() -> (
    None
):
    """Keep relaxed Prisma opt-in separate from required Drizzle contexts."""
    _node(
        _render("lib/multi-tenant/isolation.ts.jinja"),
        """
mod.initTenantIsolation({ strictMode: false });
const extension = mod.createPrismaExtension({ $extends: extension => extension });
const args = { where: { id: 'x' } };
assert.equal(await extension.query.$allModels.$allOperations({
  model: 'Invoice', operation: 'findMany', args, query: async value => value,
}), args);
const db = new Proxy({}, { get() { throw new Error('Database touched without tenant'); } });
const helper = mod.createDrizzleHelper(db, {});
assert.throws(() => helper.select(), /Tenant context/);
await assert.rejects(helper.insert({}), /Tenant context/);
await assert.rejects(helper.update('x', {}), /Tenant context/);
await assert.rejects(helper.delete('x'), /Tenant context/);
assert.throws(() => mod.buildTenantQuery('SELECT * FROM invoices'), /Tenant context/);
await mod.withTenant({ id: 'tenant-A' }, async () => {
  const fakeDb = { select: () => ({ from: () => ({ where: filter => {
    assert.deepEqual(filter, { tenantId: 'tenant-A' });
    return [{ id: 'scoped-result' }];
  } }) }) };
  const builder = mod.createDrizzleHelper(fakeDb, {}).select();
  assert.throws(() => builder.where({ title: 'requested-filter' }), /require an application/);
  assert.throws(() => builder.orderBy('id', 'asc'), /requires an application/);
  assert.throws(() => builder.limit(1), /requires an application/);
  assert.throws(() => builder.offset(1), /requires an application/);
  await assert.rejects(builder.count(), /requires an application/);
  assert.deepEqual(await builder.first(), { id: 'scoped-result' });
});
""",
    )


def test_raw_select_binds_tenant_and_wraps_or_predicates() -> None:
    """Bind tenant values outside caller predicates and reject unsafe SQL shapes."""
    _node(
        _render("lib/multi-tenant/isolation.ts.jinja"),
        """
await mod.withTenant({ id: "tenant' OR 1=1 --" }, async () => {
  const query = mod.buildTenantQuery(
    'SELECT * FROM invoices WHERE status = $1 OR status = $2;',
    'tenant_id', ['open', 'overdue']);
  assert.equal(query.sql,
    'SELECT * FROM (SELECT * FROM invoices WHERE status = $1 OR status = $2)' +
    ' AS tenant_data WHERE tenant_data."tenant_id" = $3');
  assert.deepEqual(query.params, ['open', 'overdue', "tenant' OR 1=1 --"]);
  assert.ok(!query.sql.includes("tenant'"));
  assert.throws(
    () => mod.buildTenantQuery('SELECT * FROM invoices', 'x; DROP TABLE invoices'),
    /identifier/
  );
  assert.throws(
    () => mod.buildTenantQuery('SELECT * FROM invoices; SELECT * FROM users'),
    /one SELECT/
  );
  assert.throws(() => mod.buildTenantQuery('DELETE FROM invoices'), /one SELECT/);
});
""",
    )


@pytest.mark.parametrize("provider", ["clerk", "authjs"])
@pytest.mark.parametrize("auth_module", ["enabled", "disabled"])
def test_middleware_imports_match_enabled_modules(
    provider: str, auth_module: str
) -> None:
    """Import providers only when enabled, while always importing Next types."""
    source = _render(
        "runtime/nextjs/middleware.ts.jinja",
        saas_auth_provider=provider,
        saas_auth_module=auth_module,
    )
    assert "import { NextResponse } from 'next/server'" in source
    assert "import type { NextRequest } from 'next/server'" in source
    assert "observability/logger" not in source
    assert ("@clerk/nextjs/server" in source) == (
        provider == "clerk" and auth_module == "enabled"
    )
    assert ("from '@/lib/auth'" in source) == (
        provider == "authjs" and auth_module == "enabled"
    )
    assert "authMiddleware" not in source


@pytest.mark.parametrize("provider", ["clerk", "authjs"])
def test_i18n_cannot_short_circuit_authentication(provider: str) -> None:
    """Allow public auth routes without allowing localized private routes."""
    source = _render(
        "runtime/nextjs/middleware.ts.jinja",
        saas_auth_provider=provider,
        saas_i18n=True,
    )
    dependencies = {
        "import createMiddleware from 'next-intl/middleware';": (
            "const createMiddleware = () => () => new Response('intl');"
        ),
        "import { locales, defaultLocale, localePrefix } from '@/i18n/config';": (
            "const locales = ['en', 'fr'], "
            "defaultLocale = 'en', localePrefix = 'always';"
        ),
        "import { NextResponse } from 'next/server';": (
            "const NextResponse = { next: () => new Response('next') };"
        ),
        "import { withSecurityHeaders } from '@/config/security-headers';": (
            "const withSecurityHeaders = (_req, response) => response;"
        ),
        "import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';": """
const clerkMiddleware = callback => callback;
const createRouteMatcher = patterns => req => patterns.some(
  pattern => new RegExp('^' + pattern + '$').test(req.nextUrl.pathname)
);
""",
        "import { auth } from '@/lib/auth';": "const auth = callback => callback;",
    }
    for original, stub in dependencies.items():
        source = source.replace(original, stub)
    if provider == "clerk":
        assert "'/:locale'" not in source
        assertions = """
let protectedCalls = 0;
const auth = () => ({
  protect() {
    protectedCalls++;
    throw new Error('authentication required');
  },
});
for (const pathname of ['/', '/sign-in', '/sign-in/sso-callback', '/sign-up',
  '/sign-up/sso-callback', '/en', '/fr', '/en/sign-in', '/fr/sign-up/sso-callback']) {
  const response = await mod.default(auth, {
    headers: new Headers(), nextUrl: new URL('https://app.test' + pathname),
  });
  assert.equal(response.status, 200, pathname);
}
assert.equal(protectedCalls, 0);
for (const pathname of ['/dashboard', '/en/dashboard', '/fr/dashboard', '/private', '/de']) {
  await assert.rejects(mod.default(auth, {
    headers: new Headers(), nextUrl: new URL('https://app.test' + pathname),
  }), /authentication required/);
}
assert.equal(protectedCalls, 5);
"""
    else:
        assertions = """
const response = mod.default({ auth: null, nextUrl: new URL('https://app.test/en/dashboard') });
assert.equal(response.status, 302);
assert.equal(
  response.headers.get('location'),
  'https://app.test/en/sign-in?callbackUrl=%2Fen%2Fdashboard'
);
"""
    _node(source, assertions)


@pytest.mark.parametrize("provider", ["clerk", "authjs"])
def test_auth_disabled_layout_does_not_import_missing_provider(provider: str) -> None:
    """Render the application shell without disabled authentication packages."""
    layout = _render(
        "runtime/nextjs/app/layout.tsx.jinja",
        saas_auth_module="disabled",
        saas_auth_provider=provider,
    )
    assert "ClerkProvider" not in layout
    assert "SessionProvider" not in layout
    assert "<html" in layout and "{children}" in layout


def test_clerk_organization_admin_cannot_query_platform_statistics() -> None:
    """Require trusted platform metadata before accessing global statistics."""
    helpers = _render("integrations/auth/helpers.ts.jinja").replace(
        "import { auth, currentUser } from '@clerk/nextjs/server';",
        "const auth = async () => ({ userId: 'user-1', has: () => true }); "
        "const currentUser = async () => globalThis.platformAdminUser;",
    )
    dashboard = _render("runtime/nextjs/app/admin/page.tsx.jinja")
    page_guard = dashboard[
        dashboard.index(
            "export default async function AdminDashboardPage()"
        ) : dashboard.index("  const quickLinks:")
    ]
    source = (
        helpers
        + "\nconst getDashboardStats = async () => { globalThis.statsCalls++; return {}; };\n"
        + page_guard
        + "  return stats;\n}\n"
    )
    _node(
        source,
        """
globalThis.statsCalls = 0;
globalThis.platformAdminUser = { publicMetadata: {}, unsafeMetadata: { role: 'admin' } };
await assert.rejects(mod.default(), /Admin role required/);
assert.equal(globalThis.statsCalls, 0);
globalThis.platformAdminUser = { publicMetadata: { role: 'member' } };
await assert.rejects(mod.default(), /Admin role required/);
assert.equal(globalThis.statsCalls, 0);
globalThis.platformAdminUser = {};
await assert.rejects(mod.default(), /Admin role required/);
assert.equal(globalThis.statsCalls, 0);
globalThis.platformAdminUser = { publicMetadata: { role: 'admin' } };
assert.deepEqual(await mod.default(), {});
assert.equal(globalThis.statsCalls, 1);
""",
    )


def test_clerk_remix_platform_guard_requires_trusted_user_metadata() -> None:
    """Apply the platform metadata boundary to Remix organization admins."""
    source = _render("integrations/auth/helpers.ts.jinja", saas_runtime="remix-2")
    source = source.replace(
        "import { getAuth } from '@clerk/remix/ssr.server';",
        "const getAuth = async () => ({ userId: 'user-1', orgRole: 'org:admin' });",
    ).replace(
        "import { createClerkClient } from '@clerk/backend';",
        """
const createClerkClient = () => ({
  users: { getUser: async () => globalThis.platformAdminUser },
});
""",
    )
    _node(
        source,
        """
globalThis.platformAdminUser = { publicMetadata: {}, unsafeMetadata: { role: 'admin' } };
await assert.rejects(mod.requireAdminRole({}), /Admin role required/);
globalThis.platformAdminUser = { publicMetadata: { role: 'admin' } };
assert.equal(await mod.requireAdminRole({}), undefined);
""",
    )


def test_authjs_platform_guard_requires_trusted_session_admin_role() -> None:
    """Deny missing or organization roles and accept the platform session role."""
    source = _render(
        "integrations/auth/helpers.ts.jinja", saas_auth_provider="authjs"
    ).replace(
        "import { auth } from '@/integrations/auth/authjs/auth.config';",
        "const auth = async () => globalThis.platformSession;",
    )
    _node(
        source,
        """
for (const session of [null, {}, { user: { id: 'user-1' } },
  { user: { id: 'user-1', role: 'member' } }, { user: { role: 'org:admin' } }]) {
  globalThis.platformSession = session;
  await assert.rejects(mod.requireAdminRole(), /Admin role required/);
}
globalThis.platformSession = { user: { id: 'user-1', role: 'admin' } };
assert.equal(await mod.requireAdminRole(), undefined);
""",
    )


@pytest.mark.parametrize("section", ["users", "tenants"])
def test_admin_interactive_pages_have_authorized_server_entries(section: str) -> None:
    """Separate client interactivity from server authorization and data loading."""
    entry = _render(f"runtime/nextjs/app/admin/{section}/page.tsx.jinja")
    client = _render(f"runtime/nextjs/app/admin/{section}/client.tsx.jinja")
    assert "'use client'" not in entry
    assert "React.useState" not in entry and "useEffect" not in entry
    return_boundary = "return (" if section == "users" else "return <"
    assert entry.index("await requireAdminRole();") < entry.index(return_boundary)
    assert client.lstrip().startswith("'use client';")
    assert "export default async function" not in client
    assert "from '@/lib/multi-tenant';" not in client
    assert not _render(
        f"runtime/nextjs/app/admin/{section}/page.tsx.jinja",
        saas_auth_module="disabled",
    ).strip()
    if section == "users":
        assert "emailVerified: new Date" not in entry


def test_admin_dashboard_and_subscriptions_run_throwing_role_guards() -> None:
    """Run throwing authorization guards before fetching admin-wide records."""
    dashboard = _render("runtime/nextjs/app/admin/page.tsx.jinja")
    page_body = dashboard[dashboard.index("export default async function") :]
    assert page_body.index("await requireAdminRole();") < page_body.index(
        "await getDashboardStats()"
    )
    subscriptions = _render("runtime/nextjs/app/admin/subscriptions/page.tsx.jinja")
    assert "await requireAdminRole();" in subscriptions
    assert "const isAdmin =" not in subscriptions
    assert "redirect('/unauthorized')" not in subscriptions


def test_enterprise_payload_uses_the_public_level_key() -> None:
    """Gate the enterprise subtree on the actual public tenancy answer key."""
    for path in (SAAS / "lib" / "multi-tenant").glob("*.jinja"):
        assert _render(str(path.relative_to(SAAS))).strip(), path
        assert not _render(
            str(path.relative_to(SAAS)), saas_multi_tenancy_level="teams"
        ).strip(), path


@pytest.mark.parametrize("runtime", ["nextjs-16", "remix-2"])
def test_saas_test_toolchain_uses_patched_compatible_versions(runtime: str) -> None:
    """Pair patched test packages while preserving the runtime framework major."""
    manifest = json.loads(
        _render(
            "package.json.jinja",
            project_name="Security regression",
            project_slug="security-regression",
            saas_runtime=runtime,
            saas_hosting="vercel",
            saas_database="neon",
        )
    )
    dev = manifest["devDependencies"]
    assert dev["vitest"] == dev["@vitest/coverage-v8"] == "^4.1.12"
    assert manifest["scripts"]["test"] == "vitest run"
    if runtime == "remix-2":
        assert dev["vite"] == "^6.4.5"
        assert manifest["dependencies"]["@remix-run/react"].startswith("^2.")
    else:
        assert "vite" not in dev
        assert manifest["dependencies"]["next"].startswith("^16.")


def _paddle_source_with_installed_sdk() -> str:
    """Use the existing sample SDK offline, without installing dependencies."""
    sdk_entry = (
        SAAS.parents[3]
        / "samples/saas-starter/all-in-one/render/node/saas/node_modules"
        / "@paddle/paddle-node-sdk/dist/cjs/index.js"
    )
    if not sdk_entry.is_file():
        pytest.skip("Install the declared Paddle SaaS sample SDK for provider fixtures")
    source = _render(
        "integrations/billing/paddle/webhooks.ts.jinja",
        saas_billing_provider="paddle",
    )
    sdk_import = next(
        line for line in source.splitlines() if "from '@paddle/paddle-node-sdk'" in line
    )
    sdk_path = json.dumps(str(sdk_entry.resolve()))
    source = source.replace(
        sdk_import,
        "import { createRequire } from 'node:module';\n"
        f"const {{ Paddle, EventName }} = createRequire({sdk_path})({sdk_path});",
    )
    source = source.replace(
        "import { prisma } from '@/lib/database/client';",
        "const prisma = { subscription: { updateMany: async args => { "
        "globalThis.paddleMutations.push(args); return { count: 1 }; } } };",
    ).replace("process.env.PADDLE_API_KEY!", "'fixture-only-not-a-real-paddle-api-key'")
    return (
        "process.env.PADDLE_WEBHOOK_SECRET = 'fixture-only-webhook-secret';\n" + source
    )


def test_paddle_sdk_checks_provider_header_expiry_and_raw_body() -> None:
    """Reject stale or tampered signatures before any database handler runs."""
    _node(
        _paddle_source_with_installed_sdk(),
        """
const { createHmac } = await import('node:crypto');
const secret = 'fixture-only-webhook-secret';
globalThis.paddleMutations = [];
const payload = JSON.stringify({
  event_id: 'evt_fixture_only', event_type: 'subscription.updated',
  notification_id: 'ntf_fixture_only', occurred_at: '2026-01-01T00:00:00Z',
  data: {
    id: 'sub_fixture_only', customer_id: 'ctm_fixture_only', status: 'active',
    currency_code: 'USD', items: [], billing_cycle: { interval: 'month', frequency: 1 },
    current_billing_period: null, scheduled_change: null,
  },
});
const timestamp = Math.floor(Date.now() / 1000);
const sign = (body, seconds) => {
  const digest = createHmac('sha256', secret).update(`${seconds}:${body}`).digest('hex');
  return `ts=${seconds};h1=${digest}`;
};
const signature = sign(payload, timestamp);
assert.equal(mod.verifyPaddleWebhook(payload, signature), true);
assert.equal(mod.verifyPaddleWebhook(payload + ' ', signature), false);
assert.equal(mod.verifyPaddleWebhook(payload, sign(payload, timestamp - 60)), false);
assert.equal(mod.verifyPaddleWebhook(payload, 'malformed'), false);
assert.equal(mod.verifyPaddleWebhook(payload, `ts=${timestamp};h1=not-a-valid-hash`), false);
await mod.processWebhook(payload, signature);
assert.equal(globalThis.paddleMutations.length, 1);
assert.deepEqual(globalThis.paddleMutations[0].where, {
  paddleSubscriptionId: 'sub_fixture_only',
});
assert.equal(globalThis.paddleMutations[0].data.status, 'active');
await assert.rejects(mod.processWebhook(payload + ' ', signature), /signature/i);
await assert.rejects(
  mod.processWebhook(payload, sign(payload, timestamp - 60)), /signature/i
);
assert.equal(globalThis.paddleMutations.length, 1);
delete process.env.PADDLE_WEBHOOK_SECRET;
assert.throws(() => mod.verifyPaddleWebhook(payload, signature), /not set/);
""",
    )


def test_paddle_route_passes_raw_body_and_single_signature_header() -> None:
    """Preserve provider bytes and reject absent headers before dispatch."""
    source = _render(
        "runtime/nextjs/app/api/webhooks/paddle/route.ts.jinja",
        saas_billing_provider="paddle",
    ).replace(
        "import { NextResponse } from 'next/server';",
        "const NextResponse = { json: (body, options) => "
        "new Response(JSON.stringify(body), options) };",
    )
    source = source.replace(
        "import { processWebhook } from '@/integrations/billing/service';",
        "const processWebhook = async (...args) => { "
        "globalThis.paddleReceived.push(args); };",
    )
    _node(
        source,
        """
globalThis.paddleReceived = [];
const payload = '{ "event_type": "customer.updated" }';
const signature = 'ts=123;h1=fixture-only-header';
const response = await mod.POST(new Request('https://app.test/api/webhooks/paddle', {
  method: 'POST', body: payload, headers: { 'paddle-signature': signature },
}));
assert.equal(response.status, 200);
assert.deepEqual(globalThis.paddleReceived, [[payload, signature]]);
const missing = await mod.POST(new Request('https://app.test/api/webhooks/paddle', {
  method: 'POST', body: payload,
}));
assert.equal(missing.status, 400);
assert.equal(globalThis.paddleReceived.length, 1);
""",
    )


@pytest.mark.parametrize("runtime", ["nextjs-16", "remix-2"])
@pytest.mark.parametrize("auth_module", ["enabled", "disabled"])
def test_uploadthing_payload_requires_authenticated_next_runtime(
    runtime: str, auth_module: str
) -> None:
    """Never emit upload server or client imports without supported auth."""
    context = {
        "saas_runtime": runtime,
        "saas_auth_module": auth_module,
        "saas_file_upload": "uploadthing",
    }
    expected = runtime == "nextjs-16" and auth_module == "enabled"
    for path in (
        "runtime/nextjs/app/api/uploadthing/core.ts.jinja",
        "runtime/nextjs/app/api/uploadthing/route.ts.jinja",
        "integrations/uploads/file-upload.tsx.jinja",
    ):
        assert bool(_render(path, **context).strip()) == expected, path
    manifest = json.loads(
        _render("package.json.jinja", project_name="Fixture", **context)
    )
    assert ("uploadthing" in manifest["dependencies"]) == expected
    assert ("@uploadthing/react" in manifest["dependencies"]) == expected
    typed_env = _render("config/env.ts.jinja", **context)
    assert ("UPLOADTHING_SECRET" in typed_env) == expected
    assert ("UPLOADTHING_APP_ID" in typed_env) == expected


def test_uploadthing_middleware_rejects_unauthenticated_uploads() -> None:
    """The emitted SDK middleware must propagate authentication rejection."""
    source = _render(
        "runtime/nextjs/app/api/uploadthing/core.ts.jinja",
        saas_file_upload="uploadthing",
    ).replace(
        "import { createUploadthing, type FileRouter } from 'uploadthing/next';",
        """
const createUploadthing = () => () => ({
  middleware(callback) { this.authenticate = callback; return this; },
  onUploadComplete() { return this; },
});
""",
    )
    source = source.replace(
        "import { requireUserId } from '@/lib/auth/helpers';",
        "const requireUserId = async () => { throw new Error('Authentication required'); };",
    )
    _node(
        source,
        """
await assert.rejects(
  mod.ourFileRouter.imageUploader.authenticate(), /Authentication required/
);
""",
    )
