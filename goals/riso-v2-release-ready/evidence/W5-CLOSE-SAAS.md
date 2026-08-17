# W5 CLOSE-SAAS — flatten-path leftovers

- Wave: CLOSE-SAAS / lane SAAS
- Date: 2026-08-14
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive writes: `template/files/node/saas/**`, `template/files/saas-starter/**`, this file
- `samples/*/render/**` writes: **0**
- Status: **green** (lock P0/P1 closed)

## Confirmed finding (re-verified live)

`NODE-P1-saas-flatten-path-leftovers` was still live after W2 unflatten:

| Surface | Before | After |
| --- | --- | --- |
| `Dockerfile.jinja` runner COPY | `/app/.next`, `/app/public`, `/app/next.config.js`; Remix `/app/build` + `/app/public` | Next: `runtime/nextjs/.next` + `runtime/nextjs/next.config.js`. Remix: `runtime/remix/build`. No `public/` (no payload). |
| `package.json.jinja` `db:seed` | `prisma/seed.ts` / `db/seed.ts` | `integrations/orm/prisma/seed.ts` / `integrations/orm/drizzle/seed.ts` |
| `package.json.jinja` `prisma.seed` | absent | `tsx integrations/orm/prisma/seed.ts` when fixtures on |
| `package.json.jinja` next/remix CLI | flatten cwd (`next build`, `remix-serve build/index.js`) | `runtime/nextjs` / `runtime/remix` so Docker `pnpm start` matches COPY |
| `runtime/remix/remix.config.js.jinja` | Cloudflare `server: './server.ts'` with no `server.ts.jinja` | Dropped `server` key (no new Cloudflare vendor). Kept `serverModuleFormat` + `serverBuildPath`. |
| Seed payloads | 404 | `integrations/orm/{prisma,drizzle}/seed.ts.jinja` gated on `saas_include_fixtures` |

Flatten stay-dropped probes still **absent** at `node/saas` root: `next.config.js.jinja`, `remix.config.js.jinja`, `middleware.ts.jinja`, `public/`, `prisma/`, `db/`. Runtimes remain under `runtime/{nextjs,remix}`. Generated Node floor stays **20**.

Did **not** add `@remix-run/cloudflare*`. Official dest refresh is PLATFORM (`render-samples.sh` / `render_matrix.py`); dest was not hand-edited.

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas/Dockerfile.jinja \
  template/files/node/saas/package.json.jinja \
  template/files/node/saas/runtime/remix/remix.config.js.jinja \
  template/files/node/saas/integrations/orm/prisma/seed.ts.jinja \
  template/files/node/saas/integrations/orm/drizzle/seed.ts.jinja \
  template/files/node/saas/runtime/nextjs \
  template/files/node/saas/runtime/remix
# Validated 33 Jinja template(s): all OK
# RENDER_ASSERT_OK (next+prisma and remix+cloudflare+drizzle+fixtures)
```

Rendered checks (in-process Jinja, not dest writes):

- Next Docker COPY stays under `runtime/nextjs/`; no root `next.config.js` / `public`
- Remix Docker COPY stays under `runtime/remix/build`
- `db:seed` + Prisma `seed` point at `integrations/orm/**`
- Cloudflare remix.config has no `./server.ts`
- Seed files emit `demo@example.com` fixtures; empty when fixtures off

## Tests

Maintainer `tests/**` is a foreign tree (not in this lock). No silent test add. Behavior change is asserted by jinja syntax + rendered path contract above.

## Foreign / not this lock

- Official `samples/*/render/**` still stale until PLATFORM re-renders
- `docs/migrations/orm.md.jinja` still shows historical `prisma/seed.ts` / `db/seed.ts` as ORM-migration prose (not Docker leftovers)
- `@/db/schema` imports and `.github/workflows/database.yml.jinja` flatten path globs were not in the confirmed P1 list

## Path lock

| Class | Count |
| --- | --- |
| This-session product writes | 5 template files (3 edited, 2 added) |
| Evidence | this file |
| `samples/*/render/**` | 0 |
| Lockfiles / secrets / commit / tag / push | 0 |
| Foreign-tree edits | 0 |
