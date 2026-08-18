# ASSURANCE — Riso lanes W4 report

**Generated:** 2026-07-29\
**Updated:** 2026-08-18 (W0–W4 re-orchestrate; PL-T06 live re-run)\
**Branch:** `main` · **Workspace:** `/Users/ww/dev/projects/riso`\
**Status:** **residualed** (W0–W4 task IDs done except PL-T06; validate 37/37; live `render_matrix` pid 70136; post-fix smoke classes: llms prefix-slug EISDIR + CLI-off pylint — patches landed mid-run)\
**Report tasks:** A-T01…A-T04

## Executive summary

| Gate                    | Result    | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **validate_green**      | **true**  | `evidence/W5-validate-37.json` **37/37 ok** (2026-08-17 in-process `run_validate`); prior `W3-PL-T05-validate-summary.json`                                                                                                                                                                                                                                                                                                           |
| **quality_green**       | **true**  | Maintainer: ruff check 0; sphinx `-W` 0; CLI/hooks/ci unit **341 passed**; web eslint 0 errors / 308 vitest. Historical dest `just quality`: `W3-PL-T09-just-quality-rerun.log` (877 passed)                                                                                                                                                                                                                                          |
| **render_matrix_green** | **false** | Official re-run **live** (`evidence/W5-PL-T06-render_matrix.log`, pid 70136). This-run reds (5): prefix-slug EISDIR/EEXIST on `api-monorepo` / `api-python` / `changelog-full-stack` / `changelog-monorepo`; Sphinx linkify on `changelog-python`. Later dests through `mcp-typescript` passed after mid-run patches. Last started dest: `rust-api`. Official JSON still 2026-08-14 until process exit. Do not start a second matrix. |
| **riso_mcp_clean**      | **true**  | `evidence/W4-A-T04-riso-mcp.txt` — no matches under `src/riso` / `template`                                                                                                                                                                                                                                                                                                                                                           |
| **path_lock**           | **clean** | `evidence/W4-A-T03-pathlock.md` — 93 dirty paths; unowned=0; foreign-tree=0                                                                                                                                                                                                                                                                                                                                                           |

Waves W0–W3 completed with owned residuals. **Fact #11 quality closed green** in residual close-out. Open bar residual: **PLATFORM R1** full `render_matrix` (`residuals/PLATFORM.md`).

______________________________________________________________________

## A-T01 — Fact → evidence / residual map

