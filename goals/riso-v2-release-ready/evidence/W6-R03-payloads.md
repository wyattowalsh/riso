# W6-R03 — Review pass, surface=payloads

- **Task:** `W6-R03` · surface=`payloads`
- **Mode:** read-only inspection of live source
- **Scope:** `template/files/python/**`, `template/files/node/**` except `node/saas/**`, `template/files/go/**`, `template/files/rust/**`, `template/files/electron/**`, `template/files/tauri/**`, `template/hooks/**` (plus known-closed GHA / Circle / GitLab / quality justfile checks from W5-R1)
- **Date:** 2026-08-18
- **Repo / cwd:** `/Users/ww/dev/projects/riso`
- **Prior blob:** `goals/riso-v2-release-ready/evidence/W5-R1-payloads.md` treated as a map, not truth. Live files re-verified.
- **Product / hook edits:** **0**
- **`samples/*/render/**` writes:** **0** (dests read as smoke evidence only)
- **Dest-stale smoke:** residual, **not** a new P0, when SOURCE jinja is already fixed.

P0 = source still broken on a default or official/common path (file:line). P1 = lockstep / extra / DX. Empty lists only after inspection.

## Contract (re-read live)

- Remap: apply-then-reject. No leftover remapped Copier keys as live jinja identifiers.
- Generated Node floor **20**. OpenSpec extra **off**. SaaS flatten stays reverted (out of this write; configs still unflattened).
- Generated Python `test` extra includes `hypothesis` + `respx`. mypy is not default.
- Generated `mise.toml` always-on: `python = "3.11"`, `node = "20"`.
- No `riso-mcp` package.

## Known source-closed (verified live)

| Check                                                                                              | Verdict              | Live evidence                                                                                                                                                                                                                                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Leftover remap apply-then-reject                                                                   | **closed**           | `pre_gen` L310–313 apply then reject; `main()` L809 before `_write_copier_context`. `post_gen` L138–150 apply then leftover `SystemExit(1)`. No `{% if saas_auth %}` / `api_language` / `docs_site` / `mcp_language` / `api_tracks` / `saas_starter_module` / `include_admin` jinja identifiers.                                                                                           |
| Jinja dir walk                                                                                     | **closed**           | `scripts/ci/validate_jinja_templates.py` L73–80 `_expand_jinja_paths` walks dirs.                                                                                                                                                                                                                                                                                                          |
| OpenSpec `EMPTY_SCAFFOLD`                                                                          | **closed**           | `post_gen` L74 `openspec` in `EMPTY_SCAFFOLD_DIRS`. `openspec/specs/project/spec.md.jinja` exists.                                                                                                                                                                                                                                                                                         |
| Fumadocs `as const` + sitemap/robots                                                               | **closed**           | `next.config.ts.jinja` L13 `output: 'export' as const`. `robots.ts.jinja` L4–5 and `sitemap.ts.jinja` L5–6 `dynamic = 'force-static'` + `revalidate = false`. Sibling llms/rss routes match.                                                                                                                                                                                               |
| Search `GET()` wrapper                                                                             | **closed in source** | `app/api/search/route.ts.jinja` L15–16 and L29–30: `export async function GET() { return staticGET(); }`. Official `samples/default/render` (smoke 2026-08-18, docs **passed**) matches source.                                                                                                                                                                                            |
| GHA matrix / deps gated + `uv --directory python`                                                  | **closed**           | `riso-matrix.yml.jinja` L25 python-track gate, L66 `working-directory: python`, L76 `uv --directory python`; else L132 `scaffold-ok`. `riso-deps-update.yml.jinja` L14 gate + L37–43 `uv --directory python`.                                                                                                                                                                              |
| Circle / GitLab docs paths + dest-root uv                                                          | **closed**           | Both: `uv --directory python sync` / ruff / ty / pylint / sphinx. Fumadocs `mv node/docs/fumadocs/out public/`. Docusaurus `pnpm --filter docs-docusaurus` + `mv node/docs/docusaurus/build public/`. Artifacts are `public/`, not leftover `docs/out`.                                                                                                                                    |
| Quality justfile python gate                                                                       | **closed**           | `justfile.quality.jinja` L2 `_python` / L20–45 gated recipes; `uv --directory` `python_dir`.                                                                                                                                                                                                                                                                                               |
| PAY-P0-06 MCP pytest                                                                               | **closed**           | GHA `working-directory: python` + `tests/test_mcp.py`. Circle/GitLab `cd python` then same path. Rust MCP GHA `working-directory: rust/mcp`.                                                                                                                                                                                                                                               |
| Node 20 / mermaid / sidebar / electron-store / go.work / no clang-lld / hypothesis+respx / no mypy | **closed**           | `mise.toml.jinja` L7 `node = "20"`. Docusaurus mermaid is file-local (no `export {`). Sidebars have no `require(...sidebar.js)`. `electron.vite.config.ts.jinja` L8 + L24 exclude `electron-store`. `go.work.jinja` `.` + `./mcp`. Tauri `src-tauri` has no clang/lld (lldb in launch.json only). `pyproject.toml.jinja` L38–39 + shipped tests. `rg -i mypy template/files/python` empty. |

