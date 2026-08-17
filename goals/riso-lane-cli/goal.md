# Goal — Riso Lane CLI

## Articulated goal

Own the maintainer-facing **`riso` CLI** exclusive write lane in the Riso Copier template repository: implement and harden agent-native commands under `src/riso/**`, keep unit tests under `tests/unit/test_cli/**` aligned with behavior, and preserve stable JSON envelopes, exit codes, path resolution, and timeout semantics — without writing template contracts, samples renders, CI, or web surfaces, and without reintroducing maintainer `riso-mcp`.

## Shared understanding

Accepted facts: [`facts.md`](./facts.md) (metadata: [`facts.meta.json`](./facts.meta.json)).

## Execution plan

Approved plan: [`plan.md`](./plan.md)  
Machine-readable task graph: [`tasks.graph.json`](./tasks.graph.json)

**Default dispatch when `/goal` has no extra task:** Recipe **A** (health: help, doctor --json, pytest test_cli).  
**Highest-value follow-on when green:** Recipe **C** (P0 coverage: prompts / variants / recopy tests in parallel).

## Done condition

- `uv run riso --help` works  
- `uv run riso doctor --json` succeeds with envelope keys `ok`, `command`, `data`, `errors`, `warnings`  
- `uv run pytest tests/unit/test_cli/ -q` passes  
- Behavior changes include matching tests under `tests/unit/test_cli/`  
- No writes outside `src/riso/**` and `tests/unit/test_cli/**` (optional handoffs under `goals/riso-lane-cli/handoffs/**`)  
- No maintainer `riso-mcp`; COORD contract gaps are handoffs only  

## Provenance

- Interview: [`interview.json`](./interview.json) → [`interview-result.json`](./interview-result.json)  
- Facts review: [`facts-review.json`](./facts-review.json) → [`facts-result.json`](./facts-result.json)  
- Plan gate: approved by human (2026-07-25)