All **22** umbrella facts from [`facts.md`](./facts.md) are mapped.\
**facts_covered = 22** · **facts_residual = 1** (fact #13 render_matrix; fact #11 quality closed green).

| #   | Fact (abbrev)                                                                            | Verdict              | Evidence / residual                                                                                                                                                                                                                                                                                                                                                                                          |
| --- | ---------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Integrator goal over 8 lanes, not product backlog                                        | **green**            | This report + `plan.md` / `plan.taskgraph.json` waves W0–W4 only                                                                                                                                                                                                                                                                                                                                             |
| 2   | NODE + SAAS get launchable `goal.md`                                                     | **green**            | `goals/riso-lane-node/goal.md`, `goals/riso-lane-saas/goal.md`; evidence `W0-T01-node-goal.md`, `W0-T02-saas-goal.md`                                                                                                                                                                                                                                                                                        |
| 3   | Every lane facts green **or** residual with owner/command/log                            | **green**            | Lane residuals: `residuals/{COORD,PY,NODE,SAAS,SYS,DESKTOP,PLATFORM}.md` (SAAS empty-blocking); CLI green no residual; evidence tree under `evidence/W2-*` / `W3-*`                                                                                                                                                                                                                                          |
| 4   | Wave order W0→W1→W2→W3→W4                                                                | **green**            | `plan.md` + upstream wave results; taskgraph `plan.taskgraph.json`                                                                                                                                                                                                                                                                                                                                           |
| 5   | Exclusive write roots; no silent cross-lane                                              | **green**            | Lane packs `grok-context/*.md`; W4 path-lock `evidence/W4-A-T03-pathlock.md`; inventory `inventory-dirty.md`                                                                                                                                                                                                                                                                                                 |
| 6   | All open handoffs triaged/applied/residualed                                             | **green**            | `handoffs-board.md` (A-T02 closed; 0 open unowned)                                                                                                                                                                                                                                                                                                                                                           |
| 7   | COORD contract applies + outbox + context parity                                         | **green**            | W1-H01…H08 / W1-OUT; outbox under `goals/riso-lane-coord/outbox/`; `W1-H08-context-sync.txt`; residual only GraphQL **policy** (now applied on answers)                                                                                                                                                                                                                                                      |
| 8   | Payload lanes finish under exclusive trees                                               | **green**            | Commits: PY `1685488`, NODE `de65da9`, SAAS `bfd6f00`, SYS `33e544e`/`abcb762`, DESKTOP `75eca3e`/`9591394`, CLI `8415e62`                                                                                                                                                                                                                                                                                   |
| 9   | Correctness first; planned refine only; no new modules                                   | **green**            | Lane summaries `W2-SAAS-sweep.md`, `W2-DESKTOP-summary.md`, `W2-NODE-summary.md`, SYS residual (modernize only)                                                                                                                                                                                                                                                                                              |
| 10  | PLATFORM answers after outbox; no invented keys; official render scripts                 | **green**            | `W3-PL-T01-answers-diff.md` (no invented keys); answers normalize commit `0327b1b`; rust samples commit `c130324`                                                                                                                                                                                                                                                                                            |
| 11  | Maintainer `just quality` passes before done                                             | **green**            | Owner **PLATFORM** residual close-out · cmd `just quality` · log `W3-PL-T09-just-quality-rerun.log` · **877 passed, 17 skipped** · fixes: rename hooks `test_hooks_quality_tool_check.py`, move `tests/unit/scripts`→`setup_scripts` (avoid `scripts` package clash); historical fail log `W3-PL-T09-just-quality.log`                                                                                       |
| 12  | Every `samples/*/copier-answers.yml` validates                                           | **green**            | `W3-PL-T05-validate-summary.json` **37/37** (26 top-level + 11 saas-starter); W4 spot: full-stack/go-api/rust-api/docs-docusaurus `ok:true` (`evidence/W4-A-T01-validate-spot.json`)                                                                                                                                                                                                                         |
| 13  | Full `render_matrix.py` completes; never hand-edit renders                               | **residual**         | Owner **PLATFORM** · live W5 re-run (`evidence/W5-PL-T06-render_matrix.log`, pid 70136) — **not green**. This-run reds: 4 early fumadocs prefix-slug dests + `changelog-python` linkify. Mid-run patches held for later dests (`docs-fumadocs`, `docs-sphinx`, `full-stack`, go/\*). Remaining rust/saas/tauri still in this run. Residual `residuals/PLATFORM.md` R1. Do not hand-edit `samples/*/render/`. |
| 14  | `validate_jinja_templates.py` for owned trees                                            | **green**            | PY `W2-PY-jinja-validate.txt` (145); NODE `W2-NODE-jinja*.txt` (129); SAAS `W2-SAAS-jinja.txt` (196); SYS `W2-SYS-jinja-validate.txt` (79); DESKTOP `W2-DESKTOP-jinja.txt` (63); PLATFORM `W3-PL-T10-jinja-validate.txt`                                                                                                                                                                                     |
| 15  | Lane-targeted pytest where surfaces change                                               | **green** (targeted) | CLI 78 pass `W2-CLI-pytest.txt`; go templates 42–45 pass `W2-SYS-pytest-go-templates.txt` / `W3-PL-T04-go-templates.txt`; electron 42 pass `W2-DESKTOP-pytest-electron.txt`; CI suite pass `W3-PL-T07-ci-pytest.txt`. Full suite residual under fact #11                                                                                                                                                     |
| 16  | Context/agents validators when those surfaces change                                     | **green**            | COORD `W1-H08-context-sync.txt`; PLATFORM PL-T10 N/A (no context/agents edits)                                                                                                                                                                                                                                                                                                                               |
| 17  | Done = green **or** owned residual with evidence                                         | **green**            | This document + residual ledger; no silent matrix skip                                                                                                                                                                                                                                                                                                                                                       |
| 18  | Final assurance report maps facts + handoffs                                             | **green**            | This file `goals/riso-lanes-assurance/ASSURANCE.md`                                                                                                                                                                                                                                                                                                                                                          |
| 19  | Atomic conventional commits OK; no force-push/secrets/lock hand-edits                    | **green**            | Recent conventional commits (see `git log`); no lockfile hand-edits in assurance scope                                                                                                                                                                                                                                                                                                                       |
| 20  | Out of scope: new product modules; hand-edit renders/locks/secrets; reintroduce riso-mcp | **green**            | Path-lock + A-T04 clean; no render hand-edits claimed                                                                                                                                                                                                                                                                                                                                                        |
| 21  | Maintainer surface = riso CLI + skills; no riso-mcp                                      | **green**            | `rg` clean `evidence/W4-A-T04-riso-mcp.txt`; CLI join `W2-CLI-join.txt`                                                                                                                                                                                                                                                                                                                                      |
| 22  | Pre-existing dirty work finished under correct ownership                                 | **green**            | `inventory-dirty.md` (222 paths → lanes, unowned=0 at W0); subsequent commits per lane                                                                                                                                                                                                                                                                                                                       |

### Superseded W2 residuals (answers shape)

W2 PY/NODE/SYS residuals for scalar `api_features` were **resolved in W3** by PLATFORM list normalize (`0327b1b`) and revalidated (`W3-PL-T05-validate-summary.json`). Those residual docs remain as historical W2 ledger entries; current bar for answers validate is **green**.

GraphQL sample coverage: COORD residualed contract change → PLATFORM enabled `graphql` on `samples/full-stack` (+ existing `changelog-full-stack`). Handoff closed **applied**.

______________________________________________________________________

## A-T02 — Handoffs board closeout

See updated [`handoffs-board.md`](./handoffs-board.md).

| Handoff id                         | Final status | Close note                                             |
| ---------------------------------- | ------------ | ------------------------------------------------------ |
| `coord-mcp-languages-typescript`   | applied      | W1-H01; mcp-typescript validate green                  |
| `COORD-go-version-mcp`             | applied      | W1-H02; go-mcp validate green                          |
| `COORD-rust-module-excludes`       | applied      | W1-H03                                                 |
| `exclude-empty-dirs`               | applied      | W1-H04 + PY-T09 recheck green                          |
| `api-features-normalize`           | applied      | W1-H05 + PLATFORM answer lists                         |
| `graphql-sample-coverage`          | **applied**  | PL-T02 full-stack `api_features: [graphql, websocket]` |
| `PLATFORM-rust-samples`            | **applied**  | PL-T03 `samples/rust-{api,cli,mcp}`; validate ok       |
| `PLATFORM-go-api-features-answers` | **applied**  | go-api `api_features: []`; validate ok                 |
| `QUAL-go-template-tests`           | **applied**  | PL-T04 QUAL asserts; go template pytest green          |
| `bootstrap-verify`                 | applied      | W1-OUT smoke                                           |

**open unowned = 0**

Open **bar** residual (not handoffs): PLATFORM R1 `render_matrix`. R2 `just quality` **closed green**.

______________________________________________________________________

## A-T03 — Path-lock audit

**Command:** `git status --short` at assurance time → 93 dirty leaf paths.

| Class                                                            | Count | Notes                                                                         |
| ---------------------------------------------------------------- | ----: | ----------------------------------------------------------------------------- |
| Mapped to lane root                                              |    91 | ASSURANCE 50, COORD 16, DESKTOP 9, NODE 8, PLATFORM 4, CLI/PY/SAAS/SYS 1 each |
| OUT-OF-SCOPE                                                     |     2 | `.claude/skills/mcp-installer/`, `.grok/` (local harness; not product locks)  |
| Unowned                                                          | **0** |                                                                               |
| Foreign-tree violations                                          | **0** |                                                                               |
| Forbidden `samples/*/render/**` hand-edits in dirty product list | **0** | Renders only via official scripts (matrix process regenerating)               |

Detail: [`evidence/W4-A-T03-pathlock.md`](./evidence/W4-A-T03-pathlock.md)

**path_lock_violations:** `[]`

______________________________________________________________________

## A-T04 — No riso-mcp reintroduction

```bash
rg -n 'riso-mcp' src/riso template
# (no matches)
```

Evidence: [`evidence/W4-A-T04-riso-mcp.txt`](./evidence/W4-A-T04-riso-mcp.txt)\
Mentions of `mcp_languages` / MCP modules are intentional product features, not the removed maintainer `riso-mcp` package.

______________________________________________________________________

## Wave join rollup

| Wave       | Status                          | Green tasks (selected)                  | Residuals                                                   |
| ---------- | ------------------------------- | --------------------------------------- | ----------------------------------------------------------- |
| W0         | green                           | W0-T01…T06                              | none                                                        |
| W1         | residualed→closed               | W1-H01…H05, H07, H08, OUT               | H06 GraphQL answers → applied W3                            |
| W2-PY      | residualed→superseded           | dual-gates, jinja, empty-dirs, cli-docs | answers shape → W3 green                                    |
| W2-NODE    | residualed→superseded           | T01–T05, T07                            | join answers → W3 green                                     |
| W2-SAAS    | green                           | T01–T11                                 | none blocking                                               |
| W2-SYS     | residualed→partially superseded | GO/RS modernize; go-cli/mcp             | go-api answers + rust samples → W3 applied                  |
| W2-DESKTOP | green                           | E\*/T\*/JOIN/H                          | foreign quality_tool_check → PLATFORM full quality residual |
| W2-CLI     | green                           | T01–JOIN; 78 pytest                     | none                                                        |
| W3         | residualed→partial close        | PL-T01…T05, T07–T09, T10                | PL-T06 matrix re-run in progress; PL-T09 quality **green**  |
| W4         | residualed                      | A-T01…T04 report complete               | inherits PLATFORM R1 matrix only                            |

______________________________________________________________________

## Residual ledger (active blockers only)

### PLATFORM R1 — `render_matrix` live W5 re-run (active)

| Field           | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| owner           | PLATFORM                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| command         | `uv run python scripts/ci/render_matrix.py`                                                                                                                                                                                                                                                                                                                                                                                                                       |
| evidence        | Live: `evidence/W5-PL-T06-render_matrix.log` · pid `evidence/W5-PL-T06-render_matrix.pid` (70136) · validate `evidence/W5-validate-37.json`. Prior complete red run: `evidence/W3-PL-T06-render_matrix-rerun.log`                                                                                                                                                                                                                                                 |
| redacted log    | Official re-run **in_progress**. Early dests: `ai-tools-off` docs passed (2026-08-17 export-meta/`force-static` holds). `api-monorepo` / `api-python` failed on **llms.mdx prefix-slug EISDIR** + **pylint E0611** on CLI-off `test_cli.py`. Mid-run template patches landed (prefix-skip `generateStaticParams`; Jinja-gate CLI tests). Remaining dests in this run use those templates. Do not start a second matrix. No full-matrix score until the run exits. |
| blocking reason | 37-variant matrix still running; `render_matrix_green` stays false until exit 0. Answers validate is 37/37.                                                                                                                                                                                                                                                                                                                                                       |
| fix             | Let pid 70136 finish. Never hand-edit `samples/*/render/`.                                                                                                                                                                                                                                                                                                                                                                                                        |

### PLATFORM R2 — `just quality` — **CLOSED green**

| Field        | Value                                                                                                                                                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| owner        | PLATFORM                                                                                                                                                                                                               |
| command      | `just quality`                                                                                                                                                                                                         |
| evidence     | `evidence/W3-PL-T09-just-quality-rerun.log` (historical fail: `W3-PL-T09-just-quality.log`)                                                                                                                            |
| redacted log | **877 passed, 17 skipped** · lint + ty green · no collection errors                                                                                                                                                    |
| fix applied  | Rename `tests/unit/hooks/test_quality_tool_check.py` → `test_hooks_quality_tool_check.py`; move `tests/unit/scripts/` → `tests/unit/setup_scripts/` (avoid shadowing repo `scripts` package); re-run after matrix idle |
| status       | **closed**                                                                                                                                                                                                             |

Historical W2 residuals (answers shape) are **closed by W3** but files kept for audit trail.

______________________________________________________________________

## Schema fields (assurance_schema)

| Field                | Value                                     |
| -------------------- | ----------------------------------------- |
| status               | `residualed`                              |
| facts_covered        | `22`                                      |
| facts_residual       | `1`                                       |
| quality_green        | `true`                                    |
| validate_green       | `true`                                    |
| render_matrix_green  | `false`                                   |
| riso_mcp_clean       | `true`                                    |
| path_lock_violations | `[]`                                      |
| report_path          | `goals/riso-lanes-assurance/ASSURANCE.md` |

______________________________________________________________________

## Commands rechecked at W4 (read-only)

```bash
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
# 2026-08-17: in-process run_validate over 37 sample answers → evidence/W5-validate-37.json
# uv run ruff check scripts template/hooks tests src
# uv run --group docs sphinx-build -W -b html docs /tmp/riso-docs-build-release
# TMPDIR=/tmp/riso-pytest-tmp pytest tests/unit/test_cli tests/unit/hooks/test_post_gen_project.py tests/unit/ci/test_render_matrix.py …
# web/node_modules/.bin/eslint web/src --ext .ts,.tsx
rg -n 'riso-mcp' src/riso template   # only migration/do-not-document mentions
```

**Fail-closed notes:** `render_matrix_green` stays false until the live W5 37-variant matrix (pid 70136) exits 0. Do not infer green from validate-only, mid-run dests, or the historical 4/37 matrix file.
