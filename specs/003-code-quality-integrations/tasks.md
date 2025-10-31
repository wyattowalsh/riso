# Tasks: Code Quality Integration Suite

**Input**: Design documents from `/specs/003-code-quality-integrations/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Create `ruff.toml` in `template/files/python/`
- [X] T002 [P] Create `mypy.ini` in `template/files/python/`
- [X] T003 [P] Create `.pylintrc` in `template/files/python/`
- [X] T004 Create `Makefile` in `template/files/` with a placeholder `quality` target
- [X] T005 Create `pyproject.toml` in `template/files/` with a placeholder `[tool.uv.tasks.quality]` definition

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T006 Implement pre-generation hook in `template/hooks/pre_gen_project.py` to verify quality tooling
- [X] T007 Implement post-generation hook in `template/hooks/post_gen_project.py` to verify quality tooling
- [X] T008 Create `run_quality_suite.py` script in `scripts/ci/`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Unified Quality Gate for Baseline Render (Priority: P1) 🎯 MVP

**Goal**: A template maintainer can run a single quality command that executes all quality checks.

**Independent Test**: Render `samples/default/`, run `make quality`, and confirm all checks pass and update `smoke-results.json`.

### Implementation for User Story 1

- [X] T009 [US1] Implement the `quality` target in `template/files/Makefile` to run Ruff, Mypy, Pylint, and pytest
- [X] T010 [US1] Implement the `quality` task in `template/files/pyproject.toml` to run Ruff, Mypy, Pylint, and pytest
- [X] T011 [US1] Create a smoke test in `template/files/python/tests/smoke_test.py`
- [X] T012 [US1] Update `scripts/ci/run_baseline_quickstart.py` to log durations in `baseline_quickstart_metrics.json`
- [X] T013 [US1] Update `scripts/render-samples.sh` to update `smoke-results.json` with pass/fail status

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - CI Automation Blocks Template Regressions (Priority: P2)

**Goal**: CI automatically runs the quality suite and blocks merge on failure.

**Independent Test**: Open a PR with a linting error and verify that the CI job fails.

### Implementation for User Story 2

- [X] T014 [US2] Create a GitHub Actions workflow in `.github/workflows/quality.yml` to run the quality suite on pull requests
- [X] T015 [US2] Configure the workflow to use the `run_quality_suite.py` script
- [X] T016 [US2] Configure the workflow to run jobs in parallel for different Python versions and quality profiles
- [X] T017 [US2] Update `scripts/render_matrix.py` to update `samples/metadata/module_success.json` with pass/fail status per variant

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Downstream Teams Extend Quality Controls (Priority: P3)

**Goal**: Downstream teams can customize the quality suite.

**Independent Test**: Render the `full-stack` sample with `quality_profile=strict` and confirm both Python and Node quality jobs execute.

### Implementation for User Story 3

- [X] T018 [US3] Implement the `quality_profile` prompt in `copier.yml`
- [X] T019 [US3] Implement logic in the template to toggle ESLint/TypeScript checks based on the `api_tracks` prompt
- [X] T020 [US3] Create a `full-stack` sample in `samples/full-stack/` with `quality_profile=strict`

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T021 [P] Create documentation in `docs/modules/quality.md.jinja`
- [X] T022 [P] Create a test script in `tests/automation/sync_test.py` that runs both `make quality` and `uv run task quality` and compares their output for consistency.
- [X] T023 [P] Integrate the sync test script into the CI workflow in `.github/workflows/quality.yml`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- All Setup tasks can run in parallel.
- Once Foundational phase completes, all user stories can start in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 → Test independently
3. Add User Story 2 → Test independently
4. Add User Story 3 → Test independently