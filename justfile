# Riso maintainer task runner (SSOT). Rendered projects use template justfile/Makefile tracks.
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list

alias h := help
help:
    @printf '\n\033[1m\033[34mRiso maintainer commands\033[0m\n\n'
    @just --list
    @printf '\n\033[2mUsage:\033[0m just <recipe>  ·  just --help <recipe>\n\n'

# ── Setup & installation ──────────────────────────────────────────────────────

[group("setup")]
install:
    @printf '\033[34m▸ Installing dependencies...\033[0m\n'
    uv sync --group dev --group docs
    @printf '\033[32m✓ Dependencies installed\033[0m\n'

[group("setup")]
install-dev:
    @printf '\033[34m▸ Installing dev dependencies...\033[0m\n'
    uv sync --group dev
    @printf '\033[32m✓ Dev dependencies installed\033[0m\n'

[group("setup")]
install-docs:
    @printf '\033[34m▸ Installing docs dependencies...\033[0m\n'
    uv sync --group docs
    @printf '\033[32m✓ Docs dependencies installed\033[0m\n'

[group("setup")]
setup: install
    @printf '\033[34m▸ Setting up pre-commit hooks...\033[0m\n'
    uv run pre-commit install --install-hooks
    uv run pre-commit install --hook-type commit-msg
    uv run pre-commit install --hook-type pre-push
    @printf '\033[32m✓ Setup complete\033[0m\n'

[group("setup")]
setup-check:
    @printf '\033[34m▸ Checking required tooling...\033[0m\n'
    ./scripts/setup/setup.sh --check-only

[group("setup")]
bootstrap:
    @printf '\033[34m▸ Bootstrapping development tools...\033[0m\n'
    ./scripts/setup/setup.sh --install

[group("setup")]
hooks:
    @printf '\033[34m▸ Running pre-commit hooks...\033[0m\n'
    uv run pre-commit run --all-files
    @printf '\033[32m✓ Hooks passed\033[0m\n'

[group("setup")]
hooks-update:
    @printf '\033[34m▸ Updating pre-commit hooks...\033[0m\n'
    uv run pre-commit autoupdate
    @printf '\033[32m✓ Hooks updated\033[0m\n'

# ── Documentation ─────────────────────────────────────────────────────────────

docs_port := "3141"

[group("docs")]
docs: install-docs
    @printf '\033[34m▸ Starting docs server on http://localhost:{{ docs_port }}\033[0m\n'
    uv run sphinx-autobuild docs docs/_build \
        --port {{ docs_port }} \
        --open-browser \
        --watch docs \
        --ignore "*.pyc" \
        --ignore "__pycache__"

[group("docs")]
docs-build: install-docs
    @printf '\033[34m▸ Building documentation...\033[0m\n'
    uv run sphinx-build -b html docs docs/_build
    @printf '\033[32m✓ Docs built at docs/_build/index.html\033[0m\n'

[group("docs")]
docs-clean:
    @printf '\033[34m▸ Cleaning docs build...\033[0m\n'
    rm -rf docs/_build
    @printf '\033[32m✓ Docs cleaned\033[0m\n'

[group("docs")]
docs-linkcheck: install-docs
    @printf '\033[34m▸ Checking documentation links...\033[0m\n'
    uv run sphinx-build -b linkcheck docs docs/_build/linkcheck
    @printf '\033[32m✓ Link check complete\033[0m\n'

# ── Code quality ──────────────────────────────────────────────────────────────

[group("quality")]
quality: lint typecheck test
    @printf '\033[32m✓ All quality checks passed\033[0m\n'

[group("quality")]
lint:
    @printf '\033[34m▸ Running ruff...\033[0m\n'
    uv run ruff check scripts template/hooks src tests
    uv run ruff format --check scripts template/hooks src tests
    @printf '\033[32m✓ Lint passed\033[0m\n'

