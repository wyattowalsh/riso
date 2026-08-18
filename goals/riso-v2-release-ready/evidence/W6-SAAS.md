# W6 SAAS — retarget leftover `@/db/schema` imports

- Wave: W6 / lane SAAS (exclusive-write closeout)
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `ddc50a0081ed6a5159cd308594d5bfaad7c9971f`
- Exclusive writes: `template/files/node/saas/**`, `template/files/saas-starter/**`, this file
- `samples/*/render/**` writes: **0**
- Status: **green** (`@/db/schema` leftover rg empty)

## Confirmed finding

Flatten stays dropped. Live Drizzle schema is `integrations/orm/drizzle/schema.ts` (import `@/integrations/orm/drizzle/schema`). Prisma stays client-based (`@/lib/database/client` / `@prisma/client`). Dest-root `@/db/schema` and dest-root `db/schema.ts` do not exist.

Correct nearby pattern already live in:

- `app/api/examples/users/route.ts.jinja`
- `app/api/examples/subscriptions/[id]/route.ts.jinja`

Leftover Drizzle-gated imports still used `@/db/schema`. Extra hit beyond the known list: `integrations/scheduler/cron.ts.jinja` (dynamic `import()`).

## Files changed (17 templates + this evidence)

### Product imports (Drizzle-gated only; Prisma branches untouched)

| File                                                                             | Change                                              |
| -------------------------------------------------------------------------------- | --------------------------------------------------- |
| `template/files/node/saas/runtime/nextjs/app/admin/page.tsx.jinja`               | `@/db/schema` → `@/integrations/orm/drizzle/schema` |
| `template/files/node/saas/runtime/nextjs/app/admin/subscriptions/page.tsx.jinja` | same                                                |
| `template/files/node/saas/integrations/billing/stripe/webhooks.ts.jinja`         | same                                                |
| `template/files/node/saas/integrations/billing/paddle/webhooks.ts.jinja`         | same                                                |
| `template/files/node/saas/integrations/billing/lemonsqueezy/webhooks.ts.jinja`   | same                                                |
| `template/files/node/saas/integrations/compliance/gdpr.ts.jinja`                 | same (3 gated imports)                              |
| `template/files/node/saas/integrations/scheduler/cron.ts.jinja`                  | dynamic import retargeted                           |

### Docs (retarget to live schema; not left historical)

| File                                                                  | Change                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------- |
| `template/files/node/saas/docs/API_EXAMPLES.md.jinja`                 | 4 example imports                                             |
| `template/files/node/saas/docs/migrations/auth.md.jinja`              | 3 example imports + schema/middleware dest-root paths         |
| `template/files/node/saas/docs/migrations/orm.md.jinja`               | all `@/db/schema` examples + live seed/schema/dir targets     |
| `template/files/node/saas/docs/DEPLOYMENT.md.jinja`                   | `runtime/nextjs/next.config.js`                               |
| `template/files/node/saas/docs/ARCHITECTURE.md.jinja`                 | tree `prisma/` / `db/` → `integrations/orm/{prisma,drizzle}/` |
| `template/files/node/saas/README.md.jinja`                            | same tree retarget                                            |
| `template/files/node/saas/i18n/README.md.jinja`                       | Next wiring → `runtime/nextjs/middleware.ts`                  |
| `template/files/node/saas/integrations/observability/README.md.jinja` | Next config + `instrumentation.ts` under `runtime/nextjs/`    |
| `template/files/node/saas/config/security-headers.ts.jinja`           | comment → `runtime/nextjs/next.config.js`                     |

### Dest-root flatten leftover (executable)

| File                                                            | Change                                                                                                        |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `template/files/node/saas/.github/workflows/database.yml.jinja` | path filters and schema/seed checks: dest-root `prisma/**` / `db/**` → `integrations/orm/{prisma,drizzle}/**` |

Did **not** remount dest-root `next.config.js`, `middleware.ts`, `prisma/seed.ts`, or `db/schema.ts`.

`template/files/saas-starter/**`: **0** writes.

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # ddc50a0081ed6a5159cd308594d5bfaad7c9971f
rg -n "@/db/schema" template/files/node/saas   # empty
# flatten dest-root probes: next.config.js.jinja, remix.config.js.jinja,
# middleware.ts.jinja, prisma/seed.ts.jinja, db/schema.ts.jinja,
# db/seed.ts.jinja, public/favicon.ico — all ABSENT
uv run python scripts/ci/validate_jinja_templates.py <17 edited templates>
# Validated 17 Jinja template(s): all OK
git status --short -- 'samples/*/render/**'   # empty
```

## Remaining residuals

| Residual                                                                                                           | Disposition                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `docs/migrations/orm.md.jinja` dest-root `prisma/seed.ts` / `db/seed.ts` phrases                                   | **historical incoming only** — explicitly labeled “older flatten layout”; live After/scripts use `integrations/orm/**` |
| README / ARCHITECTURE dest-root `app/` and `public/` tree rows                                                     | **docs-only** — no dest-root payload; runtimes stay under `runtime/{nextjs,remix}`; `public/` still 404                |
| Generic “add to middleware.ts” comments (`lib/multi-tenant/**`, rate-limit, feature-flags, logger, health example) | usage snippets, not dest-root remounts; Next middleware file is `runtime/nextjs/middleware.ts`                         |
| Official `samples/*/render/**`                                                                                     | stale until PLATFORM re-render; dest not hand-edited                                                                   |
| No `drizzle.config.ts.jinja` in payload                                                                            | pre-existing; out of this import-retarget lock                                                                         |

## Path lock

| Class                                     | Count                                            |
| ----------------------------------------- | ------------------------------------------------ |
| This-session product writes               | 17 templates under `template/files/node/saas/**` |
| Evidence                                  | this file                                        |
| `saas-starter/**`                         | 0                                                |
| `samples/*/render/**`                     | 0                                                |
| Lockfiles / secrets / commit / tag / push | 0                                                |
| Foreign-tree edits                        | 0                                                |
| Flatten remounts                          | 0                                                |
