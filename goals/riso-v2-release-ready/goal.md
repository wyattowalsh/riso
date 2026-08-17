# Goal — Riso 2.0 release-ready

## Articulated goal

Make the Riso **maintainer** repo evidence-ready for a hard 2.0.0: reshape existing tracks (not new languages/runtimes/vendors), add a super-good answers migrate (`apply` then fail-closed), keep generated payloads / `riso` CLI / web wizard / docs / CI gates in lockstep, and prove the official release ladder green — including a completed `scripts/ci/render_matrix.py`. This goal does **not** create a git tag, push, or publish to PyPI.

Start from the current dirty tree. Keep matching polish. Drop or rewrite what fights (SaaS Next/Remix flatten stays reverted). Correctness first, then planned refine until two consecutive review passes find no new P0/P1 and the ladder is green.

## Shared understanding

Accepted facts: [`facts.md`](./facts.md) (metadata: [`facts.meta.json`](./facts.meta.json)).

Interview: [`interview.json`](./interview.json) → [`interview-result.json`](./interview-result.json).

## Execution plan

Primary plan (Plannotator-**approved**): [`plan.md`](./plan.md)

Machine DAG: [`plan.taskgraph.json`](./plan.taskgraph.json)

Evidence / residuals land under [`evidence/`](./evidence/) when `/goal` runs.

### Wave summary

| Wave | Mode | What |
|------|------|------|
| W0 | parallel docs | Dirty-tree lane map, 8-key hit list, keep/drop, taskgraph checksum |
| W1 | serial COORD/CLI | Machine remap SSOT, hook twin, gates/hooks apply-then-reject, Copier extras (mise always-on, OpenSpec off), no-legacy policy rewrite |
| W2 | 9 parallel leaders | CLI migrate + call-site wiring, wizard twin, PY hypothesis+respx, NODE/SAAS/SYS/DESKTOP keep-fixes, mise pins |
| W3 | PLATFORM shards | 6 answer shards → 37/37 validate → quality/jinja/ssot → **full** `render_matrix.py` |
| W4 | docs + refine | v2 migration guide, CHANGELOG Unreleased 2.0.0, sphinx `-W`, two dry review passes, `ASSURANCE.md` |

## Done condition

- Every fact in `facts.md` is mapped in `ASSURANCE.md` to green evidence **or** an owned residual (owner, command, redacted log, blocking reason). `render_matrix` may **not** be residualed.
- `riso update` / `riso migrate` remap all eight `REMOVED_ANSWER_KEYS` with dry-run preview, idempotence, and tests; leftovers fail closed. No dual-path after remap.
- No sample `copier-answers.yml` and no generated default answers contain a removed Copier key.
- Generated payloads, CLI, wizard, and maintainer docs stay in lockstep (including three-way remap SSOT).
- Maintainer + generated ship mise pins; generated Node floor stays 20+ (do not raise to maintainer 22). OpenSpec is maintainer-used; generated extra default off.
- Generated Python `test` extra includes `hypothesis` and `respx` with one shipped test each.
- Official ladder green: `just quality`; 37/37 `riso validate --json`; jinja; context/agents if those surfaces changed; `render_matrix.py` writes `samples/metadata/render_matrix.json`; `sphinx-build -W`; release validators; no `riso-mcp`.
- `docs/guides/v2-migration.md` exists and CHANGELOG has Unreleased 2.0.0 breaking remaps. **No version tag.**
- Exclusive write locks honored; `samples/*/render/` never hand-edited.

## Provenance

| Artifact | Path |
|----------|------|
| Interview | [interview-result.json](./interview-result.json) |
| Facts | [facts-result.json](./facts-result.json) |
| Plan gate | [plan-gate-result.json](./plan-gate-result.json) (`approved`) |

## Launch

```text
/goal goals/riso-v2-release-ready/goal.md
```
