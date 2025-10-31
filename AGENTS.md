# Riso Template • Agent Operations

> Maintained per [AGENTS.md specification](https://agents.md) (observed: 2025-10-29) and [maintainer field guide](https://github.com/openai/agents.md) (observed: 2025-10-29).

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
- `.github/context/` – canonical context snippets; must match `template/files/shared/.github/context/` (`uv run python scripts/ci/verify_context_sync.py`).
- `docs/` – Jinja-templated quickstart and module docs rendered into downstream projects.
- `.specify/specs/` – canonical GitHub Spec Kit workspace (access via `specs/` symlink if tooling expects the legacy location).

## Python Execution Convention
**CRITICAL**: All Python scripts MUST be executed via `uv run python` to ensure proper virtual environment isolation and dependency management. Never invoke Python directly (`python`, `python3`, or `python3.11`). This applies to all automation scripts, CI workflows, and local development commands.

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
- `uv run python scripts/ci/render_matrix.py` – render every `samples/*/copier-answers.yml`, update metadata, and recompute module success.
- `uv run python scripts/ci/record_module_success.py` – regenerate `samples/metadata/module_success.json` from existing smoke logs.
- `uv run python scripts/ci/run_quality_suite.py --profile {standard|strict}` – execute make/uv quality lanes and emit artifacts consumed by `.github/workflows/quality-matrix.yml`.
- `uv run python scripts/ci/run_baseline_quickstart.py` – refresh command timing evidence for downstream documentation.
- `uv run python scripts/ci/verify_context_sync.py` – ensure shared `.github/context` files stay byte-identical between template and repo.

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

- 003-code-quality-integrations: Added unified quality suite (ruff, mypy, pylint, pytest, coverage) with standard/strict profiles, auto-healing tool provisioning, parallelized CI jobs, and 90-day artifact retention
- 002-docs-template-expansion: Added Python 3.11 (uv-managed), Node.js 20 LTS, TypeScript 5.6, POSIX shell + Fumadocs (Next.js 15), Sphinx 7.4 + Shibuya theme, Docusaurus 3, pnpm ≥8, mise 2024.9+, uv ≥0.4
- 002-docs-template-expansion: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

## Active Technologies
