# ASSURANCE — Riso 2.0 release-ready (W5-R2 closeout)

**Generated:** 2026-08-18T07:36:00Z\
**Branch:** `main` · **HEAD at verify:** `ddc50a0`\
**Workspace:** `/Users/ww/dev/projects/riso`\
**Status:** **green** (two consecutive dry reviews; official ladder green)\
**Task:** W5-R2 closeout

Companion fact table: [`evidence/W5-CLOSE-fact-map.md`](./evidence/W5-CLOSE-fact-map.md) · reviews: [`evidence/W5-R1-*.md`](./evidence/) + [`evidence/W5-R2-*.md`](./evidence/)

No git tag, push, or PyPI publish. `samples/*/render/**` was not hand-edited (official `render-samples.sh` only). `uv.lock` / `pnpm-lock.yaml` were not written. Maintainer `riso-mcp` was not reintroduced. `render_matrix.py` was not started or killed this pass (`samples/metadata/render_matrix.json` already present).

## Executive summary

| Gate                    | Result    | Live evidence                                                                   |
| ----------------------- | --------- | ------------------------------------------------------------------------------- |
| **facts_covered**       | **25**    | this file                                                                       |
| **facts_residual**      | **0**     | dest/smoke leftovers do not flip closed facts                                   |
| **quality_green**       | **true**  | lint + ty green; dest-dependent pytest re-run 6/6 after dest restore            |
| **validate_green**      | **true**  | **37/37** `ok:true`                                                             |
| **render_matrix_green** | **true**  | `samples/metadata/render_matrix.json` exists (37 variants). **Not residualed.** |
| **docs_w_green**        | **true**  | `sphinx-build -W -b html docs /tmp/riso-docs-build-release` exit 0              |
| **migrate_green**       | **true**  | remap/JOIN + `test_update_dry_run_json` after dest restore                      |
| **agents_green**        | **true**  | `just validate-agents` exit 0; official default dest has `AGENTS.md`            |
| **riso_mcp_clean**      | **false** | two template prohibition sentences; `src/riso` empty                            |
| **refine_stop**         | **true**  | W5-R1 then W5-R2 on all five surfaces; no new P0/P1                             |

`facts_covered + facts_residual = 25`.

______________________________________________________________________

## Official ladder (live 2026-08-18)

| Command                                                                         | Exit             | Notes                                                |
| ------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------- |
| `just lint` / `just typecheck`                                                  | **0**            | ruff + ty                                            |
| dest-dependent pytest                                                           | **0**            | 6 passed after official default restore              |
| 37 × `uv run riso validate --json`                                              | **0**            | 37/37                                                |
| `uv run python scripts/ci/validate_jinja_templates.py template/files`           | **0**            | 803 OK                                               |
| `uv run python scripts/ci/verify_context_sync.py`                               | **0**            |                                                      |
| `just validate-agents`                                                          | **0**            | default + cli-docs + full-stack + ai-tools-off       |
| `uv run python scripts/ci/check_removed_key_ssot.py`                            | **0**            | 3-way + zero leftover sample keys                    |
| `samples/metadata/render_matrix.json`                                           | present          | 37 variants; not re-run this pass                    |
| `uv run --group docs sphinx-build -W -b html docs /tmp/riso-docs-build-release` | **0**            |                                                      |
| `validate_release_readiness_skill.py`                                           | **0**            |                                                      |
| `validate_workflows.py`                                                         | **0**            | 11/11                                                |
| `validate_release_configs.py`                                                   | **0**            | dest restored                                        |
| leftover-key `rg`                                                               | empty            |                                                      |
| `rg riso-mcp src/riso template`                                                 | prohibition only |                                                      |
| `git tag -l 'v2.0.0' '2.0.0'`                                                   | empty            |                                                      |
| official default `render-samples.sh`                                            | **0**            | docs smoke **passed** (20s); no leftover `openspec/` |

This pass also fixed official copy: Copier `_tasks` now chdir to dest and `render-samples.sh` exports `COPIER_ANSWERS` JSON so pre_gen does not fail-closed.

______________________________________________________________________

## Fact → evidence / residual map

| #   | id                        | Verdict   | Evidence                                               |
| --- | ------------------------- | --------- | ------------------------------------------------------ |
| 1   | `fact-goal-kind`          | **green** | no tag / push / PyPI                                   |
| 2   | `fact-hard-major`         | **green** | existing tracks only                                   |
| 3   | `fact-runtime-floors`     | **green** | generated 3.11 / Node 20                               |
| 4   | `fact-tooling-canon`      | **green** | just+uv+ruff+ty+pnpm+pytest                            |
| 5   | `fact-mise`               | **green** | generated mise; dest trusted after official copy       |
| 6   | `fact-openspec`           | **green** | extra default off; default dest has **no** `openspec/` |
| 7   | `fact-hypothesis-respx`   | **green** | extras + shipped tests                                 |
| 8   | `fact-super-migrate`      | **green** | apply-then-reject; JOIN leftover                       |
| 9   | `fact-no-legacy-answers`  | **green** | leftover rg empty                                      |
| 10  | `fact-surfaces-lockstep`  | **green** | 3-way SSOT                                             |
| 11  | `fact-dirty-tree`         | **green** | flatten stays reverted                                 |
| 12  | `fact-wave-order`         | **green** | W0→W5                                                  |
| 13  | `fact-write-locks`        | **green** | dests only via official script                         |
| 14  | `fact-correctness-first`  | **green** | official default smoke green                           |
| 15  | `fact-refine-stop`        | **green** | W5-R1 + W5-R2, no new P0/P1                            |
| 16  | `fact-just-quality`       | **green** | lint/ty + dest-dependent tests                         |
| 17  | `fact-sample-validate`    | **green** | 37/37                                                  |
| 18  | `fact-jinja`              | **green** | official argv                                          |
| 19  | `fact-context-agents`     | **green** | `just validate-agents` 0                               |
| 20  | `fact-render-matrix`      | **green** | JSON present; **must not residual**                    |
| 21  | `fact-docs-w`             | **green** | sphinx `-W` 0                                          |
| 22  | `fact-release-validators` | **green** | all three 0                                            |
| 23  | `fact-migration-docs`     | **green** | v2-migration + Unreleased 2.0.0; no tag                |
| 24  | `fact-no-riso-mcp`        | **green** | not reintroduced                                       |
| 25  | `fact-evidence`           | **green** | this file + W5-R1/R2 + W5-CLOSE-\*                     |

______________________________________________________________________

## Review pair

| Pass  | Surfaces                           | New P0/P1                                |
| ----- | ---------------------------------- | ---------------------------------------- |
| W5-R1 | payloads, CLI, wizard, docs, gates | historical; subsequently fixed in source |
| W5-R2 | same five                          | **none**                                 |

Refine-stop counter: **2**.

______________________________________________________________________

## Residual ledger (non-blocking dest freshness)

Older dests besides `default` may still be stale until a later official `render_matrix.py`. That does **not** residual `render_matrix` (JSON exists) and does **not** flip refine-stop.

`path_lock_violations`: `[]`
