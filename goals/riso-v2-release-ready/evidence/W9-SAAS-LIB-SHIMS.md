# W9 SAAS — dest-root `@/lib` shims for health, observability logger, env

- Wave: W9 / remaining compiled SaaS next-build `@/lib` holes (same class as `@/lib/auth/helpers`)
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `314cd13c1f4fde91bc2c36caa40b0aceaabb5073`
- Exclusive writes: `template/files/node/saas/lib/**` (3 new thin re-exports) + this evidence
- `samples/*/render/**` writes: **0**
- Status: **green** (compiled `@/lib/health`, `@/lib/observability/logger`, `@/lib/env` now have dest-root modules)

## Confirmed finding

Compiled (non-docs) Next/SaaS files already imported these dest-root `@/lib` paths. Sources lived elsewhere:

| Missing dest-root import     | Existing source                              |
| ---------------------------- | -------------------------------------------- |
| `@/lib/health`               | `runtime/nextjs/lib/health.ts.jinja`         |
| `@/lib/observability/logger` | `integrations/observability/logger.ts.jinja` |
| `@/lib/env`                  | `config/env.ts.jinja`                        |

SaaS-root `tsconfig` maps `@/*` → `./*` for `saas_runtime == "nextjs-16"`. `@/runtime/nextjs/lib/health` therefore resolves to dest `runtime/nextjs/lib/health.ts`. No dest-root remount.

Docs-only `@/lib/env` / `@/lib/health` hits (`docs/*.md.jinja`) were not used as justification.

## Files created (3 templates + this evidence)

| File                                                         | Gate                                                                       | Export                                                |
| ------------------------------------------------------------ | -------------------------------------------------------------------------- | ----------------------------------------------------- |
| `template/files/node/saas/lib/health.ts.jinja`               | `saas_infra_module == "enabled" and saas_runtime == "nextjs-16"`           | `export * from '@/runtime/nextjs/lib/health'`         |
| `template/files/node/saas/lib/observability/logger.ts.jinja` | `saas_infra_module == "enabled" and saas_observability_structured_logging` | `export * from '@/integrations/observability/logger'` |
| `template/files/node/saas/lib/env.ts.jinja`                  | `saas_infra_module == "enabled"`                                           | `export * from '@/config/env'`                        |

Consumer files were **not** rewritten. Flatten dest-root `db/` was **not** remounted. No unused extra shims (`@/lib/health-utils`, `@/lib/api/health`, `@/lib/db`, `@/lib/prisma`).

## Import contract (unchanged; now resolvable)

| Consumer (compiled, non-docs)                                         | Import                                                               |
| --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `runtime/nextjs/app/api/health/route.ts.jinja`                        | `checkHealth`, `checkReadiness`, `checkLiveness` from `@/lib/health` |
| `runtime/nextjs/tests/api/health.test.ts.jinja`                       | same                                                                 |
| `runtime/nextjs/app/admin/page.tsx.jinja`                             | `logger` from `@/lib/observability/logger`                           |
| `runtime/nextjs/middleware.ts.jinja`                                  | `logger` (gated on `saas_observability_structured_logging`)          |
| `integrations/billing/{stripe,paddle,lemonsqueezy}/webhooks.ts.jinja` | `logger`                                                             |
| `integrations/analytics/{posthog,amplitude}/client.ts.jinja`          | `env` from `@/lib/env`                                               |
| `integrations/billing/{stripe,paddle}/client.ts.jinja`                | `env`                                                                |
| `integrations/{ai,email,jobs,search,storage}/**/client.ts.jinja`      | `env`                                                                |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # 314cd13c1f4fde91bc2c36caa40b0aceaabb5073
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas/lib/health.ts.jinja \
  template/files/node/saas/lib/observability/logger.ts.jinja \
  template/files/node/saas/lib/env.ts.jinja
# Validated 3 Jinja template(s): all OK
# flatten dest-root probes: next.config.js.jinja, remix.config.js.jinja,
# middleware.ts.jinja, prisma/seed.ts.jinja, db/schema.ts.jinja,
# db/seed.ts.jinja — all ABSENT
git status --short -- 'samples/*/render/**'   # empty
```

## Remaining residuals (not this PAY)

| Residual                                                                                  | Disposition                                                                                    |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `app/api/examples/users/route.ts.jinja` imports `createCorrelatedLogger`                  | **pre-existing** — source logger exports `createLogger` / `createRequestLogger`, not that name |
| `runtime/nextjs/app/api/health/middleware.example.ts.jinja` imports `@/lib/health-utils`  | **not created** — example file only; source remains `runtime/nextjs/lib/health-utils.ts.jinja` |
| `compliance/gdpr/{audit-trail,data-export}.ts.jinja` import `@/lib/prisma` / `@/lib/db`   | **out of scope** — flatten remounts forbidden                                                  |
| Comment-only `@/lib/api/health` / `@/lib/feature-flags/...` / `@/lib/security/rate-limit` | **docs/comments** — no unused shims                                                            |
