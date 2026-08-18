# W7 SAAS — add missing `@/lib/database/client` and `@/lib/auth/helpers`

- Wave: W7 / PAY-P0-saas-next-missing-modules
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `e4029ca8d8213a896bd9ca841525ce4d73bbca19`
- Exclusive writes: `template/files/node/saas/lib/auth/helpers.ts.jinja`, `template/files/node/saas/lib/database/client.ts.jinja`, this file
- `samples/*/render/**` writes: **0**
- Status: **green** (compiled `@/lib/database/client` and `@/lib/auth/helpers` now have payload modules)

## Confirmed finding

Next health/admin (and billing/auth/compliance/scheduler/example routes) already imported `@/lib/database/client` and `@/lib/auth/helpers`. Auth helpers lived only at `integrations/auth/helpers.ts.jinja`. No `lib/database/` client existed. Official Next dests run `next build runtime/nextjs` with saas-root `tsconfig` `@/*` → `./*`, so those imports failed at compile.

Flatten stays dropped. Live Drizzle schema remains `@/integrations/orm/drizzle/schema`. Prisma stays `@prisma/client` behind this new singleton.

## Files created (2 templates + this evidence)

| File                                                    | Gate                                                               | Exports                                                                                                                                                                                                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `template/files/node/saas/lib/auth/helpers.ts.jinja`    | `saas_infra_module == "enabled" and saas_auth_module == "enabled"` | `export * from '@/integrations/auth/helpers'` — includes `requireUserId` / `requireAdminRole`                                                                                                                                                           |
| `template/files/node/saas/lib/database/client.ts.jinja` | `saas_infra_module == "enabled"`                                   | Prisma: `prisma` + `db` (same `PrismaClient`, `globalThis` singleton in non-prod). Drizzle: `db` only (neon-http vs postgres-js per `saas_database`, schema from `@/integrations/orm/drizzle/schema`). Throws if `process.env.DATABASE_URL` is missing. |

`runtime/nextjs/**` imports were **not** rewritten: compiled names already match (`prisma` vs `db` by `saas_orm`; `requireUserId` / `requireAdminRole` from helpers). Docs `*.md.jinja` were not rewritten.

Did **not** remount dest-root `db/`, `next.config.js`, `middleware.ts`, or `prisma/seed.ts`.

## Import contract (unchanged; now resolvable)

| Consumer                                                | Import                                                      |
| ------------------------------------------------------- | ----------------------------------------------------------- |
| `runtime/nextjs/app/api/health/route.ts.jinja`          | `prisma` or `db` from `@/lib/database/client`               |
| `runtime/nextjs/lib/health.ts.jinja`                    | same                                                        |
| `runtime/nextjs/tests/api/health.test.ts.jinja`         | same (+ `vi.mock('@/lib/database/client')`)                 |
| `runtime/nextjs/app/admin/page.tsx.jinja`               | `requireUserId` from `@/lib/auth/helpers`; `prisma` or `db` |
| `runtime/nextjs/app/admin/subscriptions/page.tsx.jinja` | `requireUserId`, `requireAdminRole`; `prisma` or `db`       |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # e4029ca8d8213a896bd9ca841525ce4d73bbca19
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas/lib/auth/helpers.ts.jinja \
  template/files/node/saas/lib/database/client.ts.jinja
# Validated 2 Jinja template(s): all OK
# flatten dest-root probes: next.config.js.jinja, remix.config.js.jinja,
# middleware.ts.jinja, prisma/seed.ts.jinja, db/schema.ts.jinja,
# db/seed.ts.jinja — all ABSENT
git status --short -- 'samples/*/render/**'   # empty
```

## Remaining residuals

| Residual                                                                                                                             | Disposition                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `lib/ai/token-tracking.ts.jinja` and `integrations/ai/rag/vector-store.ts.jinja` import `@/integrations/orm/{prisma,drizzle}/client` | **out of this PAY** — those ORM client files still do not exist; health/admin use `@/lib/database/client` |
| `requireAdminRole()` returns void but subscriptions page assigns `const isAdmin = await requireAdminRole()`                          | **pre-existing consumer** — re-export does not change the integrations helper contract                    |
| `@/lib/health` lives at `runtime/nextjs/lib/health.ts`                                                                               | **out of this PAY** — not a dest-root remount                                                             |
