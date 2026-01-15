# Scripts API Reference

This document provides API documentation for the riso automation scripts.

## CI Scripts (`scripts/ci/`)

### validate_release_configs.py

Validates release management configuration files.

**Functions:**

- `validate_commitlint_config(project_dir: Path) -> tuple[bool, list[str]]`
  - Validates `.commitlintrc.yml` configuration
  - Returns: (is_valid, list of error messages)

- `validate_releaserc_config(project_dir: Path) -> tuple[bool, list[str]]`
  - Validates `.releaserc.yml` semantic-release configuration
  - Returns: (is_valid, list of error messages)

- `validate_release_workflow(project_dir: Path) -> tuple[bool, list[str]]`
  - Validates release workflow file
  - Returns: (is_valid, list of error messages)

**CLI Usage:**
```bash
uv run python scripts/ci/validate_release_configs.py [project_dir]
```

---

### validate_dockerfiles.py

Validates Dockerfiles using hadolint.

**Functions:**

- `find_dockerfiles(project_dir: Path) -> list[Path]`
  - Discovers Dockerfile and Dockerfile.* files

- `validate_dockerfile_syntax(dockerfile: Path) -> dict`
  - Runs hadolint validation on a single Dockerfile
  - Returns: validation result dictionary

**CLI Usage:**
```bash
uv run python scripts/ci/validate_dockerfiles.py [directory]
```

---

### validate_workflows.py

Validates GitHub Actions workflow files using actionlint.

**Functions:**

- `validate_workflow(workflow_path: Path) -> dict`
  - Validates a single workflow file
  - Returns: {"valid": bool, "errors": list}

- `validate_workflows(workflows_dir: Path, strict: bool = False) -> int`
  - Validates all workflows in directory
  - Returns: exit code (0 = success)

---

### render_matrix.py

Renders all sample variants and generates metadata.

**Functions:**

- `discover_variants(samples_dir: Path) -> list[str]`
  - Discovers sample variant directories

- `load_smoke_results(path: Path) -> dict | None`
  - Loads smoke test results JSON

- `render_variant(variant: str, answers_file: Path) -> dict`
  - Renders a single variant

---

### record_module_success.py

Records and aggregates module success metrics.

**Classes:**

- `ModuleStats`
  - Dataclass tracking passed/failed/errored/skipped counts
  - Methods: `total()`, `success_rate()`, `to_dict()`

- `ModuleSuccessRecorder`
  - Aggregates module statistics across variants
  - Methods: `record()`, `write()`

---

## Hook Scripts (`scripts/hooks/`)

### quality_tool_check.py

Checks and provisions quality tools.

**Classes:**

- `ToolCheck`
  - Dataclass for tool status: name, status, command, stderr, next_steps

**Functions:**

- `ensure_python_quality_tools() -> list[ToolCheck]`
  - Ensures ruff, mypy, pylint, coverage are available

- `ensure_node_quality_tools(require_pnpm: bool) -> list[ToolCheck]`
  - Ensures pnpm is available via corepack

---

## Automation Scripts (`scripts/automation/`)

### render_client.py

HTTP client for automation API.

**Classes:**

- `RenderClient`
  - Base URL configuration
  - Bearer token authentication
  - Methods: `get_sample()`, `_request()`

**Exceptions:**

- `APIError` - Raised for HTTP errors with status_code and payload

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation failure |
| 2 | Configuration error |
| 127 | Tool not found |
