# Residual — Lane NODE (W5-CLOSE-NODE)

## Summary

Lock P0/P1 under `template/files/node/**` except `node/saas/**` are closed in the template. Official dests are stale until PLATFORM re-renders. Maintainer pytest for the new contracts was not added because `tests/**` is outside this lock.

`samples/*/render/**` writes this lane: **0**. `render_matrix.py` was not residualed, started, or killed.

## Residuals

### R1 — official dests still carry the old Node docs / api-node payloads

| Field | Value |
| --- | --- |
| **task_id** | CLOSE-NODE / dest-rerender |
| **owner** | PLATFORM |
| **status** | open |
| **command** | `./scripts/render-samples.sh --variant docs-docusaurus --answers samples/docs-docusaurus/copier-answers.yml` then the same for `docs-fumadocs`, `docs-fumadocs-full`, `circleci-node`, and `default` (or a later `uv run python scripts/ci/render_matrix.py`). Never hand-edit `samples/*/render/**`. |
| **blocking reason** | Template fixes do not update official dests. `docs-docusaurus` dest still has the named mermaid export and missing `api-node/package.json`. `docs-fumadocs` dest still has `middleware.ts`. `samples/default/render` is absent (`just validate-agents`). |
| **redacted log** | Matrix `docs-docusaurus` / `docs-fumadocs` / `default` `render_status=failed` at last official run. This session did not write dests. |
| **fix** | Official re-render after this template close. Do not hand-create dest files. |
| **evidence** | `goals/riso-v2-release-ready/evidence/W5-CLOSE-NODE.md` |

### R2 — maintainer tests for NODE close contracts (foreign tree)

| Field | Value |
| --- | --- |
| **task_id** | CLOSE-NODE / test-node-templates |
| **owner** | GOAL |
| **status** | open |
| **command** | add `tests/unit/test_node_templates.py` asserting: no `export { mermaidThemeByColorMode }`; no `require('./docs/api-reference/sidebar.js')`; no `template/files/node/docs/fumadocs/middleware.ts.jinja`; fumadocs `output: 'export' as const`; api-node package name/engines>=20/fastify/vitest; tailwind.config.ts.jinja stays deleted |
| **blocking reason** | CLOSE-NODE exclusive writes are `template/files/node/**` except saas plus this residual/evidence pair. `tests/**` is foreign. Ephemeral render assertions already passed in W5-CLOSE-NODE. |
| **redacted log** | ephemeral jinja render assertions: PASS; 31 adjacent unit tests passed |
| **fix** | GOAL/PLATFORM add the pytest module. Do not reopen NODE lock for it. |
| **evidence** | `goals/riso-v2-release-ready/evidence/W5-CLOSE-NODE.md` |

### R3 — npm_surfaces.json missing api-node (optional)

| Field | Value |
| --- | --- |
| **task_id** | CLOSE-NODE / npm-surfaces-api-node |
| **owner** | PLATFORM |
| **status** | open |
| **command** | add an `api-node` row to `scripts/ci/npm_surfaces.json` pointing at `template/files/node/apps/api-node/package.json.jinja` |
| **blocking reason** | `scripts/ci/**` is PLATFORM. Not a payload P0/P1. |
| **redacted log** | `npm_surfaces.json` lists docs-fumadocs, docs-docusaurus, node-mcp-ts, node-saas; no api-node |
| **fix** | PLATFORM add the surface on the next npm bump pass. |
| **evidence** | `scripts/ci/npm_surfaces.json` |

## Closed this wave

- NODE-P0-docusaurus-mermaid-named-export
- NODE-P1-docusaurus-sidebar-js
- NODE-P1-fumadocs-middleware-static-export
- NODE-P1-api-node-missing-package-json
- Fumadocs `as const` not regressed
- `tailwind.config.ts.jinja` not resurrected

## Not this lane

- NODE-P1-saas-flatten-path-leftovers — SAAS (`template/files/node/saas/**`)
