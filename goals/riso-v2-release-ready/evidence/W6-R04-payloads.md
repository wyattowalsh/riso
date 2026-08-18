# W6-R04 — Review pass, surface=payloads

- **Task:** `W6-R04` · surface=`payloads`
- **Mode:** read-only inspection of live source
- **Scope:** `template/files/python/**`, `template/files/node/**` except `node/saas/**`, `template/files/go/**`, `template/files/rust/**`, `template/files/electron/**`, `template/files/tauri/**`, `template/hooks/**` (plus W6-R03 GHA / Circle / GitLab / quality justfile follow-ups)
- **Date:** 2026-08-18
- **Repo / cwd:** `/Users/ww/dev/projects/riso`
- **Prior blobs:** `W6-R03-payloads.md` + `W6-PY-linkify.md` treated as maps, not truth. Live files re-verified.
- **Product / hook edits:** **0**
- **`samples/*/render/**` writes:** **0** (dests read as smoke evidence only)
- **Dest-stale smoke:** residual, **not** a new P0, when SOURCE jinja is already fixed.

P0 = source still broken on a default or official/common path (`file:line`). P1 = lockstep / extra / DX. Empty lists only after inspection.

## Contract (re-read live)

- Remap: apply-then-reject. No leftover remapped Copier keys as live jinja identifiers.
- Generated Node floor **20**. OpenSpec extra **off**. SaaS flatten stays reverted (out of this write).
- Generated Python `test` extra includes `hypothesis` + `respx`. mypy is not default.
- Generated `mise.toml` always-on: `python = "3.11"`, `node = "20"`.
- No `riso-mcp` package.

## W6-R03 P0 — PAY-P0-sphinx-myst-linkify-dep

| Field          | Live                                                                                                      |
| -------------- | --------------------------------------------------------------------------------------------------------- |
| Status         | **closed in source**                                                                                      |
| Enable         | `template/files/python/docs/conf.py.jinja:191` still `"linkify"`                                          |
| Extra          | `template/files/python/pyproject.toml.jinja:54` `linkify-it-py>=2.1.0` next to `myst-parser>=3.0.1` (L53) |
| Close evidence | `W6-PY-linkify.md` (source write). Pin matches myst-parser 5.x extra `linkify` (`linkify-it-py~=2.0`).    |

Not re-opened. A fresh Sphinx dest will install `linkify-it-py` with the docs group.

## Dest-stale (residual, not new P0)

- `samples/changelog-python/render/python/pyproject.toml` docs extra still ends at `myst-parser>=3.0.1` (L51); **no** `linkify-it-py`. Smoke `2026-08-18T07:36:46Z` `just linkcheck` still red: `ModuleNotFoundError: Linkify enabled but not installed.` **Source already ships the dep.** Official re-render only.
- `samples/docs-sphinx/render/python/pyproject.toml` L42 same dest-stale extra (no `linkify-it-py`). Older smoke class (`No rule to make target 'linkcheck'`) remains `residuals/PY.md` R1.
- `samples/docs-fumadocs/smoke-results.json` (2026-08-17) still red on `/api/search` `request.url`. **Source** `app/api/search/route.ts.jinja` L15–16 / L29–30 is `export async function GET() { return staticGET(); }`.
- `samples/docs-fumadocs-full` robots/sitemap dest-stale. **Source** `robots.ts.jinja` L4–5 and `sitemap.ts.jinja` L5–6 already `dynamic = 'force-static'` + `revalidate = false`.

## Known source-closed (verified live)

| Check                                         | Verdict              | Live evidence                                                                                                                                                                                                                                |
| --------------------------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leftover remap identifiers                    | **closed**           | No `{% if saas_auth %}` / `api_language` / `docs_site` / `mcp_language` / `api_tracks` / `saas_starter_module` / `include_admin` jinja identifiers. SaaS uses `saas_auth_provider` only (out of this write).                                 |
| Fumadocs static-export flags + search wrapper | **closed**           | `as const` kept. robots/sitemap + named `GET()` wrapper as above.                                                                                                                                                                            |
| GHA matrix / deps + quality justfile          | **closed**           | Quality `justfile.quality.jinja` L2 `_python` / L20–45 gated; `uv --directory`.                                                                                                                                                              |
| hypothesis + respx / no mypy / Node 20        | **closed**           | `pyproject.toml.jinja` L38–39. `mise.toml.jinja` L6–7 `python = "3.11"` / `node = "20"`.                                                                                                                                                     |
| PAY-P1-gha-release-uv-root                    | **closed in source** | `riso-release.yml.jinja` L46 python-track gate; L60–61 `working-directory: python` + `uv sync`; L64 `uv --directory python run task quality`; else L66–67 echo. Release-job L105–107 same cwd. Dest-stale official changelog workflows only. |
| PAY-P1-gitlab-circle-sys-cwd                  | **closed in source** | GitLab `.rust-base` L225 `cd rust`; `.go-base` L279 `cd go`; build L327–333 `./cli` / `./api` / `go -C mcp … ./cmd/server`. Circle rust/go `working_directory: rust` / `go`. No dest-root `./cmd/...`.                                       |

## Findings

### PAY-P1-fumadocs-ai-search-static-export — P1 (extra-only residual)

- **Files:** `template/files/node/docs/fumadocs/app/api/chat/route.ts.jinja:1-18`, `template/files/node/docs/fumadocs/components/search/ai-search.tsx.jinja:4` / L54
- **Live:** Extra-on route no longer emits `POST(req: Request)` / `streamText`. It emits request-less `GET()` + `dynamic = 'force-static'` + `revalidate = false` (static “unavailable” JSON). Default + official fumadocs samples keep `fumadocs_ai_search: disabled`.
- **Still open:** extra-on UI still `useChat()` (POST `/api/chat`). Extra cannot stream live chat under always-on `output: 'export'`. Not a default/official path → **not P0**.
- **Why not new:** same id as W6-R03; NODE narrowed the POST-route hole (`W6-NODE-chat.md`) and residualed the extra-only gap.
- **Fix (NODE, extra-only):** stop wiring `useChat()` (or drop the extra) while export stays on. Do not restore middleware/`rewrites()`. Do not drop `output: 'export'`.

## Not elevated

- Dest-stale Sphinx `linkify` import / fumadocs search/robots smokes: residuals when SOURCE is fixed.
- SaaS `@/db/schema` leftovers: **out of scope**.
- `.docker/Dockerfile.jinja` dest-root `COPY pyproject.toml`: flatten-era; not official smoke.
- GHA rust quality MCP-only (`rust/mcp`): missing job, not a red default smoke.
- COORD Makefile exclude on just-only Sphinx dests: `residuals/PY.md` R1, not a missing PY recipe.

## Strengths (do not regress)

- MyST `"linkify"` kept **and** docs extra now pins `linkify-it-py>=2.1.0`.
- Changelog release quality no longer dest-root `uv`.
- GitLab/Circle rust/go cwd matches `rust/` / `go/` Makefiles.
- Fumadocs extra-on chat route is static-export-safe (GET stub).
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
  PAY-P0-sphinx-myst-linkify-dep is closed in source
  (pyproject.toml.jinja:54 linkify-it-py>=2.1.0; conf.py.jinja:191
  still enables linkify). Official changelog-python / docs-sphinx dests
  and their smokes remain dest-stale residuals, not a new P0. W6-R03
  release.yml dest-root uv and GitLab/Circle rust/go cwd P1s are
  source-closed. One extra-only P1 remains (same id). Empty p0 —
  refine-stop increment on this surface is allowed.
```
