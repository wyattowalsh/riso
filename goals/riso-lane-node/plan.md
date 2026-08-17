# Plan — Riso Lane NODE (non-SaaS Node/TypeScript)

## Solution approach

Bounded **lane execution** on the Riso Copier maintainer repo: validate non-SaaS Node scaffold, fix defects **only** under the exclusive write root, and emit **COORD handoffs** for contract/out-of-root gaps. Optimized for a **massively parallel subagent team** with exclusive file-write shards (no two agents write the same path).

### Hard constraints (always on)

| Rule | Detail |
| --- | --- |
| Write root | `template/files/node/**` **except** `template/files/node/saas/**` |
| Never write | `node/saas/**`, `saas-starter/**`, `copier.yml`, `hooks/**`, `macros/**`, `module_catalog.json.jinja`, other language/desktop/frontend trees, `src/riso/**`, `web/**`, `samples/*/render/**`, `samples/*/copier-answers.yml` |
| No git | No branches/worktrees/commits/pushes unless human asks |
| No locks | Never hand-edit `uv.lock` / `pnpm-lock.yaml` |
| No new answers | No new Copier keys; handoff to COORD |
| Tooling | `uv run` for Python; `pnpm` only when exercising Node surfaces |
| Secrets | Never commit/print/persist |
| Depth | Validate → fix owned defects → COORD handoffs; **no dep modernization** unless a gate fails |

### Priority (serial only when capacity-constrained)

Fumadocs → Docusaurus → TypeScript MCP → api-node → workspace/shared-config/release.

When running the full parallel graph below, **all surface shards run in Wave 2 simultaneously**; priority is used only if the orchestrator must drop shards under time pressure.

### Codebase snapshot

| Surface | Path | Notes |
| --- | --- | --- |
| Fumadocs | `template/files/node/docs/fumadocs/**` | Large package: app/, content/, components/, lib/, openapi/, scripts/, package.json |
| Docusaurus | `template/files/node/docs/docusaurus/**` | docs/, blog/, src/, openapi/, workflows, package.json |
| TS MCP | `template/files/node/mcp/**` | package + tools/resources/prompts (~13 jinja) |
| api-node | `template/files/node/apps/api-node/**` | **4 files only** (src ×3 + 1 skipped test); **no** package-local `package.json.jinja` / `tsconfig` |
| Lane workspace | `template/files/node/pnpm-workspace.yaml.jinja` | Keep `saas` list entry; never edit saas content |
| Root workspace/package | `template/files/pnpm-workspace.yaml.jinja`, `template/files/package.json.jinja` | **Outside write root** → handoff only |
| shared-config | `template/files/node/shared-config/logic.ts.jinja` | Thin |
| release | `template/files/node/release/commitizen.config.js.jinja` | Thin |
| Gates | `template/macros/module_flags.jinja` | Read-only (`docs_fumadocs()`, `node_api_enabled()`, …) |
| Samples | `docs-fumadocs`, `docs-docusaurus`, `mcp-typescript` | Validate only; answers = PLATFORM |

Owned non-SaaS Jinja ≈ 128 files vs saas ≈ 193 (forbidden).

---

## Parallelization model

### Agent roles

| Role ID | Capability | Write scope |
| --- | --- | --- |
| **ORCH** | Orchestrator (serial) | No template writes; runs gates, merges findings, owns handoff list |
| **INV** | Inventory / boundary | Read-only |
| **VAL-\*** | Validators | Read-only (command runners) |
| **FD-\*** | Fumadocs writers | Exclusive shards under `docs/fumadocs/` |
| **DX-\*** | Docusaurus writers | Exclusive shards under `docs/docusaurus/` |
| **MCP-\*** | MCP writers | Exclusive shards under `mcp/` |
| **API** | api-node writer | All of `apps/api-node/**` (tiny; single agent) |
| **WS** | Workspace/shared/release | Only `pnpm-workspace.yaml.jinja`, `shared-config/**`, `release/**` |
| **AUDIT** | Untouched-SaaS + forbidden-path audit | Read-only `git status` / path checks |
| **HO** | Handoff author | Writes only under `goals/riso-lane-node/` (handoffs.md) |

### Exclusive-write shards (no overlapping writers)

