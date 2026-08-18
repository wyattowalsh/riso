# W6-R05 — Review pass, surface=payloads

- **Task:** `W6-R05` · surface=`payloads` (second dry pass after `W6-R04`)
- **Mode:** read-only inspection of live source
- **Scope:** `template/files/python/**`, `template/files/node/**` except `node/saas/**`, `template/files/go/**`, `template/files/rust/**`, `template/files/electron/**`, `template/files/tauri/**`, `template/hooks/**` (plus W6-R03/R04 GHA / Circle / GitLab / quality justfile follow-ups)
- **Date:** 2026-08-18
- **Repo / cwd:** `/Users/ww/dev/projects/riso`
- **Prior blobs:** `W6-R04-payloads.md` + `W6-R03-payloads.md` + `W6-PY-linkify.md` + `W6-NODE-chat.md` treated as maps, not truth. Live files re-verified.
- **Product / hook edits:** **0**
- **`samples/*/render/**` writes:** **0** (dests read as smoke evidence only)
- **Dest-stale smoke:** residual, **not** a new P0, when SOURCE jinja is already fixed.
- **New P0/P1 rule:** only if SOURCE is newly broken (`file:line`). Known extra-only P1 kept.

P0 = source still broken on a default or official/common path (`file:line`). P1 = lockstep / extra / DX. Empty lists only after inspection.

## Contract (re-read live)

- Remap: apply-then-reject. No leftover remapped Copier keys as live jinja identifiers.
- Generated Node floor **20**. OpenSpec extra **off**. SaaS flatten stays reverted (out of this write).
- Generated Python `test` extra includes `hypothesis` + `respx`. mypy is not default.
- Generated `mise.toml` always-on: `python = "3.11"`, `node = "20"`.
- No `riso-mcp` package.

## W6-R04 P0 — still empty (source re-check)

| Field                                   | Live                                                                                                      |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| W6-R03 `PAY-P0-sphinx-myst-linkify-dep` | **closed in source** (not re-opened)                                                                      |
| Enable                                  | `template/files/python/docs/conf.py.jinja:191` still `"linkify"`                                          |
| Extra                                   | `template/files/python/pyproject.toml.jinja:54` `linkify-it-py>=2.1.0` next to `myst-parser>=3.0.1` (L53) |
| Fresh dest                              | A new Sphinx dest will install `linkify-it-py` with the docs group                                        |

No other default/official source hole found on this pass.

## Dest-stale (residual, not new P0)

- `samples/changelog-python/render/python/pyproject.toml` docs extra still ends at `myst-parser>=3.0.1` (L51); **no** `linkify-it-py`. Smoke `2026-08-18T07:36:46Z` `just linkcheck` still red: `ModuleNotFoundError: Linkify enabled but not installed.` **Source already ships the dep.** Official re-render only.
- `samples/docs-sphinx/render/python/pyproject.toml` L42 same dest-stale extra (no `linkify-it-py`). Smoke `2026-08-14` still `No rule to make target 'linkcheck'` under `uv run make linkcheck`. **Source** `python/{Makefile,justfile}.jinja` already define `linkcheck` (justfile gated on sphinx). `residuals/PY.md` R1 (COORD exclude + PLATFORM argv).
- `samples/docs-fumadocs` dest **and** smoke moved since W6-R04: dest `app/api/search/route.ts` is now the named `GET()` wrapper; smoke `2026-08-18T08:37:08Z` docs **passed**. Prior `/api/search` `request.url` dest-stale is **closed on this official dest**. Not a new P0.
- `samples/docs-fumadocs-full` dest `robots.ts` / `sitemap.ts` already have `dynamic = 'force-static'` + `revalidate = false`. Smoke `2026-08-14` still red on `/robots.txt` missing those flags — **stale smoke only**. Source `robots.ts.jinja` L4–5 / `sitemap.ts.jinja` L5–6 already patched.

## Known source-closed (verified live)

