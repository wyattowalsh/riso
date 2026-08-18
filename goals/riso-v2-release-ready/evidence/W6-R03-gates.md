# W6-R03 — Review pass, surface=gates (read-only)

- Task: `W6-R03`
- Wave: W6
- Lane: GOAL inspect-only; exclusive write is this file
- Surface: gates (`scripts/ci/**`, `scripts/lib/**`, `scripts/render-samples.sh`, `justfile` `validate-agents` / `quality` / `ssot`, `.github/workflows/**`, skill mirrors, `samples/**/copier-answers.yml`)
- Focus: `check_removed_key_ssot.py`, `validate_jinja_templates.py` dir walk, `scripts/lib/sphinx_smoke.py`, `mise trust` in `render-samples.sh`, `just validate-agents`
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-18
- Prior blobs (`W4-R03-gates`, `W5-AUDIT-gates`, `W5-R1-gates`, `W5-R2-gates`, `W5-CLOSE-GATES`, `ASSURANCE.md`, `residuals/GATES.md`): **untrusted**. Every keep/drop re-read in the live tree.
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**
- `render_matrix.py`: **not started, not killed**. Live official matrix is in flight (do not start a second).
- Status: **no new P0 / no new P1**

## Contract

P0 = correctness / contract break on this surface. P1 = lockstep / DX on this surface. Dest absence while an official dest writer is live is a **dest-restore residual**, not a new source P0.

This pass did **not** run `uv` / `just` / `pytest` (read-only source review). Verdicts are from live file reads + `rg`.

## Prior findings — disposition

| id                                      | Prior                             | This pass                                     |
| --------------------------------------- | --------------------------------- | --------------------------------------------- |
| GATES-P0-sphinx-make-linkcheck          | W5-R1 P0; W5-R2 source-fixed      | **still fixed in source**                     |
| GATES-P1-mise-trust                     | W5-R1 P1; W5-R2 source-fixed      | **still fixed in source**                     |
| GATES-P0-container-build-empty-needs    | W5-AUDIT P0; W5-CLOSE source+dest | **still fixed in source** (and rust-api dest) |
| GATES-P0-container-publish-empty-matrix | W5-AUDIT P0; W5-CLOSE source+dest | **still fixed in source** (and rust-api dest) |
| GATES-CLOSED-jinja-dir-walk             | closed W4/W5                      | **closed**                                    |
| GATES-CLOSED-ssot-gate                  | closed W4/W5                      | **closed**                                    |
| GATES-CLOSED-quality-ssot-wiring        | closed W4/W5                      | **closed**                                    |
| GATES-CLOSED-skill-mirrors              | closed W4/W5                      | **closed** (policy texts match on read)       |

## Findings (this pass)

Empty P0 list. Empty P1 list.

| id  | sev | file | issue |
| --- | --- | ---- | ----- |
| —   | —   | —    | none  |

## Checklist

