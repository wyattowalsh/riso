# Agent Scaffolding with Riso CLI

Use the `riso` CLI and the `riso-scaffold` agent skill instead of the removed `riso-mcp` server.

## For AI agents

1. Install the skill from `.agents/skills/riso-scaffold/`
1. Verify environment: `uv run riso doctor --json`
1. Discover variants: `uv run riso variants list --json`
1. Validate answers before copy: `uv run riso validate --answers-file copier-answers.yml --json`
1. Scaffold: `uv run riso copy ./dest --answers-file copier-answers.yml --json`

Agents read `template/` files directly for file content; use CLI for structured introspection and mutations.

## Web wizard

The web wizard at `web/` exports `copier copy` commands and YAML client-side. No MCP server is required for `pnpm run dev`.
