# Maintainer Quickstart

Work on the Copier template in this checkout. Generated apps live under
`samples/*/render/` (regenerate only).

## Setup

```bash
git clone https://github.com/wyattowalsh/riso.git && cd riso
just setup
just setup-check
uv run pytest tests/ -x -q
uv run riso doctor --json
```

`make setup-check` / `make setup` only shim to `just` in this maintainer repo.
Rendered projects get a Makefile when `task_runner` is `makefile` or `both`.

Windows: `.\scripts\setup\setup.ps1 -Install`. Bootstrap details:
[scripts/setup/README.md](https://github.com/wyattowalsh/riso/blob/main/scripts/setup/README.md).

1.x Copier answers must be remapped before validate/copy/update. Preview with
**exactly one** target:

```bash
uv run riso migrate ./existing-project --dry-run
uv run riso migrate --answers-file samples/default/copier-answers.yml --dry-run
```

See {doc}`v2-migration` for the eight-key apply-then-reject table.

## Render and exercise a sample

```bash
./scripts/render-samples.sh --variant api-python \
  --answers samples/api-python/copier-answers.yml
cd samples/api-python/render/python
uv sync --group quality --group test --group api_python --group api_python_test
just quality
```

The default sample exercises documentation. The Python API sample above has a
Python package under `render/python/`; Node workspaces run from `render/`.

Use `make quality` only when that sample was rendered with `task_runner=makefile`
or `both`. When `task_runner=none`, run `uv run task quality`.

Rendered Python packages declare their floor in `coverage.cfg`: currently 90%
when the Python CLI is enabled and 85% otherwise. Individual CI jobs may require
90% explicitly. Maintainer CI is 70% (`just ci-full`).

```bash
# Inside a rendered Python package, using its configured floor
uv run pytest --cov --cov-config=coverage.cfg --cov-report=term-missing --cov-report=xml
```

## Maintainer smoke (this repo)

```bash
uv run riso doctor --json
uv run riso validate --answers-file samples/default/copier-answers.yml --json
uv run riso catalog dependencies --json
uv run pytest tests/ -x -q
just quality
```

## Refresh documentation builds

```bash
uv sync --group docs
just docs-build
# equivalent: uv run --group docs sphinx-build -W -b html docs docs/_build/html
```

Do not regenerate `web/public/docs` HTML by hand.

## Smoke-test optional modules (rendered project)

After a render with the matching modules enabled:

- **CLI**: `uv run python -m <package>.cli --help`
- **FastAPI**: `uv run uvicorn <package>.api.main:app --reload`
- **Fastify**: `pnpm --filter api-node run dev`
- **Python MCP**: from `render/python/`, run
  `uv run --group mcp python -m <package>.mcp --help`. Choose a package name
  other than `mcp`, which belongs to the SDK.
- **TypeScript MCP**: from the rendered workspace root, run
  `pnpm --filter ./node/mcp --fail-if-no-match run test`. Follow the generated
  MCP README for the selected language and transport.

## Coverage and confidence

- Maintainer CI uses `--cov-fail-under=70` (`just ci-full`). Check each rendered
  package's `coverage.cfg` and CI arguments for its applicable threshold.
- Integration suites live under `tests/integration/` and are wired into CI.
- CLI and e2e evidence live under `tests/e2e/`.
- `uv run python scripts/ci/run_quality_suite.py --profile strict` mirrors
  branch protection locally across Python 3.11–3.13.

## CI parity

Quality workflows are orchestrated via GitHub Actions, mirroring `just quality`
locally. Branch protection relies on matrix jobs across Python 3.11–3.13.
