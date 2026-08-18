# W6-NODE-chat — Fumadocs `/api/chat` vs static export

- **Wave:** W6 / NODE
- **Task:** `PAY-P1-fumadocs-ai-search-static-export`
- **Date (UTC):** 2026-08-18T08:13:50Z
- **Repo:** `/Users/ww/dev/projects/riso`
- **Branch:** `main`
- **HEAD:** `f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87` (worktree dirty; this session did not commit)
- **Exclusive writes:** `template/files/node/docs/fumadocs/**`; this file
- **`samples/*/render/**` writes:** 0
- **Lockfile / secrets / tag / push:** 0
- **`render_matrix.py` started or killed:** 0
- **Status:** extra-only P1 residualed; default dest not broken

## Decision (copier default)

`fumadocs_ai_search` default is **off**. Live chat is extra-only, not a default/official P0.

| Surface                                             | Live value                                                                 |
| --------------------------------------------------- | -------------------------------------------------------------------------- |
| `template/copier.yml` `_answers_defaults` L99       | `fumadocs_ai_search: "disabled"`                                           |
| `template/copier.yml` prompt L586–595               | `default: disabled`; `when` also requires `fumadocs_llms_txt == 'enabled'` |
| `samples/docs-fumadocs/copier-answers.yml` L28      | `disabled`                                                                 |
| `samples/docs-fumadocs-full/copier-answers.yml` L42 | `disabled`                                                                 |
| Wizard `web/src/lib/store.ts`                       | `fromMatrix("fumadocs_ai_search", "disabled")`                             |

`next.config.ts.jinja` L13 is always `output: 'export' as const`. There is no export toggle. A request-body POST cannot prerender.

Algorithm from the lock: default off → residual as extra-only P1 and do not break default dest. Keep the extra. Do not ship a dynamic POST next to static export. Do not restore middleware or `rewrites()`.

## Changes

1. `app/api/chat/route.ts.jinja` — still gated on `docs_module` + `docs_framework == 'fumadocs'` + `fumadocs_ai_search == 'enabled'`. Extra-off render is empty (`post_gen` deletes the stub). Extra-on render no longer emits `POST(req: Request)` / `streamText` / `maxDuration`. It emits a request-less `GET()` with `dynamic = 'force-static'` and `revalidate = false` that returns JSON saying chat is unavailable on the exported site.
1. `README.md.jinja` — extra-on only: document the extra as **dynamic-only**; `/api/chat` is the static GET; live chat would need a server runtime.

Default dest answers (`fumadocs_ai_search: disabled`) still render no chat route and no AI Search README section.

## Residual — extra-only P1

| Field              | Value                                                                                                                                                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **id**             | PAY-P1-fumadocs-ai-search-static-export                                                                                                                                                                                 |
| **status**         | residual (extra-only)                                                                                                                                                                                                   |
| **why not closed** | Extra-on dests still cannot stream live chat under `output: 'export'`. `components/search/ai-search.tsx.jinja` still uses `useChat()` (POST `/api/chat`). Package extras `@ai-sdk/openai` / `ai` stay (keep the extra). |
| **default dest**   | unchanged. Extra off on default + official fumadocs samples.                                                                                                                                                            |
| **not this lock**  | `copier.yml` prompt help still says "Scaffolds chat interface with Vercel AI SDK" (COORD). Official dest re-render (PLATFORM). Do not drop `output: 'export'` or restore middleware/`rewrites()`.                       |

## Verify

```text
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/docs/fumadocs/app/api/chat/route.ts.jinja \
  template/files/node/docs/fumadocs/README.md.jinja
# Validated 2 Jinja template(s): all OK

# ephemeral jinja render (FileSystemLoader + StrictUndefined)
# extra off: chat route empty; README has no "### AI Search"
# extra on: GET() + force-static + revalidate false;
#           no export async function POST; no streamText; no Request
# extra on README: "dynamic-only" + output: 'export'
```

## Path lock

| Class                          | Count                                                |
| ------------------------------ | ---------------------------------------------------- |
| Product writes                 | 2 — `app/api/chat/route.ts.jinja`, `README.md.jinja` |
| Evidence                       | this file                                            |
| `residuals/**`                 | 0 (not this exclusive write)                         |
| `copier.yml` / hooks / prompts | 0 (COORD)                                            |
| `samples/*/render/**`          | 0                                                    |
| `tests/**`                     | 0                                                    |

## Not this lane

- Flipping `fumadocs_ai_search` default or prompt `when` — COORD
- Official re-render of `docs-fumadocs` / `docs-fumadocs-full` — PLATFORM
- Making Ask-AI stream on a server runtime (would require dropping `output: 'export'`) — do not