## Dest-stale (residual, not new P0)

- `samples/docs-fumadocs/smoke-results.json` (2026-08-17) still red on `/api/search` `request.url`. Dest `route.ts` is `export const GET = search.staticGET`. **Source already uses the named `GET()` wrapper.** Official default dest matches source and docs smoke passed.
- `samples/docs-fumadocs-full/smoke-results.json` (2026-08-14) still red on `/robots.txt` missing `dynamic`/`revalidate`. **Source robots/sitemap already patched.**
- `samples/docs-sphinx/smoke-results.json` (2026-08-14) still `No rule to make target 'linkcheck'` under old `uv run make linkcheck`. **Source `python/{Makefile,justfile}.jinja` already define `linkcheck`.** COORD exclude of Makefile on just-only dests remains `residuals/PY.md` R1. Newer official Sphinx smoke (`changelog-python`, 2026-08-18) now invokes `just linkcheck` and gets past the missing-recipe class.

## Findings

### PAY-P0-sphinx-myst-linkify-dep — P0

- **Files:** `template/files/python/docs/conf.py.jinja:191`, `template/files/python/pyproject.toml.jinja:50-70`
- **Live:** `myst_enable_extensions` includes `"linkify"`. Docs extra ships `myst-parser>=3.0.1` but not `linkify-it-py` and not `myst-parser[linkify]`.
- **Why it breaks:** MyST raises `ModuleNotFoundError: Linkify enabled but not installed.` Official `samples/changelog-python` was re-rendered 2026-08-18 (dest `conf.py` / `pyproject.toml` match live jinja). Docs smoke `just linkcheck` is now the correct runner and **fails on this import**, not on a missing recipe.
- **Not dest-stale.** `docs-sphinx` dest is older (make-target residual); a fresh Sphinx dest will hit this same source hole.
- **Fix (PY):** add `linkify-it-py` (or `myst-parser[linkify]`) to the generated `docs` extra, **or** drop `"linkify"` from `myst_enable_extensions`. Official re-render only.

### PAY-P1-fumadocs-ai-search-static-export — P1

- **File:** `template/files/node/docs/fumadocs/app/api/chat/route.ts.jinja:5-8`
- **Live:** gated on `fumadocs_ai_search == 'enabled'`. Emits `export async function POST(req: Request)` next to `output: 'export' as const`. Extra is **disabled** on default + official fumadocs samples (`copier.yml` default `"disabled"`).
- **Why P1 not P0:** not a default/official path. Enabling the extra still cannot static-export a POST route.
- **Fix (NODE):** do not emit the chat route (or drop `output: 'export'`) when AI search is on. Do not restore middleware/rewrites.

### PAY-P1-gha-release-uv-root — P1

- **File:** `template/files/.github/workflows/riso-release.yml.jinja:58-62` (and L99–100)
- **Live:** changelog-gated workflow still `uv sync` / `uv run task quality` at dest root. Quality.yml / matrix / deps-update already use `uv --directory python`. Canonical pyproject is `python/pyproject.toml` (`post_gen` `cleanup_legacy_root_pyproject`). Official `changelog-python` ships this workflow (`changelog_module: enabled`, `ci_platform: github-actions`).
- **Why P1 not P0:** same class as closed PAY-P1-gha-uv-root (python track is present; path is wrong). Not the default dest.
- **Fix:** `uv --directory python sync` / `uv --directory python run task quality`. Official re-render only.

### PAY-P1-gitlab-circle-sys-cwd — P1

