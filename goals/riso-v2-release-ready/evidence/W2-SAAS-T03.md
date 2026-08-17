# W2 SAAS-T03 — no flatten copies at saas app root

- Task: `SAAS-T03`
- Wave: W2 / lane SAAS
- Deps: SAAS-T01, SAAS-T02
- Exclusive write roots: `template/files/node/saas/**`, `template/files/saas-starter/**`
- Verify: no mixed Next+Remix at `node/saas` root
- Status: **green**
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `samples/*/render/**` writes: **0**

## Flatten probes (`template/files/node/saas/`)

| Probe | Result |
| --- | --- |
| `next.config.js.jinja` | **absent** |
| `remix.config.js.jinja` | **absent** |
| `middleware.ts.jinja` | **absent** |
| `open-next.config.ts.jinja` | **absent** |
| `postcss.config.mjs.jinja` | **absent** (lives under `runtime/nextjs/` or `runtime/remix/`) |
| `app/page.tsx.jinja` | **absent** |
| `app/layout.tsx.jinja` | **absent** |
| `app/root.tsx.jinja` | **absent** |
| `app/globals.css.jinja` | **absent** |
| `app/(marketing)/`, `app/admin/`, `app/dashboard/`, `app/routes/`, `app/styles/` | **absent** |
| flatten `lib/auth.ts.jinja`, `prisma/`, `db/`, `hooks/` | **absent** |

`app/` at the package root is only `api/examples/**` (shared API examples; not a mixed Next+Remix app tree).

## Isolation

- Next App Router + `next.config` stay in `runtime/nextjs/**`.
- Remix `root` / `routes` / `remix.config` stay in `runtime/remix/**`.
- `components.json.jinja` css paths point at those runtime-isolated files (`runtime/nextjs/app/globals.css` vs `runtime/remix/app/styles/globals.css`), not flattened `app/globals.css`.

## plan.md

SaaS Next/Remix flatten **stays dropped**. Copier continues to emit runtime files from `runtime/{nextjs,remix}` only.
