# W2-NODE-T01 — mermaid/docs docusaurus

- Task: `NODE-T01`
- Wave: W2 / lane NODE
- Deps: `W1-OUT` (coord-outbox present)
- Exclusive writes: `template/files/node/docs/docusaurus/**`
- Verify: jinja `node/docs/docusaurus`
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `samples/*/render/**` writes: **0**

## Done

Kept dirty-tree DESIGN + mermaid polish and closed leftover Infima-blue chrome.

| Surface | Result |
| --- | --- |
| `docusaurus.config.ts.jinja` | `theme: { light: 'base', dark: 'base' }`; `startOnLoad: false`; `securityLevel: 'strict'`; `htmlLabels: false`; `deterministicIds: true`; light token bag in `themeConfig` (JSON-clone limit); dark twin exported as `mermaidThemeByColorMode.dark` |
| Tokens | `--ifm-color-primary` teal `#14b8a6`; PWA `theme-color` / status bar `#14b8a6`; announcement bar `#14b8a6`; hero gradient `#0f766e` |
| CSS | mermaid SVG `background: transparent` when mermaid enabled; Tailwind v4 CSS-first (`tailwind.css.jinja`) |
| Docs | mermaid feature bullet on `docs/index.md.jinja`; diagrams already in `features-demo.md.jinja` |
| Workflow | GHA `${{ }}` wrapped in `{% raw %}` |

## Verify

`find template/files/node/docs -name '*.jinja' \| xargs uv run python scripts/ci/validate_jinja_templates.py` → **108** templates all OK (`W2-NODE-jinja.txt`).

`uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json` → **ok:true** (`W2-NODE-validate-docs-docusaurus.json`). Warnings are only Copier `_commit` / `_src_path`.
