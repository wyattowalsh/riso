# Residual — Lane PY (W2)

## Summary

Python payload dual-gates + CLI package init finished and committed (`1685488`).
Jinja (145) and dual-gate audit (31 GQL/WS files) are green.
Empty optional-dir recheck after COORD `exclude-empty-dirs` is green.

W2 sample-validate residuals (scalar `api_features`, GraphQL sample coverage) are **historical / closed**. PLATFORM applied list normalize and full-stack GraphQL in W3. Rechecked answers 2026-08-18: no scalar `api_features` remain; `api-python`, `docs-sphinx`, and `changelog-python` use `api_features: []`; `full-stack` and `changelog-full-stack` use `[graphql, websocket]`.

**Active bar residual (not PY-owned):** PLATFORM R1 full `render_matrix` — [`PLATFORM.md`](./PLATFORM.md). See [`ASSURANCE.md`](../ASSURANCE.md).

## Residuals

### R1 — Sample answers: `api_features` multiselect list shape — **CLOSED (W3)**

| Field | Value |
|-------|-------|
| **status** | historical / closed |
| **owner** | PLATFORM |
| **task_ids** | PY-T02, PY-T03, PY-T04, PY-T06, PY-T07 (validate gate) · PL-T01 / PL-T02 / PL-T05 |
| **blocking** | No — W3 answers list-normalize landed; 37/37 validate green |
| **applied** | PLATFORM commit `0327b1b` (`api_features` list form). Recheck: listed PY samples are lists, not scalars (`none` / comma-string). |
| **evidence** | [`ASSURANCE.md`](../ASSURANCE.md) fact #12 + superseded W2 residuals · `evidence/W5-validate-37.json` (37/37) · `evidence/W3-PL-T05-validate-summary.json` · `evidence/W3-PL-T01-answers-diff.md` |
| **do not** | PY must not edit answers; do not hand-edit `samples/*/render/`. |

### R2 — GraphQL sample coverage — **CLOSED (W3)**

| Field | Value |
|-------|-------|
| **status** | historical / closed |
| **owner** | PLATFORM |
| **handoff** | `graphql-sample-coverage` (COORD residual → PLATFORM; board **applied**) |
| **task_ids** | PY-T03 follow-through / PL-T02 |
| **applied** | `samples/full-stack/copier-answers.yml` has `api_features: [graphql, websocket]` (+ existing `changelog-full-stack`). PY GraphQL dual-gates were already complete. |
| **evidence** | [`ASSURANCE.md`](../ASSURANCE.md) A-T02 · `evidence/W5-validate-37.json` · `evidence/W3-PL-T05-validate-summary.json` · `evidence/W3-PL-T01-answers-diff.md` |

## Payload work completed (not residual)

- Dual-gate audit script: `goals/riso-lane-py/scripts/check_dual_gates.py` → 31/31 ok
- GraphQL leaf dual-gates + CLI `__init__` disabled stub → commit `1685488`
- WS surfaces already dual-gated
- Jinja validate python tree: 145 OK
- PY-T09 empty-dir recheck after COORD excludes: all optional trees absent post cleanup

## Environment note

W2 note: full `riso copy` post_gen could fail here with missing hook helper / `workflow_validator` import path; PY-T09 exercised `cleanup_empty_rendered_files` + `cleanup_empty_scaffold_dirs` after `--skip-post-gen`. PLATFORM later restored post_gen helpers (`c130324`). This is not an open PY residual.
