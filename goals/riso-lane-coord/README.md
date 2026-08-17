# goals/riso-lane-coord

COORD exclusive-write lane package for the Riso Copier maintainer repository: serial owner of template contracts (answers, hooks, macros, module catalog, context parity).

## Launch

```text
/goal goals/riso-lane-coord/goal.md
```

## Documents

| Doc | Purpose |
|-----|---------|
| [goal.md](./goal.md) | Goal entry + done conditions |
| [facts.md](./facts.md) | Accepted testable facts |
| [plan.md](./plan.md) | Waves, task graph, verify stages |
| [LANE.md](./LANE.md) | Day-to-day operating manual |
| [APPLY-CHECKLIST.md](./APPLY-CHECKLIST.md) | Serial apply micro-steps (one change-id) |
| [handoff-template.md](./handoff-template.md) | Inbound request schema (copy into inbox) |
| [outbox-template.md](./outbox-template.md) | Outbound contract delta for payload/CLI |

## Directories

| Path | Purpose |
|------|---------|
| [inbox/](./inbox/) | Pending handoffs (`<change-id>.md`) |
| [inbox/done/](./inbox/done/) | Applied/archived handoffs |
| [outbox/](./outbox/) | Published contract deltas |
| [examples/](./examples/) | **Non-executable** worked examples (do not apply) |

## How other lanes request a contract change

1. Copy [handoff-template.md](./handoff-template.md) → `inbox/<change-id>.md` (or `goals/<lane>/handoffs/`).
2. Fill required sections (prompt keys, when/defaults, hook rules, catalog, context, payload follow-ups).
3. Wait for COORD to apply and publish `outbox/<change-id>.md`.
4. Implement **only** your exclusive payload paths; **do not re-touch COORD paths**.

## Hard constraints (summary)

- COORD writes only contract surfaces listed in [LANE.md](./LANE.md).
- Never edit `src/riso/**` from this lane (CLI owns `generation_gates`).
- Never hand-edit `samples/*/render/` or lockfiles.
- No git branch/commit/push unless the human asks.
- Use `uv run` for all Python commands.

## Bootstrap vs apply

| Mode | When | What |
|------|------|------|
| Bootstrap | First run / missing process artifacts; empty inbox | Templates + dirs + dry-run verify only |
| Apply | Real handoff in inbox | Smallest coherent contract + outbox |
| Idle | Empty inbox; artifacts present | Report idle; invent nothing |
