# W2-NODE-T02 — mermaid/docs fumadocs

- Task: `NODE-T02`
- Wave: W2 / lane NODE
- Deps: `W1-OUT`
- Exclusive writes: `template/files/node/docs/fumadocs/**`
- Verify: jinja `node/docs/fumadocs`
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `samples/*/render/**` writes: **0**

## Done

| Surface | Result |
| --- | --- |
| `components/mermaid/theme.ts.jinja` | New (untracked → keep). `securityLevel: 'strict'`; `startOnLoad: false`; `theme: 'base'`; light/dark DESIGN token bags; `prefersDark()` + `mermaidOptions(dark)` |
| `components/mermaid/index.tsx.jinja` | No `securityLevel: 'loose'`; no `Math.random` / `useId` ids (`mermaid-1`…); no `bindFunctions`; `role="alert"` / `role="status"`; dark-mode observer |
| `mdx-components.tsx.jinja` | Mermaid `pre` interceptor joins array children |
| `content/docs/index.mdx.jinja` | Gated mermaid flowchart / sequence / ER examples (`docs-fumadocs-full` has mermaid on) |
| Tokens | shadcn `--primary` / custom `--fd-primary` teal (`173 80%`); logos `#14b8a6` |
| `next.config.ts.jinja` | `output: 'export'` + unoptimized images for Pages `./out`; **removed `rewrites()`** (invalid with static export). LLM markdown stays at `/llms.mdx/docs/...` |
| Search / deploy | `fumadocs_search_provider` (not removed `fumadocs_search`); pnpm + Node 20 |

## Verify

Jinja node/docs: **108 OK**.

`uv run riso validate --answers-file samples/docs-fumadocs/copier-answers.yml --json` → **ok:true**.

`uv run riso validate --answers-file samples/docs-fumadocs-full/copier-answers.yml --json` → **ok:true**.
