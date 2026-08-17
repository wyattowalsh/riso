# W5-AUDIT-facts — live-tree map of 25 accepted facts

- **Lane:** `facts` (read-only; exclusive write = this file)
- **Date (UTC):** 2026-08-14
- **Repo:** `/Users/ww/dev/projects/riso` (cwd via `.git/HEAD` = `ref: refs/heads/main`)
- **Branch:** `main`
- **HEAD:** `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (`.git/refs/heads/main`)
- **Sources:** `facts.md` / `facts.meta.json` (25 accepted ids). `ASSURANCE.md` was **read and not trusted**.
- **`samples/*/render/**` writes this audit:** **0**
- **Product-code edits:** **0**
- **Commands re-executed this audit:** **none** (this worker has no shell; some `.git` reads are hook-denied). Verdicts are live **file:line** plus historical command artifacts **only when the live tree still matches**.
- **`git tag`:** no `v2.0.0` or `2.0.0` in `.git/refs/tags/` (v1.2.0–v1.2.11 only) or `.git/packed-refs` (`refs/tags/v1.0.0`–`v1.1.4` only). Grep `refs/tags/(v2\.0\.0|2\.0\.0)$` → empty.

**Score:** **23 green** · **2 still-open** · **0 blocked** (`render_matrix.json` present; not residualed).

ASSURANCE W4-A01 claimed 23 covered / 2 residual after a parent closeout, but its residual *ledger* still lists quality/jinja as red and PAY-P0-06 as live. The live tree has moved: those two implementation gaps are gone; `fact-context-agents` and `fact-refine-stop` remain open.

______________________________________________________________________

## Tag / publish (fact-goal-kind + fact-migration-docs)

| Check | Live result |
| --- | --- |
| `.git/HEAD` | `ref: refs/heads/main` |
| `.git/refs/heads/main` | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` |
| Last reflog | `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| `refs/tags/v2.0.0` / `2.0.0` | **absent** |
| Latest packed tags | `v1.1.4` |
| PyPI / commit / push this audit | not performed |

______________________________________________________________________

## Fact table (all 25)

| # | id | Verdict | Live evidence |
| --- | --- | --- | --- |
| 1 | `fact-goal-kind` | **green** | Goal is evidence-ready only. No `v2.0.0`/`2.0.0` tag objects. This audit did not commit/tag/push/PyPI. |
| 2 | `fact-hard-major` | **green** | Existing tracks only. `cli_languages` choices `python\|rust\|go` (`template/copier.yml:282-293`). `docs_framework` `fumadocs\|sphinx-shibuya\|docusaurus` (`copier.yml:490-501`). No new language/runtime/vendor prompts. |
| 3 | `fact-runtime-floors` | **green** | Generated `mise.toml.jinja:6-7` `python = "3.11"` / `node = "20"`. `python/pyproject.toml.jinja:10` `requires-python = ">=3.11"`. Copier + maintainer CI matrices `["3.11","3.12","3.13"]` (`copier.yml:47,265-268`; `.github/workflows/quality.yml:19`). Generated GHA Node `'20'` (`riso-quality.yml.jinja:121,152`). Grep `node = "22"` / `node-version: 22` under `template/files` = **empty**. Maintainer `.mise.toml:7` stays `22.23.1` (not copied onto generated floor). |
| 4 | `fact-tooling-canon` | **green** | Maintainer `justfile:98-134` `quality: lint typecheck test ssot` (ruff + ty + pytest). Generated extras: ruff/ty/pytest/pre-commit (`python/pyproject.toml.jinja:36-48`); pydantic/loguru (`:13-16`); typer (`:80,109`). `task_runner` default `just` with Makefile alternative (`copier.yml:46,250-263,1908-1917`). Playwright + Vitest where UI already exists (`node/saas/package.json.jinja:36-44,349-354`). |
| 5 | `fact-mise` | **green** | Always-on generated `template/files/mise.toml.jinja` (comment L1–2). Copier excludes `.mise.toml` (`copier.yml:2103-2105`). Maintainer `.mise.toml:5-9` ships pins. `W2-MISE-join.md`. |
| 6 | `fact-openspec` | **green** | Maintainer instructions require OpenSpec (`Claude.md` / AGENTS). Generated extra `openspec_extra` default `disabled` (`copier.yml:534-551`, `_defaults` `:95`). `_exclude` only when not enabled (`copier.yml:2105`). Payload under `template/files/openspec/**`. Related residuals R1/R2 are **stale** (see below). |
| 7 | `fact-hypothesis-respx` | **green** | `python/pyproject.toml.jinja:36-39` test extra includes both. Shipped tests: `python/tests/test_hypothesis.py.jinja:9-20`, `python/tests/test_respx.py.jinja:11-22`. |
| 8 | `fact-super-migrate` | **green** | SSOT 8 keys + operators `src/riso/core/removed_answer_keys.py:10-18,75-116`. `_write_dests` does not overwrite set dests (`:312-318`). `apply_removed_key_remaps` then drop old key (`:321-343`). `apply_then_reject_removed_keys` (`answers.py:79-83`). Wired: `helpers.resolve_answers`/`validate_and_raise` (`helpers.py:73,93`), `update.py:41-50` dry-run preview, `migrate.py:44` + `app.py:270-292`, hooks `pre_gen_project.py:291-313`, `generation_gates.py:145-146`. Tests + fixtures: `tests/unit/test_cli/{test_remap,test_migrate,test_update}.py` + `fixtures/remap/` (8 keys + mixed + leftover + canonical). Historical `W4-A01-ladder.txt` migrate suite **98 passed**. JOIN tests now assert unmapped leftover `saas_auth=firebase` (`test_riso_cli.py:52-64`; `test_control_plane_gates.py:15-24`). |
| 9 | `fact-no-legacy-answers` | **green** | Grep `^(api_tracks\|api_language\|docs_site\|mcp_language\|saas_starter_module\|saas_auth\|saas_billing\|include_admin):` in `samples/**` and as Copier questions = **empty**. 37 `project_name:` hits in `samples/**/copier-answers.yml`. Same 8 keys absent from rendered `.copier-answers.yml`. `check_removed_key_ssot.py:280-312` leftover scan. `justfile:102-104` `ssot` in `quality`. Historical leftover `rg` empty (`W4-A01-ladder.txt`). |
| 10 | `fact-surfaces-lockstep` | **green** | Three-way remap: core / `scripts/lib/removed_answer_keys.py` / `web/src/lib/removedAnswerKeys.ts:360-442` (`applyThenRejectRemovedKeys`). Historical `check_removed_key_ssot` exit 0 (`W4-A01-ladder.txt:98-117`). Docs lockstep: `docs/guides/v2-migration.md:13-48`, `CHANGELOG.md:9-67`, generated `upgrade-guide.md.jinja`, skill policy 8 keys. PAY-P0-06 pytest path is **fixed** in tree (`riso-quality.yml.jinja:78-82` `python/tests/test_mcp.py` with `working-directory: python`). |
| 11 | `fact-dirty-tree` | **green** | Flatten stay-dropped: no root `next.config.js.jinja` / `remix.config.js.jinja` under `node/saas/`; `runtime/nextjs` + `runtime/remix` present. `W0-keep-drop.md:28,81,133-145`. |
| 12 | `fact-wave-order` | **green** | Evidence prefixes W0 → W1 → W2 → W3 → W4 exist under `evidence/`. `plan.md` wave table + `plan.taskgraph.json`. |
| 13 | `fact-write-locks` | **green** | Exclusive roots in `plan.md:46-64`. This audit wrote only this file. `samples/*/render` not hand-edited. Official dests are matrix output. |
| 14 | `fact-correctness-first` | **green** | Electron ESM boot kept: `electron.vite.config.ts.jinja:8` `externalizeDepsPlugin({ exclude: ['electron-store'] })`. |
| 15 | `fact-refine-stop` | **still-open** | See detail. Only on-disk review file is `W4-R03-gates.md`. No `W4-R01*` / `W4-R02*`. Official closeout ladder is not fully green (`just validate-agents`). |
| 16 | `fact-just-quality` | **green** | Recipe `justfile:98-134`. W4-A01 format-fail log is **stale**: the two JOIN failures now use leftover `saas_auth=firebase`; residual `PLATFORM.md` R1 marked closed (parent closeout). `ty` + `ssot` remain in the recipe. **This audit did not re-run `just quality`.** No remaining implementation hole visible in the five previously unformatted paths. |
| 17 | `fact-sample-validate` | **green** | 37 live `samples/**/copier-answers.yml`. Historical `W4-A01-validate.txt` `TOTAL=37 OK=37 FAIL=0`. No subsequent leftover-key reintroduction. **Not re-run.** |
| 18 | `fact-jinja` | **green** | Official argv now walks dirs: `validate_jinja_templates.py:73-81` `_expand_jinja_paths` `is_dir()` + `rglob("*.jinja")`. W4-A01 `Not a file` log is **stale**. Residual `PLATFORM.md` R3 marked closed. **Not re-run.** |
| 19 | `fact-context-agents` | **still-open** | See detail. `verify_context_sync.py` last exit 0 (`W4-A01-ladder.txt:119-121`). `just validate-agents` (`justfile:217-229`) still requires `samples/default/render`. That dest **does not exist** (`samples/default/` = answers + smoke + baseline only). `cli-docs` / `full-stack` / `ai-tools-off` `render/AGENTS.md` present. Matrix `default` `render_status=failed` (`render_matrix.json:551-608`). |
| 20 | `fact-render-matrix` | **green** | `samples/metadata/render_matrix.json` present (37 `render_status` rows; 3 `ok` = electron-app / mcp-typescript / tauri-app; 34 `failed`). `W3-PL-T06.log` ends `variants 37` / `ok 3` / `failed 34`. **Not residualed.** Historical pid `W3-PL-T06.pid` = `2924`; log says complete. This audit did not start or kill a matrix process. |
| 21 | `fact-docs-w` | **green** | `docs/guides/v2-migration.md` + toctree `docs/guides/index.md:18`. Built page `docs/_build/html/guides/v2-migration.html`. Historical `sphinx-build -W` `build succeeded` / `sphinx_exit:0` (`W4-A01-ladder.txt:14-62`). **Not re-run.** |
| 22 | `fact-release-validators` | **green** | Scripts present: `validate_release_readiness_skill.py`, `validate_workflows.py`, `validate_release_configs.py`. Historical exits 0 (`W4-A01-ladder.txt:64-96`). Policy contract 8 keys (`.agents/skills/riso-release-readiness/references/no-legacy-answer-policy.md:1-48`). Claude mirror residual **closed**. **Not re-run.** |
| 23 | `fact-migration-docs` | **green** | `docs/guides/v2-migration.md` (apply-then-reject + 8-key table). `CHANGELOG.md:9-67` `## [Unreleased] 2.0.0` names all eight remaps. No version tag (above). Older leftover `## [Unreleased]` at `CHANGELOG.md:420` is pre-2.0 noise; does not remove the required section. |
| 24 | `fact-no-riso-mcp` | **green** | `src/riso/` has `cli/`, `core/`, `template/` only — no mcp package. Grep `riso-mcp` under `src/riso` = **empty**. Template hits are prohibition sentences only (`DESIGN.md.jinja:257`, `docs/upgrade-guide.md.jinja:188`). |
| 25 | `fact-evidence` | **green** | Closeout artifacts exist: `ASSURANCE.md` + `evidence/W4-A01-fact-map.md` + residuals. This file remaps every accepted fact to **live** green or an owned still-open. Do not treat ASSURANCE residual ledger as current. |

