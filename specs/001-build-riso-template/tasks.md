---
description: Task list template for feature implementation
---

# Tasks: Riso Template Foundation

**Input**: Design documents from `/.specify/specs/001-build-riso-template/` (legacy symlink available at `specs/001-build-riso-template/`)\
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Include explicit test scaffolds only when required to validate the user stories’ acceptance criteria.

**Constitution Gates**: Regenerate template samples, refresh documentation, and prove governance automation prior to closing the feature.

**Organization**: Tasks are grouped by user story so each increment remains independently testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish template skeleton, metadata, and documentation placeholders.

- [x] T001 Create template source directories in template/prompts/, template/hooks/, and template/files/ per implementation plan.
- [x] T002 Document default stack metadata and prompts in template/copier.yml.
- [x] T003 [P] Scaffold sample automation stub scripts/render-samples.sh.
- [x] T004 [P] Initialize documentation placeholders docs/modules/.keep and docs/upgrade-guide/.keep for upcoming content.

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide shared prompts, macros, context syncing, and automation hooks that every story depends on.\
**⚠️ CRITICAL**: Complete this phase before starting any user story.

- [x] T005 Define consolidated prompt schema in template/prompts/options.yml.jinja covering layout and module toggles.
- [x] T006 [P] Implement module flag macros in template/files/shared/macros/module_flags.jinja for reuse across templates.
- [x] T007 [P] Create environment guard hook template/hooks/pre_gen_project.py validating uv and pnpm availability.
- [x] T008 [P] Scaffold governance-aware hook skeleton in template/hooks/post_gen_project.py with placeholder functions.
- [x] T009 Establish render matrix orchestrator scripts/ci/render_matrix.py coordinating sample permutations.
- [x] T010 [P] Mirror `.github/context/` assets into template/files/shared/.github/context/ ensuring generated projects receive best-practice workflows.
- [x] T011 [P] Add context sync verification script scripts/ci/verify_context_sync.py comparing template sources against `.github/context/`.

**Checkpoint**: Foundation ready—user story development may now proceed.

______________________________________________________________________

## Phase 3: User Story 1 – Baseline Render Works (Priority: P1) 🎯 MVP

**Goal**: Ship a default render that installs, lints, tests, and documents itself using the quickstart workflow.\
**Independent Test**: Render with default answers, execute quickstart commands (uv sync, pytest, ruff, mypy, pylint, notebook smoke), and confirm all pass without manual intervention.

### Tests for User Story 1

- [x] T012 [P] [US1] Add baseline quickstart smoke test template/files/python/tests/test_quickstart.py.jinja.

### Implementation for User Story 1

- [x] T013 [P] [US1] Populate uv-managed dependencies (uv, pytest, jupyter, nbclient, ruff, mypy, pylint, tenacity, pydantic, pydantic-settings, loguru) in template/files/python/pyproject.toml.jinja.
- [x] T014 [P] [US1] Scaffold package entrypoint in template/files/python/src/{{ package_name }}/__init__.py.jinja.
- [x] T015 [P] [US1] Implement quickstart runner in template/files/python/src/{{ package_name }}/quickstart.py.jinja executing smoke commands.
- [x] T016 [P] [US1] Add typed configuration module using pydantic-settings in template/files/python/src/{{ package_name }}/config.py.jinja.
- [x] T017 [P] [US1] Provide structured logging utilities with loguru in template/files/python/src/{{ package_name }}/logging.py.jinja.
- [x] T018 [US1] Draft docs/quickstart.md.jinja detailing baseline render workflow and notebook usage.
- [x] T019 [US1] Extend template/hooks/post_gen_project.py to emit post-render quickstart guidance without triggering network-dependent commands.
- [x] T020 [US1] Create baseline quickstart automation script scripts/ci/run_baseline_quickstart.py logging durations and capturing success metrics.
- [x] T021 [US1] Capture default prompt selections in samples/default/copier-answers.yml.
- [x] T022 [US1] Update scripts/render-samples.sh to call scripts/ci/run_baseline_quickstart.py, persist timing evidence, and render samples/default/.

**Checkpoint**: Baseline render validated; MVP ready to demo independently.

______________________________________________________________________

## Phase 4: User Story 2 – Optional Modules Compose (Priority: P2)

**Goal**: Allow any combination of CLI, FastAPI, Fastify, FastMCP, docs site, and shared logic modules to interoperate without conflicts.\
**Independent Test**: Script renders toggling each module solo and in combined scenarios, run module-specific smoke commands (CLI invocation, FastAPI/Fastify tests, MCP tool validation, docs preview), and ensure all succeed.

