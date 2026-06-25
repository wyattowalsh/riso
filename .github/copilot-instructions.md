# GitHub Copilot — Riso Maintainer Repo

**SSOT**: [AGENTS.md](../AGENTS.md) at the repository root.

This file is a pointer only. All build, test, lint, boundary, and workflow instructions live in AGENTS.md.

Quick maintainer commands:

- `make quality` — lint + typecheck + test
- `make samples` — render sample projects
- `uv run riso doctor --json` — verify CLI/tooling (after `uv sync --group cli`)

Human docs: [README.md](../README.md)
