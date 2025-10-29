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
- `.github/context/` – canonical context snippets; must match `template/files/shared/.github/context/` (`python scripts/ci/verify_context_sync.py`).
- `docs/` – Jinja-templated quickstart and module docs rendered into downstream projects.

## Render & Validate Default Variant
```bash
./scripts/render-samples.sh
cd samples/default/render
PACKAGE=$(awk -F': ' '$1=="package_name"{print $2}' ../copier-answers.yml)
uv sync
uv run python -m ${PACKAGE}.quickstart
uv run pytest
uv run ruff check
uv run mypy
uv run pylint ${PACKAGE}
```
- The render writes metrics to `samples/default/baseline_quickstart_metrics.json` and smoke logs to `samples/default/smoke-results.json`.

## Render Specific Variant
```bash
./scripts/render-samples.sh --variant full-stack --answers samples/full-stack/copier-answers.yml
```
- Output lands in `samples/<variant>/render`; inspect `<variant>/smoke-results.json` for module statuses and `<variant>/metadata.json` for configuration.

## Aggregate & Governance Checks
- `python scripts/ci/render_matrix.py` – render every `samples/*/copier-answers.yml`, update metadata, and recompute module success.
- `python scripts/ci/record_module_success.py` – regenerate `samples/metadata/module_success.json` from existing smoke logs.
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