### Tests for User Story 2

- [x] T023 [P] [US2] Create Typer CLI smoke test template/files/python/tests/test_cli.py.jinja gated by cli_module prompt.
- [x] T024 [P] [US2] Create FastAPI smoke test template/files/python/tests/test_api_fastapi.py.jinja gated by api_tracks selection.
- [x] T025 [P] [US2] Create Fastify smoke test template/files/node/apps/api-node/tests/test_api_fastify.spec.ts.jinja gated by api_tracks selection.

### Implementation for User Story 2

- [x] T026 [P] [US2] Populate module catalog entries in template/files/shared/module_catalog.json.jinja for CLI, api_python, api_node, mcp_module, docs_site, and shared_logic.
- [x] T027 [P] [US2] Implement Typer CLI entrypoint in template/files/python/src/{{ package_name }}/cli/__main__.py.jinja invoking shared logic and logging utilities.
- [x] T028 [P] [US2] Document CLI usage in docs/modules/cli.md.jinja with configuration and validation commands.
- [x] T029 [P] [US2] Document FastAPI runbook in docs/modules/api-python.md.jinja covering setup, smoke tests, and CI expectations.
- [x] T030 [P] [US2] Document Fastify runbook in docs/modules/api-node.md.jinja covering setup, smoke tests, and CI expectations.
- [x] T031 [P] [US2] Build FastAPI service skeleton in template/files/python/src/{{ package_name }}/api/main.py.jinja with tenacity-backed retry hooks.
- [x] T032 [P] [US2] Add FastAPI configuration models in template/files/python/src/{{ package_name }}/api/settings.py.jinja using pydantic-settings.
- [x] T033 [P] [US2] Build Fastify service skeleton in template/files/node/apps/api-node/src/main.ts.jinja with shared logic wiring.
- [x] T034 [P] [US2] Provide Fastify configuration helper in template/files/node/apps/api-node/src/config.ts.jinja.
- [x] T035 [P] [US2] Create shared logic package in template/files/shared/logic/__init__.py.jinja consumable by CLI and APIs.
- [x] T036 [P] [US2] Add FastMCP tooling scaffold in template/files/shared/mcp/tooling.py.jinja with sample tools and contracts.
- [x] T037 [P] [US2] Configure Fumadocs site defaults in template/files/node/docs/fumadocs.config.ts.jinja.
- [x] T038 [US2] Record CLI + docs sample prompts in samples/cli-docs/copier-answers.yml.
- [x] T039 [US2] Record full-stack sample prompts in samples/full-stack/copier-answers.yml.
- [x] T040 [US2] Extend scripts/render-samples.sh and scripts/ci/render_matrix.py to execute all module smoke tests and log individual permutation outcomes.

**Checkpoint**: Optional modules compose cleanly with deterministic renders for documented variants.

______________________________________________________________________

## Phase 5: User Story 3 – Multi-Layout Support (Priority: P3)

**Goal**: Offer single-package and monorepo layouts without rework for downstream teams.\
**Independent Test**: Render in single-package and monorepo modes, run layout-specific bootstrap scripts (uv sync, pnpm install), and confirm automation + docs adjust for each selection.

### Implementation for User Story 3

- [x] T041 [P] [US3] Implement project layout prompt logic in template/prompts/project_layout.yml.jinja.
- [x] T042 [P] [US3] Define single-package blueprint in template/files/shared/layouts/single_package.yml.jinja.
- [x] T043 [P] [US3] Define monorepo blueprint in template/files/shared/layouts/monorepo.yml.jinja covering apps/ and packages/.
- [x] T044 [US3] Update template/hooks/post_gen_project.py to invoke layout bootstrap routines for uv and pnpm workflows.
- [x] T045 [US3] Scaffold pnpm workspace template in template/files/node/pnpm-workspace.yaml.jinja.
- [x] T046 [US3] Capture monorepo sample prompts in samples/api-monorepo/copier-answers.yml.

**Checkpoint**: Layout choices toggle cleanly with aligned tooling and documentation.

______________________________________________________________________

## Phase 6: User Story 4 – Governance Automation Protects Releases (Priority: P4)

**Goal**: Ensure automated checks enforce constitutional compliance for every template change.\
**Independent Test**: Trigger CI on a template modification; verify render matrix, docs build, compliance checkpoints, baseline timing metrics, and module success-rate checks block merges until samples and docs refresh.

### Implementation for User Story 4

