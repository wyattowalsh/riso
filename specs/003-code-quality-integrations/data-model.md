# Data Model: Code Quality Integration Suite

## QualitySuite
- **Fields**
  - `profile` (enum: `standard`, `strict`)
  - `tools` (set enum: `ruff`, `mypy`, `pylint`, `pytest`, `eslint`, `tsc`)
  - `commands` (map<string, string>) — CLI commands per tool (`make quality`, `uv run task quality`, etc.)
  - `ci_jobs` (array<string>) — GitHub Actions job identifiers per tool/profile lane
  - `is_default` (bool)
  - `applies_to_modules` (set enum: `python`, `node`)
- **Relationships**
  - 1..* -> `QualityRunEvidence`
  - 1..* -> `ToolInstallAttempt`
- **Constraints**
  - Exactly one suite per render has `is_default=true`
  - `profile=strict` MUST include `eslint` and `tsc` when `node` module selected

## QualityRunEvidence
- **Fields**
  - `suite_profile` (foreign key -> `QualitySuite.profile`)
  - `tool_name` (enum: `ruff`, `mypy`, `pylint`, `pytest`, `eslint`, `tsc`)
  - `status` (enum: `pass`, `fail`, `skipped`)
  - `duration_seconds` (float)
  - `artifact_uri` (string) — GitHub Actions artifact link
  - `recorded_at` (datetime)
  - `ci_run_id` (string)
  - `retention_expires_at` (datetime)
- **Constraints**
  - `status=pass` requires both `artifact_uri` and `retention_expires_at`
  - Retention must be ≥ 90 days from `recorded_at`
  - Entries sync to `samples/metadata/module_success.json`

## QualityProfileSelection
- **Fields**
  - `render_id` (string) — unique identifier for template render/sample
  - `selected_profile` (enum: `standard`, `strict`)
  - `modules_enabled` (set enum: `python`, `node`, `cli`, `shared_logic`)
  - `reason` (string) — optional justification when deviating from default
- **Relationships**
  - 1 -> 1 `QualitySuite` (selected suite applies to render)
- **Constraints**
  - Defaults to `standard` for new renders unless prompt overrides
  - `selected_profile=strict` must record a non-empty `reason`

## ToolInstallAttempt
- **Fields**
  - `tool_name` (enum: `ruff`, `mypy`, `pylint`, `pnpm`, `eslint`)
  - `installer` (enum: `uv`, `corepack`, `custom`)
  - `attempted_at` (datetime)
  - `status` (enum: `installed`, `already_present`, `failed`)
  - `stderr_path` (string) — captured log on failure
  - `next_steps` (string)
- **Constraints**
  - Only one attempt per tool per render within hooks
  - `status=failed` aborts render before quality suite runs

## QualityArtifactRetention
- **Fields**
  - `ci_artifact_name` (string)
  - `ci_run_id` (string)
  - `uploaded_at` (datetime)
  - `expires_at` (datetime)
  - `size_mb` (float)
- **Constraints**
  - `expires_at - uploaded_at` ≥ 90 days
  - Warn when `expires_at - now` < 14 days to trigger refresh automation
