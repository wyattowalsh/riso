# W10 SAAS — dest-root `@/lib/analytics` client providers

- Wave: W10 / PAY-P0-saas-lib-analytics-provider
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `89882fff946e10692de1e1eb634ad4aa355ed694`
- Exclusive writes: `template/files/node/saas/lib/analytics/**` + this evidence
- `samples/*/render/**` writes: **0**
- `runtime/nextjs/app/layout.tsx.jinja` edits: **0** (import contract unchanged)
- Status: **green** (compiled `@/lib/analytics/posthog-provider` and `@/lib/analytics/amplitude-provider` now have dest-root modules)

## Confirmed finding

`runtime/nextjs/app/layout.tsx.jinja` already imported dest-root client providers. No `lib/analytics/` modules existed.

| Consumer import                      | Gate in layout                  | Missing dest-root module |
| ------------------------------------ | ------------------------------- | ------------------------ |
| `@/lib/analytics/posthog-provider`   | `saas_analytics == 'posthog'`   | **was missing**          |
| `@/lib/analytics/amplitude-provider` | `saas_analytics == 'amplitude'` | **was missing**          |

SaaS-root `tsconfig` maps `@/*` → `./*` for `saas_runtime == "nextjs-16"`. Layout is a server component (`export const metadata`) so the providers must be `'use client'` boundaries.

`package.json.jinja` adds browser SDKs only when `saas_app_module == "enabled"`:

| `saas_analytics` | Browser dep (app module on)    | Server-only sibling                                                        |
| ---------------- | ------------------------------ | -------------------------------------------------------------------------- |
| `posthog`        | `posthog-js`                   | `integrations/analytics/posthog/client.ts` (`posthog-node`)                |
| `amplitude`      | `@amplitude/analytics-browser` | `integrations/analytics/amplitude/client.ts` (`@amplitude/analytics-node`) |

`saas_analytics` defaults to `posthog` even when `saas_app_module` is `disabled`, so infra-only Next still imports `PostHogProvider`. Browser SDK import in that render would fail module resolution.

## Files created (2 templates + this evidence)

| File                                                                 | Gate                                                                 | Export                                                                                                                                                                   |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `template/files/node/saas/lib/analytics/posthog-provider.ts.jinja`   | `saas_infra_module == "enabled"` and `saas_analytics == "posthog"`   | `'use client'` `PostHogProvider`. App module on: `posthog-js` init + `createElement(PostHogProvider from posthog-js/react)`. App module off: passthrough `{ children }`. |
| `template/files/node/saas/lib/analytics/amplitude-provider.ts.jinja` | `saas_infra_module == "enabled"` and `saas_analytics == "amplitude"` | `'use client'` `AmplitudeProvider`. App module on: `@amplitude/analytics-browser` `init(apiKey)`. App module off: passthrough `{ children }`.                            |

No JSX in `.ts` (tsconfig `jsx: "preserve"` + `noUnusedLocals`). Amplitude `init` takes only the API key so the options object is not passed as `userId`.

Consumer files were **not** rewritten. Flatten dest-root `db/` / root Next configs were **not** remounted.

## Import contract (unchanged; now resolvable)

| Consumer (compiled, non-docs)         | Import                                                        |
| ------------------------------------- | ------------------------------------------------------------- |
| `runtime/nextjs/app/layout.tsx.jinja` | `PostHogProvider` from `@/lib/analytics/posthog-provider`     |
| `runtime/nextjs/app/layout.tsx.jinja` | `AmplitudeProvider` from `@/lib/analytics/amplitude-provider` |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # 89882fff946e10692de1e1eb634ad4aa355ed694
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas/lib/analytics/posthog-provider.ts.jinja \
  template/files/node/saas/lib/analytics/amplitude-provider.ts.jinja
# Validated 2 Jinja template(s): all OK
# render: app-on posthog starts with 'use client' + posthog-js; app-off is passthrough
# render: app-on amplitude starts with 'use client' + @amplitude/analytics-browser; app-off is passthrough
# flatten dest-root probes: next.config.js.jinja, remix.config.js.jinja,
# middleware.ts.jinja, prisma/seed.ts.jinja, db/schema.ts.jinja,
# db/seed.ts.jinja — all ABSENT
# lib/analytics/ contains only the two .ts.jinja providers (no .tsx sibling)
git status --short -- template/files/node/saas/lib/analytics
# ?? template/files/node/saas/lib/analytics/
```

## Remaining residuals (not this PAY)

| Residual                                                            | Disposition                                                               |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `PAY-P0-saas-theme-toggle`                                          | **out of this PAY** — `@/components/theme-toggle` still missing           |
| Amplitude server client imports `@amplitude/analytics-node`         | **pre-existing** — package.json only lists `@amplitude/analytics-browser` |
| `integrations/feature-flags/posthog.tsx.jinja` imports `posthog-js` | **pre-existing** — not gated on `saas_app_module`                         |
