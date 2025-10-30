# Feature Specification: Code Quality Integration Suite

**Feature Branch**: `003-code-quality-integrations`  
**Created**: 2025-10-30  
**Status**: Draft  
**Input**: User description: "code quality integrations including ruff, mypy, pylint, ci/cd flows, makefile integrations, etc in both the project level and templates levels."

## Clarifications

### Session 2025-10-30

- Q: When required Python quality binaries are missing during render, how should hooks respond? → A: Attempt a one-time `uv` install of missing tools, rerun validation, and abort only if the install or recheck fails.
- Q: When Node quality tooling is missing while the Node API track is enabled, what should happen? → A: Attempt a one-time `corepack pnpm install`, rerun checks, and fail only if the install or recheck fails.
- Q: How should CI handle long-running quality tasks to avoid timeouts? → A: Split the quality suite into parallel CI jobs per tool/profile with shared caching and aggregate the results.
- Q: What should the default `quality_profile` be for new renders? → A: Default every render to the `standard` profile and treat `strict` as an opt-in upgrade.
- Q: How long must quality artifacts remain accessible for governance review? → A: Retain quality logs and coverage evidence for 90 days to support quarterly audits.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Quality Gate for Baseline Render (Priority: P1)

A template maintainer renders the default project and runs a single quality command that executes Ruff, Mypy, Pylint, pytest smoke tests, and records evidence without manual wiring.

**Why this priority**: Without an opinionated baseline quality gate the template cannot prove parity across renders, and regressions slip into downstream teams.

**Independent Test**: Render `samples/default/`, run the generated `make quality` (or `uv run task quality`) target, and confirm Ruff, Mypy, Pylint, pytest, and coverage summaries succeed and update `smoke-results.json`.

**Acceptance Scenarios**:

1. **Given** a freshly rendered default project, **When** the maintainer runs the documented quality command, **Then** Ruff, Mypy, Pylint, and pytest all report success and the command exits 0 while logging durations in `baseline_quickstart_metrics.json`.
2. **Given** the maintainer introduces a Ruff violation in the rendered project, **When** the quality command runs, **Then** it fails fast with actionable messaging and the CI status surfaces the failure in `samples/default/smoke-results.json`.

---

### User Story 2 - CI Automation Blocks Template Regressions (Priority: P2)

A template contributor opens a pull request and CI automatically runs the full quality suite against template sources and regenerated samples, blocking merge on any lint/type failure.

**Why this priority**: Governance principles require deterministic automation; human reviewers should never merge code that violates linting or type guarantees.

**Independent Test**: Open a PR that intentionally violates Mypy or Pylint, observe GitHub Actions rejecting the run, and verify the failure links to the remediation playbook.

**Acceptance Scenarios**:

1. **Given** a pull request touching template Python files, **When** GitHub Actions execute, **Then** the workflow runs Ruff, Mypy, and Pylint against the template plus regenerated samples and marks the check as failed when any tool reports errors.
2. **Given** `scripts/render_matrix.py` regenerates multiple variants, **When** the quality matrix job finishes, **Then** it uploads consolidated lint/type logs and updates `samples/metadata/module_success.json` with pass/fail status per variant.

---

### User Story 3 - Downstream Teams Extend Quality Controls (Priority: P3)

A downstream team toggles optional modules (Node API, shared logic) and can customize the quality suite (e.g., enable JavaScript linting) while preserving the Python baseline and automation evidence.

**Why this priority**: Teams adopting optional stacks must inherit sane defaults and extend them without rewriting the automation harness.

**Independent Test**: Render the `full-stack` sample with `quality_profile=strict`, run the generated Makefile targets, and confirm both Python and Node quality jobs execute with accurate skips when modules are disabled.

**Acceptance Scenarios**:

1. **Given** a render with `api_tracks=["python","node"]` and `quality_profile=strict`, **When** the maintainer runs `make quality`, **Then** the command orchestrates Ruff, Mypy, Pylint, pytest, and ESLint/TypeScript checks, and reports per-language sections in the summary artifact.
2. **Given** a render with Node tracks disabled, **When** the quality command runs, **Then** Node-focused checks are automatically skipped with logged rationale while Python checks still execute.

---

### Edge Cases

- If required Python quality binaries are missing but `uv` is available, the pre/post-generation hooks attempt a single auto-install via `uv`; if the retry still fails, the render aborts with remediation guidance.
- If Node API tooling is enabled but `pnpm` (and Node quality binaries) are missing, the hooks attempt a one-time `corepack pnpm install` (or equivalent installer) before re-running checks; if the retry fails, the render aborts with guidance.
- Long-running quality tasks (e.g., strict Mypy) run in parallelized CI jobs per tool/profile with shared caches; aggregated results preserve a unified status while maintaining manageable runtimes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (B)**: Generated projects MUST expose a documented `make quality` (with `uv` fallback) target that chains Ruff, Mypy, Pylint, pytest smoke tests, and coverage collection, exiting non-zero when any step fails.
- **FR-002 (B)**: Template files MUST provide shared configuration (`ruff.toml`, `mypy.ini`, `.pylintrc`, coverage config) that render deterministically into projects and align with published style guides.
- **FR-003 (B)**: Quickstart documentation and sample metadata MUST instruct maintainers to run the quality target and capture durations in `baseline_quickstart_metrics.json`.
- **FR-004 (B)**: Template-level CI workflows MUST run Ruff, Mypy, and Pylint against template Python sources plus regenerated samples on every pull request, split these checks into parallel jobs per tool/profile with shared caching, and block merge on failure.
- **FR-005 (B)**: `scripts/render-samples.sh` MUST execute the quality target for each rendered sample, updating `smoke-results.json` with per-tool pass/fail details and storing logs as CI artifacts.
- **FR-006 (B)**: Pre- and post-generation hooks MUST verify required quality tooling is available, attempt a single `uv`-managed install when binaries are missing, and abort with remediation guidance only if the retry still fails.
- **FR-007 (O)**: When the Node API track is enabled, the quality target MUST optionally include ESLint/TypeScript checks wired through pnpm, attempt a single `corepack pnpm install` when tooling is missing, and abort with remediation guidance only if the retry still fails without affecting the Python-only baseline.
- **FR-008 (O)**: A `quality_profile` prompt MUST allow maintainers to choose between `standard` (default) and `strict` suites, toggling additional Pylint plugins, Ruff rulesets, and Mypy strictness.
- **FR-009 (B)**: Quality artifacts (logs, JUnit exports, coverage reports) MUST be captured to `.riso/post_gen_metadata.json`, surfaced in governance dashboards, and retained for at least 90 days to support quarterly audits.
- **FR-010 (B)**: Documentation in `docs/modules/quality.md.jinja` MUST enumerate the quality suite, configuration knobs, and troubleshooting steps for downstream teams.
- **FR-011 (B)**: The template MUST ensure Makefile targets and `uv run` equivalents remain in sync through automation tests, preventing drift between the CLI experiences.

