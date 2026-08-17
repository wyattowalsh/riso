# Goal: Riso Lane PLATFORM

## Articulated goal

Operate the **PLATFORM** exclusive-write lane for the Riso Copier **maintainer** repository: own CI automation (`scripts/ci/**`, sample render entrypoints), shared quality/testing template payload (`template/files/quality/**`, `template/files/testing/**`), sample answers/metadata currency, and minimal maintainer workflow glue. Integrate COORD contracts and payload-lane outputs without implementing language features or inventing Copier keys. Investigate any red CI when needed, but fix only PLATFORM-owned roots and hand off foreign failures via durable outbox files.

## Shared understanding

Accepted facts (testable outcomes and operating constraints):

→ [`facts.md`](./facts.md)

Provenance: `facts-result.json`, `facts.meta.json`, interview in `interview-result.json`.

## Execution plan

Parallel-optimized first `/goal` run and standing protocol (approved as-is):

→ [`plan.md`](./plan.md)

Machine-readable DAG / concurrency / shards:

→ [`plan.taskgraph.json`](./plan.taskgraph.json)

## Done when

1. Ops artifacts exist under `goals/riso-lane-platform/` (inbox/outbox templates, `OPERATING.md`, audit report).
2. Sample-answer drift is fixed for all PLATFORM-owned rows (or COORD-outboxed when keys are ambiguous); every touched answers file passes `uv run riso validate --answers-file … --json`.
3. If answers changed, full matrix completed via `uv run python scripts/ci/render_matrix.py` (no hand-edited `samples/*/render/**`).
4. Quality/testing coherence checked (`check_quality_parity` / reviews); foreign gaps outboxed (e.g. PY `python/tasks/quality.py.jinja`).
5. CI coverage pack progressed (top modules tested or intentional gaps documented) and `tests/unit/ci` / `just quality` run as applicable.
6. No foreign-tree edits, no lockfile hand-edits, no secrets, no unsolicited branches/commits/pushes.
7. Every line in `facts.md` is evidenced or explicitly deferred with reason in the audit report.

## Launch

```text
/goal goals/riso-lane-platform/goal.md
```
