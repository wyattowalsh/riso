# Tasks: Code Quality Integration Suite

**Input**: Design documents from `/.specify/specs/003-code-quality-integrations/` (legacy symlink available at `specs/003-code-quality-integrations/`)
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Only add new or updated automated checks where explicitly called out below.

**Organization**: Tasks are grouped by user story so each increment can ship independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task can be executed in parallel because it touches independent files and has no unmet dependencies.
- **[Story]**: Maps the task to its user story (US1, US2, US3). Setup, Foundational, and Polish tasks omit the story label.
- Include exact file paths in every description.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared directories so quality assets have a home before implementation work begins.

- [X] T001 Create quality scaffolding root at `template/files/shared/quality/` with placeholder `.gitkeep` to anchor new configs.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Baseline automation updates that every user story depends on.

- [X] T002 Extend `scripts/render-samples.sh` to invoke the new quality command and capture per-tool durations in sample logs.
- [X] T003 Update `samples/metadata/module_success.json` and `scripts/ci/record_module_success.py` to reserve slots for quality results across variants.

**Checkpoint**: Sample regeneration now records quality placeholders—user stories may proceed.

---

## Phase 3: User Story 1 – Unified Quality Gate for Baseline Render (Priority: P1) 🎯 MVP

**Goal**: Ship a single `make quality` / `uv run task quality` command that lints, type-checks, tests, and records evidence for baseline renders.

**Independent Test**: Render `samples/default`, run `make quality`, and confirm Ruff/Mypy/Pylint/Pytest succeed with durations logged in `samples/default/smoke-results.json` and `baseline_quickstart_metrics.json`.

### Implementation Tasks

- [X] T004 [P] [US1] Add baseline Ruff configuration at `template/files/shared/quality/ruff.toml.jinja` with shared excludes and rule set.
- [X] T005 [P] [US1] Add `template/files/shared/quality/mypy.ini.jinja` aligning with `uv` interpreter discovery and strict optional toggles.
- [X] T006 [P] [US1] Add `template/files/shared/quality/pylintrc.jinja` capturing core checks and shared suppressions.
- [X] T007 [P] [US1] Add `template/files/shared/quality/coverage.cfg.jinja` to standardize coverage collection.
- [X] T008 [US1] Create `template/files/shared/quality/makefile.quality.jinja` defining the chained `quality` target and per-tool sub-commands.
- [X] T009 [US1] Create `template/files/shared/quality/uv_tasks/quality.py.jinja` so `uv run task quality` mirrors the Makefile workflow.
- [X] T010 [US1] Implement auto-install logic in `scripts/hooks/quality_tool_check.py` to attempt one `uv` pass for Ruff/Mypy/Pylint and log outcomes.
- [X] T011 [US1] Wire quality hook entry in `template/hooks/pre_gen_project.py` so renders invoke Python and Node auto-install retries.
- [X] T012 [US1] Record `tool_install_attempts` and quality evidence payload in `template/hooks/post_gen_project.py` metadata writer.
- [X] T013 [US1] Add automated parity check in `scripts/ci/check_quality_parity.py` ensuring `make quality` and `uv run task quality` stay in sync via CI regression tests.
- [X] T014 [P] [US1] Add quality runtime metrics to `samples/default/baseline_quickstart_metrics.json` aligning with new command durations.
- [X] T015 [P] [US1] Seed `samples/full-stack/baseline_quickstart_metrics.json` with strict-profile quality timings.
- [X] T016 [P] [US1] Append quality module results to `samples/default/smoke-results.json` including artifact URIs and retention timestamps.
- [X] T017 [P] [US1] Append quality module results to `samples/full-stack/smoke-results.json` with strict profile coverage.
- [X] T018 [P] [US1] Document unified quality workflow in `docs/quickstart.md.jinja` (local command, log locations, remediation flow).
- [X] T019 [US1] Author `docs/modules/quality.md.jinja` describing suite composition, evidence expectations, and troubleshooting steps.

**Checkpoint**: Maintainers can run the unified quality command locally with auto-healed tooling and updated documentation.

---

## Phase 4: User Story 2 – CI Automation Blocks Template Regressions (Priority: P2)

**Goal**: Parallelize quality checks in GitHub Actions, enforce required statuses, and retain artifacts for 90 days.

**Independent Test**: Trigger template CI, verify `quality-matrix` jobs run per tool/profile, fail fast on an injected lint error, and confirm artifacts upload with 90-day retention metadata.

### Implementation Tasks

