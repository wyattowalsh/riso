# W2 SAAS-T02 — `runtime/remix` present

- Task: `SAAS-T02`
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
test -d template/files/node/saas/runtime/remix && echo T02_OK
find template/files/node/saas/runtime/remix -type f | sort
```

## Result

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/remix` | **yes** |
| `app/root.tsx.jinja` | yes |
| `app/routes/comparison.tsx.jinja` | yes |
| `remix.config.js.jinja` | yes |
| `app/styles/globals.css.jinja` | yes (T04 token SSOT; Remix-only) |
| `postcss.config.mjs.jinja` | yes (T04; shadcn + remix-2 only) |

Runtime files stay under `runtime/remix/**` (gated `saas_runtime == "remix-2"`). Not mixed with Next at the `node/saas` app root.
