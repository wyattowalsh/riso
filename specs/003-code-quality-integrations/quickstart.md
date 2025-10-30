# Quickstart: Code Quality Integration Suite

## Prerequisites
- Install `uv` ≥0.4 to manage Python 3.11 environments (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
- Ensure `corepack` is enabled (`corepack enable`) so `corepack pnpm install` can provision pnpm ≥8 when needed.
- Verify `make` is available; if not, plan to use the `uv run task quality` shim.
- (Optional) Configure GitHub CLI to download CI artifacts when auditing retained logs.

## Render & Setup Steps
1. Run `copier copy path/to/riso-template ./my-service` and answer prompts as usual.
2. Accept the default `quality_profile=standard` unless your team is ready for the stricter rule set.
3. If you enable the Node API track, ensure Node.js 20 LTS is available; the hook will perform `corepack pnpm install` if pnpm is missing.
4. After render, inspect `.riso/post_gen_metadata.json` for `tool_install_attempts` to confirm auto-install results.

## Local Quality Commands
- **Preferred**: `make quality`
  ```bash
  QUALITY_PROFILE=standard make quality
  ```
- **Without Make**: `uv run task quality`
  ```bash
  QUALITY_PROFILE=strict uv run task quality
  ```
- Both commands:
  - Execute Ruff, Mypy, Pylint, pytest, and optional ESLint/TypeScript checks (when Node tracks enabled).
  - Emit per-tool logs under `.riso/quality/`.
  - Exit non-zero if any tool fails after auto-install retries.

## CI Validation Matrix
1. Ensure `scripts/render-samples.sh` is invoked (locally or in CI) to regenerate `samples/default` and `samples/full-stack` renders.
2. The GitHub Actions workflow `quality-matrix.yml` runs the following jobs in parallel:
   - `python-quality-standard`
   - `python-quality-strict` (gate-controlled via prompt/flag)
   - `node-quality-standard` (only when Node API track enabled)
   - `aggregate-status` — consolidates artifacts, updates `samples/metadata/module_success.json`, and enforces runtime budgets.
3. Each job uploads `quality-logs-<job>.tar.gz` retained for 90 days; failures block merge until resolved.

## Troubleshooting
- If hooks report failed installs, rerun `make quality` after manually installing the missing tool (`uv tool install <name>` or `corepack pnpm install`).
- Clearing `.uv/` and rerunning `uv sync` resolves corrupted virtual environments.
- Use `QUALITY_SKIP_NODE=1 make quality` temporarily if Node tooling is offline; document the skip and re-run once dependencies are restored.
- Review `.riso/quality/*.log` to pinpoint failing rules, then update configuration templates under `template/files/shared/quality/` as needed.
