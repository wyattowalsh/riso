# Lane ASSURANCE (W4-only / integrator)

## Mission (3 lines)
Report-only after W3 join: write `ASSURANCE.md` mapping every fact → evidence or residual.
Close handoffs-board statuses; final path-lock audit; confirm no riso-mcp reintroduction.
No exclusive product write roots — do not patch payload/contract/CLI/scripts to “fix” reports.

## Exclusive write roots
- `goals/riso-lanes-assurance/**` only (report + residuals + evidence + board)
- **No exclusive product paths** — ASSURANCE is report-only on template/src/scripts/samples trees

## Forbidden roots
- Any product tree edit “to make the report green” (foreign residual instead)
- `samples/*/render/**` hand-edits, lockfile hand-edits, secrets
- reintroduce `riso-mcp`
- Re-running matrix as a silent substitute for residual ownership

## Facts file path
- Umbrella facts (22): `goals/riso-lanes-assurance/facts.md`
- Plan W4: `goals/riso-lanes-assurance/plan.md`
- Graph: `goals/riso-lanes-assurance/plan.taskgraph.json`
- Board: `goals/riso-lanes-assurance/handoffs-board.md`
- Dirty map: `goals/riso-lanes-assurance/inventory-dirty.md`
- Residuals dir: `goals/riso-lanes-assurance/residuals/`
- Evidence dir: `goals/riso-lanes-assurance/evidence/`

## Plan tasks this agent owns (IDs)
**Barrier:** W3 join (PL-T09 / full bar).

| ID | Work | verify |
|----|------|--------|
| A-T01 | Write `ASSURANCE.md` mapping every fact → evidence/residual | all 22 facts covered |
| A-T02 | Close handoffs-board statuses | no open unowned |
| A-T03 | Final path-lock audit (git status vs lane roots) | no foreign-tree violations |
| A-T04 | Confirm no riso-mcp reintroduction | `rg` clean on `src/riso` |

## COORD outbox paths to read
- All published: `goals/riso-lane-coord/outbox/*.md`
- Per-lane residuals under `goals/riso-lanes-assurance/residuals/<LANE>.md`
- Evidence artifacts from W1–W3 under `goals/riso-lanes-assurance/evidence/`

## Dirty paths assigned
From inventory (ASSURANCE integrator package paths only):
- `goals/riso-lanes-assurance/**` (facts*, goal, plan*, grok-context/*, inventory-dirty, handoffs-board, evidence/*, interview*)
- After A-T01 also: `ASSURANCE.md`, residual ledger updates

## Verify commands (copy-paste)
```bash
# A-T01 coverage: every facts.md bullet has evidence or residual path
test -f goals/riso-lanes-assurance/ASSURANCE.md

# A-T02
# handoffs-board.md — no status=open without residual path

# A-T03 path-lock audit
git status --short
# every dirty path must map to inventory-dirty.md lane ownership

# A-T04 no riso-mcp
rg -n "riso-mcp" src/riso || true
# expect no reintroduction of maintainer riso-mcp

# Full bar recheck (read-only confirmation; do not skip residuals)
just quality
for f in samples/*/copier-answers.yml; do uv run riso validate --answers-file "$f" --json; done
```

## Handoff template path if blocked
- Residual: `goals/riso-lanes-assurance/residuals/ASSURANCE.md` (meta only)
- Per-lane residuals stay under `residuals/<LANE>.md` with owner, command, redacted log, blocking reason
- Evidence: `goals/riso-lanes-assurance/evidence/`

## Done =
A-T01…T04 green; all 22 facts mapped; handoffs-board closed or residualed; path-lock clean; no riso-mcp; failure policy satisfied (green or owned residual with evidence).
