# Residual — Lane PY (W2)

## Summary

Python payload dual-gates + CLI package init finished and committed (`1685488`).  
Jinja (145) and dual-gate audit (31 GQL/WS files) are green.  
Empty optional-dir recheck after COORD `exclude-empty-dirs` is green.

Several python-heavy `riso validate` sample checks fail because sample answers still use **scalar** `api_features` strings (`none`, `websocket`, `graphql,websocket`) while CLI validate requires a **list** for multiselect prompts. PY must not edit `samples/*/copier-answers.yml` (PLATFORM lock).

## Residuals

### R1 — Sample answers: `api_features` multiselect list shape

| Field | Value |
|-------|-------|
| **owner** | PLATFORM |
| **task_ids** | PY-T02, PY-T03, PY-T04, PY-T06, PY-T07 (validate gate) |
| **blocking** | Yes for full sample validate green bar; not blocking PY payload correctness |
| **command** | `uv run riso validate --answers-file samples/api-python/copier-answers.yml --json` |
| **error (redacted)** | `api_features: expected list for multiselect` |
| **affected samples** | api-python, full-stack, docs-sphinx, changelog-full-stack, changelog-python |
| **green sample** | cli-docs (no `api_features` key / when inactive) |
| **evidence** | `goals/riso-lanes-assurance/evidence/W2-PY-validate-*.json`, `W2-PY-validate-summary.json` |
| **fix** | Normalize sample answers to list form (e.g. `api_features: []` or `[websocket]` / `[graphql, websocket]`) under PLATFORM exclusive write root. Aligns with COORD W1-H05 hook token normalize + CLI multiselect schema. |
| **do not** | PY must not edit answers; do not hand-edit `samples/*/render/`. |

### R2 — GraphQL sample coverage (already residualed)

| Field | Value |
|-------|-------|
| **owner** | PLATFORM |
| **handoff** | `graphql-sample-coverage` (COORD residual → PLATFORM; board residualed) |
| **task_ids** | PY-T03 follow-through / PL-T02* |
| **note** | PY GraphQL dual-gates complete; dedicated GraphQL-heavy sample answers remain PLATFORM. |

## Payload work completed (not residual)

- Dual-gate audit script: `goals/riso-lane-py/scripts/check_dual_gates.py` → 31/31 ok
- GraphQL leaf dual-gates + CLI `__init__` disabled stub → commit `1685488`
- WS surfaces already dual-gated
- Jinja validate python tree: 145 OK
- PY-T09 empty-dir recheck after COORD excludes: all optional trees absent post cleanup

## Environment note

Full `riso copy` post_gen may fail here with missing hook helper / workflow_validator import path; PY-T09 exercised `cleanup_empty_rendered_files` + `cleanup_empty_scaffold_dirs` directly after `--skip-post-gen` render (same functions COORD post_gen runs).