- **Files:** `template/files/.gitlab/.gitlab-ci.yml.jinja:235-236` / `L307`; `template/files/.circleci/config.yml.jinja:278` / `L370`
- **Live:** Rust jobs `cargo …` at dest root (crate is `rust/Cargo.toml`). Go jobs `go build … ./cmd/...` at dest root (module is `go/`; bins are `./cli` / `./api` per `go/Makefile.jinja` L42–45; there is no `cmd/` at module root).
- **Why P1 not P0:** official `rust-*` / `go-api` dests use `ci_platform: github-actions`. GHA rust quality is MCP-only (`rust/mcp`); no official GitLab/Circle rust/go sample.
- **Fix:** `cd rust` / `cd go` (or `working-directory`) and `go build ./api` / `./cli` to match the Makefile.

## Not elevated

- Nested fumadocs `deploy.yml.jinja`: **absent** (W5-R1 P1 closed by deletion). Repo-root `riso-docs-deploy.yml.jinja` uses Node 20 + `node/docs/fumadocs/out`.
- SaaS `@/db/schema` leftovers: **out of scope** (`node/saas/**`).
- `.docker/Dockerfile.jinja` dest-root `COPY pyproject.toml`: flatten-era; not official smoke. Same class as dest-root uv.
- GHA `riso-quality.yml` has no rust/go jobs for rust-api / go-api (MCP rust only). Missing job, not a red default smoke.
- GitLab monorepo `NODE_VERSION: ['20', '22']`: tests 22; does not raise generated engines floor (`>=20.0.0`).
- Container `needs` / scan matrix: still gated on python/node API (`riso-container-build.yml.jinja` L180).
- `residuals/GATES.md` R3 dest-root Circle/GitLab `uv sync`: **stale residual** — source now uses `uv --directory python`.

## Strengths (do not regress)

- Hooks apply-then-reject; leftover reject shape unchanged.
- Eight remapped keys are not live jinja aliases.
- Generated mise Node **20**; OpenSpec extra excluded + hook cleanup lists `openspec`.
- Fumadocs static-export flags on MetadataRoute + search wrapper; `as const` kept.
- GHA python jobs gated; Circle/GitLab docs paths and python `uv --directory` match `python/`.
- Quality justfile no longer always `quality-python`.
- hypothesis + respx extras and shipped tests; no mypy under `template/files/python`.
- `go.work` `.` + `./mcp`; electron-store exclude; no clang/lld; Docusaurus mermaid file-local.

## Path lock

| Class                                   | Count                  |
| --------------------------------------- | ---------------------- |
| This-session writes                     | 1 — this evidence file |
| Product / hook edits                    | 0                      |
| `samples/*/render/**` hand-edits        | 0                      |
| Lockfile / secret / commit / tag / push | 0                      |
| `render_matrix.py` started or killed    | 0                      |

## Verdict

```yaml
surface: payloads
p0:
  - id: PAY-P0-sphinx-myst-linkify-dep
    files:
      - template/files/python/docs/conf.py.jinja:191
      - template/files/python/pyproject.toml.jinja:50-70
    summary: myst linkify enabled without linkify-it-py; official changelog-python just linkcheck red
p1:
  - id: PAY-P1-fumadocs-ai-search-static-export
    files: [template/files/node/docs/fumadocs/app/api/chat/route.ts.jinja:5-8]
    summary: POST chat route incompatible with output export when extra on
  - id: PAY-P1-gha-release-uv-root
    files: [template/files/.github/workflows/riso-release.yml.jinja:58-62]
    summary: changelog release quality still dest-root uv
  - id: PAY-P1-gitlab-circle-sys-cwd
    files:
      - template/files/.gitlab/.gitlab-ci.yml.jinja:235
      - template/files/.circleci/config.yml.jinja:370
    summary: rust/go jobs dest-root; go ./cmd/... does not match go/Makefile
summary: >
  W5-R1 payload P0/P1 cluster is closed in source. Dest-stale fumadocs/sphinx
  smokes are residuals. New P0 is Sphinx MyST linkify missing linkify-it-py
  (changelog-python 2026-08-18 smoke). Three P1s (AI-search extra vs static
  export; release.yml dest-root uv; GitLab/Circle rust/go cwd). Refine-stop
  does not increment. Owner PY for the P0; NODE / GATES for P1s.
```