______________________________________________________________________

## Still-open

### `fact-context-agents` (P1) — default render dest missing

| Field | Value |
| --- | --- |
| **owner** | PLATFORM (official re-render only) |
| **command** | `uv run python scripts/ci/verify_context_sync.py ; just validate-agents` |
| **live** | `samples/default/` has no `render/`. `justfile:221-226` passes `--render-enabled samples/default/render`. Historical `W4-A01-pytest-agents.txt:2171-2174`: `render missing AGENTS.md: samples/default/render` exit 1. Context-sync-only and template-only agents validators pass. |
| **blocking reason** | Closeout fact requires agents-ecosystem validators at closeout. `render_matrix.json` `default.render_status=failed` (Fumadocs `next.config.ts` `output: string` smoke). Dest must be restored only via `scripts/render-samples.sh` / `render_matrix.py`. **Never hand-create `samples/*/render/**`.** |
| **fix** | Re-render `default` through the official scripts after the Fumadocs NextConfig smoke is fixed (NODE/docs payload). Then re-run `just validate-agents`. |

### `fact-refine-stop` (P1) — two consecutive dry reviews + green ladder not met

| Field | Value |
| --- | --- |
| **owner** | GOAL |
| **command** | Two consecutive review passes on payloads / CLI / wizard / docs / gates with **no new P0/P1**, **and** official ladder green |
| **live** | On disk: `evidence/W4-R03-gates.md` only (gates: no new P0/P1). **Missing** `evidence/W4-R01*` and `evidence/W4-R02*`. `just validate-agents` still red (above). Residual `GOAL.md` R1 is partly stale (it still cites PAY-P0-06 + quality/jinja red) but the **stop rule itself is unmet**. |
| **fix** | Write R01/R02/R03 evidence for all five surfaces after PLATFORM restores default render. If any new P0/P1, reset the dry counter. |

