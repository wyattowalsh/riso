# Residual — Lane GOAL (W5-CLOSE-GOAL-EVIDENCE)

## Summary

Live closeout (`main` @ `f7951fe`, 2026-08-14T05:42Z) remapped all 25 accepted facts from re-run commands. `render_matrix.py` is **not** residualed. This session did not commit, tag, push, or hand-edit `samples/*/render/**`.

Official ladder that this lane re-ran is **green**: `just quality`; 37/37 `riso validate --json`; jinja dir-walk; context-sync; `just validate-agents`; sphinx `-W`; skill + workflows + official `validate_release_configs.py`; remap/JOIN pytest.

Refine-stop is **not** green: Review has not written `W5-R01` / `W5-R03`. Official dest smoke and dest-stale leftovers still include P0/P1s, so the dry counter stays at zero.

## Residuals

### R1 — refine-stop not met (`fact-refine-stop`)

| Field | Value |
| --- | --- |
| **task_id** | W5-CLOSE / `fact-refine-stop` / RES-GOAL-01 |
| **owner** | Review (W5-R01 / W5-R03) + payload owners of remaining dest/smoke P0/P1s |
| **status** | open |
| **command** | two consecutive review passes on payloads / CLI / wizard / docs / gates with **no new P0/P1**, **and** official ladder green |
| **blocking reason** | Plan (`facts.md` L17; `plan.md` L42, L291–296). On-disk review evidence is still only `evidence/W4-R03-gates.md` (gates-only). `W4-R01*` / `W4-R02*` / `W5-R01*` / `W5-R02*` / `W5-R03*` are **absent**. `W5-AUDIT-*` and `W5-CLOSE-*` lane files are not that pair. After official default restore, dest smoke is still red (Fumadocs `/sitemap.xml` + `output: export`). Sphinx dest smoke still calls `make linkcheck` on just-only dests. |
| **redacted log** | `ls evidence/W5-R0*` → no files. `just validate-agents` now exit 0. `samples/default/smoke-results.json` docs failed: `Failed to collect configuration for /sitemap.xml` with `output: export`. |
| **fix** | NODE/COORD/PLATFORM finish remaining dest/smoke P0/P1s (below). Review then writes **W5-R01** and **W5-R03** on all five surfaces. If any new P0/P1, reset the pair. Do not tag 2.0.0. |
| **evidence** | `evidence/W5-CLOSE-GOAL-EVIDENCE.md`, `evidence/W5-CLOSE-dest-recheck.txt`, `residuals/GATES.md` R2, `residuals/PY.md` R1 |

Live remaining P0/P1s (template locks mostly closed this wave; dest/smoke still open):

| id | sev | live | residual |
| --- | --- | --- | --- |
| GATES-R2-default-fumadocs-smoke | P0 | official default dest exists; fumadocs `next build` fails `/sitemap.xml` + `output: export` | `residuals/GATES.md` R2 |
| PAY-P0-linkcheck-smoke | P0 | PY added `linkcheck` recipes; `copier.yml` still excludes `python/Makefile` when `task_runner=just`; dest `docs-sphinx` has no Makefile; smoke still `uv run make linkcheck` | `residuals/PY.md` R1 |
| RES-OS-01 dest openspec shells | P1 | default dest has **no** `openspec/`; 23 other dests still have empty shells | `residuals/OPENSPEC.md` R1 |
| GATES-R1-mise-trust | P1 | rust-api/go-api official copy OK; bootstrap `mise` dest untrusted | `residuals/GATES.md` R1 |
| GATES-R3-circle-gitlab-uv-root | P1 | GHA uv path fixed; Circle/GitLab still dest-root `uv sync` | `residuals/GATES.md` R3 |
| MS-P1-pnpm-false-green dest | P1 | `samples/mcp-typescript/render/package.json` still a blank line (dest stale) | PLATFORM re-render |

Template items **closed this wave** (do not treat as live source P0/P1s): docusaurus mermaid named export; sidebar.js require; fumadocs middleware; api-node package.json; SaaS flatten Docker/seed paths; GHA dest-root uv; conf.py E402 / StrEnum / pylint wrap; wizard dest lucia; container empty `needs`/matrix (template + rust-api/go-api dests); default dest absence; PAY-P0-06 MCP pytest path.
