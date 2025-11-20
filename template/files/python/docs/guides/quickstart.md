# Maintainer Quickstart

Follow these steps to work on the template render and build confidence before
opening a pull request.

## Render and exercise the baseline

```bash
uv sync
make quality
```

The render includes Typer CLI, FastAPI/Fastify tracks, and optional MCP tooling
behind prompt flags. When `make` is unavailable, run `uv run task quality` to
mirror the same toolchain with Taskipy.

Run explicit coverage gates before opening a PR:

```bash
uv run pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=90
uv run coverage run -m pytest tests/integration
uv run coverage run -m pytest tests/e2e
uv run coverage combine
uv run coverage xml
```

## Refresh documentation builds

Use the Shibuya Sphinx site to validate documentation changes before shipping
new defaults to downstream renders.

```bash
uv sync --group docs
uv run sphinx-build docs docs/_build
```

For projects rendered with `docs_site=sphinx-shibuya`, the CI workflow runs the
same command (`uv run sphinx-build docs dist/docs`).

## Smoke-test optional modules

- **CLI**: `uv run python -m {{ package_name }}.cli --help`
- **FastAPI**: `uv run uvicorn {{ package_name }}.api.main:app --reload`
- **Fastify**: `pnpm --filter api-node run dev`
- **MCP**: `uv run python -c "from shared.mcp import tooling; print(tooling.list_tools())"`

## Coverage and confidence

- Enforce `--cov-fail-under=90` locally to match CI; commits with lower
  coverage must include offsetting tests or a linked issue.
- Ensure integration suites live under `tests/integration/` and are wired into
  CI (no optional skips without issue links). Emit coverage via `coverage run`
  so combined reports include cross-service flows.
- Capture CLI and e2e evidence in `tests/e2e/` and combine coverage artifacts
  before publishing `coverage.xml` to artifacts.
- Use `scripts/ci/run_quality_suite.py --profile strict` to mirror branch
  protections locally across Python 3.11–3.13.

## CI parity

Quality workflows are orchestrated via GitHub Actions, mirroring the `make
quality` and Taskipy lanes locally. Branch protection relies on matrix jobs
across Python 3.11–3.13; keep dependency groups and lockfiles current to
maintain parity.
