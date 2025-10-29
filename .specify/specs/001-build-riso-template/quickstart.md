# Quickstart: Riso Template Foundation

## 1. Install Prerequisites

1. Ensure GitHub CLI (or git), Python 3.11+, Node.js 20 LTS, and pnpm are available on your workstation.
2. Install `uv` once via `pipx install uv` (or download the standalone installer).
3. Install Playwright browsers only when the docs or API modules request them (CI handles caching).

## 2. Render the Baseline Project

```bash
copier copy gh:org/riso-template riso-example
cd riso-example
```

Accept the defaults to keep the project in single-package mode with Python-only tooling.

## 3. Bootstrap the Environment

```bash
uv sync
uv run pytest
uv run ruff check
uv run mypy
uv run pylint src
```

> Tip: `uv run jupyter lab` launches the baseline notebook showcase.

## 4. Explore Optional Modules

Run `copier copy` with `--data` or interactively to enable modules:
- `cli_module=yes` adds a Typer-powered CLI and Vitest smoke tests.
- `api_tracks=python,node` scaffolds FastAPI and Fastify services with shared logic.
- `docs_site=fumadocs` switches the docs prompt to the TypeScript-oriented site.
- `mcp_module=yes` generates FastMCP scaffolding and contract examples.

Each module exposes validation commands inside `scripts/` and corresponding CI jobs.

## 5. Regenerate Samples

Recreate sample outputs to prove Template Sovereignty:

```bash
pnpm dlx copier diff
./scripts/render-samples.sh
```

Commit updated artifacts under `samples/` before opening a pull request.

## 6. Publish Documentation

```bash
uv run sphinx-build docs/shibuya build/docs
pnpm --filter docs-fumadocs build
```

Use GitHub Pages or the provided workflow to deploy docs previews.

## 7. Run Governance Automation Locally

```bash
pnpm lint
pnpm test --filter vitest
uv run pytest
uv run scripts/compliance.py
```

These commands mirror the CI matrix and must pass prior to merge.
