# W6-R04 — Review pass, surface=gates (read-only)

- Task: `W6-R04`
- Wave: W6
- Lane: GOAL inspect-only; exclusive write is this file
- Surface: gates (`scripts/ci/**`, `scripts/lib/**`, `scripts/render-samples.sh`, `justfile` `validate-agents` / `quality` / `ssot`, `.github/workflows/**`, `template/files/.github/workflows/riso-release.yml.jinja`)
- Focus: `validate_jinja_templates.py` dir walk, `check_removed_key_ssot.py`, `scripts/lib/sphinx_smoke.py`, `mise trust` in `render-samples.sh`, `riso-release.yml.jinja` now `uv --directory python`
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-18
- Prior blobs (`W4-R03-gates`, `W5-AUDIT-gates`, `W5-R1-gates`, `W5-R2-gates`, `W5-CLOSE-GATES`, `W6-R03-gates`, `W6-WF-GHA-release`, `ASSURANCE.md`, `residuals/GATES.md`): **untrusted**. Every keep/drop re-read in the live tree.
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**
- `render_matrix.py`: **not started, not killed**. Official dest writer / matrix is the restore path. Do not start a second.
- Status: **no new P0 / no new P1**

## Contract

P0 = correctness / contract break on this surface. P1 = lockstep / DX on this surface. Dest absence while an official dest writer is live is a **dest-restore residual**, not a new source P0.

This pass did **not** run `uv` / `just` / `pytest` (read-only source review). Verdicts are from live file reads + `rg`.

There is **no** `scripts/ci/sphinx_smoke.py`. Live helper is `scripts/lib/sphinx_smoke.py`. There is **no** `_run_linkcheck_and_collect` / `_LINKCHECK_SOFT_FAIL_MARKERS` / `--fail-on-linkcheck` collector in this tree. The Sphinx gate on this surface is `task_runner`-aware `sphinx_linkcheck_command`, not a soft-fail linkcheck wrapper.

## Prior findings — disposition

| id                                      | Prior                                        | This pass                                   |
| --------------------------------------- | -------------------------------------------- | ------------------------------------------- |
| GATES-P0-sphinx-make-linkcheck          | W5-R1 P0; W5-R2 / W6-R03 source-fixed        | **still fixed in source**                   |
| GATES-P1-mise-trust                     | W5-R1 P1; W5-R2 / W6-R03 source-fixed        | **still fixed in source**                   |
| PAY-P1-gha-release-uv-root              | W6-R03 payloads P1; W6-WF-GHA-release closed | **source-closed** (`uv --directory python`) |
| GATES-P0-container-build-empty-needs    | W5-AUDIT P0; W5-CLOSE source+dest            | **not re-opened**                           |
| GATES-P0-container-publish-empty-matrix | W5-AUDIT P0; W5-CLOSE source+dest            | **not re-opened**                           |
| GATES-CLOSED-jinja-dir-walk             | closed W4/W5/W6-R03                          | **closed**                                  |
| GATES-CLOSED-ssot-gate                  | closed W4/W5/W6-R03                          | **closed**                                  |
| GATES-CLOSED-quality-ssot-wiring        | closed W4/W5/W6-R03                          | **closed**                                  |

## Findings (this pass)

Empty P0 list. Empty P1 list.

| id  | sev | file | issue |
| --- | --- | ---- | ----- |
| —   | —   | —    | none  |

## Checklist

