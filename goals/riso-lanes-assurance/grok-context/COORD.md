# Lane COORD

## Mission (3 lines)
Apply open contract handoffs serially in W1 (copier.yml / hooks / macros / catalog / prompts / context).
Publish outbox deltas for payload + PLATFORM follow-through. Never parallelize writers on the same contract file.
Correctness first; no product-module invention.

## Exclusive write roots
- `template/copier.yml`
- `template/hooks/**`
- `template/macros/**`
- `template/files/module_catalog.json.jinja`
- `template/prompts/**`
- `.github/context/**`
- `template/files/.github/context/**` (byte-parity with `.github/context/**`)
- `goals/riso-lane-coord/**` (package + outbox)

## Forbidden roots
- `samples/*/render/**` (never hand-edit)
- `uv.lock` / `pnpm-lock.yaml` (hand-edit)
- secrets / `.env*`
- reintroduce `riso-mcp`
- payload trees: `template/files/{python,node,go,rust,electron,tauri,saas-starter,quality,testing}/**`
- `src/riso/**`, `scripts/ci/**`, `samples/*/copier-answers.yml`

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-coord/facts.md`
- Plan: `goals/riso-lanes-assurance/plan.md` (W1 section)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
Serial only (deps chain):
| ID | Handoff / work | Priority |
|----|----------------|----------|
| W1-H01 | `coord-mcp-languages-typescript` — add `typescript` to `mcp_languages` (or publish rename) | P0 |
| W1-H02 | `COORD-go-version-mcp` — extend `go_version` when for MCP go | P1 |
| W1-H03 | `COORD-rust-module-excludes` — `_exclude` for rust/cli + rust/api | P2 |
| W1-H04 | `exclude-empty-dirs` — python optional empty-dir `_exclude` | P1 |
| W1-H05 | `api-features-normalize` — hook align with CLI normalize | P1 |
| W1-H06 | `graphql-sample-coverage` policy (COORD residual vs PLATFORM answers) | P2 |
| W1-H07 | module_catalog / prompts smoke if rows changed | — |
| W1-H08 | context parity if context touched | — |
| W1-OUT | Publish outbox under `goals/riso-lane-coord/outbox/` per change-id; re-smoke bootstrap-verify | — |

**Barrier:** W0 join green. **One change-id → one conventional commit recommended.**

## COORD outbox paths to read
- Write (this lane): `goals/riso-lane-coord/outbox/<change-id>.md`
- Read PLATFORM inbox source: `goals/riso-lane-platform/outbox/coord-mcp-languages-typescript.md`
- Read SYS handoffs: `goals/riso-lane-sys/handoffs/COORD-go-version-mcp.md`, `COORD-rust-module-excludes.md`
- Read PY handoffs: `goals/riso-lane-py/handoffs/exclude-empty-dirs.md`, `api-features-normalize.md`, `graphql-sample-coverage.md`
- Existing: `goals/riso-lane-coord/outbox/bootstrap-verify.md` (applied; re-smoke at W1-OUT)

## Dirty paths assigned
From `inventory-dirty.md` (19 paths — package only; no contract tree dirty yet):
- All under `goals/riso-lane-coord/**` (APPLY-CHECKLIST, LANE, README, examples, facts*, goal, handoff-template, inbox, interview*, outbox*, plan*)
- Product contract trees are clean until W1 applies.

## Verify commands (copy-paste)
```bash
# Always uv run for Python
uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json   # W1-H01
uv run riso validate --answers-file samples/go-mcp/copier-answers.yml --json             # W1-H02
# W1-H03: grep rust excludes + dry validate monorepo if present
rg -n "_exclude|rust/cli|rust/api" template/copier.yml template/hooks || true
uv run riso validate --answers-file samples/cli-docs/copier-answers.yml --json           # W1-H04
uv run riso validate --answers-file samples/api-python/copier-answers.yml --json         # W1-H05
uv run riso validate --answers-file samples/full-stack/copier-answers.yml --json         # W1-H05
uv run riso catalog                                                                       # W1-H07 (if catalog changed)
uv run riso prompts                                                                       # W1-H07
uv run python scripts/ci/verify_context_sync.py                                           # W1-H08
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/COORD.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- Template: `goals/riso-lane-coord/handoff-template.md` / `outbox-template.md`
- Never silent cross-lane edit — residual with owner, failing command, redacted log, blocking reason.

## Done =
All W1-H01…H08 applied or residualed; W1-OUT outbox published; mcp-typescript + go-mcp validate green (or residual with evidence); board statuses updated; evidence under `goals/riso-lanes-assurance/evidence/`.
