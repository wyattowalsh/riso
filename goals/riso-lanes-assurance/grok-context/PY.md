# Lane PY

## Mission (3 lines)
Finish + planned-refine Python payload under `template/files/python/**` after W1-OUT.
Correctness green first (dual-gate audit, API/GraphQL/WS/CLI/MCP/docs), then PY-T10 refine only if green.
No foreign-tree edits; empty-dir recheck after COORD excludes.

## Exclusive write roots
- `template/files/python/**` (~145 jinja)
- `goals/riso-lane-py/**` (package + dual-gate script + handoffs)

## Forbidden roots
- `samples/*/render/**` (never hand-edit)
- `uv.lock` / `pnpm-lock.yaml` hand-edit
- secrets / reintroduce `riso-mcp`
- COORD contract: `template/copier.yml`, `template/hooks/**`, `template/macros/**`, prompts, catalog, context
- Other payload: `node/**`, `go/**`, `rust/**`, `electron/**`, `tauri/**`, `saas-starter/**`
- `src/riso/**`, `scripts/ci/**`, `samples/*/copier-answers.yml`

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-py/facts.md` + `goals/riso-lane-py/plan.md`
- Plan: `goals/riso-lanes-assurance/plan.md` (PY sub-graph)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W1-OUT. parallel_group PY0 → PY1 fan-out → PY2 join → PY3 refine.

| ID | Work | parallel_group |
|----|------|----------------|
| PY-T01 | Inventory + dual-gate audit script | PY0 |
| PY-T02 | API FastAPI + health/CRUD jinja | PY1 |
| PY-T03 | GraphQL dual-gate surface | PY1 |
| PY-T04 | WebSocket dual-gate surface | PY1 |
| PY-T05 | Typer CLI under python | PY1 |
| PY-T06 | FastMCP python mcp | PY1 |
| PY-T07 | Sphinx docs + packaging/pyproject gates | PY1 |
| PY-T08 | Shipped tests / codegen / release helpers | PY1 |
| PY-T09 | Join: empty-dir recheck after COORD excludes | PY2 |
| PY-T10 | Planned refine only if green | PY3 |

Handoff follow-through: `exclude-empty-dirs` (W1-H04 + PY-T09), GraphQL dual-gate (PY-T03), `api-features-normalize` is COORD-owned (read outbox only).

## COORD outbox paths to read
- `goals/riso-lane-coord/outbox/` (especially empty-dirs + api-features deltas after W1)
- Lane handoffs (already filed):  
  - `goals/riso-lane-py/handoffs/exclude-empty-dirs.md`  
  - `goals/riso-lane-py/handoffs/api-features-normalize.md`  
  - `goals/riso-lane-py/handoffs/graphql-sample-coverage.md` (answers = PLATFORM)

## Dirty paths assigned
From inventory (26 paths):
- Package: `goals/riso-lane-py/**` (facts*, goal, plan*, handoffs/*, scripts/check_dual_gates.py)
- Product (M):
  - `template/files/python/src/{{ package_name }}/cli/__init__.py.jinja`
  - GraphQL dual-gate set under `.../graphql_api/**` (auth, complexity, context, dataloaders, errors, mutations, pagination, queries, subscriptions, types)

## Verify commands (copy-paste)
```bash
# Dual-gate audit if present
uv run python goals/riso-lane-py/scripts/check_dual_gates.py || true

uv run riso validate --answers-file samples/api-python/copier-answers.yml --json      # PY-T02
uv run riso validate --answers-file samples/full-stack/copier-answers.yml --json       # PY-T03/T04
uv run riso validate --answers-file samples/cli-docs/copier-answers.yml --json         # PY-T05 / PY-T09
uv run riso validate --answers-file samples/docs-sphinx/copier-answers.yml --json      # PY-T07
uv run riso validate --answers-file samples/changelog-full-stack/copier-answers.yml --json  # GraphQL sample
uv run python scripts/ci/validate_jinja_templates.py                                  # owned python tree
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/PY.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- Foreign contract gap → handoff to COORD (do not edit copier/hooks)
- GraphQL sample answers gap → PLATFORM residual, not silent answers edit

## Done =
PY-T01…T10 green or residualed; PY-T09 empty-dir recheck after COORD; evidence under `goals/riso-lanes-assurance/evidence/`; no foreign-tree edits.
