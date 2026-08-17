# Changelog

- **2026-08-17** — Enabled the [`wyattowalsh/agents`](https://github.com/wyattowalsh/agents)
  plugin for Cursor, Claude Code, and GitHub Copilot (`/add-plugin github.com/wyattowalsh/agents`).
  Generated projects with `ai_tools_module=enabled` receive the same project settings.
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