- [x] T047 [P] [US4] Implement governance compliance script scripts/compliance/checkpoints.py posting to /templates/riso/compliance-checks.
- [x] T048 [P] [US4] Implement automation API client scripts/automation/render_client.py covering render and module catalog endpoints.
- [x] T049 [P] [US4] Implement module success recorder script scripts/ci/record_module_success.py capturing pass/fail counts for each permutation.
- [x] T050 [P] [US4] Update scripts/ci/render_matrix.py to stream permutation results into scripts/ci/record_module_success.py and persist nightly metrics.
- [x] T051 [P] [US4] Update .github/workflows/template-ci.yml to enforce baseline timing, ≥98% optional-module success-rate thresholds, and documentation publish SLA checks with artifact uploads.
- [x] T052 [P] [US4] Implement documentation publish tracker script scripts/ci/track_doc_publish.py logging build timestamps and SLA status.
- [x] T053 [US4] Extend scripts/render-samples.sh to emit samples/\*\*/metadata.json, baseline timing summaries, module success logs, and documentation publish timestamps.
- [x] T054 [US4] Document governance monitoring (timing, success rate, documentation SLA) in docs/modules/governance.md.jinja with remediation guidance.

**Checkpoint**: Governance automation enforces template sovereignty, deterministic generation, and documentation parity.

______________________________________________________________________

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Align documentation, upgrade guidance, SLA tracking, and release validation across all stories.

- [x] T055 [P] Refresh docs/upgrade-guide.md.jinja with module enablement, `.github/context/` syncing steps, SLA expectations, and layout migration guidance.
- [x] T056 [P] Update docs/modules/prompt-reference.md.jinja with defaults, compatibility matrix, validation commands, and context sync notes.
- [x] T057 [P] Add docs/modules/sample-matrix.md.jinja summarizing samples/default/, samples/cli-docs/, samples/api-monorepo/, and samples/full-stack/.
- [x] T058 Execute scripts/render-samples.sh, scripts/ci/run_baseline_quickstart.py, scripts/ci/verify_context_sync.py, scripts/ci/record_module_success.py, scripts/ci/track_doc_publish.py, and scripts/compliance/checkpoints.py, recording outputs in samples/README.md for release readiness.

______________________________________________________________________

## Dependencies & Execution Order

- **Phase Order**: Setup → Foundational → US1 → US2 → US3 → US4 → Polish. Each phase depends on completion of its predecessor.
- **Story Independence**: US1 delivers the MVP baseline; US2, US3, and US4 rely on foundational work and build atop US1 artifacts but remain independently testable after their prerequisites finish.
- **Shared Files**: template/hooks/post_gen_project.py, scripts/render-samples.sh, scripts/ci/render_matrix.py, scripts/ci/run_baseline_quickstart.py, scripts/ci/verify_context_sync.py, scripts/ci/record_module_success.py, and scripts/ci/track_doc_publish.py evolve across phases—apply changes sequentially to avoid conflicts.
- **Automation Flow**: scripts/ci/render_matrix.py feeds compliance scripts, baseline timing checks, success-rate recording, and documentation SLA tracking; update it before wiring governance tasks.

______________________________________________________________________

## Parallel Execution Examples

- **US1 (P1)**: T013–T017 can proceed in parallel across separate modules before sequencing T018–T022.
- **US2 (P2)**: Develop code scaffolds T026–T037 simultaneously while another contributor records sample prompts T038–T039 and extends automation T040.
- **US3 (P3)**: T041–T043 can be divided among engineers, with T044–T046 following once blueprints are ready.
- **US4 (P4)**: Build compliance tooling T047–T050 concurrently, then update CI workflow T051 before finalizing evidence tasks T052–T053.

______________________________________________________________________

## Implementation Strategy

- **MVP First**: Complete Phases 1–2, deliver US1 (T012–T022), and validate the baseline quickstart with recorded timing evidence to establish a releasable MVP.
- **Incremental Delivery**: Add US2 to unlock optional modules, then US3 for layout flexibility, and US4 for governance automation—validating renders, success metrics, and documentation after each phase.
- **Parallel Teams**: After foundational work, assign engineers per story using the parallel examples while coordinating shared automation files.
- **Validation Cadence**: After each story, run scripts/render-samples.sh, scripts/ci/run_baseline_quickstart.py, scripts/ci/verify_context_sync.py, scripts/ci/record_module_success.py, scripts/ci/track_doc_publish.py, and scripts/compliance/checkpoints.py to capture deterministic evidence before progressing.
