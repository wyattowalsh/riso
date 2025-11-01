# Riso Template • Agent Operations

> Maintained per [AGENTS.md specification](https://agents.md) (observed: 2025-10-30) and [maintainer field guide](https://github.com/openai/agents.md) (observed: 2025-10-30).

## Quickstart

Get started with the default template variant:

```bash
# Render the default sample
./scripts/render-samples.sh

# Navigate to the rendered project
cd samples/default/render

# Set up the environment and run quickstart
PACKAGE=$(awk -F': ' '$1=="package_name"{print $2}' ../copier-answers.yml)
uv sync
uv run python -m ${PACKAGE}.quickstart

# Run quality checks
make quality
# or, when make is unavailable
QUALITY_PROFILE=standard uv run task quality
```

## Scope & Ownership

- Riso is a Copier template plus automation helpers; render actual projects with `copier copy` or `scripts/render-samples.sh`.
- Template maintainers keep sample renders, automation scripts, and documentation synchronized; rendered projects must author their own AGENTS.md.
- Apply the "lean, link out" pattern—keep this file as the control plane and point to deeper docs like `docs/quickstart.md.jinja`.

## Required Tooling
- Python ≥3.11 with uv (`python3 --version`, `uv version`); hooks expect uv to manage virtual environments.
- Node.js 20 LTS and pnpm ≥8 (`node --version`, `pnpm --version`) for TypeScript/Fumadocs/Fastify tracks.
- Copier CLI (`copier --version`); `template/hooks/pre_gen_project.py` fails fast if any prerequisite is missing.
- Optional: set `COPIER_CMD` to point at a custom Copier binary when invoking automation.

## Repository Map

- `template/` – Copier payload (Python + Node variants, shared logic, docs, module catalog).
- `scripts/` – local/CI automation (rendering, metrics, context sync); run from repo root.
- `samples/` – curated answer files, rendered artifacts, `smoke-results.json`, performance metrics.
- `.github/context/` – canonical context snippets; must match `template/files/shared/.github/context/` (`python scripts/ci/verify_context_sync.py`).
- `docs/` – Jinja-templated quickstart and module docs rendered into downstream projects.
- `specs/` – GitHub Spec Kit workspace (canonical specifications for features and plans).

## Build & Test Parity

**Local development:**

```bash
# From repo root - render and test template
./scripts/render-samples.sh
cd samples/default/render
uv sync
make quality
```

**CI workflows:** GitHub Actions workflows automatically run quality checks on PRs and commits to main. Rendered projects include:

- **`riso-quality.yml`**: Main quality workflow running ruff, mypy, pylint, pytest with retry logic and artifact uploads (90-day retention)
- **`riso-matrix.yml`**: Matrix testing across Python 3.11, 3.12, 3.13 with fail-fast disabled and per-version artifacts

**Required branch protection checks:**
- `python-quality` - Main quality suite (ruff, mypy, pylint, pytest)
- `python-matrix / test-py311` - Python 3.11 compatibility
- `python-matrix / test-py312` - Python 3.12 compatibility
- `python-matrix / test-py313` - Python 3.13 compatibility
- `matrix-summary` - Overall matrix status (blocks merge if any version fails)

**CI features:**
- Dependency caching with 70%+ hit rate target (uv.lock and pnpm-lock.yaml hashing)
- Retry logic with exponential backoff (3 attempts)
- Conditional Node.js job when `api_tracks` includes `node`
- Profile-based timeouts (10min standard, 20min strict)
- Cache hit/miss logging for debugging

**Viewing CI status:**
```bash
# In rendered project with GitHub remote
gh run list --limit 5
gh run view <run-id> --log
```

## Code Quality

Quality tools run via `make quality` or `uv run task quality` in rendered projects:

- **Linting:** ruff (configuration in `pyproject.toml`)
- **Type checking:** mypy (configuration in `pyproject.toml`)
- **Static analysis:** pylint (configuration in `pyproject.toml`)
- **Testing:** pytest with coverage (configuration in `pytest.ini` and `coverage.cfg`)
- **Profiles:** `QUALITY_PROFILE=standard` (default) or `QUALITY_PROFILE=strict` for enhanced checks

Quality suite implementation:

- `template/files/shared/quality/makefile.quality.jinja` – Makefile targets
- `template/files/shared/quality/uv_tasks/quality.py.jinja` – uv task definitions
- `scripts/ci/check_quality_parity.py` – ensures Makefile and uv tasks stay synchronized
- `scripts/ci/run_quality_suite.py` – CI orchestration script

**Critical Convention:** All Python commands MUST use `uv run` prefix (never bare `python` or `pytest`). This ensures consistent virtual environment usage across local development, CI/CD workflows, and rendered projects. Examples:
- ✅ `uv run pytest tests/`
- ✅ `uv run python -m mypackage.cli`
- ✅ `uv run task quality`
- ❌ `python -m pytest` (incorrect)
- ❌ `pytest tests/` (incorrect)

## Security

**Secrets management:**

- Never commit secrets to the repository
- Use environment variables for sensitive configuration
- Rendered projects should implement `.env` files (gitignored by default)

**Production safety:**

- Pre-generation hook (`template/hooks/pre_gen_project.py`) validates required tooling and fails fast on missing dependencies
- Post-generation hook writes metadata to `.riso/post_gen_metadata.json` for audit trails
- Quality checks must pass before merging changes

**Security-critical paths:**

- `template/hooks/` – validation and initialization logic
- `scripts/ci/verify_context_sync.py` – ensures shared context files remain synchronized

## Render & Validate Default Variant
```bash
./scripts/render-samples.sh
cd samples/default/render
PACKAGE=$(awk -F': ' '$1=="package_name"{print $2}' ../copier-answers.yml)
uv sync
uv run python -m ${PACKAGE}.quickstart
make quality
# or, when make is unavailable
QUALITY_PROFILE=standard uv run task quality
```
- The render writes metrics to `samples/default/baseline_quickstart_metrics.json` and smoke logs to `samples/default/smoke-results.json`.
- The quality suite logs tool durations to `.riso/quality-durations.json`; CI archives the full log bundle with 90-day retention.

## Render Specific Variant
```bash
./scripts/render-samples.sh --variant full-stack --answers samples/full-stack/copier-answers.yml
```
- Output lands in `samples/<variant>/render`; inspect `<variant>/smoke-results.json` for module statuses and `<variant>/metadata.json` for configuration.

## Aggregate & Governance Checks
- `python scripts/ci/render_matrix.py` – render every `samples/*/copier-answers.yml`, update metadata, and recompute module success.
- `python scripts/ci/record_module_success.py` – regenerate `samples/metadata/module_success.json` from existing smoke logs.
- `python scripts/ci/run_quality_suite.py --profile {standard|strict}` – execute make/uv quality lanes and emit artifacts consumed by `.github/workflows/quality-matrix.yml`.
- `python scripts/ci/run_baseline_quickstart.py` – refresh command timing evidence for downstream documentation.
- `python scripts/ci/verify_context_sync.py` – ensure shared `.github/context` files stay byte-identical between template and repo.

## Module Validation Matrix (run inside a rendered project root)
- `cli_module=enabled`
  ```bash
  uv run python -m ${PACKAGE}.cli --help
  uv run pytest tests/test_cli.py
  ```
- `api_tracks` includes `python`
  ```bash
  uv run pytest tests/test_api_fastapi.py
  uv run uvicorn ${PACKAGE}.api.main:app --host 0.0.0.0 --port 8000
  ```
- `api_tracks` includes `node`
  ```bash
  pnpm install
  pnpm --filter api-node test
  pnpm --filter api-node run dev
  ```
- `mcp_module=enabled`
  ```bash
  uv run python -c "from shared.mcp import tooling; print(tooling.list_tools())"
  ```
- `docs_site=fumadocs`
  ```bash
  pnpm install
  pnpm --filter docs-fumadocs build
  pnpm --filter docs-fumadocs run dev
  ```
- `shared_logic=enabled`
  ```bash
  uv run python -c "from shared.logic import summarize_payload; print(summarize_payload({'service': 'shared', 'status': 'ok'}))"
  ```

## Key Artifacts & Logs
- `samples/<variant>/smoke-results.json` – per-module pass/fail/skip reasoning from render scripts.
- `samples/metadata/render_matrix.json` – inventory of rendered variants and latest smoke outcomes.
- `samples/metadata/module_success.json` – aggregated success rates per module for trend tracking.
- `.riso/post_gen_metadata.json` (inside renders) – rendered-at timestamp and module selections.

## References
- Quickstart playbook: `docs/quickstart.md.jinja`
- Automation: `scripts/render-samples.sh`, `scripts/hooks/post-init.sh`
- Module catalog: `template/files/shared/module_catalog.json.jinja`

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Recent Changes

- 004-github-actions-workflows: Added GitHub Actions CI/CD workflows with quality checks (ruff, mypy, pylint, pytest), matrix testing across Python 3.11/3.12/3.13, retry logic with exponential backoff, dependency caching, artifact uploads with 90-day retention, and conditional Node.js job support
- 003-code-quality-integrations: Added unified quality suite (ruff, mypy, pylint, pytest, coverage) with standard/strict profiles, auto-healing tool provisioning, parallelized CI jobs, and 90-day artifact retention
- 002-docs-template-expansion: Added Python 3.11 (uv-managed), Node.js 20 LTS, TypeScript 5.6, POSIX shell + Fumadocs (Next.js 15), Sphinx 7.4 + Shibuya theme, Docusaurus 3, pnpm ≥8, mise 2024.9+, uv ≥0.4

## Active Technologies

- YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering) + GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`, `nick-fields/retry@v3`), actionlint (workflow validation), existing quality tools from feature 003 (004-github-actions-workflows)
- Workflow artifacts (JUnit XML, coverage reports, logs) stored in GitHub Actions artifact storage with 90-day retention (004-github-actions-workflows)
- Matrix testing across Python 3.11, 3.12, 3.13 with fail-fast disabled and per-version artifacts (004-github-actions-workflows)
- Python 3.11 (uv-managed), optional Node.js 20 LTS + ruff, mypy, pylint, pytest, coverage, optional eslint + typescript (003-code-quality-integrations)
