# W0-T05 evidence — grok-context packs

- Captured (UTC): `2026-07-29T02:00:00Z`
- Repo: `/Users/ww/dev/projects/riso`
- Task: W0-T05 Materialize/enrich `grok-context/*.md` prompt packs per lane
- Inputs: `plan.md`, `facts.md`, `inventory-dirty.md`, `handoffs-board.md`, `plan.taskgraph.json`

## Packs written (9)

| Pack      | Path                                                   | Schema sections                                                                                    |
| --------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| COORD     | `goals/riso-lanes-assurance/grok-context/COORD.md`     | Mission, locks, forbidden, facts, W1-H01…H08+OUT tasks, outbox, dirty (19), verify, residual, done |
| PY        | `goals/riso-lanes-assurance/grok-context/PY.md`        | PY-T01…T10, dirty GraphQL+cli (26)                                                                 |
| NODE      | `goals/riso-lanes-assurance/grok-context/NODE.md`      | NODE-T01…T07, exclude saas, package-only dirty (8)                                                 |
| SAAS      | `goals/riso-lanes-assurance/grok-context/SAAS.md`      | SAAS-T01…T11, package.json owners, package-only dirty (8)                                          |
| SYS       | `goals/riso-lanes-assurance/grok-context/SYS.md`       | SYS-GO/RS/JOIN/H, dirty product bulk (41)                                                          |
| DESKTOP   | `goals/riso-lanes-assurance/grok-context/DESKTOP.md`   | DESK-E\*/T\*/JOIN/H, package-only dirty (9)                                                        |
| CLI       | `goals/riso-lanes-assurance/grok-context/CLI.md`       | CLI-T01…JOIN, doctor+test_cli dirty (18)                                                           |
| PLATFORM  | `goals/riso-lanes-assurance/grok-context/PLATFORM.md`  | PL-T01…T10, answers+CI dirty (67)                                                                  |
| ASSURANCE | `goals/riso-lanes-assurance/grok-context/ASSURANCE.md` | A-T01…T04 W4-only, report-only roots                                                               |

## Prior state

All 9 packs were thin stubs (~30 lines) with “see plan lock table” placeholders — no task IDs, no verify commands, no dirty path assignment.

## Completeness vs plan schema

Each pack includes:

1. Mission (3 lines)
1. Exclusive write roots
1. Forbidden roots
1. Facts file path
1. Plan tasks this agent owns (IDs)
1. COORD outbox paths to read
1. Dirty paths assigned (from inventory-dirty.md)
1. Verify commands (copy-paste)
1. Handoff/residual template path if blocked
1. Done =

## Status

**green** — 8 lane packs + ASSURANCE coordinator pack enriched; ready for W1+ dispatch.
