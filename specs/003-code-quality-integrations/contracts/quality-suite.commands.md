# Contract: Quality Automation Interfaces

## CLI Contract — `make quality`
- **Purpose**: Run the unified Python (and optional Node) quality suite locally.
- **Inputs**:
  - Environment variables: `QUALITY_PROFILE` (default `standard`), `QUALITY_SKIP_NODE` (optional `1` to skip Node checks explicitly).
  - Optional arguments: `TARGETS="tool1 tool2"` to limit execution.
- **Outputs**:
  - Exit code `0` on success, `1` on any tool failure, `2` when tooling prerequisites are missing after auto-install retry.
  - Writes per-tool logs to `.riso/quality/{tool}.log` and summary to stdout.
- **Failure Modes**:
  - Missing tooling triggers hook auto-install (see ToolInstallAttempt contract) before failing with remediation instructions.
  - Exceeding runtime threshold (>6 minutes) surfaces warning but does not change exit code (CI enforces threshold separately).

## CLI Contract — `uv run task quality`
- **Purpose**: Provide Makefile-equivalent entrypoint for environments without `make`.
- **Inputs**: Same environment controls as `make quality`.
- **Outputs**: Mirrors Makefile behavior; ensures parity by importing shared Python task definitions.
- **Failure Modes**: Propagates structured exit codes and log locations identical to Makefile contract.

## GitHub Actions Contract — `quality-matrix.yml`
- **Trigger**: `pull_request` on the template repo and nightly `schedule` for governance sweeps.
- **Jobs**:
  - `python-quality-standard`: Runs `make quality` with `QUALITY_PROFILE=standard`; caches `.uv` and `.riso/quality` directories; uploads logs.
  - `python-quality-strict`: Conditional on prompt enabling strict profile; runs in parallel with tighter lint/type settings.
  - `node-quality-standard`: Conditional on `api_tracks` containing `node`; installs pnpm via `corepack pnpm install`; runs ESLint + TypeScript checks.
  - `aggregate-status`: Needs all previous jobs; collates artifacts, updates `samples/metadata/module_success.json`, and enforces runtime budget (<6 minutes per job).
- **Outputs**:
  - Artifacts: `quality-logs-${job}.tar.gz`, retained for 90 days.
  - Summary: GitHub job summary includes pass/fail table and runtime metrics.
- **Failure Modes**:
  - Any job failure blocks merge via required status checks.
  - Aggregate job fails if logs are missing or retention <90 days.

## Hook Contract — `quality_tool_check.py`
- **Purpose**: Pre/post-generation hook verifying required tooling before quality suite runs.
- **Behavior**:
  - Checks for Ruff, Mypy, Pylint binaries via `uv tool run --describe`.
  - Checks for `pnpm` when Node modules selected; attempts `corepack pnpm install` once.
  - Records each attempt in `.riso/post_gen_metadata.json` under `tool_install_attempts`.
- **Failure Modes**:
  - If auto-install fails, hook aborts render with actionable follow-up instructions.
  - Hook never performs more than one install attempt per tool.