| Item                                       | Verdict                     | Live evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------ | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sphinx official smoke honors `task_runner` | **closed**                  | `scripts/lib/sphinx_smoke.py` `sphinx_linkcheck_command`: default `just`; `just`/`both` + dest `python/justfile` → `["just","linkcheck"]`; `makefile`/`both` + `Makefile` → `uv run make linkcheck`; else `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck` (no dest-root make). Embedded smoke in `scripts/render-samples.sh` L102 / L173–177 imports the helper and reads `config.get("task_runner") or "just"`. Hardcoded `docs_command = ["uv", "run", "make", "linkcheck"]` is **gone**. Tests: `tests/unit/ci/test_sphinx_smoke.py`.                         |
| Dest `mise.toml` trusted before bootstrap  | **closed (source)**         | `render-samples.sh` `render_variant` L665–671: after copy, if dest `mise.toml` exists and `mise` is on PATH, `mise trust "${destination}/mise.toml"` then `mise trust "${destination}"` (dir-level so `just`/`uv` from `python/` still accept the pin). Then `bootstrap_render_dependencies`. Tests: `test_render_samples_trusts_dest_mise_toml`. `render_matrix.py` only invokes `render-samples.sh` — no second dest writer that skips trust.                                                                                                                                           |
| Jinja official argv dir walk               | **closed**                  | `validate_jinja_templates.py` usage `[file1.jinja] [dir ...]`; `_expand_jinja_paths` `is_dir()` → `sorted(rglob("*.jinja"))`. Official ladder `template/files` does not hit `Not a file`. Tests: `tests/unit/ci/test_validate_jinja_templates.py`. Pre-commit still passes filenames (`pass_filenames: true`) — compatible.                                                                                                                                                                                                                                                               |
| 3-way SSOT + leftover sample scan          | **closed**                  | `check_removed_key_ssot.py`: 8 `EXPECTED_KEYS` + `CANONICAL_OPS`; core / `scripts/lib` `_FALLBACK_*` / `web/src/lib/removedAnswerKeys.ts`; `plan.taskgraph.json` `remap_keys` matches the same 8. `scan_sample_answers_for_removed_keys()` via `iter_sample_answer_files()` (skips `render/`, `metadata/`, `node_modules`). `justfile:98` `quality: lint typecheck test ssot`; `justfile:102-104` SSOT command; `quality.yml` cli-tests L274–275 same. Tests: `tests/unit/ci/test_check_removed_key_ssot.py`. Exact leftover YAML-key `rg` on `samples/**/copier-answers.yml`: **empty**. |
| Nested variant names                       | **closed**                  | `render-samples.sh:605` `^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$`. Dest must be `samples/<variant>/render`. GHA `validate-samples` still uses `saas-starter/*`. Bootstrap fail-closed (`failed=1` → variant exit 1).                                                                                                                                                                                                                                                                                                                                                                         |
| `just validate-agents` wiring              | **closed (source)**         | `justfile:217-230`: dest-independent `validate_agents_ecosystem.py` + `check_quality_parity.py`, then dest-dependent `--render-enabled` `samples/{default,cli-docs,full-stack}/render` + `--render-disabled samples/ai-tools-off/render`, then `agent_smoke_agents_md.py` on those four. GHA `validate-agents-ecosystem` **renders those four via official `render-samples.sh` first**, then the same dest argv. Template-only checks do not require dests.                                                                                                                               |
| Skill mirrors + policy                     | **closed**                  | `.agents` and `.claude` `references/no-legacy-answer-policy.md` match on read: 8 keys, apply then reject, lucia fail-closed, no “Do not convert removed keys into canonical keys.” Validator still forbids that sentence. `release-gates.md` still lists SSOT + jinja `template/files` + leftover scan.                                                                                                                                                                                                                                                                                   |
| Container empty `needs` / matrix           | **closed**                  | `riso-container-build.yml.jinja` L180 wraps `scan` in `api_module == enabled` and python/node in `api_languages`. `riso-container-publish.yml.jinja` L24 wraps `publish-ghcr` the same way. Official dest `samples/rust-api/render/.github/workflows/riso-container-build.yml`: `summary.needs: [hadolint]`; no `scan` job; no `needs: []`. Publish dest has no live `publish-ghcr` (commented dockerhub `target:` only).                                                                                                                                                                 |
| Sample answers / no removed keys           | **closed**                  | 26 top-level + 11 `saas-starter/*` answers still live. Canonical dest keys only (`api_module` / `docs_framework` / …). `openspec_extra` absent in sample answers.                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `riso-mcp` in `scripts/`                   | **closed**                  | `rg riso-mcp` under `scripts/`: **empty**.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Official `COPIER_ANSWERS` for pre_gen      | **closed**                  | `render-samples.sh` L652–657 exports JSON from `--answers`. `template/copier.yml` `_tasks` chdir to dest and, if env unset, load dest `.copier-answers.yml`. Tests: `test_render_samples_exports_copier_answers_json`.                                                                                                                                                                                                                                                                                                                                                                    |
| `samples/default/render`                   | **dest-restore residual**   | First listing of `samples/default/` had **no** `render/` child. Later listings showed a partial dest (`AGENTS.md` readable). Official `render_matrix.py` is live. **Not a new source P0.** Do not hand-restore. Do not start a second matrix. Do not treat a mid-copy dest as ladder-green.                                                                                                                                                                                                                                                                                               |
| `just validate-agents` dest steps          | **dest-restore residual**   | Local recipe assumes the four dest trees exist (GHA creates them first). While default dest is absent/partial, dest-dependent steps will fail `check_render_tree` / smoke. Template-only half of the recipe is still valid. After the live official writer finishes, re-run `just validate-agents` — do not invent dests.                                                                                                                                                                                                                                                                 |
| Stale dest smoke JSON                      | **dest-stale, not source**  | `samples/docs-sphinx/smoke-results.json` timestamp `2026-08-14` still records `["uv","run","make","linkcheck"]` + untrusted dest `mise.toml`. That is the **old** harness. Live source no longer emits that argv and now `mise trust`s before bootstrap. Re-render via the official writer only.                                                                                                                                                                                                                                                                                          |
| `render_matrix.json`                       | **present; not residualed** | `samples/metadata/render_matrix.json` exists (37 variants). Contents are from 2026-08-14 (historical smoke reds). A live official rewrite is in progress. Missing JSON would be a fail; stale JSON during a live run is not a new source P0.                                                                                                                                                                                                                                                                                                                                              |

## 1. Sphinx smoke — source closed

`scripts/lib/sphinx_smoke.py`:

