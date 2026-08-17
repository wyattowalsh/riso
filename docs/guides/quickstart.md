# Maintainer Quickstart

Follow these steps to work on the template and build confidence before opening a
pull request.

## Prerequisites

Before working on the template, ensure all required tooling is installed:

```bash
# Check what tools are installed (exit 0 if all present)
just setup-check
# or: ./scripts/setup/setup.sh --check-only

# Install missing tools (interactive)
just bootstrap
# or: ./scripts/setup/setup.sh --install
```

`make setup-check` / `make bootstrap` work only as a thin shim to `just` in this
maintainer repo. Rendered projects get a Makefile when `task_runner` is
`makefile` or `both`.

The setup script detects your platform (macOS, Linux distros, Windows/WSL) and
installs: Python 3.11+, uv, Node.js 20 LTS, pnpm, pre-commit, and actionlint.

**Windows users**: Run `.\scripts\setup\setup.ps1 -Install` in PowerShell.

**CI environments**: Use `./scripts/setup/setup.sh --install --yes` with
`GITHUB_TOKEN` set to avoid API rate limits.

1.x Copier answers must be remapped before validate/copy/update. Preview:

```bash
uv run riso migrate --answers-file samples/default/copier-answers.yml --dry-run
```

See {doc}`v2-migration` for the eight-key apply-then-reject table. Generated
Node stays on **20**; `openspec_extra` stays off unless you opt in.

## Render and exercise the baseline

```bash
./scripts/render-samples.sh
cd samples/default/render
uv sync
just quality
```

The render includes Typer CLI, FastAPI/Fastify tracks, and optional MCP tooling
behind prompt flags. Default `task_runner` is `just` (Makefile is excluded).
Use `make quality` only when the sample was rendered with `task_runner=makefile`
or `both`. When no aggregator is present (`task_runner=none`), run
`uv run task quality` to mirror the same toolchain with Taskipy.

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
uv run --group docs sphinx-build -W -b html docs docs/_build/html
```

For projects rendered with `docs_module=enabled` with `docs_framework=sphinx-shibuya`, the CI workflow runs the
same command (`uv run sphinx-build docs dist/docs`).

## Smoke-test optional modules

- **CLI**: `uv run python -m <package>.cli --help`
- **FastAPI**: `uv run uvicorn <package>.api.main:app --reload`
- **Fastify**: `pnpm --filter api-node run dev`
- **MCP**: `uv run python -c "from shared.mcp import tooling; print(tooling.list_tools())"`

## Coverage and confidence

- Maintainer CI uses `--cov-fail-under=70` (`just ci-full`). Enforce
  `--cov-fail-under=90` inside rendered Python packages to match sample
  quality profiles; commits with lower coverage must include offsetting tests
  or a linked issue.
- Ensure integration suites live under `tests/integration/` and are wired into
  CI (no optional skips without issue links). Emit coverage via `coverage run`
  so combined reports include cross-service flows.
- Capture CLI and e2e evidence in `tests/e2e/` and combine coverage artifacts
  before publishing `coverage.xml` to artifacts.
- Use `scripts/ci/run_quality_suite.py --profile strict` to mirror branch
  protections locally across Python 3.11–3.13.

## CI parity

Quality workflows are orchestrated via GitHub Actions, mirroring `just quality`
(and Taskipy) locally. Branch protection relies on matrix jobs across Python
3.11–3.13; keep dependency groups and lockfiles current to maintain parity.
