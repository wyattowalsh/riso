# Quickstart: Release Candidate Validation

Run from the repository root.

Restore the locked maintainer and separate web environments first:

```bash
uv sync --locked --group dev --group docs --group cli
pnpm --dir web install --frozen-lockfile
```

## 1. Confirm State

```bash
git status --short --branch
uv run python scripts/ci/validate_release_readiness_skill.py
```

## 2. Validate Docs And Spec Artifacts

```bash
uv run --group docs sphinx-build -W -b html docs /tmp/riso-docs-build-release
uv run python - <<'PY'
from pathlib import Path
import json
for path in Path("specs/016-prod-release-readiness/contracts").glob("*.json"):
    json.loads(path.read_text())
    print(path)
PY
```

## 3. Validate Template And Python Surfaces

```bash
uv run pytest tests/unit/hooks/test_post_gen_project.py -q --override-ini='addopts='
uv run pytest tests/integration/test_template_rendering.py -q --override-ini='addopts='
uv run pytest tests/unit/ci/test_render_matrix.py -q --override-ini='addopts='
uv run pytest tests/unit/test_cli/ -q --override-ini='addopts='
uv run ruff check scripts template/hooks tests src
uv run ruff format --check scripts template/hooks tests src
uv run ty check --extra-search-path scripts --extra-search-path template scripts template/hooks src
```

## 4. Validate Samples And Web

```bash
uv run python scripts/ci/render_matrix.py
pnpm --dir web run lint
pnpm --dir web run test:run
pnpm --dir web run build
pnpm --dir web run test:e2e
```

The integrated web build runs strict Sphinx first and includes `dist/docs`.
Python 3.11+ and `uv` must therefore be available in the web deployment builder,
including a Vercel build environment. Generated sample bootstrap installs sample
dependencies; its mise trust is scoped to the render process, with automatic
toolchain installation disabled. Install missing toolchain prerequisites
explicitly before retrying.

## 5. Validate Package And Release Dry Run

```bash
uv build --no-sources
uv run --with twine twine check dist/*
pnpm install --frozen-lockfile
pnpm run release:dry
```

Semantic-release rebuilds and checks final assets during `prepare`, after applying
the selected version. Push workflows rehearse; real release requires an explicit
workflow dispatch with `dry_run=false`. Local dry-run still requires appropriate
repository access and must not be treated as permission to publish.

Record all final pass/fail evidence in `tmp/riso-prod-ready-release-todo.md`.
