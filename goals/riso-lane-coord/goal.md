# Goal — Riso Lane COORD

## Articulated goal

Operate the **COORD exclusive-write lane** for the Riso Copier maintainer repo: the serial Wave-0 owner of template contracts (`copier.yml`, hooks, macros, module catalog, prompts, context parity). Accept structured markdown handoffs from other lanes, apply the smallest coherent contract change, publish an outbox delta for payload/CLI follow-up, and never implement language-tree payloads or edit `src/riso/**`.

This package is a **standing operating protocol** (not a fixed product backlog). The first `/goal` run bootstraps process artifacts under `goals/riso-lane-coord/` and dry-runs verification without unsolicited contract churn.

## Shared understanding

See [facts.md](./facts.md) for the accepted fact sheet (testable outcomes and constraints).

## Execution plan

See [plan.md](./plan.md) for the parallel-team wave model, hyperfine task graph (R/B/C/O/P/V), schemas, subagent spawn matrix, verification stages, and recovery ladder. Plan gate: **approved**.

## Done condition

**Bootstrap (first run):**

- Handoff/outbox templates, `LANE.md`, apply checklist, README, inbox/outbox dirs, and examples exist under `goals/riso-lane-coord/`
- Context parity, default `riso validate`, and prompts/catalog smoke pass via `uv run`
- Path audit shows no unsolicited COORD contract edits under `template/`
- No branches/commits/pushes unless the human explicitly asked

**Apply runs (later, when handoffs exist):**

- One change-id applied end-to-end with published `outbox/<CID>.md`
- Illegal combos enforced; catalog/context coherent; staged verification green for touched surfaces
- Payload and CLI lanes can implement without re-touching COORD paths

## Provenance

| Artifact | Path |
|----------|------|
| Interview | [interview.json](./interview.json) → [interview-result.json](./interview-result.json) |
| Facts review | [facts-review.json](./facts-review.json) → [facts-result.json](./facts-result.json) |
| Facts meta | [facts.meta.json](./facts.meta.json) |
| Plan gate | [plan-gate-result.json](./plan-gate-result.json) (`approved`) |