| Check                                         | Verdict              | Live evidence                                                                                                                                                                                                                                                                            |
| --------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leftover remap identifiers                    | **closed**           | No `{% if saas_auth %}` / `api_language` / `docs_site` / `mcp_language` / `api_tracks` / `saas_starter_module` / `include_admin` jinja identifiers. Mentions are remap docs only (`AGENTS.md.jinja`, `docs/upgrade-guide.md.jinja`). SaaS uses `saas_auth_provider` (out of this write). |
| Hooks apply-then-reject                       | **closed**           | `pre_gen` `_validate_removed_answer_keys` L310–313 apply then reject; `main()` L809 before `_write_copier_context`. `post_gen` L138–150 apply then leftover `SystemExit(1)`.                                                                                                             |
| OpenSpec `EMPTY_SCAFFOLD`                     | **closed**           | `post_gen` `EMPTY_SCAFFOLD_DIRS` includes `openspec` (L74). Extra default remains `disabled`.                                                                                                                                                                                            |
| Fumadocs static-export flags + search wrapper | **closed**           | `next.config.ts.jinja` L13 `output: 'export' as const`. robots/sitemap + named `GET()` wrapper as above. Sibling llms/rss routes keep `force-static` + `revalidate = false`. **No** `export async function POST` under `template/files/node/docs`.                                       |
| GHA matrix / deps + quality justfile          | **closed**           | `riso-matrix.yml.jinja` L25 python-track gate, L66 `working-directory: python`, L76 `uv --directory python`. `riso-deps-update.yml.jinja` L14 gate + L37–43 `uv --directory python`. Quality `justfile.quality.jinja` L2 `_python` / L20–45 gated; `uv --directory`.                     |
| GHA quality dest-root uv                      | **closed**           | `riso-quality.yml.jinja` L54 `working-directory: python` + `uv sync`; L68 `uv --directory python run task quality`; MCP pytest L80–83 `working-directory: python` + `tests/test_mcp.py`.                                                                                                 |
| hypothesis + respx / no mypy / Node 20        | **closed**           | `pyproject.toml.jinja` L38–39. `tests/test_hypothesis.py.jinja` `@given`. `tests/test_respx.py.jinja` `@respx.mock`. `rg -i mypy template/files/python` empty. `mise.toml.jinja` L6–7 `python = "3.11"` / `node = "20"` (not `.mise.toml.jinja`).                                        |
| PAY-P1-gha-release-uv-root                    | **closed in source** | `riso-release.yml.jinja` L46 python-track gate; L60–61 `working-directory: python` + `uv sync`; L64 `uv --directory python run task quality`; else L66–67 echo. Release-job L105–107 same cwd. Dest-stale official changelog workflows only.                                             |
| PAY-P1-gitlab-circle-sys-cwd                  | **closed in source** | GitLab `.rust-base` L225 `cd rust`; `.go-base` L279 `cd go`; build L327–333 `./cli` / `./api` / `go -C mcp … ./cmd/server`. Circle rust/go `working_directory: rust` / `go`. GitLab/Circle pages `mv node/docs/fumadocs/out public/` + `uv --directory python`.                          |
| `go.work` / electron-store / no clang-lld     | **closed**           | `go.work.jinja` `.` + optional `./mcp`. `electron.vite.config.ts.jinja` L8 + L24 exclude `electron-store`. `rg` empty under `template/files/tauri/src-tauri` for clang/lld.                                                                                                              |

## Findings

### PAY-P1-fumadocs-ai-search-static-export — P1 (extra-only residual; not new)

- **Files:** `template/files/node/docs/fumadocs/app/api/chat/route.ts.jinja:1-18`, `template/files/node/docs/fumadocs/components/search/ai-search.tsx.jinja:4` / L54
- **Live:** Extra-on route still emits request-less `GET()` + `dynamic = 'force-static'` + `revalidate = false` (static “unavailable” JSON). No `POST` / `streamText`. Extra-on UI still `useChat()` (POST `/api/chat`). Default + official fumadocs samples keep `fumadocs_ai_search: disabled` (`copier.yml` `_answers_defaults` L99). Package extras `@ai-sdk/openai` / `ai` stay gated (`package.json.jinja` L35–38).
- **Still open:** extra cannot stream live chat under always-on `output: 'export'`. Not a default/official path → **not P0**.
- **Why not new:** same id as W6-R03 / W6-R04; NODE already residualed the extra-only gap (`W6-NODE-chat.md`). Source not newly broken.
- **Fix (NODE, extra-only):** stop wiring `useChat()` (or drop the extra) while export stays on. Do not restore middleware/`rewrites()`. Do not drop `output: 'export'`.

## Not elevated

- Dest-stale Sphinx `linkify` import / docs-sphinx missing-`make` / fumadocs-full robots smoke: residuals when SOURCE is fixed. Do not reopen as P0.
- Official `docs-fumadocs` dest+smoke catching up to the search wrapper: dest restore, not a new finding.
- SaaS `@/db/schema` leftovers: **out of scope**.
- `.docker/Dockerfile.jinja` dest-root `COPY pyproject.toml`: flatten-era; not official smoke.
- GHA rust quality MCP-only (`rust/mcp`): missing job, not a red default smoke.
- COORD Makefile exclude on just-only Sphinx dests: `residuals/PY.md` R1, not a missing PY recipe.
- Fumadocs `llms.mdx` `GET(_req: Request, …)`: unused Request + `generateStaticParams` + `force-static`. Same source as W6-R04; official dests already build this path after the search-wrapper dest refresh. Not newly broken.

## Strengths (do not regress)

- MyST `"linkify"` kept **and** docs extra now pins `linkify-it-py>=2.1.0`.
- Changelog release quality no longer dest-root `uv`.
- GitLab/Circle rust/go cwd matches `rust/` / `go/` Makefiles.
- Fumadocs extra-on chat route is static-export-safe (GET stub). Search `GET()` wrapper + robots/sitemap flags stay in source.
- Hooks leftover-reject shape, Node 20, hypothesis + respx, no mypy under `template/files/python`.

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
p0: []
p1:
  - id: PAY-P1-fumadocs-ai-search-static-export
    files:
      - template/files/node/docs/fumadocs/app/api/chat/route.ts.jinja:1-18
      - template/files/node/docs/fumadocs/components/search/ai-search.tsx.jinja:54
    summary: extra-on AI search still useChat POST under output export; route is static GET stub; not default/official
summary: >
  Second dry pass after W6-R04. No new SOURCE P0/P1.
  PAY-P0-sphinx-myst-linkify-dep stays closed in source
  (pyproject.toml.jinja:54 linkify-it-py>=2.1.0; conf.py.jinja:191
  still enables linkify). Official changelog-python dest + 07:36Z
  smoke remain dest-stale residuals, not a new P0. Official
  docs-fumadocs dest+smoke now match the search GET wrapper
  (08:37Z passed). W6-R03 release.yml dest-root uv and
  GitLab/Circle rust/go cwd P1s stay source-closed. One
  extra-only P1 remains (same id). Empty p0 — refine-stop
  increment on this surface is allowed.
```