[group("quality")]
lint-fix:
    @printf '\033[34m▸ Fixing lint issues...\033[0m\n'
    uv run ruff check --fix scripts template/hooks src tests
    uv run ruff format scripts template/hooks src tests
    @printf '\033[32m✓ Lint fixes applied\033[0m\n'

[group("quality")]
typecheck:
    @printf '\033[34m▸ Running ty...\033[0m\n'
    uv run ty check --extra-search-path scripts --extra-search-path template scripts template/hooks src
    @printf '\033[32m✓ Type check passed\033[0m\n'

[group("quality")]
test:
    @printf '\033[34m▸ Running tests...\033[0m\n'
    uv run pytest tests -v
    @printf '\033[32m✓ Tests passed\033[0m\n'

[group("quality")]
test-cov:
    @printf '\033[34m▸ Running tests with coverage...\033[0m\n'
    uv run pytest tests -v --cov=scripts --cov=template/hooks --cov-report=term-missing --cov-report=html
    @printf '\033[32m✓ Coverage report at htmlcov/index.html\033[0m\n'

[group("quality")]
security:
    @printf '\033[34m▸ Scanning for vulnerabilities...\033[0m\n'
    uv run pip-audit --strict --vulnerability-service osv
    @printf '\033[32m✓ Security scan complete\033[0m\n'

# ── Template generation ───────────────────────────────────────────────────────

[group("template")]
tui dest="./riso-demo" answers="":
    #!/usr/bin/env bash
    set -euo pipefail
    printf '\033[34m▸ Launching Riso TUI...\033[0m\n'
    args=(--dest "$1")
    if [[ -n "${2:-}" ]]; then args+=(--answers "$2"); fi
    uv run riso tui "${args[@]}"

[group("template")]
generate dest="./riso-demo" answers="":
    #!/usr/bin/env bash
    set -euo pipefail
    printf '\033[34m▸ Generating project at %s...\033[0m\n' "$1"
    if [[ -n "${2:-}" ]]; then
      uv run copier copy . "$1" --answers-file "$2"
    else
      uv run copier copy . "$1"
    fi
    printf '\033[32m✓ Project generated at %s\033[0m\n' "$1"

[group("template")]
generate-default dest="./riso-demo":
    @printf '\033[34m▸ Generating default project...\033[0m\n'
    uv run copier copy . {{ dest }} --defaults --force
    @printf '\033[32m✓ Default project at {{ dest }}\033[0m\n'

[group("template")]
samples:
    @printf '\033[34m▸ Rendering sample projects...\033[0m\n'
    ./scripts/render-samples.sh
    @printf '\033[32m✓ Samples rendered\033[0m\n'

# ── Maintenance ───────────────────────────────────────────────────────────────

[group("maintenance")]
clean: docs-clean
    @printf '\033[34m▸ Cleaning build artifacts...\033[0m\n'
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @printf '\033[32m✓ Clean complete\033[0m\n'