```python
runner = str(task_runner or "just").strip().lower() or "just"
if runner in {"just", "both"} and (python_cwd / "justfile").exists():
    return ["just", "linkcheck"]
if runner in {"makefile", "both"} and (python_cwd / "Makefile").exists():
    return ["uv", "run", "make", "linkcheck"]
return ["uv", "run", "--group", "docs", "sphinx-build", "-b", "linkcheck", "docs", "dist/docs-linkcheck"]
```

Default sample Sphinx dests omit `task_runner` in answers (`samples/docs-sphinx/copier-answers.yml` L26–27 `docs_framework: sphinx-shibuya` only). Copier default is `just`, which excludes `python/Makefile`. The helper prefers `just linkcheck` when `python/justfile` exists, else sphinx-build — never dest-root `make` on a just dest.

## 2. `mise trust` — source closed

Official dest writer trusts the generated pin **after copy, before** `uv`/`pnpm`/`just`. Trust failure is logged as WARNING; bootstrap still fail-closes if mise then refuses the pin. That is fail-closed dest bootstrap, not a missing-trust source hole.

`residuals/GATES.md` R1 still says dest `mise.toml` is untrusted on rust-api/go-api bootstrap. That residual is **dest/env leftover vs live source**. Do not re-open a source P1.

## 3. `just validate-agents` — dest-coupled by design

```text
justfile:218-229
  validate_agents_ecosystem.py                  # templates + maintainer bridges
  check_quality_parity.py                       # template quality files only
  validate_agents_ecosystem.py --render-*       # requires dest trees
  agent_smoke_agents_md.py <four dests>         # requires dest AGENTS.md
```

`validate_agents_ecosystem.py` `check_render_tree` fail-closes if dest `AGENTS.md` is missing. GHA L216–229 restores dests via `./scripts/render-samples.sh` before that. Local `just validate-agents` does not render. While the official matrix is wiping/restoring `samples/default/render`, dest-dependent local green is **blocked on dest restore**, not on a gates source bug.

## 4. SSOT / leftover keys — closed

`plan.taskgraph.json` `remap_keys` = the same 8 as `EXPECTED_KEYS`. Sample answer leftover `rg` (`api_tracks` / `api_language` / `docs_site` / `mcp_language` / `saas_starter_module` / `saas_auth` / `saas_billing` / `include_admin` as YAML roots): **empty**.

## Closed on this surface (do not re-open)

- Jinja official argv `template/files` directory walk.
- `just quality` includes `ssot`; GHA `cli-tests` runs `check_removed_key_ssot.py`.
- Skill `.agents` ↔ `.claude` policy: 8-key apply-then-reject; no “Do not convert”.
- Nested `saas-starter/*` variant regex + GHA matrix paths.
- Bootstrap fail-closed in `render-samples.sh`.
- Container jinja + rust-api dest: no live empty `needs` / empty publish matrix.
- Sample answers: zero leftover removed keys.
- `scripts/` has no `riso-mcp`.
- Official copy exports `COPIER_ANSWERS`; Copier `_tasks` chdir to dest.
- GHA `riso-quality.yml.jinja` uses `working-directory: python` + `uv --directory python` (live dest `samples/api-python/render/.github/workflows/riso-quality.yml` matches). `residuals/GATES.md` R4 is **stale**.
- Circle / GitLab jinja now `uv --directory python sync` (`template/files/.circleci/config.yml.jinja:82`, `.gitlab/.gitlab-ci.yml.jinja:51,327`). `residuals/GATES.md` R3 is **stale vs live source** (foreign tree; not re-opened here).

## Foreign / dest / below-P1 (not this pass’s P0/P1)

- Default / fumadocs dest smoke in the 2026-08-14 `render_matrix.json` blob — NODE payload / dest-stale until the live official run rewrites JSON. Gate reports dest smoke; do not treat historical JSON as a new gates source P0.
- `just ci-full` still does not call `ssot`; `just quality` / `just ci` / GHA cli-tests do.
- `just clean-all` is `rm -rf samples/*/render` (does not clean nested `saas-starter/*/render`).
- `task-graph.md` still names an `src/riso/mcp/**` lane. Policy forbids reintroducing `riso-mcp`.
- `residuals/GATES.md` R1 still marked open — dest/env vs source-fixed `mise trust`.
- Do not hand-edit dests. Do not start a second `render_matrix.py`.

## Path lock

| Class                                            | Count                                      |
| ------------------------------------------------ | ------------------------------------------ |
| This-session writes                              | 1 — this evidence file                     |
| `samples/*/render/**` hand-edits                 | 0                                          |
| Lockfile / secret / foreign-tree / product edits | 0                                          |
| `render_matrix.py` started or killed             | 0                                          |
| `just validate-agents` executed                  | 0 (dest-dependent; dest restore in flight) |
