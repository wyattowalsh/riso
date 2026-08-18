# Residual — Lane PLATFORM (W3)

## Summary

PLATFORM W3 applied COORD outbox answer follow-through (`api_features` list shape, GraphQL coverage on full-stack, rust sample answers), restored post_gen hook helpers, and QUAL go asserts. Full validate loop is green (37/37 including saas-starter + rust).

**Close-out (2026-08-18, resumed):** R2 `just quality` remains **green** historically. R1 is **in_progress** — live official re-run (`evidence/W5-PL-T06-render_matrix.log`, pid 70136). This-run smoke **fails (5, early dests only):** `api-monorepo` / `api-python` / `changelog-full-stack` / `changelog-monorepo` (fumadocs `llms.mdx` prefix-slug EISDIR/EEXIST) plus `changelog-python` (Sphinx linkify missing). Mid-run patches landed; dests from `circleci-node` through `mcp-typescript` passed this run. Last started dest: `rust-api`. Do not start a second matrix. `render_matrix_green` stays false until this run exits 0. Official JSON stays stale (2026-08-14) until process exit.

## Residuals

### R1 — Full `render_matrix.py` live W5 re-run

| Field               | Value                                                                                                                                                                                                                                                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **task_id**         | PL-T06                                                                                                                                                                                                                                                                                                                                                             |
| **owner**           | PLATFORM                                                                                                                                                                                                                                                                                                                                                           |
| **status**          | **in_progress** (live official re-run; pid 70136; not green)                                                                                                                                                                                                                                                                                                       |
| **command**         | `uv run python scripts/ci/render_matrix.py`                                                                                                                                                                                                                                                                                                                        |
| **blocking reason** | Live W5 matrix still running (pid 70136). This-run reds: prefix-slug EISDIR/EEXIST on four early fumadocs dests + changelog-python Sphinx linkify. Later dests inherited mid-run prefix-skip / CLI-off jinja / myst linkify patches and passed. Remaining: rust-\* , 11 saas-starter/\* , tauri-app. Full official exit-0 still required.                          |
| **redacted log**    | Live: `evidence/W5-PL-T06-render_matrix.log` + pid `W5-PL-T06-render_matrix.pid` (70136). Pass after patches: `docs-fumadocs`, `docs-fumadocs-full`, `docs-sphinx`, `full-stack`, go/\*, etc. Prior complete red: `evidence/W3-PL-T06-render_matrix-rerun.log`. Validate: `evidence/W5-validate-37.json` (37/37). Do not score rust/saas/tauri from leftover JSON. |
| **fix**             | Wait for pid 70136. Do not start a second matrix. Never hand-edit `samples/*/render/`.                                                                                                                                                                                                                                                                             |
| **evidence**        | `goals/riso-lanes-assurance/evidence/W5-PL-T06-render_matrix.log`, `W5-PL-T06-render_matrix.pid`, `W5-validate-37.json`                                                                                                                                                                                                                                            |

### R2 — Full `just quality` — **CLOSED green**

| Field               | Value                                                                                                                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **task_id**         | PL-T09                                                                                                                                                                                                                                                                   |
| **owner**           | PLATFORM                                                                                                                                                                                                                                                                 |
| **status**          | **closed / green** (2026-07-29 residual close-out)                                                                                                                                                                                                                       |
| **command**         | `just quality`                                                                                                                                                                                                                                                           |
| **blocking reason** | (resolved) Basename clash `tests/unit/hooks/test_quality_tool_check.py` vs `tests/unit/ci/test_quality_tool_check.py`; `tests/unit/scripts/*` shadowed repo `scripts` package; timeout flake on `test_copier_cmd_rejects_non_copier_executable` under concurrent matrix. |
| **fix applied**     | Renamed hooks test → `tests/unit/hooks/test_hooks_quality_tool_check.py`; moved `tests/unit/scripts/` → `tests/unit/setup_scripts/`; re-ran quality with matrix idle.                                                                                                    |
| **result**          | lint ✓ · ty ✓ · **877 passed, 17 skipped, 0 failed, 0 errors**                                                                                                                                                                                                           |
| **evidence**        | `goals/riso-lanes-assurance/evidence/W3-PL-T09-just-quality-rerun.log` (also historical fail log `W3-PL-T09-just-quality.log`)                                                                                                                                           |

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