- [X] T020 [US2] Create `template/files/shared/.github/workflows/quality-matrix.yml.jinja` with per-tool jobs, shared caches, and 90-day artifact retention.
- [X] T021 [US2] Update `template/files/shared/.github/workflows/template-ci.yml.jinja` to invoke the quality matrix workflow and mark jobs as required checks.
- [X] T022 [US2] Add orchestration helper `scripts/ci/run_quality_suite.py` to drive per-tool commands and summarize results for job outputs.
- [X] T023 [US2] Enhance `scripts/ci/render_matrix.py` to ingest quality artifacts, enforce retention windows, and write aggregated status blocks.
- [X] T024 [US2] Extend `samples/metadata/render_matrix.json` with quality job entries for baseline and full-stack variants.
- [X] T025 [US2] Extend `scripts/ci/record_module_success.py` (or companion helper) to ingest "quality tooling setup" support-ticket metrics into `samples/metadata/support_tickets.json` and surface SC-004 evidence in job summaries.

**Checkpoint**: CI now blocks merges when any quality lane fails and preserves evidence artifacts automatically.

---

## Phase 5: User Story 3 – Downstream Teams Extend Quality Controls (Priority: P3)

**Goal**: Expose a `quality_profile` prompt, respect Node module toggles, and keep documentation aligned so downstream projects can opt in to stricter suites.

**Independent Test**: Render the `full-stack` sample with `quality_profile=strict`, verify Node checks run when `api_tracks` includes `node`, and confirm skips with rationale when Node is disabled.

### Implementation Tasks

- [X] T026 [US3] Add `quality_profile` prompt defaults to `template/copier.yml` and `defaults` block (standard baseline, strict opt-in).
- [X] T027 [US3] Document new prompt in `template/prompts/options.yml.jinja` with guidance for standard vs strict.
- [X] T028 [US3] Update `template/files/shared/quality/makefile.quality.jinja` to branch on `quality_profile` and skip Node checks when `api_tracks` lacks Node.
- [X] T029 [US3] Update `scripts/hooks/quality_tool_check.py` to attempt `corepack pnpm install` only when Node tracks are enabled and log skip rationale.
- [X] T030 [US3] Add `quality_profile` field to `samples/default/copier-answers.yml` (standard) and `samples/full-stack/copier-answers.yml` (strict).
- [X] T031 [US3] Clarify strict vs standard usage and Node skips in `docs/modules/quality.md.jinja`.
- [X] T032 [US3] Register the quality suite in `template/files/shared/module_catalog.json.jinja` with docs path and validation commands.
- [X] T033 [US3] Ensure `samples/metadata/module_success.json` entries and tooling summaries reference strict/standard profiles accurately.

**Checkpoint**: Downstream teams can toggle strict profiles and Node coverage while keeping automation evidence in sync.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize governance trail and validation scripts.

- [X] T034 Refresh governance guidance in `AGENTS.md` to note the new quality automation and 90-day retention requirement.
- [X] T035 Run the context sync script `scripts/ci/verify_context_sync.py` and commit updated `.github/context/` snapshots if deltas appear.
- [X] T036 [P] Update `.github/context/quality.md` (template copy at `template/files/shared/.github/context/quality.md`) with the new quality suite details.
- [X] T037 [P] Update `docs/upgrade-guide.md.jinja` to describe enabling the unified quality suite and migrating to strict profiles.

---

## Dependencies & Execution Order

1. **Setup** → 2. **Foundational** → 3. **User Story 1 (P1)** → 4. **User Story 2 (P2)** → 5. **User Story 3 (P3)** → 6. **Polish**.
2. User Story phases may begin only after Foundational tasks complete. Stories 2 and 3 can run in parallel once Story 1’s artifacts and command scaffolding exist.
3. Within each story: configuration files precede hooks, hooks precede documentation updates, and metadata updates occur before CI integration.

### Story Dependency Graph

- **US1** → unlocks local quality command, required by US2 & US3.
- **US2** depends on US1’s configs/hook outputs to run in CI.
- **US3** depends on US1 for baseline command and on US2’s artifact schema for strict profile telemetry.

### Parallel Execution Examples

- After T004 completes, tasks T005–T007 may run in parallel.
- Once T014 executes, tasks T015–T017 can run concurrently across sample variants.
- With Foundational tasks finished, separate contributors can tackle US2 (CI workflow) and US3 (prompt + docs) in parallel while coordinating on shared files noted above.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundational phases (T001–T003).
2. Deliver User Story 1 (T004–T019) to establish the unified quality command and evidence logging.
3. Validate MVP by running `make quality` on `samples/default` and inspecting updated metrics.

### Incremental Delivery

1. Ship US1 (local quality automation) → release as MVP.
2. Ship US2 (CI enforcement) → ensures governance locking.
3. Ship US3 (strict profile + Node UX) → enables downstream customization.
4. Finish with Polish tasks for governance alignment.

### Parallel Team Strategy

- Dual-track after US1: one contributor hardens CI (US2) while another implements prompt and docs (US3).
- Use `[P]` flags to assign independent config/doc updates concurrently.
- Reconvene for Polish tasks to validate context sync and documentation completeness.
