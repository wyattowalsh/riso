# Lane DESKTOP

## Mission (3 lines)
Finish + deep-feature refine for Electron + Tauri under `template/files/electron/**` and `template/files/tauri/**`.
Electron-vite main/preload/ipc + updater/tray/titlebar/packaging; Tauri core/capabilities/features/packaging.
Join validates electron-app + tauri-app; forge/non-enum contract gaps → COORD handoff only.

## Exclusive write roots
- `template/files/electron/**`
- `template/files/tauri/**` (~63 jinja)
- `goals/riso-lane-desktop/**`

## Forbidden roots
- `samples/*/render/**`, lockfile hand-edits, secrets, `riso-mcp`
- COORD contract / other payload / CLI / PLATFORM answers
- Do not invent new desktop product modules outside lane plan

## Facts file path
- Umbrella: `goals/riso-lanes-assurance/facts.md`
- Lane: `goals/riso-lane-desktop/facts.md` + `plan.md` + `goal.md`
- Plan: `goals/riso-lanes-assurance/plan.md` (DESKTOP sub-graph)
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`

## Plan tasks this agent owns (IDs)
**Barrier:** W1-OUT. Electron and Tauri may run parallel (D1).

| ID | Work | parallel_group |
|----|------|----------------|
| DESK-E01 | electron-vite main/preload/ipc | D1 |
| DESK-E02 | electron features: updater/tray/titlebar | D1 |
| DESK-E03 | electron packaging platforms | D1 |
| DESK-T01 | tauri core + capabilities | D1 |
| DESK-T02 | tauri updater/tray/titlebar | D1 |
| DESK-T03 | tauri packaging | D1 |
| DESK-JOIN | validate electron-app + tauri-app | D2 |
| DESK-H | COORD handoffs forge/non-enum only | D2 |

## COORD outbox paths to read
- `goals/riso-lane-coord/outbox/` if desktop-related contract keys appear
- No open DESKTOP-owned handoffs on board at W0

## Dirty paths assigned
From inventory (9 paths — package only; **no dirty DESKTOP product tree**):
- `goals/riso-lane-desktop/**` (facts*, goal, interview*, plan*, plan-gate)

## Verify commands (copy-paste)
```bash
uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
uv run python scripts/ci/validate_jinja_templates.py
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/DESKTOP.md`
- Evidence: `goals/riso-lanes-assurance/evidence/`
- Forge/non-enum contract → COORD handoff (DESK-H); never edit copier.yml

## Done =
DESK-E* + DESK-T* + DESK-JOIN + DESK-H green or residualed; evidence under `goals/riso-lanes-assurance/evidence/`.
