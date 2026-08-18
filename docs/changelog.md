# Changelog

- **Unreleased 2.0.0** — Dual mise: generated `mise.toml` pins Node **20**;
  maintainer `.mise.toml` pins Node **22**. Maintainer coverage floor is 70%;
  rendered Python packages may still enforce 90%.
- **Unreleased 2.0.0** — **Breaking remaps:** eight 1.x Copier keys
  (`api_tracks`, `api_language`, `docs_site`, `mcp_language`,
  `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`) are
  remapped then leftovers fail closed. Operator (exactly one target):
  `uv run riso migrate DEST [--dry-run] [--json]` or
  `uv run riso migrate --answers-file PATH [--dry-run] [--json]`. Full table:
  {doc}`guides/v2-migration` and root `CHANGELOG.md`.
- **2026-06-24** — **Breaking:** Removed maintainer `riso-mcp` server; replaced with
  agent-native `riso` Typer CLI (`uv run riso --help`) and `riso-scaffold` agent skill.
  See {doc}`guides/mcp-to-cli-migration`.
- **2025-11-04** — Expanded maintainer docs with a coverage-focused testing
  strategy, refreshed quickstart/implementation guidance, and new navigation
  cards for Shibuya authors.
- **2025-11-01** — Introduced the Shibuya Sphinx site with dynamic sys.path
  injection, Mermaid defaults, and autodoc-backed API references.
- **2025-10-30** — Added governance reporting hooks for docs publishing across
  Shibuya, Fumadocs, and Docusaurus.
- **2025-10-15** — Refreshed quality gates for Python 3.11–3.13 and standardized
  `uv run` enforcement in automation scripts.