| Item                                       | Verdict                     | Live evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Jinja official argv dir walk               | **closed**                  | `scripts/ci/validate_jinja_templates.py` usage `[file1.jinja] [dir ...]`; `_expand_jinja_paths` L73–81 `is_dir()` → `sorted(rglob("*.jinja"))`. Official ladder `template/files` does not hit `Not a file`. Tests: `tests/unit/ci/test_validate_jinja_templates.py`. Pre-commit `pass_filenames: true` remains compatible.                                                                                                                                                                                                                                                                                       |
| 3-way SSOT + leftover sample scan          | **closed**                  | `scripts/ci/check_removed_key_ssot.py`: 8 `EXPECTED_KEYS` + `CANONICAL_OPS`; core / `scripts/lib` `_FALLBACK_*` / `web/src/lib/removedAnswerKeys.ts`; `plan.taskgraph.json` `remap_keys` is the same 8. `scan_sample_answers_for_removed_keys()` via `iter_sample_answer_files()` (skips `render/`, `metadata/`, `node_modules`). `justfile:98` `quality: lint typecheck test ssot`; `justfile:102-104` SSOT command; `quality.yml` cli-tests L274–275 same. Tests: `tests/unit/ci/test_check_removed_key_ssot.py`. Exact leftover YAML-key `rg` on `samples/**/copier-answers.yml`: **empty**.                  |
| Sphinx official smoke honors `task_runner` | **closed**                  | `scripts/lib/sphinx_smoke.py` `sphinx_linkcheck_command`: default `just`; `just`/`both` + dest `python/justfile` → `["just","linkcheck"]`; `makefile`/`both` + `Makefile` → `uv run make linkcheck`; else `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck` (no dest-root make). Embedded smoke in `scripts/render-samples.sh` L102 / L173–177 imports the helper and reads `config.get("task_runner") or "just"`. Hardcoded `docs_command = ["uv", "run", "make", "linkcheck"]` is **gone**. Tests: `tests/unit/ci/test_sphinx_smoke.py`.                                                |
| Dest `mise.toml` trusted before bootstrap  | **closed (source)**         | `render-samples.sh` `render_variant` L665–671: after copy, if dest `mise.toml` exists and `mise` is on PATH (`command -v mise`, not `MISE_BIN`), `mise trust "${destination}/mise.toml"` then `mise trust "${destination}"` (dir-level so `just`/`uv` from `python/` still accept the pin). Then `bootstrap_render_dependencies`. Tests: `test_render_samples_trusts_dest_mise_toml`. `render_matrix.py` only invokes `render-samples.sh`.                                                                                                                                                                       |
| Release workflow dest-root `uv`            | **closed (source)**         | `template/files/.github/workflows/riso-release.yml.jinja` quality job L46 Python-track gate (cli/api/mcp python **or** sphinx); L60–61 `working-directory: python` / `uv sync`; L64 `uv --directory python run task quality`; non-Python dests L66–67 echo only. Release job L105–107 same `working-directory: python` / `uv sync`; L131–132 `uv --directory python run python`. Matches `riso-quality.yml.jinja` / `riso-matrix.yml.jinja`. Official dest `samples/changelog-python/render/.github/workflows/riso-release.yml` is **dest-stale** (still dest-root `uv sync` / `uv run`). Do not hand-edit dest. |
| `just validate-agents` wiring              | **closed (source)**         | `justfile:217-230`: dest-independent `validate_agents_ecosystem.py` + `check_quality_parity.py`, then dest-dependent `--render-enabled` `samples/{default,cli-docs,full-stack}/render` + `--render-disabled samples/ai-tools-off/render`. Local recipe does not render. GHA restores those dests via official `render-samples.sh` first.                                                                                                                                                                                                                                                                         |
| `samples/default/render`                   | **dest-restore residual**   | `samples/default/` listing has **no** `render/` child (`copier-answers.yml`, `smoke-results.json`, metadata only). `samples/default/smoke-results.json` timestamp `2026-08-18T07:48:02Z` records docs **passed** — dest existed, then was wiped. Official writer `rm -rf "${destination}"` before copy (`render-samples.sh` L648–649). Official `samples/metadata/render_matrix.json` is present (37 variants; historical 2026-08-14 blob). **Not a new source P0.** Do not hand-restore. Do not start a second matrix.                                                                                          |
| `just validate-agents` dest steps          | **dest-restore residual**   | Recipe assumes the four dest trees exist. `cli-docs` / `full-stack` / `ai-tools-off` dests are present; `samples/default/render` is absent. Dest-dependent steps will fail `check_render_tree` / smoke until official restore finishes. Template-only half of the recipe is still valid.                                                                                                                                                                                                                                                                                                                         |
| Stale dest smoke JSON                      | **dest-stale, not source**  | `samples/docs-sphinx/smoke-results.json` timestamp `2026-08-14` still records `["uv","run","make","linkcheck"]` + missing `linkcheck` recipe. Live source no longer emits that argv and now `mise trust`s before bootstrap. Re-render via the official writer only.                                                                                                                                                                                                                                                                                                                                              |
| `render_matrix.json`                       | **present; not residualed** | `samples/metadata/render_matrix.json` exists (37 variants). Contents remain the 2026-08-14 historical smoke set. Missing JSON would be a fail; stale JSON during dest restore is not a new source P0.                                                                                                                                                                                                                                                                                                                                                                                                            |

## 1. Jinja dir walk — source closed

```python
def _expand_jinja_paths(raw_paths: Iterable[Path]) -> list[Path]:
    expanded: list[Path] = []
    for file_path in raw_paths:
        if file_path.is_dir():
            expanded.extend(sorted(file_path.rglob("*.jinja")))
            continue
        expanded.append(file_path)
    return expanded
```

Official argv `template/files` is a directory. After expand, `main()` only reports `Not a file` for leftover non-files — dirs are already walked.

## 2. SSOT — source closed

`EXPECTED_KEYS` / `plan.taskgraph.json` `remap_keys` =

`api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`.

Sample leftover YAML-root `rg` for those eight keys: **empty**. Scan skips dest trees.

## 3. Sphinx smoke — source closed

`scripts/lib/sphinx_smoke.py`:

