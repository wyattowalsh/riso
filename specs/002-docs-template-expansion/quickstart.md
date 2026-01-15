# Quickstart: Expanded Documentation Template Options

## Prerequisites

- Install `uv` ≥0.4 (`curl -LsSf https://astral.sh/uv/install.sh | sh`) to manage Python 3.11 environments automatically.citeturn5search2
- Install `mise` ≥2024.9 and ensure `auto_install = true` to provision Node.js 20 LTS and pnpm ≥8 from `.mise.toml`.citeturn1search3turn1search6
- (Optional) Install GitHub CLI for downloading documentation artifacts published by CI.citeturn2view0

## Render Steps

1. Run `copier copy path/to/riso-template ./my-service` and answer the prompts.
1. Select `docs_site`:
   - `fumadocs` (default)
   - `sphinx-shibuya`
   - `docusaurus`
   - `none`
1. During `copier` execution, hooks will:
   - Use mise to install Node.js and pnpm declared in `.mise.toml` if absent.citeturn1search3turn1search6
   - Use `uv python install 3.11` and `uv sync` to hydrate the docs environment deterministically.citeturn5search2turn5search3
   - Abort with remediation commands if provisioning fails after one auto-install attempt.

## Variant Commands

- **Fumadocs (Next.js 15 / Tailwind 4)**

  ```bash
  pnpm --filter docs-fumadocs dev
  pnpm --filter docs-fumadocs build
  pnpm --filter docs-fumadocs lint
  ```

  Tailwind 4-compatible config and MDX islands follow the v15 guide.citeturn1search0turn1search1

- **Sphinx Shibuya**

  ```bash
  uv run make docs
  uv run make linkcheck
  ```

  Shibuya ships responsive layout, built-in dark mode, and curated extension defaults.citeturn3search0turn3search7

- **Docusaurus 3.9 + DocSearch v4**

  ```bash
  pnpm --filter docs-docusaurus dev
  pnpm --filter docs-docusaurus build
  pnpm --filter docs-docusaurus lint
  ```

  DocSearch v4 (AskAI) is configured via the new Docusaurus 3 release guide.citeturn4search2turn4search1

- **None**
  `docs_site=none` removes documentation scripts from quickstart and CI. Follow README guidance to re-enable a variant later.

## CI Validation

- Run `scripts/render-samples.sh --variant docs-${CHOICE}` to regenerate evidence locally.
- GitHub Actions matrix jobs (one per docs variant) will:
  1. Use mise/uv steps to ensure tooling versions.citeturn1search3turn5search2
  1. Execute the commands above.
  1. Upload the built static site as an artifact via `actions/upload-artifact@v4` (90-day retention by default).citeturn2view0turn0search2

## Troubleshooting

- Run `mise doctor` if Node/pnpm provisioning fails; inspect `.riso/toolchain.log` for captured stderr.citeturn1search3
- For Python environment issues, clear `.uv/` and rerun `uv sync`.citeturn5search3
- Re-run `scripts/render-samples.sh` after changing `docs_site` to refresh smoke evidence and README instructions.
