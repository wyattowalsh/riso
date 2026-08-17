# ASSURANCE — Riso 2.0 release-ready (W5-CLOSE)

**Generated:** 2026-08-14T05:43:00Z\
**Branch:** `main` · **HEAD:** `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`\
**Workspace:** `/Users/ww/dev/projects/riso`\
**Status:** **residualed** (official ladder commands green after dest restore; refine-stop not claimed)\
**Task:** `W5-CLOSE-GOAL-EVIDENCE` · lane **GOAL** · write roots `goals/riso-v2-release-ready/**` only

Companion fact table: [`evidence/W5-CLOSE-fact-map.md`](./evidence/W5-CLOSE-fact-map.md)

No git tag, commit, push, or PyPI publish was performed. `samples/*/render/**` was not hand-edited by this session. `uv.lock` / `pnpm-lock.yaml` were not written. Maintainer `riso-mcp` was not reintroduced. `render_matrix.py` was not started or killed.

W4-A01 residual ledger is **stale-doc**. Live commands below replace it.

## Executive summary

| Gate | Result | Live evidence |
| --- | --- | --- |
| **facts_covered** | **24** | this file + `evidence/W5-CLOSE-fact-map.md` |
| **facts_residual** | **1** | `fact-refine-stop` |
| **quality_green** | **true** | `just quality` exit 0 — lint, ty, **1067 passed / 14 skipped**, SSOT |
| **validate_green** | **true** | `evidence/W5-CLOSE-validate.txt` — **37/37** `ok:true` |
| **render_matrix_green** | **true** | `samples/metadata/render_matrix.json` exists (37 variants). **Not residualed.** |
| **docs_w_green** | **true** | `evidence/W5-CLOSE-sphinx.txt` — `sphinx-build -W` exit 0 |
| **migrate_green** | **true** | 98 remap/migrate/update + JOIN leftover 2 passed |
| **agents_green** | **true** | `just validate-agents` exit 0 after official default restore |
| **riso_mcp_clean** | **false** | two template prohibition sentences; `src/riso` empty |
| **path_lock** | **clean** | this session wrote only under `goals/riso-v2-release-ready/**` |

`facts_covered + facts_residual = 25`.

Refine-stop is **not** green: Review has not written `W5-R01` / `W5-R03`. Official dest smoke still has P0s (`residuals/GATES.md` R2, `residuals/PY.md` R1).

______________________________________________________________________

## Official ladder (live closeout)

Cwd: `/Users/ww/dev/projects/riso`. Branch `main`. Python via `uv run`.

| Command | Exit | Evidence |
| --- | --- | --- |
| `just quality` | **0** | `evidence/W5-CLOSE-quality.txt` |
| 37 × `uv run riso validate --json` | **0** | `evidence/W5-CLOSE-validate.txt` |
| `uv run python scripts/ci/validate_jinja_templates.py template/files` | **0** | 800+ OK |
| `uv run python scripts/ci/verify_context_sync.py` | **0** | `W5-CLOSE-ladder-a.txt` |
| `just validate-agents` | **0** | `W5-CLOSE-dest-recheck.txt` (earlier 1 is stale) |
| `uv run python scripts/ci/check_removed_key_ssot.py` | **0** | 3-way + zero leftover sample keys |
| `uv run python scripts/ci/render_matrix.py` | not re-run | JSON present; W3-PL-T06.log |
| `uv run --group docs sphinx-build -W -b html docs docs/_build/html` | **0** | `W5-CLOSE-sphinx.txt` |
| `uv run python scripts/ci/validate_release_readiness_skill.py` | **0** | |
| `uv run python scripts/ci/validate_workflows.py` | **0** | 11/11 |
| `uv run python scripts/ci/validate_release_configs.py` | **0** | dest restored; dest-recheck |
| leftover-key `rg` sample + dest answers | empty | dest-recheck |
| `rg riso-mcp src/riso template` | template prohibition only | |
| remap/migrate/update pytest | **0** | 98 passed |
| `git tag -l 'v2.0.0' '2.0.0'` | empty | |

______________________________________________________________________

## Fact → evidence / residual map

