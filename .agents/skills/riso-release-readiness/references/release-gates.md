# Release Gates

## Blocking Gates

- `uv run python scripts/ci/validate_release_readiness_skill.py`
- `uv run python scripts/ci/check_removed_key_ssot.py`
- `uv run python scripts/ci/validate_jinja_templates.py template/files`
- `uv run python scripts/ci/validate_workflows.py`
- `uv run python scripts/ci/validate_release_configs.py`
- `uv run --group docs sphinx-build -W -b html docs /tmp/riso-docs-build-release`
- `uv run pytest tests/unit/hooks/test_post_gen_project.py -q --override-ini='addopts='`
- `uv run pytest tests/integration/test_template_rendering.py -q --override-ini='addopts='`
- `uv run pytest tests/unit/ci/test_render_matrix.py -q --override-ini='addopts='`
- `uv run pytest tests/unit/test_cli/ -q --override-ini='addopts='`
- `uv run ruff check scripts template/hooks tests src`
- `uv run ruff format --check scripts template/hooks tests src`
- `uv run python scripts/ci/render_matrix.py`
- `pnpm --dir web run lint`
- `pnpm --dir web run test:run`
- `pnpm --dir web run build`
- `uv build --no-sources`
- `uv run --with twine twine check dist/*`
- Official 37-sample validate: `uv run riso validate --answers-file samples/<v>/copier-answers.yml --json`
- Leftover-key scan is part of `check_removed_key_ssot.py` (sample answers must have zero `REMOVED_ANSWER_KEYS`)

## Evidence Rules

- Capture exact command, exit status, and concise output.
- Preserve request IDs, run IDs, SHAs, and artifact names when available.
- Mark a gate blocked only when an external approval or external service is the
  next required action.
- Do not downgrade a release-critical failure to advisory.
