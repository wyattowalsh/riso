# W2 SAAS-T01 — `runtime/nextjs` present

- Task: `SAAS-T01`
- Wave: W2 / lane SAAS
- Deps: W1-OUT
- Exclusive write roots: `template/files/node/saas/**`, `template/files/saas-starter/**`
- Verify: path exists
- Status: **green**
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `samples/*/render/**` writes: **0**

## Command

```text
test -d template/files/node/saas/runtime/nextjs && echo T01_OK
ls template/files/node/saas/runtime/nextjs
```

## Result

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** |
| `app/` (home, layout, globals, marketing, admin, api) | yes |
| `docs/`, `lib/`, `tests/` | yes |
| `middleware.ts.jinja` | yes |
| `next.config.js.jinja` | yes |
| `postcss.config.mjs.jinja` | yes |

Runtime files stay under `runtime/nextjs/**` (gated `saas_runtime == "nextjs-16"`). Not flattened to the `node/saas` package root.

W2-T04 token/a11y polish on this tree: `app/globals.css.jinja`, `app/layout.tsx.jinja`, `app/page.tsx.jinja`, `app/(marketing)/comparison/page.tsx.jinja`.
