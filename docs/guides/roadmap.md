# Roadmap Snapshot

This snapshot tracks work already shipped in `specs/001`–`015` (see the
Completed Features list in the repository `README.md`) and what is still
planned. Spec numbers match `specs/<nnn>-*` directories. Do not reuse those
numbers for unshipped ideas.

## Shipped

| Spec | Feature | Notes |
| ---- | ------- | ----- |
| 001 | Template foundation | Copier payload, optional modules, maintainer CLI |
| 002 | Documentation templates | Fumadocs, Sphinx Shibuya, Docusaurus |
| 003 | Code quality | Ruff, ty, Pylint, pytest (not mypy) |
| 004 | GitHub Actions workflows | `riso-quality` / `riso-matrix` |
| 005 | Containers & deployment | Docker/Compose patterns |
| 006 | FastAPI scaffold | Python API track |
| 007 | GraphQL scaffold | Strawberry |
| 008 | WebSocket scaffold | Real-time Python track |
| 009 | Typer CLI scaffold | Optional CLI module |
| 010 | API versioning | Version strategy |
| 011 | API rate limiting | Throttle helpers |
| 012 | SaaS starter | Optional SaaS infrastructure |
| 013 | MCP servers | Python, TypeScript, Rust, Go tracks |
| 014 | Changelog & release | Semantic-release / commitlint |
| 015 | Codegen scaffolding | Template-based generators |

## Active

| Spec | Feature | Status |
| ---- | ------- | ------ |
| 016 | Production release readiness | In `specs/016-prod-release-readiness/` — RC gates, no publish/tag |

## Later (exploratory)

Unnumbered ideas live in `specs/ideas.md`. Treat that file as a backlog, not a
second spec series. Themes still open:

- Standalone database / persistence module beyond SaaS extras
- Deeper auth, observability, and background-job packs
- Multi-tenancy, i18n, and search as first-class template modules
- Compliance, backup, and FinOps kits

Default generated-project commands stay **just-first** (`just quality`,
`just typecheck`). `make` is only for `task_runner=makefile|both`. Type
checking is **ty**, not mypy. Visual tokens for generated apps live in
`DESIGN.md` when that file is present.
