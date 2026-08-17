# W4-R03 — Review pass 2, surface=gates

- Task: `W4-R03`
- Wave: W4
- Lane: GOAL (inspect-only; this file only)
- Surface: gates (`scripts/ci/**`, `scripts/lib/**`, `scripts/render-samples.sh`, sample answers, release-readiness skill + Claude mirror, `justfile` quality wiring, `.github/workflows/quality.yml`)
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset; `.git/HEAD` read denied by hook; prior W3 evidence + workspace path)
- Date: 2026-08-13
- Pass 1 blob: untrusted; every keep/drop re-read in-tree
- `samples/*/render/**` writes: **0**
- Status: **no new P0/P1** (pass 1 items verified fixed)

## Contract

Remap is apply-then-reject. `apply_removed_key_remaps` then `reject_removed_answer_keys`. No dest overwrite. Idempotent. No dual-path after remap. `render_matrix.py` is blocking and was not killed.

P0 = correctness / contract break. P1 = lockstep / DX. Empty lists only after inspection.

## Pass 1 disposition

| Pass 1 id | Verdict | Evidence (this pass) |
| --- | --- | --- |
| GATES-P0-nested-variant-regex | **fixed** | `scripts/render-samples.sh` L588 is `^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$`. Old `^[a-zA-Z0-9][a-zA-Z0-9._-]*$` is gone (repo-wide). Destination is `${SAMPLES_DIR}/${variant}/render` (L722). `[[ dest != ${SAMPLES_DIR}/*/render ]]` is `[[ ]]` pattern match (`*` matches `/`). Tests: `tests/unit/ci/test_render_samples_variant_names.py`, `test_render_matrix.py::test_discovers_nested_saas_starter_without_flattening`. GHA `validate-samples` still uses `saas-starter/*`. |
| GATES-P0-stale-nolegacy-mirror | **fixed** | Source and Claude `references/no-legacy-answer-policy.md` both apply-then-reject, 8 keys, `apply_removed_key_remaps` / `reject_removed_answer_keys`. No “Do not convert removed keys into canonical keys.” `SKILL.md` stop rule is fail-closed leftovers. File sets match (SKILL, policy, release-gates, task-graph, collect script). W3 residuals `PLATFORM.md` R2 / `SKILL.md` R1 are **stale**. |
| GATES-P1-ssot-gate-unwired | **fixed** | `justfile` `quality: lint typecheck test ssot`; `ssot` / `ci-ssot` run `uv run python scripts/ci/check_removed_key_ssot.py`. `quality.yml` cli-tests job L274–275 same command. `tests/unit/ci/test_check_removed_key_ssot.py` exists. |
| GATES-P1-no-sample-leftover-scan | **fixed** | `check_removed_key_ssot.py` `scan_sample_answers_for_removed_keys()` walks `iter_sample_answer_files()`. YAML-key intersection with `REMOVED_ANSWER_KEYS`. `rg` of `key:` leftovers under `samples/**/copier-answers.yml` is empty. Unit test detects a fixture leftover. |
| GATES-P1-skill-validator-content | **fixed** | `validate_release_readiness_skill.py` `validate_policy_contract`: all 8 keys, `apply_removed_key_remaps`, `reject_removed_answer_keys`, “apply then reject”, forbids the exact do-not-convert sentence. Test `test_validate_policy_contract_rejects_do_not_convert`. |
| GATES-P1-loguru-percent-format | **fixed** | `render_matrix.py` L169–172 and L339 use Loguru `{}` braces. W3-PL-T06.log still shows historical `%s` from the pre-fix run. |
| GATES-P1-release-gates-ladder | **fixed** | `.agents` and `.claude` `release-gates.md` list SSOT, jinja, workflows, release-configs, sphinx `-W`, render_matrix, 37-sample validate, leftover scan via SSOT. |

## Independent scan (not elevated)

Read and judged **below P1** (do not reset the dry-review counter):

- `references/task-graph.md` still names an `src/riso/mcp/**` lane. Policy already forbids reintroducing `riso-mcp`. Stale coordination from specs/016, not a live remap/ladder break.
- `scripts/ci/run_quality_suite.py` still uses Loguru `%s` (L37, L110). Subprocess output already shows the failed command; not the blocking matrix.
- `just clean-all` is `rm -rf samples/*/render` (does not clean nested `saas-starter/*/render`). Maintenance footgun, not a release gate.
- `just ci-full` does not call `ssot`; `just quality` / `just ci` / GHA cli-tests do.
- `samples/metadata/render_matrix.json` still records 11 `saas-starter/*` `render_status=failed` from W3 (invalid variant name). Code now accepts those names; JSON is a stale PL-T06 artifact. Remaining matrix reds are payload/smoke (foreign surfaces), not this regex.
- W3-PL-T03 / PL-T07 / PLATFORM residual still describe the old mirror mismatch.

## Remap twin (gates)

`scripts/lib/removed_answer_keys.py`: 8 `_FALLBACK_*` keys; apply drops old key after mapped dests; `_write_dests` does not overwrite a set dest; lucia is **not** in `_SAAS_AUTH_PROVIDERS` (fail-closed leftover). Matches core. Skill policy lucia row locksteps that.

## Sample answers

Canonical dest keys only (`saas_infra_module`, `saas_auth_module`/`provider`, `saas_admin_dashboard`, `mcp_languages: [typescript]`, …). W3-S4/S5 validate jsonl: saas-starter variants `ok:true`. No generated `.copier-answers.yml` leftover-key hits.

## Writes

This evidence file only. No commit / tag / push. No `render_matrix` start/kill.
