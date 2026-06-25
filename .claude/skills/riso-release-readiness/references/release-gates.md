# Release Gates

## Blocking Gates

- `uv run python scripts/ci/validate_release_readiness_skill.py`
- `uv run --group docs sphinx-build -W -b html docs /tmp/riso-docs-build-release`
- `uv run pytest tests/unit/hooks/test_post_gen_project.py -q --override-ini='addopts='`
- `uv run pytest tests/integration/test_template_rendering.py -q --override-ini='addopts='`
- `uv run pytest tests/unit/ci/test_render_matrix.py -q --override-ini='addopts='`
- `uv run pytest tests/unit/test_mcp tests/integration/test_mcp_server.py -q --override-ini='addopts='`
- `uv run ruff check scripts template/hooks tests src`
- `uv run ruff format --check scripts template/hooks tests src`
- `uv run python scripts/ci/render_matrix.py`
- `pnpm --dir web run lint`
- `pnpm --dir web run test:run`
- `pnpm --dir web run build`
- `uv build --no-sources`
- `uv run --with twine twine check dist/*`

## Evidence Rules

- Capture exact command, exit status, and concise output.
- Preserve request IDs, run IDs, SHAs, and artifact names when available.
- Mark a gate blocked only when an external approval or external service is the
  next required action.
- Do not downgrade a release-critical failure to advisory.