```
FD-pkg   → template/files/node/docs/fumadocs/package.json.jinja
           + root-level configs in fumadocs/ (next.config, tsconfig, source.config,
             mdx-components, postcss, middleware, .env.example, .gitignore, README,
             fumadocs.config.ts.jinja if present)
FD-app   → template/files/node/docs/fumadocs/app/**
FD-content → template/files/node/docs/fumadocs/content/**
FD-comp  → template/files/node/docs/fumadocs/components/**
FD-lib   → template/files/node/docs/fumadocs/lib/**
           + openapi/** + scripts/** + static/** + .github/**

DX-pkg   → template/files/node/docs/docusaurus/package.json.jinja
           + docusaurus.config.ts, sidebars, tsconfig, babel, eslint, tailwind,
             .gitignore, README
DX-docs  → template/files/node/docs/docusaurus/docs/**
DX-src   → template/files/node/docs/docusaurus/src/**
DX-meta  → template/files/node/docs/docusaurus/blog/**
           + openapi/** + static/** + i18n/** + .github/**

MCP-pkg  → template/files/node/mcp/package.json.jinja
           + biome.json.jinja + tsconfig.json.jinja
MCP-src  → template/files/node/mcp/src/**

API      → template/files/node/apps/api-node/**

WS       → template/files/node/pnpm-workspace.yaml.jinja
           + shared-config/** + release/**
```

**Conflict rule:** Same-file edits are forbidden across agents. If two findings hit one file, ORCH serializes a single fix pass for that file after Wave 2.

### Wave DAG (high level)

```
Wave 0  INV + VAL-jinja + VAL-fumadocs + VAL-docusaurus + VAL-mcp   (all parallel, read-only)
          │
          ▼
Wave 1  ORCH-triage  (serial: cluster failures → assign shards; drop empty shards)
          │
          ▼
Wave 2  FD-* ∥ DX-* ∥ MCP-* ∥ API ∥ WS   (all independent write shards in parallel)
          │
          ▼
Wave 3  VAL-jinja + VAL-fumadocs + VAL-docusaurus + VAL-mcp + AUDIT   (parallel re-verify)
          │
          ▼
Wave 4  ORCH-retry  (serial only for remaining failures; re-dispatch minimal shards)
          │
          ▼
Wave 5  HO + ORCH-done  (handoffs.md + done checklist)
```

---

## Hyperfine task graph

Each task: **ID · Agent · Deps · Paths · Action · Verify · Done-when**.

### Wave 0 — Discover & fail-first validate (full parallel)

| ID | Agent | Deps | Paths (read) | Action | Verify | Done-when |
| --- | --- | --- | --- | --- | --- | --- |
| **T0.1** | INV | — | write root + forbidden roots | Enumerate owned files; flag out-of-root refs (root package/workspace, quality, docker, workflows); confirm saas exclusion | Path inventory artifact | Inventory complete; no writes |
| **T0.2** | VAL-jinja | — | `scripts/ci/validate_jinja_templates.py`, all `node/**` jinja | `uv run python scripts/ci/validate_jinja_templates.py` | Exit 0 or structured error list | Result captured |
| **T0.3** | VAL-fumadocs | — | `samples/docs-fumadocs/copier-answers.yml` | `uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json` | JSON ok / error fields | Result captured |
| **T0.4** | VAL-docusaurus | — | `samples/docs-docusaurus/copier-answers.yml` | `uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json` | JSON ok / error fields | Result captured |
| **T0.5** | VAL-mcp | — | `samples/mcp-typescript/copier-answers.yml` | `uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json` | JSON ok / error fields | Result captured |
| **T0.6** | INV | — | `apps/api-node/**`, root package/workspace (read-only) | Document api-node package-gap (no local package.json/tsconfig) + whether gap blocks core three | Gap note for ORCH | Gap classified: in-lane fix vs COORD handoff |
| **T0.7** | INV | — | `node/pnpm-workspace.yaml.jinja` + root workspace | Compare dual workspace files; list drift; mark root changes as handoff | Drift note | Note complete |

**Wave 0 fan-out:** T0.1–T0.7 all start together (T0.6/T0.7 can share INV agent sequentially if only one INV slot; prefer two INV agents if available).

### Wave 1 — Orchestrator triage (serial)

| ID | Agent | Deps | Action | Done-when |
| --- | --- | --- | --- | --- |
| **T1.1** | ORCH | T0.* | Merge validate + inventory; map each failure to exactly one shard ID (FD-pkg, FD-app, …) | Failure→shard matrix written |
| **T1.2** | ORCH | T1.1 | Cancel/skip shards with zero findings (except keep AUDIT + final VAL always) | Active shard list published |
| **T1.3** | ORCH | T1.1 | Classify each issue: `in-lane-fix` \| `coord-handoff` \| `platform-handoff` \| `wont-fix-this-goal` | Classification complete; handoff seeds for HO |

**Triage rules**

- Undefined Copier vars / missing answer keys → **coord-handoff** (never invent keys).
- Root `template/files/package.json.jinja` or root workspace → **platform/coord-handoff**.
- Broken Jinja/conditionals under write root using existing keys → **in-lane-fix**.
- Dep pin bump only if gate fails and fix is otherwise blocked → still no lockfile hand-edit.

