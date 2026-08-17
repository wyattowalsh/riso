# W5-CLOSE-NODE

- **Wave:** CLOSE-NODE
- **Date:** 2026-08-14
- **Repo:** `/Users/ww/dev/projects/riso`
- **Branch:** `main`
- **HEAD:** `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (worktree dirty; this session did not commit)
- **Exclusive writes:** `template/files/node/**` except `node/saas/**`; this file; `residuals/NODE.md`
- **samples render writes:** 0
- **Lockfile / secrets / tag / push:** 0
- **Status:** lock P0/P1 closed (template). Official dests remain stale until PLATFORM re-render.

## Re-verified live (before edit)

| ID | Live | Disposition |
| --- | --- | --- |
| NODE-P0-docusaurus-mermaid-named-export | `docusaurus.config.ts.jinja` still named-exported mermaid bag | **fixed** |
| NODE-P1-docusaurus-sidebar-js | `sidebars.ts.jinja` required `docs/api-reference/sidebar.js` | **fixed** |
| NODE-P1-fumadocs-middleware-static-export | `middleware.ts.jinja` emitted with static export | **fixed** (template deleted) |
| NODE-P1-api-node-missing-package-json | `node/apps/api-node/` had src+tests only | **fixed** |
| NODE-CLOSED-fumadocs-output-as-const | `next.config.ts.jinja` already `as const` | **kept** |
| NODE-CLOSED-tailwind-config-deleted | `docs/docusaurus/tailwind.config.ts.jinja` absent | **kept** |
| NODE-P1-saas-flatten-path-leftovers | `node/saas/**` | **not this lock** (SAAS) |

## Changes

1. Docusaurus config: mermaid token bag stays file-local; no named export. Navbar `sidebarId: api` removed; API docs stay under the `docs` sidebar `dirName: api-reference` category.
2. Docusaurus sidebars: dropped eager `require('./docs/api-reference/sidebar.js')`. OpenAPI plugin v5 writes `sidebar.ts`, not `sidebar.js`.
3. Fumadocs middleware: deleted `template/files/node/docs/fumadocs/middleware.ts.jinja`. Static export cannot use request-time rewrite/proxy. Static `/llms.mdx/docs` routes remain. `output: 'export' as const` not regressed; `rewrites()` not restored.
4. api-node package: added `package.json.jinja` (name `api-node`, engines node `>=20.0.0`, vitest + fastify scripts) and `tsconfig.json.jinja`. `src/main.ts.jinja` starts the server only when executed as the process entry.

## Verify

```text
uv run python scripts/ci/validate_jinja_templates.py <6 touched jinja>
# Validated 6 Jinja template(s): all OK

find template/files/node/docs template/files/node/apps/api-node -name '*.jinja' -type f -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 113 Jinja template(s): all OK

# ephemeral jinja render assertions: PASS
# named mermaid export absent; sidebar.js require absent; output as const present;
# middleware.ts.jinja absent; tailwind.config.ts.jinja absent;
# api-node name/engines>=20/fastify/vitest present

uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json
uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json
uv run riso validate --answers-file samples/docs-fumadocs-full/copier-answers.yml --json
uv run riso validate --answers-file samples/circleci-node/copier-answers.yml --json
# all ok:true (warnings only _commit / _src_path)

uv run pytest tests/unit/test_new_templates.py tests/unit/test_template_validate.py tests/unit/template/test_agents_md_render.py -q -n 0
# 31 passed
```

`render_matrix.py` was not running; not started; not killed. Dest trees were not written.

## Path lock

| Class | Count |
| --- | --- |
| Product writes | 7 under `template/files/node/**` except saas |
| Evidence / residual | this file + `residuals/NODE.md` |
| `node/saas/**` | 0 |
| `samples/*/render/**` | 0 |
| `tests/**` | 0 (foreign; see residual R2) |
| `copier.yml` / hooks / scripts | 0 |

## Not this lane

- Official re-render of docs-docusaurus, docs-fumadocs, circleci-node, default dests — PLATFORM
- `scripts/ci/npm_surfaces.json` api-node row — PLATFORM
- SaaS Docker/seed/Cloudflare flatten leftovers — SAAS
- `just validate-agents` / missing `samples/default/render` — PLATFORM