```python
runner = str(task_runner or "just").strip().lower() or "just"
if runner in {"just", "both"} and (python_cwd / "justfile").exists():
    return ["just", "linkcheck"]
if runner in {"makefile", "both"} and (python_cwd / "Makefile").exists():
    return ["uv", "run", "make", "linkcheck"]
return ["uv", "run", "--group", "docs", "sphinx-build", "-b", "linkcheck", "docs", "dist/docs-linkcheck"]
```

Default Sphinx dests omit `task_runner` in answers; Copier default is `just`, which excludes `python/Makefile`. Helper prefers `just linkcheck` when `python/justfile` exists, else sphinx-build — never dest-root `make` on a just dest.

## 4. `mise trust` — source closed

Official dest writer trusts the generated pin **after copy, before** `uv`/`pnpm`/`just`. Trust failure is logged as WARNING; bootstrap still fail-closes if mise then refuses the pin. That is fail-closed dest bootstrap, not a missing-trust source hole.

`residuals/GATES.md` R1 still says dest `mise.toml` is untrusted on rust-api/go-api bootstrap. That residual is **dest/env leftover vs live source**. Do not re-open a source P1.

## 5. `riso-release.yml.jinja` — dest-root `uv` source-closed

W6-R03 payloads recorded dest-root `uv sync` / `uv run task quality` in the changelog release quality job. Live source now:

- Python-track gate on quality (same idea as matrix).
- Install: `working-directory: python` + `uv sync`.
- Quality: `uv --directory python run task quality`.
- No-Python changelog dest: no-op echo; `jobs.release` still `needs: [quality]`.
- Release-job Python: same cwd / `uv --directory python`.

Official `samples/changelog-python/render/.github/workflows/riso-release.yml` L55–58 / L94 / L110–111 is still dest-root `uv`. **Dest-stale.** Official re-render only.

## 6. `just validate-agents` — dest-coupled by design

```text
justfile:218-229
  validate_agents_ecosystem.py                  # templates + maintainer bridges
  check_quality_parity.py                       # template quality files only
  validate_agents_ecosystem.py --render-*       # requires dest trees
  agent_smoke_agents_md.py <four dests>         # requires dest AGENTS.md
```

`samples/default/render` is missing. Local dest-dependent green is **blocked on dest restore**, not on a gates source bug.

## Closed on this surface (do not re-open)

- Jinja official argv `template/files` directory walk.
- `just quality` includes `ssot`; GHA `cli-tests` runs `check_removed_key_ssot.py`.
- Sphinx smoke `task_runner` helper + render-samples wiring.
- Official dest writer `mise trust` of dest pin + dest dir.
- Changelog release jinja: no dest-root `uv`; Python track uses `working-directory: python` + `uv --directory python`.
- Nested `saas-starter/*` variant regex + GHA matrix paths.
- Bootstrap fail-closed in `render-samples.sh`.
- Sample answers: zero leftover removed keys.
- Official copy exports `COPIER_ANSWERS`.
- GHA `riso-quality.yml.jinja` / `riso-matrix.yml.jinja` / `riso-deps-update.yml.jinja` use `uv --directory python`.
- Circle / GitLab jinja `uv --directory python sync` (`template/files/.circleci/config.yml.jinja:82`, `.gitlab/.gitlab-ci.yml.jinja:51`). `residuals/GATES.md` R3 is **stale vs live source**.

## Foreign / dest / below-P1 (not this pass’s P0/P1)

- `samples/default/render` absence while official dest writer / matrix is the restore path — dest-restore residual, not source P0.
- Official dest `changelog-python` `riso-release.yml` still dest-root `uv` — dest-stale vs live jinja.
- `samples/docs-sphinx/smoke-results.json` 2026-08-14 make-linkcheck red — dest-stale vs live helper.
- 2026-08-14 `render_matrix.json` historical smoke reds — dest-stale until official rewrite.
- `just ci-full` still does not call `ssot`; `just quality` / `just ci` / GHA cli-tests do.
- `residuals/GATES.md` R1 still marked open — dest/env vs source-fixed `mise trust`.
- `residuals/GATES.md` R4 dest `riso-quality.yml` stale until official re-render.
- Payload items from W6-R03 (`PAY-P0-sphinx-myst-linkify-dep`, fumadocs AI search POST, Circle/GitLab sys cwd) stay on **payloads**, not this gates lock.
- Do not hand-edit dests. Do not start a second `render_matrix.py`.

## Path lock

| Class                                            | Count                                               |
| ------------------------------------------------ | --------------------------------------------------- |
| This-session writes                              | 1 — this evidence file                              |
| `samples/*/render/**` hand-edits                 | 0                                                   |
| Lockfile / secret / foreign-tree / product edits | 0                                                   |
| `render_matrix.py` started or killed             | 0                                                   |
| `just validate-agents` executed                  | 0 (dest-dependent; `samples/default/render` absent) |