______________________________________________________________________

## Stale residual / ASSURANCE claims (tree already fixed)

Do **not** treat these as live implementation gaps.

| Claim | Residual / ASSURANCE | Live tree |
| --- | --- | --- |
| `just quality` red (5 ruff format files) | `ASSURANCE.md` ledger; `W4-A01-quality.txt` | Residual `PLATFORM.md` R1 **closed**. JOIN tests flipped to leftover keys. |
| Official jinja argv `Not a file` | `W4-A01-ladder.txt:4-6`; old `PLATFORM.md` R3 text | `validate_jinja_templates.py:73-81` walks directories. Residual R3 **closed**. |
| PAY-P0-06 `pytest tests/test_mcp.py` | `residuals/GOAL.md` R1 | `riso-quality.yml.jinja:78-82` is `working-directory: python` + `pytest tests/test_mcp.py`. |
| CLI-JOIN reject-before-remap | historical W2/W4 pytest log 2 failed | `test_riso_cli.py:58` / `test_control_plane_gates.py:20` use `saas_auth=firebase`. Residual `CLI.md` R1 **closed**. |
| OpenSpec leftover empty dir | `residuals/OPENSPEC.md` R1 | `post_gen_project.py:74` `EMPTY_SCAFFOLD_DIRS` includes `"openspec"`. |
| Unrooted `_exclude` `README.md` / `specs/` | `residuals/OPENSPEC.md` R2 | `copier.yml:1893-1898` documents those patterns as **forbidden**; they are not in `_exclude`. |
| Skill Claude mirror mismatch | old W3 `W3-PL-T07-release.txt` | `residuals/SKILL.md` R1 **closed**; skill validator last exit 0. |

