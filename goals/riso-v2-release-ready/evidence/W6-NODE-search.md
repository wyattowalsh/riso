# W6-NODE — Fumadocs `/api/search` static export

- Task: wrap `staticGET` in a request-less `GET()`
- Files: `template/files/node/docs/fumadocs/app/api/search/route.ts.jinja` (orama + orama-cloud)
- Why: dest `docs-fumadocs` smoke failed prerender `/api/search` (`request.url` / `dynamic = "error"`) even with `export const GET = search.staticGET`
- Dest writes: 0
- Live `render_matrix.py` (lanes-assurance W5) was already running; not started or killed