### Template Prompts & Variants

- **Prompt**: `quality_profile` — **Type**: Baseline — **Default**: `standard` — **Implication**: Chooses between baseline (Ruff, Mypy, Pylint with pragmatic settings) and strict (additional Ruff rules, Mypy strict mode, Pylint plugins) quality suites; influences generated config values and Makefile targets.
- Downstream renders default to the `standard` profile; upgrading to `strict` requires an explicit prompt selection or documented post-render toggle.
- **Prompt**: `api_tracks` — **Type**: Optional — **Default**: `none` — **Implication**: When `node` is included, augments the quality target with pnpm-based lint/type checks; when absent, Node tasks are skipped while logging the omission.
- **Variant Samples**: Extend `samples/default/` for baseline evidence and create or update `samples/full-stack/` renders with `quality_profile=strict` to capture Python+Node quality logs and metadata.

### Key Entities

- **QualitySuite**: Describes the set of tools (Ruff, Mypy, Pylint, pytest, optional ESLint) enabled for a render, their severity levels, and expected runtime budgets.
- **QualityRunEvidence**: Captures per-tool exit codes, durations, and artifact locations recorded in `smoke-results.json` and governance dashboards.
- **QualityProfileSelection**: Represents the selected prompt option, mapping to configuration overrides and CI matrix entries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Baseline quality runs on fresh renders complete in under 4 minutes on a Mac M2–class machine and under 6 minutes in CI 95% of the time.
- **SC-002**: ≥98% of pull requests finish the template quality workflow without manual retries, with failures attributable to genuine lint/type issues.
- **SC-003**: 100% of rendered samples publish up-to-date quality evidence (pass/fail, durations) into `samples/metadata/module_success.json` within one business day of template changes.
- **SC-004**: Downstream projects adopting the template report a <5% month-over-month variance in “quality tooling setup” support tickets after enabling the suite.

## Principle Compliance Evidence *(mandatory)*

- **Template Sovereignty**: Store Ruff, Mypy, Pylint, and Makefile scaffolds under `template/files/**`; prove integrity via `copier diff` outputs comparing template to rendered projects.
- **Deterministic Generation**: Extend `scripts/render-samples.sh` and CI workflows to re-run quality commands for each variant, archiving logs and enforcing identical toolchain versions via `uv` lock files.
- **Minimal Baseline, Optional Depth**: Ship Python quality tooling in the baseline render; gate Node/strict enhancements behind prompts so optional modules remain isolated.
- **Documented Scaffolds**: Update `docs/quickstart.md.jinja`, `docs/modules/quality.md.jinja`, `.github/context/quality.md`, and upgrade guides with instructions, troubleshooting, and evidence expectations.
- **Automation-Governed Compliance**: Wire GitHub Actions and scheduled governance jobs to fail when quality artifacts are stale or missing, ensuring merges require passing automation.

## Assumptions

- Python 3.11 with `uv`, Ruff, Mypy, and Pylint remain the enforced stack for Python quality checks; optional Node tooling relies on pnpm ≥8.
- Developers accept Makefile as the primary aggregation surface, with `uv run` shims provided for environments lacking `make`.
- Quality evidence will be aggregated alongside existing smoke metrics without requiring a new storage backend.

## Dependencies & External Inputs

- Official releases of Ruff, Mypy, Pylint, pytest, and optional ESLint/TypeScript tooling.
- GitHub Actions runners (macOS and Ubuntu) with permissions to upload quality artifacts.
- Existing automation harness (`scripts/render_matrix.py`, `scripts/ci/run_baseline_quickstart.py`) for integrating quality metrics.

## Risks & Mitigations

- **Risk**: Strict profiles may generate noisy false positives. **Mitigation**: Provide documented suppression patterns and keep `standard` as default while tracking strict adoption metrics.
- **Risk**: Quality runs could extend CI duration. **Mitigation**: Parallelize tool execution where safe and cache dependencies via `uv` and pnpm.
- **Risk**: Missing local tooling blocks renders. **Mitigation**: Hooks attempt installs once and emit actionable remediation instructions before aborting.

## Out of Scope

- Integrating non-Python quality tooling beyond optional Node tasks (for example, Go, Rust, JVM linters).
- Building custom IDE plugins or editor integrations for the quality suite.
- Implementing organization-wide policy engines beyond the governance checks described above.
