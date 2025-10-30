# Riso Template Constitution

## Core Principles

### I. UV-Managed Python Execution (NON-NEGOTIABLE)

**ALL Python commands MUST be executed via `uv run` to ensure consistent environment management.**

- Direct `python` or `python3` invocations are PROHIBITED
- Correct: `uv run python -m package.module`, `uv run pytest`, `uv run mypy`
- Incorrect: `python -m package.module`, `pytest`, `mypy`
- Exception: Internal `uv` bootstrapping scripts may invoke `python3` to install `uv` itself
- Rationale: Ensures reproducible builds, prevents dependency drift, enforces virtual environment isolation

### II. Automation-Governed Quality

**Quality automation must be deterministic, single-attempt, and evidence-tracked.**

- Tool provisioning: ONE auto-install attempt per tool via hooks; explicit failure paths required
- CI must be deterministic with fixed tool versions and cached dependencies
- Quality evidence (logs, coverage, durations) retained for 90 days minimum
- No network-dependent operations during template render beyond documented auto-install retries
- Quality profiles (`standard`/`strict`) must be clearly documented with opt-in/opt-out semantics

### III. Template Composition Over Inheritance

**Render targets must compose independent modules with clear boundaries.**

- Each module (CLI, API, MCP, docs) scaffolds independently and conditionally
- Shared logic extracted only when reused across ≥2 modules
- Module catalog (`module_catalog.json.jinja`) is the single source of truth for module state
- Jinja2 templating must remain readable; complex logic moves to Python hooks
- No hidden dependencies between modules; explicit prompt-driven selection

### IV. Documentation Synchronization

**Documentation must stay synchronized across template and rendered projects.**

- Shared context files (`.github/context/`) must be byte-identical between template and repo root
- `scripts/ci/verify_context_sync.py` enforces synchronization in CI
- Quickstart docs (`docs/quickstart.md.jinja`) must reflect actual command sequences
- Breaking changes require upgrade guide updates (`docs/upgrade-guide.md.jinja`)

### V. Evidence-Driven Governance

**Every automation decision must produce auditable evidence.**

- Sample renders tracked in `samples/*/smoke-results.json` with pass/fail/skip reasoning
- Module success rates aggregated in `samples/metadata/module_success.json`
- Baseline quickstart metrics captured in `baseline_quickstart_metrics.json` for SLA tracking
- Tool install attempts logged in `.riso/post_gen_metadata.json`
- CI artifacts (quality logs, coverage reports) uploaded with 90-day retention

## Technology Standards

### Required Tooling

- Python ≥3.11 managed via `uv` ≥0.4
- Node.js 20 LTS + pnpm ≥8 (via `corepack`) for TypeScript/Fumadocs/Fastify tracks
- Copier ≥9.1.0 for template rendering
- `mise` ≥2024.9 for optional multi-runtime management

### Code Quality Standards

- **Linting**: Ruff (Python), ESLint (Node)
- **Type Checking**: Mypy (Python strict optional), TypeScript 5.6+ (Node)
- **Testing**: pytest (Python), Vitest (Node)
- **Coverage**: ≥85% for new modules, tracked via `coverage.cfg`
- **CI Runtime**: `<6m` per quality job (standard profile), `<8m` (strict profile)

### Naming Conventions

- Package names: `snake_case` (Python), `kebab-case` (npm packages)
- Module files: lowercase with underscores (`shared_logic.py`)
- Jinja templates: preserve target extension (`.jinja` suffix)
- Git branches: feature descriptors (`003-code-quality-integrations`)

## Development Workflow

### Render Validation Process

1. Run `./scripts/render-samples.sh` (or variant-specific invocation)
2. Inspect `samples/*/smoke-results.json` for module health
3. Execute `make quality` (or `uv run task quality`) inside rendered project
4. Review `.riso/quality-durations.json` for performance regressions
5. Commit smoke results + metadata for governance audit trail

### Hook Execution Order

1. **Pre-generation** (`template/hooks/pre_gen_project.py`):
   - Validate required tooling (uv, Node, pnpm if needed)
   - Attempt single auto-install pass for missing quality tools
   - Abort render with actionable instructions on unrecoverable failures

2. **Post-generation** (`template/hooks/post_gen_project.py`):
   - Record `tool_install_attempts` in `.riso/post_gen_metadata.json`
   - Emit next-steps guidance to stdout
   - NO network operations (constitution-compliant determinism)

### CI Quality Gates

- **Required Checks**: python-quality-standard, aggregate-status
- **Optional Checks**: python-quality-strict (when `quality_profile=strict`)
- **Artifact Retention**: 90 days for all quality logs and coverage reports
- **Failure Policy**: Block merge on any required check failure

## Governance

- This constitution supersedes all other development practices
- Amendments require: (1) documented rationale, (2) updated governance section, (3) migration plan for affected samples
- All PRs must pass constitution compliance checks via `scripts/compliance/checkpoints.py`
- Principle violations require explicit justification in PR description

**Version**: 1.0.0 | **Ratified**: 2025-10-30 | **Last Amended**: 2025-10-30