| # | id | Verdict | Evidence / residual |
| --- | --- | --- | --- |
| 1 | `fact-goal-kind` | **green** | no tag / commit / push / PyPI |
| 2 | `fact-hard-major` | **green** | existing tracks only |
| 3 | `fact-runtime-floors` | **green** | generated 3.11 / Node 20 |
| 4 | `fact-tooling-canon` | **green** | just+uv+ruff+ty+pnpm+pytest+pre-commit |
| 5 | `fact-mise` | **green** | generated mise; maintainer Node 22 |
| 6 | `fact-openspec` | **green** | extra default off; dest leftover does not flip |
| 7 | `fact-hypothesis-respx` | **green** | extras + shipped tests |
| 8 | `fact-super-migrate` | **green** | 98 tests; JOIN leftover closed |
| 9 | `fact-no-legacy-answers` | **green** | leftover rg empty; dest default answers clean |
| 10 | `fact-surfaces-lockstep` | **green** | 3-way SSOT; wizard dest lucia dropped |
| 11 | `fact-dirty-tree` | **green** | flatten dropped; SaaS leftovers retargeted |
| 12 | `fact-wave-order` | **green** | W0→W5 |
| 13 | `fact-write-locks` | **green** | GOAL-only this session |
| 14 | `fact-correctness-first` | **green** | electron-store exclude kept |
| 15 | `fact-refine-stop` | **residual** | `residuals/GOAL.md` R1 |
| 16 | `fact-just-quality` | **green** | `just quality` 0 |
| 17 | `fact-sample-validate` | **green** | 37/37 |
| 18 | `fact-jinja` | **green** | official argv OK |
| 19 | `fact-context-agents` | **green** | `just validate-agents` 0 |
| 20 | `fact-render-matrix` | **green** | JSON present; **must not residual** |
| 21 | `fact-docs-w` | **green** | sphinx `-W` 0 |
| 22 | `fact-release-validators` | **green** | all three official argv 0 |
| 23 | `fact-migration-docs` | **green** | v2-migration + Unreleased 2.0.0; no tag |
| 24 | `fact-no-riso-mcp` | **green** | not reintroduced; prohibition sentences only |
| 25 | `fact-evidence` | **green** | this file + `evidence/W5-CLOSE-*` + residuals |

______________________________________________________________________

## Wave join rollup

| Wave | Status | Notes |
| --- | --- | --- |
| W0–W2 | residualed / closed per lane | remap SSOT, migrate, extras, keep-polish |
| W3 | residualed | JSON written; smoke reds payload/dest |
| W4 | residualed | docs + sphinx-W; gates-only R03 |
| W5 close | residualed | ladder commands green; Review pair absent; dest smoke P0s remain |

______________________________________________________________________

## Residual ledger (active)

### GOAL R1 — refine-stop (`fact-refine-stop`)

See [`residuals/GOAL.md`](./residuals/GOAL.md). Do **not** treat `W5-AUDIT-*` or `W5-CLOSE-*` lane files as W5-R01/W5-R03.

### Dest / smoke leftovers (do not flip closed facts)

- [`residuals/GATES.md`](./residuals/GATES.md) R2 — default fumadocs `/sitemap.xml` + `output: export`
- [`residuals/PY.md`](./residuals/PY.md) R1 — Sphinx smoke still `make linkcheck` on just-only dests
- [`residuals/OPENSPEC.md`](./residuals/OPENSPEC.md) R1 — 23 dests still have empty `openspec/`
- [`residuals/GATES.md`](./residuals/GATES.md) R1 / R3 / R4 — mise trust, Circle/GitLab uv, stale dest quality.yml
- [`residuals/NODE.md`](./residuals/NODE.md) R1 — Node dests other than default still stale

### Closed this closeout

PLATFORM R1 quality · R3 jinja · **R4 default dest / validate-agents** · CLI JOIN · SKILL mirror · COORD unrooted exclude · wizard dest lucia (WEB) · container empty matrix (template + rust/go dests)

### Not residualed

`fact-render-matrix`.

______________________________________________________________________

## Path lock (this session)

Exclusive write: `goals/riso-v2-release-ready/**`.

| Class | Count |
| --- | --- |
| This-session writes | GOAL tree only |
| `samples/*/render/**` hand-edits | **0** |
| Lockfile / secret / foreign-tree / product edits | **0** |
| `render_matrix.py` started or killed | **0** |

`path_lock_violations`: `[]`

______________________________________________________________________

## riso-mcp

```text
rg -n riso-mcp src/riso template
# src/riso: empty
# template/files/DESIGN.md.jinja + docs/upgrade-guide.md.jinja — prohibition sentences
```

JSON `riso_mcp_clean` is **false** because the combined `rg` is not empty.

______________________________________________________________________

## Remap contract (verified, not re-implemented)

`apply_removed_key_remaps` then `reject_removed_answer_keys`. No dest overwrite. Idempotent. No dual-path after remap. Eight keys: `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`.
