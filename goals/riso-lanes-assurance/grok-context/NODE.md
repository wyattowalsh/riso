# Lane NODE

## Mission (3 lines)
Finish + planned-refine non-SaaS Node payload under `template/files/node/**` except `node/saas/**`.
Docs frameworks (Fumadocs/Docusaurus), TS MCP (post COORD typescript choice), api-node, shared-config.
No SAAS tree edits; correctness then NODE-T07 refine only if green.

## Exclusive write roots
- `template/files/node/**` except `template/files/node/saas/**` (~128 jinja)
- `goals/riso-lane-node/**`

## Forbidden roots
- `template/files/node/saas/**` and `template/files/saas-starter/**` (SAAS lane)
- `samples/*/render/**`, lockfile hand-edits, secrets, `riso-mcp`
- COORD contract trees, PY/SYS/DESKTOP/CLI/PLATFORM write roots
- `samples/*/copier-answers.yml` (PLATFORM)

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-node/facts.md` + `goals/riso-lane-node/plan.md` + `goal.md`
- Plan: `goals/riso-lanes-assurance/plan.md` (NODE sub-graph)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W1-OUT. parallel_group N1 → N2 join → N3 refine.

| ID | Work | parallel_group |
|----|------|----------------|
| NODE-T01 | Fumadocs templates | N1 |
| NODE-T02 | Docusaurus templates | N1 |
| NODE-T03 | TS MCP (post typescript choice from COORD W1-H01) | N1 |
| NODE-T04 | api-node Fastify | N1 |
| NODE-T05 | shared-config + workspace fragments (no saas content) | N1 |
| NODE-T06 | Join validate docs-fumadocs, docs-docusaurus, mcp-typescript | N2 |
| NODE-T07 | Planned refine if green | N3 |

Handoff follow-through: `coord-mcp-languages-typescript` → NODE-T03 after COORD outbox.

## COORD outbox paths to read
- `goals/riso-lane-coord/outbox/` for mcp_languages / typescript change-id
- PLATFORM source handoff: `goals/riso-lane-platform/outbox/coord-mcp-languages-typescript.md`

## Dirty paths assigned
From inventory (8 paths — package only; **no dirty NODE product tree**):
- `goals/riso-lane-node/**` (facts*, goal.md, interview*, plan.md)
- Product `template/files/node/**` is clean at W0 snapshot.

## Verify commands (copy-paste)
```bash
uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json
uv run riso validate --answers-file samples/docs-fumadocs-full/copier-answers.yml --json
uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json
uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json   # needs W1-H01
uv run riso validate --answers-file samples/circleci-node/copier-answers.yml --json
uv run python scripts/ci/validate_jinja_templates.py
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/NODE.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- If typescript choice missing → residual until COORD W1-H01 (do not edit copier.yml)

## Done =
NODE-T01…T07 green or residualed; join validates docs + mcp-typescript; evidence under `goals/riso-lanes-assurance/evidence/`.
