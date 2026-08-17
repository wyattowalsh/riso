# Lane CLI

## Mission (3 lines)
Finish + refine maintainer `riso` CLI under `src/riso/**` and unit tests under `tests/unit/test_cli/**`.
Doctor JSON envelope, validate/copy/update/recopy/diff paths, catalog/prompts/variants introspection.
Never reintroduce `riso-mcp`; always `uv run` for Python.

## Exclusive write roots
- `src/riso/**`
- `tests/unit/test_cli/**`
- `goals/riso-lane-cli/**`

## Forbidden roots
- `samples/*/render/**`, lockfile hand-edits, secrets
- reintroduce maintainer `riso-mcp` (CLI surface is `riso` + skills only)
- Template payload trees, COORD contract, PLATFORM scripts/answers
- `tests/unit/ci/**`, `tests/unit/test_go_templates.py` (PLATFORM)

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-cli/facts.md` + `plan.md` + `goal.md` + `tasks.graph.json`
- Plan: `goals/riso-lanes-assurance/plan.md` (CLI sub-graph)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W1-OUT. C1 fan-out → C2 tests → C3 join.

| ID | Work | parallel_group |
|----|------|----------------|
| CLI-T01 | doctor JSON envelope | C1 |
| CLI-T02 | validate/copy/update/recopy/diff paths | C1 |
| CLI-T03 | catalog/prompts/variants introspection | C1 |
| CLI-T04 | unit tests expand for changed behavior | C2 |
| CLI-JOIN | `riso --help`, `doctor --json`, pytest test_cli | C3 |

## COORD outbox paths to read
- `goals/riso-lane-coord/outbox/` if prompt/catalog keys affect CLI introspection
- Align with COORD W1-H05 only as consumer of normalize semantics (hooks stay COORD)

## Dirty paths assigned
From inventory (18 paths):
- Package: `goals/riso-lane-cli/**` (facts*, goal, plan*, tasks.graph.json, interview*)
- Product:
  - `M` `src/riso/cli/commands/doctor.py`
  - `M` `tests/unit/test_cli/test_doctor.py`
  - `M` `tests/unit/test_cli/test_output.py`
  - `??` `tests/unit/test_cli/test_argv_normalize.py`
  - `??` `tests/unit/test_cli/test_prompts.py`
  - `??` `tests/unit/test_cli/test_recopy.py`
  - `??` `tests/unit/test_cli/test_validate.py`
  - `??` `tests/unit/test_cli/test_variants.py`

## Verify commands (copy-paste)
```bash
uv sync --group cli
uv run riso --help
uv run riso doctor --json
uv run pytest tests/unit/test_cli/ -q
# targeted
uv run pytest tests/unit/test_cli/test_doctor.py tests/unit/test_cli/test_output.py -q
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/CLI.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- Contract prompt shape gaps → COORD; never patch hooks from CLI lane

## Done =
CLI-T01…T04 + CLI-JOIN green or residualed; doctor JSON + pytest test_cli pass; no riso-mcp; evidence under `goals/riso-lanes-assurance/evidence/`.
