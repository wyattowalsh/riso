# W5-AUDIT — payloads-node

- **Mission:** `AUDIT-payloads-node` (read-only)
- **Lane:** `payloads-node`
- **Date:** 2026-08-14
- **Repo:** `/Users/ww/dev/projects/riso` (workspace; `.git/HEAD` `read_file` hook-denied)
- **Branch:** `main` (ASSURANCE / W0-T01b / W2-NODE-join; no checkout)
- **HEAD (prior evidence):** `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- **Write root:** this file only
- **Product-code edits:** **0**
- **`samples/*/render/**` writes:** **0** (dests were read, never edited)
- **Python:** not invoked
- **Filter:** `template/files/node/**` including `docs/**` and `saas/**`

SSOT read first: `goal.md`, `facts.md`, `plan.md`, `ASSURANCE.md`, `residuals/{GOAL,PLATFORM,CLI,OPENSPEC,SKILL}.md`. Claims below are from live template reads, not stale ASSURANCE prose.

## Method

- `list_dir` on `template/files/node`, `node/docs`, `node/saas`, `node/saas/runtime/{nextjs,remix}`
- `grep` for `output:`, `gen-api-docs` / `prebuild`, `tailwind.config`, leftover remapped keys, Node engines
- Live reads of fumadocs `next.config.ts.jinja`, docusaurus `package.json.jinja` / `docusaurus.config.ts.jinja` / `sidebars.ts.jinja`, SaaS runtimes, `package.json.jinja`, Dockerfile
- Flatten probes: `read_file` on `node/saas/{next.config.js,remix.config.js,middleware.ts}.jinja` → **absent**
- Tailwind probe: `read_file` on `node/docs/docusaurus/tailwind.config.ts.jinja` → **absent**; `rg tailwind.config` under `template/files/node` → **empty**
- Official-matrix dests used as **smoke evidence only** (not sources of truth for the current template):
  - `samples/docs-docusaurus/smoke-results.json`
  - `samples/docs-fumadocs/smoke-results.json`
  - `samples/docs-fumadocs/render/node/docs/fumadocs/next.config.ts` (stale vs live jinja)

## Known historical bugs

| Historical | Live disposition | Severity |
| --- | --- | --- |
| fumadocs `next.config.ts` `output` typed as `string` (needs `as const` / `NextConfig`) | Live jinja L13 is `output: 'export' as const`. JSDoc `@type {import('next').NextConfig}` (L10) is **not** a TypeScript annotation — W3 dest without `as const` still TS2345. | **closed** in template; dest stale |
| docusaurus `gen-api-docs` prebuild fail | Still open. Sample `docs-docusaurus` has `docusaurus_openapi: enabled` + `api_module` + `api_languages: [node]`, so `prebuild` is emitted. First failure is a named export, not a missing spec. | **P0** |
| leftover `tailwind.config.ts.jinja` must stay deleted | Path absent; no `tailwind.config` hits under `template/files/node`. Tailwind v4 is CSS-first (`src/css/tailwind.css.jinja`). | **closed** |
| SaaS `runtime/nextjs` and `runtime/remix` both exist; flatten stays dropped | Both dirs present. Root Next/Remix configs **absent**. | **closed** |

## Findings

### NODE-P0-docusaurus-mermaid-named-export — P0

- **File:** `template/files/node/docs/docusaurus/docusaurus.config.ts.jinja`
- **Live:** L91–96 named-export the mermaid token bag from the Docusaurus config module:

```91:96:template/files/node/docs/docusaurus/docusaurus.config.ts.jinja
const mermaidThemeByColorMode = {
  light: mermaidThemeVariablesLight,
  dark: mermaidThemeVariablesDark,
};

export { mermaidThemeByColorMode };
```

- **Why it breaks:** Docusaurus treats **all named exports** of `docusaurus.config.ts` as config fields. `docs-docusaurus` smoke (`samples/docs-docusaurus/smoke-results.json`) `prebuild` → `docusaurus gen-api-docs api` exits 1:

```text
[ERROR] Error: These field(s) ("mermaidThemeByColorMode",) are not recognized in docusaurus.config.ts.
If you still want these fields to be in your configuration, put them in the "customFields" field.
```

- **Gating that turns this on:** `samples/docs-docusaurus/copier-answers.yml` `docusaurus_openapi: enabled`, `docusaurus_mermaid: enabled`, `api_module: enabled`, `api_languages: [node]`. Template `package.json.jinja` L8–10 emits `prebuild` only under that gate — and that gate **is** the official sample.
- **Fix (NODE lane):** stop named-exporting from `docusaurus.config.ts`. Keep `mermaidThemeByColorMode` as a file-local const (already referenced at L563), or move the dark twin to `customFields` / a sibling module that is **not** `docusaurus.config.ts`.

### NODE-P1-docusaurus-sidebar-js — P1

- **File:** `template/files/node/docs/docusaurus/sidebars.ts.jinja`
- **Live:** L88–100 (same openapi gate) `require('./docs/api-reference/sidebar.js')` at config-load time:

```88:100:template/files/node/docs/docusaurus/sidebars.ts.jinja
{%- if docusaurus_openapi == 'enabled' and api_module == 'enabled' and api_languages %}

  api: [
    {
      type: 'category',
      label: 'API',
      ...
      items: require('./docs/api-reference/sidebar.js').default,
    },
  ],
{%- endif %}
```

- **Why it is still open:** `docs/api-reference/sidebar.js` is produced by `docusaurus gen-api-docs`. `prebuild` is that command. After P0 is fixed, the same `prebuild` will load `sidebars.ts` before the file exists. Render dest has **no** `docs/api-reference/` tree. Spec itself is present (`openapi/openapi.yaml.jinja` gated the same way).
- **Fix:** drop the eager `require`; use only the autogenerated `docs` sidebar `dirName: 'api-reference'` block (already L54–71); or wrap the require in a try/exists guard; or commit a stub `sidebar.js` that gen-api-docs overwrites.

### NODE-CLOSED-fumadocs-output-as-const — closed

- **File:** `template/files/node/docs/fumadocs/next.config.ts.jinja`
- **Live:**

```10:25:template/files/node/docs/fumadocs/next.config.ts.jinja
/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  output: 'export' as const,
  ...
};
export default withMDX(config);
```

- **W3 dest is stale:** `samples/docs-fumadocs/render/node/docs/fumadocs/next.config.ts` L12 is `output: 'export'` **without** `as const`. Smoke TS2345:

```text
next.config.ts(24,24): error TS2345: Argument of type '{ ... output: string; ... }' is not assignable to parameter of type 'NextConfig'.
  Types of property 'output' are incompatible.
    Type 'string' is not assignable to type '"export" | "standalone" | undefined'.
```

- JSDoc `@type` did **not** make `config` a `NextConfig` (error type is the inferred object, not `NextConfig`). Live `as const` is the prescribed fix. Optional hardening (not required to close this item): `import type { NextConfig } from 'next'` + `satisfies NextConfig`. Do not hand-edit the dest; official re-render will pick up L13.
- **Fix:** none. Do not regress `as const`. Do not restore `rewrites()`.

### NODE-P1-fumadocs-middleware-static-export — P1

- **Files:** `template/files/node/docs/fumadocs/middleware.ts.jinja`, `template/files/node/docs/fumadocs/next.config.ts.jinja`
- **Live:** `output: 'export' as const` (config L13) **and** middleware that `NextResponse.rewrite`s `/docs` → `/llms.mdx/docs` when `fumadocs_llms_txt == 'enabled'` (middleware L1–21). Official `docs-fumadocs` sample has `fumadocs_llms_txt: enabled`. W2-NODE-T02 already removed `rewrites()` because they are invalid with static export; the middleware rewrite is the same class of API.
- W3 stderr also: Next 16 deprecates the `middleware` file convention (`use "proxy" instead`). Typecheck failed first, so export+middleware was not the recorded exit cause.
- **Fix:** do not emit `middleware.ts` when `output: 'export'` (static `/llms.mdx/docs/...` routes already exist). Or drop static export if Accept-based negotiation is required. Do not reintroduce `rewrites()`.

### NODE-CLOSED-tailwind-config-deleted — closed

- **File:** `template/files/node/docs/docusaurus/tailwind.config.ts.jinja` (must stay **deleted**)
- **Live:** `read_file` 404. `rg tailwind.config` under `template/files/node` empty. CSS-first surface is `template/files/node/docs/docusaurus/src/css/tailwind.css.jinja` (`@import 'tailwindcss/theme.css'`). Plan NODE-T03 / W2-NODE-T03 honored.
- **Fix:** none. Do not restore.

### NODE-CLOSED-saas-runtimes-unflattened — closed

- **Files:** `template/files/node/saas/runtime/nextjs/**`, `template/files/node/saas/runtime/remix/**`
- **Live present:**
  - `runtime/nextjs/` — `app/`, `lib/`, `docs/`, `tests/`, `middleware.ts.jinja`, `next.config.js.jinja`, `postcss.config.mjs.jinja`
  - `runtime/remix/` — `app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `app/styles/globals.css.jinja`, `postcss.config.mjs.jinja`, `remix.config.js.jinja`
- **Live absent (flatten probes):** `node/saas/next.config.js.jinja`, `node/saas/remix.config.js.jinja`, `node/saas/middleware.ts.jinja`. Root `app/` is only `api/examples/**`. `components.json.jinja` L9 css paths stay runtime-isolated.
- Generated Node floor stays **20**: `node/docs/{fumadocs,docusaurus}/package.json.jinja` engines `>=20.0.0`; `node/saas/package.json.jinja` L7–8; `node/mcp/package.json.jinja` L38–39; SaaS Dockerfile `FROM node:20-alpine`; generated `mise.toml.jinja` `node = "20"`.
- No leftover remapped keys under `template/files/node` (`saas_auth` / `saas_billing` / `include_admin` / `saas_starter_module` / `api_tracks` / `api_language` / `mcp_language` / `docs_site` rg empty). Auth payload is clerk/authjs only.
- **Fix:** none. Flatten stays dropped.

### NODE-P1-api-node-missing-package-json — P1

- **File:** `template/files/node/apps/api-node/` (missing `package.json.jinja`)
- **Live:** only `src/{config,health,main}.ts.jinja` and `tests/test_api_fastify.spec.ts.jinja`. Dest `samples/docs-docusaurus/render/node/apps/api-node/` matches (no `package.json`).
- Root `template/files/package.json.jinja` L10 / L38–40 still workspace-includes `node/apps/api-node` and scripts `pnpm --filter api-node run {dev,build,test}`. Maintainer Dockerfiles (foreign tree) `COPY apps/api-node/package.json`. `pnpm --filter api-node` cannot resolve a package with no manifest.
- **Fix:** add `template/files/node/apps/api-node/package.json.jinja` (`name: api-node`, Node `>=20`, vitest/fastify scripts). Do not invent a flatten; keep the package under `node/apps/api-node`.

### NODE-P1-saas-flatten-path-leftovers — P1

- **Files:** `template/files/node/saas/Dockerfile.jinja`, `template/files/node/saas/runtime/remix/remix.config.js.jinja`, `template/files/node/saas/package.json.jinja`
- **Live leftovers that still assume a flattened app root:**
  - Dockerfile L60–62 copies `/app/.next`, `/app/public`, `/app/next.config.js`. Next config actually renders at `runtime/nextjs/next.config.js`. No `public/` payload under `node/saas`.
  - Remix Cloudflare (`samples/saas-starter/remix-cloudflare-neon-drizzle/copier-answers.yml` `saas_runtime: remix-2`, `saas_hosting: cloudflare`) emits `server: './server.ts'` (`remix.config.js.jinja` L5–8) but **no** `server.ts.jinja` exists under `runtime/remix` (or elsewhere in `node/saas`).
  - `package.json.jinja` L32 `db:seed` runs `prisma/seed.ts` or `db/seed.ts`; prisma schema is `integrations/orm/prisma/schema.prisma` (L61–64). Flatten `prisma/` / `db/` dirs are absent (W2-SAAS-T03).
- **Fix:** point Docker/COPY and seed scripts at `runtime/{nextjs,remix}` / `integrations/orm/**`. Add a Remix Cloudflare `server.ts` under `runtime/remix` **or** drop the `server: './server.ts'` key when the file is not shipped. Do not copy Next+Remix configs back to the SaaS package root.

## Strengths (not extra findings)

- Canonical Copier keys only in this tree; remap leftovers rg-empty.
- Generated Node engines/mise pin **20**, not maintainer 22.
- Fumadocs mermaid theme adapter + gated diagrams still present (`components/mermaid/{index,theme}.ts.jinja`).
- Docusaurus mermaid uses `theme: { light: 'base', dark: 'base' }` + DESIGN token bags (the bug is the **export**, not the tokens).
- `next.config.mjs.jinja` leftover is gone (fumadocs is `next.config.ts.jinja` only).

## Not this lane

- PAY-P0-06 (`template/files/.github/workflows/riso-quality.yml.jinja` `pytest tests/test_mcp.py`) — payloads workflow, not `node/**`.
- `just validate-agents` missing `samples/default/render` — PLATFORM; restore only via official render after payload smoke is green.
- Root `.docker/Dockerfile*.jinja` path `apps/api-node` vs dest `node/apps/api-node` — foreign tree.

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 1 — this evidence file |
| Product / template edits | 0 |
| `samples/*/render/**` hand-edits | 0 |
| Lockfile edits | 0 |
| Secrets printed | 0 |
| Commit / tag / push | 0 |
