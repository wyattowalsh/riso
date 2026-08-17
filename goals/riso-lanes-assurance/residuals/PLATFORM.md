# Residual — Lane PLATFORM (W3)

## Summary

PLATFORM W3 applied COORD outbox answer follow-through (`api_features` list shape, GraphQL coverage on full-stack, rust sample answers), restored post_gen hook helpers, and QUAL go asserts. Full validate loop is green (37/37 including saas-starter + rust).

**Close-out (2026-08-17):** R2 `just quality` remains **green** historically. R1 matrix **completed** with 33/37 smoke-red variants. Smoke-root-cause patches landed (Fumadocs `dynamic='force-static'`, dest quality extras, dest `mise trust`, parent `VIRTUAL_ENV` isolation). Full matrix not re-run this session.

## Residuals

### R1 — Full `render_matrix.py` smoke red after complete run

| Field               | Value                                                                                                                                                                                                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **task_id**         | PL-T06                                                                                                                                                                                                                                                                                                                                |
| **owner**           | PLATFORM                                                                                                                                                                                                                                                                                                                              |
| **status**          | **residualed** (metadata written; 4/37 `render_status=ok`; patches landed 2026-08-17; re-run still required)                                                                                                                                                                                                                          |
| **command**         | `uv run python scripts/ci/render_matrix.py`                                                                                                                                                                                                                                                                                           |
| **blocking reason** | Completed run failed on Fumadocs static-export metadata routes and dest `just quality` extras/mise trust. Fixes are in the template/scripts tree; a fresh 37-variant pass is still required before `render_matrix_green`.                                                                                                           |
| **redacted log**    | Prior incomplete: `evidence/W3-PL-T06-render_matrix.log`. Completed: `evidence/W3-PL-T06-render_matrix-rerun.log` + `samples/metadata/render_matrix.json`. Validate recheck: `evidence/W5-validate-37.json` (37/37).                                                                                                                  |
| **fix**             | Re-run the official matrix after the 2026-08-17 patches. Never hand-edit `samples/*/render/`.                                                                                                                                                                                                                                         |
| **evidence**        | `goals/riso-lanes-assurance/evidence/W3-PL-T06-render_matrix-rerun.log`, `W5-validate-37.json`                                                                                                                                                                                                                                         |

### R2 — Full `just quality` — **CLOSED green**

| Field               | Value                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **task_id**         | PL-T09                                                                                                                                                                                                                                                                                                                                                                                                              |
| **owner**           | PLATFORM                                                                                                                                                                                                                                                                                                                                                                                     |
| **status**          | **closed / green** (2026-07-29 residual close-out)                                                                                                                                                                                                                                                                                                                                                                 |
| **command**         | `just quality`                                                                                                                                                                                                                                                                                                                                                                          |
| **blocking reason** | (resolved) Basename clash `tests/unit/hooks/test_quality_tool_check.py` vs `tests/unit/ci/test_quality_tool_check.py`; `tests/unit/scripts/*` shadowed repo `scripts` package; timeout flake on `test_copier_cmd_rejects_non_copier_executable` under concurrent matrix.                                                                                                                             |
| **fix applied**    | Renamed hooks test → `tests/unit/hooks/test_hooks_quality_tool_check.py`; moved `tests/unit/scripts/` → `tests/unit/setup_scripts/`; re-ran quality with matrix idle.                                                                                                                                                                                                                                               |
| **result**          | lint ✓ · ty ✓ · **877 passed, 17 skipped, 0 failed, 0 errors**                                                                                                                                                                                                                                                                                                                                                      |
| **evidence**        | `goals/riso-lanes-assurance/evidence/W3-PL-T09-just-quality-rerun.log` (also historical fail log `W3-PL-T09-just-quality.log`)                                                                                                                                                                                                                                                                                      |

## Green work (this wave)

| Task                                                    | Result                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------ |
| PL-T01 outbox vs answers diff                           | evidence `W3-PL-T01-answers-diff.md`                         |
| PL-T02a/b/c answers list normalize + full-stack graphql | commit `0327b1b`                                             |
| PL-T03 rust-api/cli/mcp answers                         | in commit `c130324`                                          |
| PL-T04 QUAL go shared internal asserts                  | 45 go template tests + 3 new QUAL                            |
| PL-T05 validate loop                                    | **37/37 ok** (`W3-PL-T05-validate-summary.json`)             |
| PL-T07 `tests/unit/ci/`                                 | 228+ passed after helper fix                                 |
| PL-T08 quality parity                                   | passed (`W3-PL-T08-quality-parity.txt`)                      |
| PL-T09 full quality                                     | **green** (`W3-PL-T09-just-quality-rerun.log`)               |
| PL-T10 context/agents                                   | not required (PLATFORM did not edit context/agents surfaces) |
| jinja validate                                          | script invoked (no file args → no-op OK)                     |

## Commits

- `0327b1b` fix(samples): normalize api_features multiselect to list form
- `c130324` fix(hooks): restore post_gen quality helper imports and mise trust (includes rust samples, QUAL tests, render_matrix continue-on-fail)
- (pending) test path renames for quality collection (hooks basename + setup_scripts package)

## Do not

- Hand-edit `samples/*/render/**`
- Invent answer keys not published by COORD
- Silent cross-lane payload edits