### Wave 2 — Parallel fix shards

Activate only shards with `in-lane-fix` work (empty shards no-op).

#### Fumadocs cluster (parallel internals)

| ID | Agent | Deps | Exclusive write paths | Action | Verify |
| --- | --- | --- | --- | --- | --- |
| **T2.FD.pkg** | FD-pkg | T1.2 | fumadocs package.json + top-level configs listed above | Fix scripts/deps/conditionals for existing `fumadocs_*` / `docs_*` answers; no new keys | Jinja parse of touched files |
| **T2.FD.app** | FD-app | T1.2 | `docs/fumadocs/app/**` | Fix routes/layouts/llms/search/blog gates vs existing answers | Jinja parse of touched files |
| **T2.FD.content** | FD-content | T1.2 | `docs/fumadocs/content/**` | Fix MDX/meta for modules (api-node, mcp, …) without inventing modules | Jinja parse |
| **T2.FD.comp** | FD-comp | T1.2 | `docs/fumadocs/components/**` | Fix component Jinja conditionals (search, sidebar, banner, openapi page, …) | Jinja parse |
| **T2.FD.lib** | FD-lib | T1.2 | `lib/**`, `openapi/**`, `scripts/**`, `static/**`, `.github/**` under fumadocs | Fix helpers, openapi stubs, deploy workflow templates | Jinja parse |

#### Docusaurus cluster (parallel internals)

| ID | Agent | Deps | Exclusive write paths | Action | Verify |
| --- | --- | --- | --- | --- | --- |
| **T2.DX.pkg** | DX-pkg | T1.2 | docusaurus package + config/sidebars/tooling files | Align with existing `docusaurus_*` answers | Jinja parse |
| **T2.DX.docs** | DX-docs | T1.2 | `docs/docusaurus/docs/**` | Fix guides/modules/reference MD | Jinja parse |
| **T2.DX.src** | DX-src | T1.2 | `docs/docusaurus/src/**` | Components/CSS/pages | Jinja parse |
| **T2.DX.meta** | DX-meta | T1.2 | blog/, openapi/, static/, i18n/, .github/ under docusaurus | Ancillary surfaces + workflows | Jinja parse |

#### MCP cluster

| ID | Agent | Deps | Exclusive write paths | Action | Verify |
| --- | --- | --- | --- | --- | --- |
| **T2.MCP.pkg** | MCP-pkg | T1.2 | mcp package.json, biome, tsconfig | Scripts/deps/tooling consistency for TS MCP sample | Jinja parse |
| **T2.MCP.src** | MCP-src | T1.2 | `mcp/src/**` | Tools/resources/prompts/index/config vs `mcp_transport`, `mcp_example_tools`, languages | Jinja parse |

#### api-node (single agent — small tree)

| ID | Agent | Deps | Exclusive write paths | Action | Verify |
| --- | --- | --- | --- | --- | --- |
| **T2.API** | API | T1.2, T0.6 | `apps/api-node/**` | Fix Fastify main/config/health/tests; if package.json/tsconfig belong in-lane and use existing keys, add under write root; else emit handoff seed (do **not** edit root package.json) | Optional: `uv run riso validate --answers-file samples/circleci-node/copier-answers.yml --json` if API touched and sample available |

#### Workspace / shared / release

| ID | Agent | Deps | Exclusive write paths | Action | Verify |
| --- | --- | --- | --- | --- | --- |
| **T2.WS** | WS | T1.2, T0.7 | `node/pnpm-workspace.yaml.jinja`, `shared-config/**`, `release/**` | Fix non-SaaS globs only; **preserve saas list entry**; handoff conditionals needing new keys | Diff shows no saas content; saas entry retained |

### Wave 3 — Parallel re-verification

| ID | Agent | Deps | Action | Done-when |
| --- | --- | --- | --- | --- |
| **T3.1** | VAL-jinja | T2.* (all active) | Re-run Jinja validate | Exit 0 or residual error list |
| **T3.2** | VAL-fumadocs | T2.FD.* | Re-run docs-fumadocs validate | JSON success or residual list |
| **T3.3** | VAL-docusaurus | T2.DX.* | Re-run docs-docusaurus validate | JSON success or residual list |
| **T3.4** | VAL-mcp | T2.MCP.* | Re-run mcp-typescript validate | JSON success or residual list |
| **T3.5** | AUDIT | T2.* | `git status` / path audit: zero changes under saas, copier, hooks, macros, catalog, other lanes, render/, lockfiles | Audit clean |

### Wave 4 — Minimal retry (serial dispatch, parallel shards)