[group("maintenance")]
clean-all: clean
    @printf '\033[34m▸ Deep cleaning...\033[0m\n'
    rm -rf samples/*/render
    rm -rf /tmp/riso-*
    @printf '\033[32m✓ Deep clean complete\033[0m\n'

[group("maintenance")]
update:
    @printf '\033[34m▸ Updating dependencies...\033[0m\n'
    uv lock --upgrade
    uv sync --group dev --group docs
    uv run pre-commit autoupdate
    @printf '\033[32m✓ Dependencies updated\033[0m\n'

[group("maintenance")]
lock:
    @printf '\033[34m▸ Regenerating lockfile...\033[0m\n'
    uv lock
    @printf '\033[32m✓ Lockfile updated\033[0m\n'

# ── CI helpers ────────────────────────────────────────────────────────────────

[group("ci")]
validate-agents:
    @printf '\033[34m▸ Validating AGENTS ecosystem...\033[0m\n'
    uv run python scripts/ci/validate_agents_ecosystem.py
    uv run python scripts/ci/check_quality_parity.py
    uv run python scripts/ci/validate_agents_ecosystem.py \
        --render-enabled samples/default/render \
        --render-enabled samples/cli-docs/render \
        --render-enabled samples/full-stack/render \
        --render-disabled samples/ai-tools-off/render
    uv run python scripts/ci/agent_smoke_agents_md.py samples/default/render
    uv run python scripts/ci/agent_smoke_agents_md.py samples/cli-docs/render
    uv run python scripts/ci/agent_smoke_agents_md.py samples/full-stack/render
    uv run python scripts/ci/agent_smoke_agents_md.py samples/ai-tools-off/render
    @printf '\033[32m✓ AGENTS ecosystem validation passed\033[0m\n'

[group("ci")]
ci: install quality
    @printf '\033[32m✓ CI checks passed\033[0m\n'

[group("ci")]
ci-full: install
    @printf '\033[34m▸ Running full CI quality suite...\033[0m\n'
    uv run python scripts/ci/run_quality_suite.py --profile standard --log-dir quality-standard
    uv run pytest tests/ \
        --cov=scripts \
        --cov=template/hooks \
        --cov-report=term-missing \
        --cov-fail-under=70 \
        -v
    @printf '\033[32m✓ Full CI checks passed\033[0m\n'

[group("ci")]
ci-strict: install
    @printf '\033[34m▸ Running strict quality profile...\033[0m\n'
    uv run python scripts/ci/run_quality_suite.py --profile strict --log-dir quality-strict
    @printf '\033[32m✓ Strict CI checks passed\033[0m\n'

[group("ci")]
ci-docs: docs-build docs-linkcheck
    @printf '\033[32m✓ Docs CI passed\033[0m\n'

# ── Release ───────────────────────────────────────────────────────────────────

[group("release")]
commit:
    @printf '\033[34m▸ Starting interactive commit...\033[0m\n'
    pnpm run commit

[group("release")]
release:
    @printf '\033[34m▸ Running semantic-release...\033[0m\n'
    pnpm run release
    @printf '\033[32m✓ Release complete\033[0m\n'

[group("release")]
release-dry:
    @printf '\033[34m▸ Running semantic-release (dry run)...\033[0m\n'
    pnpm run release:dry
    @printf '\033[32m✓ Dry run complete\033[0m\n'

[group("release")]
changelog:
    @printf '\033[1m\033[34mRecent Changes\033[0m\n'
    @head -100 CHANGELOG.md

[group("release")]
version:
    @grep -E '^version\s*=' pyproject.toml | head -1 | sed 's/version = //' | tr -d '"'

[group("release")]
node-deps:
    @printf '\033[34m▸ Installing Node dependencies...\033[0m\n'
    pnpm install
    @printf '\033[32m✓ Node dependencies installed\033[0m\n'

# ── Info ──────────────────────────────────────────────────────────────────────

[group("info")]
info:
    @printf '\033[1m\033[34mProject Info\033[0m\n'
    @printf '\033[2m─────────────────────────────────\033[0m\n'
    @printf 'Python:  %s\n' "$(python3 --version 2>&1)"
    @printf 'uv:      %s\n' "$(uv --version 2>&1)"
    @printf 'ruff:    %s\n' "$(uv run ruff --version 2>&1 || echo 'not installed')"
    @printf 'ty:      %s\n' "$(uv run ty --version 2>&1 || echo 'not installed')"
    @printf 'sphinx:  %s\n' "$(uv run sphinx-build --version 2>&1 || echo 'not installed')"
    @printf 'copier:  %s\n' "$(uv run copier --version 2>&1 || echo 'not installed')"
    @printf 'just:    %s\n' "$(just --version 2>&1 || echo 'not installed')"

# Generate matrix data for web wizard + samples metadata
matrix-data:
    uv run python scripts/ci/generate_matrix_data.py
