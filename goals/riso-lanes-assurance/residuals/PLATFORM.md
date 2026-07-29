# Residual — Lane PLATFORM (W3)

## Summary

PLATFORM W3 applied COORD outbox answer follow-through (`api_features` list shape, GraphQL coverage on full-stack, rust sample answers), restored post_gen hook helpers, and QUAL go asserts. Full validate loop is green (37/37 including saas-starter + rust). Full `render_matrix.py` and full `just quality` did not reach exit-0 within this integrator session.

## Residuals

### R1 — Full `render_matrix.py` still running / incomplete

| Field               | Value                                                                                                                                                                                                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **task_id**         | PL-T06                                                                                                                                                                                                                                                                                                                                |
| **owner**           | PLATFORM                                                                                                                                                                                                                                                                                                                              |
| **command**         | `uv run python scripts/ci/render_matrix.py`                                                                                                                                                                                                                                                                                           |
| **blocking reason** | Full matrix is wall-clock heavy (per-variant copier + pnpm bootstrap + fumadocs `next build` smoke). Session partial progress only; process may still be running. One earlier abort was smoke fail on `ai-tools-off` (stale next lock / concurrent build); matrix now continues after per-variant failure (`render_status` recorded). |
| **redacted log**    | See `goals/riso-lanes-assurance/evidence/W3-PL-T06-render_matrix.log` — variants started sequentially (`ai-tools-off`, `api-monorepo`, …).                                                                                                                                                                                            |
| **fix**             | Let matrix finish to completion; ensure `samples/metadata/render_matrix.json` written; re-run once if only lock flakes. Never hand-edit `samples/*/render/`.                                                                                                                                                                          |
| **evidence**        | `goals/riso-lanes-assurance/evidence/W3-PL-T06-render_matrix.log`, optional pid file `W3-PL-T06-render_matrix.pid`                                                                                                                                                                                                                    |

### R2 — Full `just quality` not green end-to-end

| Field               | Value                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **task_id**         | PL-T09                                                                                                                                                                                                                                                                                                                                                                                                              |
| **owner**           | PLATFORM (recheck) / maintainer                                                                                                                                                                                                                                                                                                                                                                                     |
| **command**         | `just quality` (or lint+ty+`pytest tests`)                                                                                                                                                                                                                                                                                                                                                                          |
| **blocking reason** | Focused PLATFORM suites green (273 `tests/unit/ci`+go templates; ruff+ty clean on PLATFORM surfaces). Full `pytest tests` reported 839 passed / 1 failed / 3 collection errors — concurrent matrix contention timed out `test_copier_cmd_rejects_non_copier_executable` (15s), plus pre-existing import errors under `tests/unit/scripts/*` and `tests/unit/hooks/test_quality_tool_check.py` import-file mismatch. |
| **redacted log**    | `goals/riso-lanes-assurance/evidence/W3-PL-T09-just-quality.log`                                                                                                                                                                                                                                                                                                                                                    |
| **fix**             | Re-run `just quality` after matrix idle; resolve duplicate `test_quality_tool_check` module path if still erroring.                                                                                                                                                                                                                                                                                                 |

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
| PL-T10 context/agents                                   | not required (PLATFORM did not edit context/agents surfaces) |
| jinja validate                                          | script invoked (no file args → no-op OK)                     |

## Commits

- `0327b1b` fix(samples): normalize api_features multiselect to list form
- `c130324` fix(hooks): restore post_gen quality helper imports and mise trust (includes rust samples, QUAL tests, render_matrix continue-on-fail)

## Do not

- Hand-edit `samples/*/render/**`
- Invent answer keys not published by COORD
- Silent cross-lane payload edits
