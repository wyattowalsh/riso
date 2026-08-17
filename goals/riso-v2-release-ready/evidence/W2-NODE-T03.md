# W2-NODE-T03 — leftover `tailwind.config.ts` stays deleted

- Task: `NODE-T03`
- Wave: W2 / lane NODE
- Deps: `W1-OUT`
- Exclusive writes: none (absence is the contract)
- Verify: file stays deleted
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `samples/*/render/**` writes: **0**

## Check

| Path | Result |
| --- | --- |
| `template/files/node/docs/docusaurus/tailwind.config.ts.jinja` | **absent** (`git status` `D`) |
| `template/files/node/docs/docusaurus/tailwind.config.ts` | **absent** |
| `rg tailwind.config template/files/node/docs` | **empty** |

Tailwind v4 is CSS-first: `src/css/tailwind.css.jinja` + `@tailwindcss/postcss` plugin in `docusaurus.config.ts.jinja`. No restore.

Not restored. No residual.