| ID | Agent | Deps | Action | Done-when |
| --- | --- | --- | --- | --- |
| **T4.1** | ORCH | T3.* | If residuals remain and are in-lane, re-open **only** failed shards | Retry set ≤ previous active set |
| **T4.2** | (reused shard agents) | T4.1 | Second fix pass with same exclusive paths | Shards complete |
| **T4.3** | VAL-* + AUDIT | T4.2 | Re-run failed validators + audit | Core three + Jinja green or residual reclassified as handoff |

Stop after one retry cycle unless human expands scope. Remaining in-lane unknowns → document; contract gaps → handoff.

### Wave 5 — Handoffs & done

| ID | Agent | Deps | Write | Action | Done-when |
| --- | --- | --- | --- | --- | --- |
| **T5.1** | HO | T1.3, T4.3 | `goals/riso-lane-node/handoffs.md` | List COORD/PLATFORM handoffs (one bullet each: problem, evidence, suggested owner) | File written (may be empty list) |
| **T5.2** | ORCH | T5.1, T3/T4 green | — | Done checklist vs `facts.md` | All automated facts checked |

**Final commands (ORCH or VAL agents):**

```bash
uv run python scripts/ci/validate_jinja_templates.py
uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json
uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json
uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json
git status --short -- template/files/node/saas template/copier.yml template/hooks template/macros \
  template/files/module_catalog.json.jinja uv.lock '**/pnpm-lock.yaml' samples
```

---

## Orchestrator dispatch recipe

```
1. Spawn Wave 0: parallel INV, VAL-jinja, VAL-fumadocs, VAL-docusaurus, VAL-mcp
   (optional second INV for T0.6/T0.7 if bandwidth).
2. Wait for all Wave 0 task_ids.
3. Run T1.1–T1.3 serially in ORCH context.
4. Spawn Wave 2: one subagent per active shard with:
     - exclusive write path list in prompt
     - forbidden path list
     - "no new answer keys; handoff instead"
     - "no git / no lockfiles / no secrets"
5. Wait for all Wave 2 task_ids.
6. Spawn Wave 3 validators + AUDIT in parallel; wait.
7. If residuals: T4 once; else skip to Wave 5.
8. HO writes handoffs.md; ORCH marks goal complete.
```

**Max parallelism (full graph):** ~4 validators + inventory + up to **12 write shards** + audit ≈ **17 concurrent agents** in the fattest wave (Wave 2), without path conflicts.

**Min parallelism (capacity-constrained):** collapse to priority order single-threaded: FD → DX → MCP → API → WS, still using same task IDs.

---

## Dependency graph (compact)

```text
T0.1 ─┐
T0.2 ─┤
T0.3 ─┼─► T1.1 ► T1.2 ► T1.3 ─┬─► T2.FD.* ─┐
T0.4 ─┤                        ├─► T2.DX.* ─┤
T0.5 ─┤                        ├─► T2.MCP.* ┼─► T3.* ─► T4? ─► T5.1 ► T5.2
T0.6 ─┤                        ├─► T2.API  ─┤
T0.7 ─┘                        └─► T2.WS   ─┘
```

---

## Verification matrix (maps to automated facts)

| Fact ID | Command / check | Wave |
| --- | --- | --- |
| verify-jinja | `uv run python scripts/ci/validate_jinja_templates.py` | 0, 3, 4 |
| verify-fumadocs | `uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json` | 0, 3, 4 |
| verify-docusaurus | `uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json` | 0, 3, 4 |
| verify-mcp-ts | `uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json` | 0, 3, 4 |
| hard-exclude-saas | AUDIT: no diffs under `template/files/node/saas/**` | 3, 5 |
| hard-exclude-coord | AUDIT: no diffs under copier/hooks/macros/catalog | 3, 5 |
| no-lockfile-hand-edit | AUDIT: no lockfile diffs | 3, 5 |
| done-condition | All above + handoffs listed | 5 |

---

## Risks

1. **api-node package incompleteness** — only 4 source/test templates; install/build may depend on root package (out of lane). Mis-fixing in-lane without handoff leaves monorepo broken.
2. **Dual workspace files** — lane vs root drift; root not writable by NODE.
3. **SaaS workspace entry** — preserved; conditionalizing is COORD.
4. **Cross-lane quality/docker/CI filters** for `api-node` — outside write root; handoff only.
5. **False parallel thrash** — ORCH must enforce exclusive shards; never spawn two writers on same file.
6. **Sample answers drift** — PLATFORM owns answers; if validate fails on answers content, handoff PLATFORM, do not edit answers.

## Done condition

Per `goals/riso-lane-node/facts.md`: core three validates (+ Jinja) pass, `node/saas/**` untouched, no contract edits, COORD/PLATFORM handoffs listed when needed, no unauthorized git/lockfile/render changes.
