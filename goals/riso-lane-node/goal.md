# Goal — Riso Lane NODE (non-SaaS Node/TypeScript)

## Articulated goal

Own the Riso Copier **NODE lane**: exclusive write access to `template/files/node/**` except `template/files/node/saas/**`. Validate non-SaaS Node scaffold (Fumadocs, Docusaurus, TypeScript MCP, Fastify api-node, shared-config, node release config, and non-SaaS workspace fragments), fix defects only under that write root, and emit **COORD handoffs** for contract/out-of-root gaps — without touching SaaS trees, inventing Copier keys, or modernizing dependencies unless a gate fails.

## Shared understanding

Accepted facts: [`facts.md`](./facts.md) (metadata: [`facts.meta.json`](./facts.meta.json)).

Interview: [`interview.json`](./interview.json) → [`interview-result.json`](./interview-result.json).

Facts review: [`facts-review.json`](./facts-review.json) → [`facts-result.json`](./facts-result.json).

### Lane locks (from facts)

| Rule | Detail |
|------|--------|
| Write root | `template/files/node/**` **except** `template/files/node/saas/**` |
| Never write | `node/saas/**`, `saas-starter/**`, `copier.yml`, `hooks/**`, `macros/**`, `module_catalog.json.jinja`, python/go/rust/frontend/electron/tauri trees, `src/riso/**`, `web/**`, `samples/*/render/**`, `samples/*/copier-answers.yml` |
| No new answers | No inventing Copier keys; handoff to COORD |
| No lockfile hand-edit | Never hand-edit `uv.lock` or `pnpm-lock.yaml` |
| No secrets | Never commit, print, or persist secrets |
| Depth | Validate → fix owned defects → COORD handoffs; no dep modernization unless a gate fails |
| Workspace boundary | `pnpm-workspace.yaml.jinja` may keep a `saas` list entry; never edit saas content; handoff conditionals needing new keys |

### Owned surfaces (priority when capacity-constrained)

1. Fumadocs (`template/files/node/docs/fumadocs/**`)
2. Docusaurus (`template/files/node/docs/docusaurus/**`)
3. TypeScript MCP (`template/files/node/mcp/**`)
4. Fastify api-node (`template/files/node/apps/api-node/**`)
5. Workspace / shared-config / release fragments under the write root

## Execution plan

Primary plan: [`plan.md`](./plan.md) — parallel-optimized lane execution with exclusive-write shards (FD/DX/MCP/API/WS), wave DAG (discover → triage → fix → re-verify → handoffs), and verification matrix.

Interview decisions locked into facts:

- **Execution depth:** validate + fix owned paths + COORD handoffs
- **Verification matrix:** three Node samples + Jinja validate
- **Workspace/SaaS boundary:** preserve saas list entry; handoff conditionals

Umbrella integration (when run under assurance): see [`../riso-lanes-assurance/goal.md`](../riso-lanes-assurance/goal.md) and NODE tasks in that plan (NODE-T01… under W2).

## Done condition

Every line in [`facts.md`](./facts.md) is evidenced green or has an owned residual. Concretely:

### Write-root & hygiene

- [ ] Exclusive writes stay under `template/files/node/**` except `node/saas/**` (goal package docs/handoffs under `goals/riso-lane-node/**` allowed)
- [ ] `template/files/node/saas/**` and `template/files/saas-starter/**` remain untouched
- [ ] No edits to `template/copier.yml`, `template/hooks/**`, `template/macros/**`, or `template/files/module_catalog.json.jinja`
- [ ] No edits to python/go/rust/frontend/electron/tauri trees, `src/riso/**`, `web/**`, `samples/*/render/**`, or `samples/*/copier-answers.yml`
- [ ] No unauthorized branches/worktrees/commits/pushes (unless human explicitly asks for this lane package)
- [ ] No hand-edits of `uv.lock` or `pnpm-lock.yaml`
- [ ] No new Copier answer keys invented; contract gaps listed as COORD handoffs
- [ ] No secrets committed, printed, or persisted
- [ ] Python tooling via `uv run`; pnpm only when exercising Node surfaces that require it

### Surfaces & gates

- [ ] Owned surfaces coherent: Fastify api-node, Fumadocs, Docusaurus, TypeScript MCP, shared-config, node release, non-SaaS workspace fragments
- [ ] Execution depth honored: validate → fix owned defects → COORD handoffs; no dep modernization unless a gate fails
- [ ] Fix priority respected when capacity-constrained: Fumadocs → Docusaurus → TS MCP → api-node → workspace/shared-config/release
- [ ] `pnpm-workspace.yaml.jinja` saas list entry preserved when present; saas content never edited; conditionals needing new keys handed to COORD
- [ ] `docs_framework` and MCP-related Node gates stay consistent with existing answers (`fumadocs` / `docusaurus` / `typescript`) without inventing keys

### Verification commands

```bash
uv run python scripts/ci/validate_jinja_templates.py
uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json
uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json
uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json
```

Optional when api-node is touched:

```bash
uv run riso validate --answers-file samples/circleci-node/copier-answers.yml --json
```

Forbidden-path audit (no diffs under saas/contracts/lockfiles/render):

```bash
git status --short -- template/files/node/saas template/copier.yml template/hooks template/macros \
  template/files/module_catalog.json.jinja uv.lock '**/pnpm-lock.yaml' samples
```

### Close bar

- [ ] Three sample validates succeed (docs-fumadocs, docs-docusaurus, mcp-typescript)
- [ ] Jinja validate passes when available for owned Node templates
- [ ] `node/saas/**` remains untouched; no forbidden contract files edited
- [ ] Any COORD/PLATFORM handoffs listed (e.g. `goals/riso-lane-node/handoffs.md` or handoffs board)

## Provenance

| Artifact | Path |
|----------|------|
| Interview | [interview-result.json](./interview-result.json) |
| Facts | [facts-result.json](./facts-result.json) |
| Facts metadata | [facts.meta.json](./facts.meta.json) |
| Plan | [plan.md](./plan.md) |

## Launch

```text
/goal goals/riso-lane-node/goal.md
```
