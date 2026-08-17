# Goal — Riso lanes assurance

## Articulated goal

**Finish, refine, and fully assure** all eight Riso exclusive-write lanes (COORD, PY, NODE, SAAS, SYS, DESKTOP, CLI, PLATFORM): close package gaps, apply open handoffs, complete remaining in-lane work (including dirty-tree paths and planned refine), then prove green with maintainer `just quality`, all sample `riso validate`s, full `render_matrix` + smokes, Jinja, and targeted pytest—or document owned residuals with evidence.

This is an **integrator / assurance program**, not a new product feature backlog. Per-lane ownership and facts remain in `goals/riso-lane-*/`.

## Shared understanding

Accepted facts: [`facts.md`](./facts.md) (metadata: [`facts.meta.json`](./facts.meta.json)).

Interview: [`interview.json`](./interview.json) → [`interview-result.json`](./interview-result.json).

## Execution plan

Primary plan (Plannotator-**approved**): [`plan.md`](./plan.md)

Machine DAG: [`plan.taskgraph.json`](./plan.taskgraph.json)

Grok Build context packs: [`grok-context/`](./grok-context/)

Evidence / residuals: [`evidence/`](./evidence/), [`residuals/`](./residuals/)

### Wave summary

| Wave | Mode | What |
|------|------|------|
| W0 | parallel docs | NODE/SAAS goal.md, dirty inventory, handoffs board, grok packs |
| W1 | serial COORD | Apply open contract handoffs; publish outbox |
| W2 | 6 parallel lanes | PY/NODE/SAAS/SYS/DESKTOP/CLI finish+refine under locks |
| W3 | PLATFORM | Answer shards → validate all → full render_matrix → just quality |
| W4 | umbrella | `ASSURANCE.md` + path-lock + no riso-mcp |

## Done condition

- Every fact in `facts.md` is evidenced **or** has an owned residual (owner, command, redacted log, blocking reason)
- NODE + SAAS packages have `goal.md`
- Open handoffs applied or residualed; board current
- `just quality` green
- All `samples/*/copier-answers.yml` validate (or residual)
- Full `uv run python scripts/ci/render_matrix.py` complete with smoke evidence (no hand-edited renders)
- Jinja + targeted pytest green for touched surfaces
- Conditional context/agents checks if those surfaces changed
- No foreign-tree lock violations; no secrets; no riso-mcp; atomic conventional commits OK

## Provenance

| Artifact | Path |
|----------|------|
| Interview | [interview-result.json](./interview-result.json) |
| Facts | [facts-result.json](./facts-result.json) |
| Plan gate | [plan-gate-result.json](./plan-gate-result.json) (`approved`) |

## Child lane packages

| Lane | Path |
|------|------|
| COORD | [goals/riso-lane-coord/](../riso-lane-coord/) |
| PY | [goals/riso-lane-py/](../riso-lane-py/) |
| NODE | [goals/riso-lane-node/](../riso-lane-node/) |
| SAAS | [goals/riso-lane-saas/](../riso-lane-saas/) |
| SYS | [goals/riso-lane-sys/](../riso-lane-sys/) |
| DESKTOP | [goals/riso-lane-desktop/](../riso-lane-desktop/) |
| CLI | [goals/riso-lane-cli/](../riso-lane-cli/) |
| PLATFORM | [goals/riso-lane-platform/](../riso-lane-platform/) |

## Launch

```text
/goal goals/riso-lanes-assurance/goal.md
```
