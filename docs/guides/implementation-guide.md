# Implementation Guide

Use this checklist when rolling out new modules or refreshing existing ones.

## Planning

- Confirm prompts in `template/prompts/options.yml.jinja` reflect new choices.
- Update `template/files/shared/module_catalog.json.jinja` with the feature,
  including compatibility rules and dependency groups.
- Capture acceptance criteria in `specs/` so rendered projects inherit the same
  governance signals.

## Development

- Prefer `uv run` for Python commands to guarantee isolated environments.
- Keep quality groups (`test`, `quality`, `cli`, `api_python`, `mcp`) lean and
  reproducible across Python versions 3.11–3.13.
- When adding docs assets, mirror changes in both the root Sphinx site and the
  `docs_site=sphinx-shibuya` template payload.
- Keep `.github/context/` synchronized with `template/files/shared/.github/context/`
  by running `uv run python scripts/ci/verify_context_sync.py` before commits.
- Extend tests alongside features: target ≥90% unit coverage, add deterministic
  integration tests for new services, and document any exclusions inline.

## Validation

- Run `make quality` (or `uv run task quality`) inside rendered samples.
- For Sphinx changes, execute `uv run sphinx-build docs docs/_build`.
- For Node surfaces, run `pnpm --filter docs-fumadocs build` where applicable.
- Use `uv run python scripts/ci/run_quality_suite.py --profile standard` to
  validate parity between `make quality` and Taskipy flows, and `--profile strict`
  to ensure coverage stays above the floor.

## Delivery

- Regenerate sample renders with `scripts/render-samples.sh` to keep fixtures and
  metadata current.
- Commit updated lockfiles and docs assets so CI can reuse caches.
- Refresh `AGENTS.md` with any new operational expectations or docs entry points.