`residuals/OPENSPEC.md` R1/R2 do **not** flip `fact-openspec` (default extra still `disabled`). They are also stale vs the COORD files above.

______________________________________________________________________

## Official ladder (historical vs live)

| Command | Historical artifact | Live-tree read |
| --- | --- | --- |
| `just quality` | `W4-A01-quality.txt` exit 1 (format) | Blockers gone; residual closed; **not re-run** |
| 37 × `riso validate --json` | `W4-A01-validate.txt` 37/37 | 37 answer files; no leftover keys; **not re-run** |
| `validate_jinja_templates.py template/files` | W4-A01 official argv exit 1 | Dir walker present; **not re-run** |
| `verify_context_sync.py` | exit 0 | Implementation unchanged |
| `just validate-agents` | exit 1 missing default render | **Still true** — dest absent |
| `render_matrix.py` | `render_matrix.json` + `W3-PL-T06.log` complete | JSON present; 37 variants |
| `sphinx-build -W` | exit 0 + `docs/_build/html/guides/v2-migration.html` | Artifact present; **not re-run** |
| release validators | all exit 0 | Scripts + policy present; **not re-run** |
| `rg riso-mcp src/riso template` | 0 in `src/riso`; 2 prohibition hits in template | Reconfirmed |
| migrate/remap/update pytest | 98 passed | Files still present |
| `git tag -l v2.0.0 2.0.0` | empty | Reconfirmed via refs |

`render_matrix.py` remains **blocking** and was **not** residualed.

______________________________________________________________________

## Counts

| class | n | ids |
| --- | ---: | --- |
| green | 23 | all except the two still-open |
| still-open | 2 | `fact-context-agents`, `fact-refine-stop` |
| blocked (missing `render_matrix.json`) | 0 | — |
| accepted facts | 25 | `facts.meta.json` |
