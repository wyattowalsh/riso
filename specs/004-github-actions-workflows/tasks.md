# Tasks: GitHub Actions CI/CD Workflows

**Input**: Design documents from `/specs/004-github-actions-workflows/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Only automated validation checks explicitly called out in requirements (actionlint validation, workflow generation smoke tests).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This feature uses template composition pattern. Workflow files are Jinja2 templates in `template/files/shared/.github/workflows/` that render into downstream projects.

______________________________________________________________________

## Implementation Status Summary

**Date**: 2025-11-01\
**Overall Progress**: Feature complete - 81/81 tasks (100%)

### Completed Work:

- ✅ Phases 1-4: Foundational infrastructure, quality workflow, and matrix testing (T001-T037)
- ✅ Phase 5: Dependency caching with hit/miss logging and metrics (T038-T047)
- ✅ Phase 6: Artifact retention tracking (T048-T055)
- ✅ Phase 7: Node.js CI integration implementation (T056-T068)
- ✅ Phase 8: Governance, validation, documentation, and optional enhancements (T069-T081)

### Core Deliverables:

✅ Two production-ready workflow templates (riso-quality.yml, riso-matrix.yml)
✅ Optional dependency update workflow (riso-deps-update.yml)
✅ Zero actionlint errors across all rendered samples
✅ Complete caching strategy with 70%+ hit rate target
✅ 90-day artifact retention compliance
✅ Matrix testing across Python 3.11/3.12/3.13
✅ Comprehensive documentation (workflows.md, quickstart.md, upgrade-guide.md)
✅ Branch protection setup instructions
✅ Free tier optimization strategies
✅ Context file for workflow extension patterns
✅ AGENTS.md updated with CI patterns and required checks
✅ Module catalog includes workflow generation entry

______________________________________________________________________

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create workflow scaffolding and validation infrastructure.

- [x] T001 Create workflow template directory at `template/files/shared/.github/workflows/`
- [x] T002 [P] Create workflow validation helper script at `scripts/ci/validate_workflows.py`
- [x] T003 [P] Create actionlint wrapper for hooks at `scripts/hooks/workflow_validator.py`
- [x] T004 [P] Add `ci_platform` prompt definition to `template/prompts/ci_platform.yml.jinja`

______________________________________________________________________

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement workflow generation and validation hooks that all user stories depend on.

**⚠️ CRITICAL**: No workflow templates can be generated until validation infrastructure is ready.

- [x] T005 Implement actionlint availability check in `template/hooks/pre_gen_project.py`
- [x] T006 Implement workflow validation logic in `template/hooks/post_gen_project.py` calling `scripts/hooks/workflow_validator.py`
- [x] T007 [P] Update `scripts/ci/render_matrix.py` to track workflow generation status in `samples/metadata/render_matrix.json`
- [x] T008 [P] Update `samples/metadata/module_success.json` schema to include workflow generation metrics

**Checkpoint**: Validation infrastructure ready - workflow template implementation can now begin.

______________________________________________________________________

## Phase 3: User Story 1 - Automated Quality Validation on PR (Priority: P1) 🎯 MVP

**Goal**: Ship a `riso-quality.yml` workflow that automatically runs quality suite (ruff, mypy, pylint, pytest) on PRs with retry logic and artifact uploads.

**Independent Test**: Render default sample, trigger workflow in test repository, verify quality checks execute and artifacts upload with 90-day retention.

### Implementation Tasks

- [x] T009 [P] [US1] Create main quality workflow template at `template/files/shared/.github/workflows/riso-quality.yml.jinja`
- [x] T010 [P] [US1] Implement Python quality job with uv setup, cache restoration, and quality command execution in `riso-quality.yml.jinja`
- [x] T011 [P] [US1] Add retry logic using `nick-fields/retry@v3` action with 3 attempts and exponential backoff in `riso-quality.yml.jinja`
- [x] T012 [P] [US1] Implement conditional CLI module tests step (when `cli_module='enabled'`) in `riso-quality.yml.jinja`
- [x] T013 [P] [US1] Implement conditional MCP module tests step (when `mcp_module='enabled'`) in `riso-quality.yml.jinja`
- [x] T014 [US1] Add test results artifact upload with 90-day retention in `riso-quality.yml.jinja`
- [x] T015 [US1] Add quality logs artifact upload with 90-day retention in `riso-quality.yml.jinja`
- [x] T016 [US1] Implement quality profile timeout logic (10 min standard, 20 min strict) in `riso-quality.yml.jinja`
- [x] T017 [US1] Add clear error messaging for workflow failures with remediation hints in `riso-quality.yml.jinja`
- [x] T018 [P] [US1] Update `samples/default/copier-answers.yml` to include `ci_platform='github-actions'`
- [x] T019 [P] [US1] Render default sample and validate `riso-quality.yml` generates successfully
- [x] T020 [US1] Run actionlint on rendered `samples/default/render/.github/workflows/riso-quality.yml`
- [x] T021 [US1] Update `samples/default/smoke-results.json` with workflow generation status
- [x] T022 [P] [US1] Update `docs/quickstart.md.jinja` with CI status viewing instructions
- [x] T023 [P] [US1] Create workflow module documentation at `docs/modules/workflows.md.jinja`

**Checkpoint**: Main quality workflow functional - developers can see automated PR checks running.

______________________________________________________________________

## Phase 4: User Story 2 - Matrix Testing Across Python Versions (Priority: P2)

**Goal**: Ship a `riso-matrix.yml` workflow that tests code across Python 3.11, 3.12, 3.13 in parallel with all jobs required to pass.

**Independent Test**: Render project with matrix enabled, introduce Python 3.13-specific code, verify only 3.13 job fails and overall status blocks merge.

### Implementation Tasks

- [x] T024 [P] [US2] Create matrix testing workflow template at `template/files/shared/.github/workflows/riso-matrix.yml.jinja`
- [x] T025 [US2] Implement matrix strategy with Python 3.11, 3.12, 3.13 and `fail-fast: false` in `riso-matrix.yml.jinja`
- [x] T026 [US2] Add per-version cache keys with OS and Python version prefix in `riso-matrix.yml.jinja`
- [x] T027 [US2] Implement quality checks (pytest, mypy, ruff) for each matrix job in `riso-matrix.yml.jinja`
- [x] T028 [US2] Add retry logic for each matrix job independently in `riso-matrix.yml.jinja`
- [x] T029 [US2] Implement matrix summary job that depends on all matrix jobs in `riso-matrix.yml.jinja`
- [x] T030 [US2] Add per-version artifact uploads with structured naming in `riso-matrix.yml.jinja`
- [x] T031 [US2] Add failure reporting that shows which Python versions failed in `riso-matrix.yml.jinja`
- [x] T032 [US2] Set 15-minute timeout for matrix jobs in `riso-matrix.yml.jinja`
- [x] T033 [P] [US2] Render default sample and validate `riso-matrix.yml` generates successfully
- [x] T034 [US2] Run actionlint on rendered `samples/default/render/.github/workflows/riso-matrix.yml`
- [x] T035 [US2] Update `samples/default/smoke-results.json` with matrix workflow status
- [x] T036 [P] [US2] Add matrix build documentation to `docs/modules/workflows.md.jinja`
- [x] T037 [P] [US2] Update `docs/quickstart.md.jinja` with matrix failure debugging instructions

**Checkpoint**: Matrix testing functional - version-specific issues detected before merge.

______________________________________________________________________

## Phase 5: User Story 3 - Dependency Caching for Fast Builds (Priority: P2)

**Goal**: Implement cache configuration using lock file hashes with OS/Python version prefix to achieve 70%+ cache hit rate and 50%+ install time reduction.

**Independent Test**: Run CI twice with identical dependencies, verify second run completes significantly faster (3 minutes vs 6 minutes) due to cache hit.

### Implementation Tasks

- [x] T038 [P] [US3] Implement Python dependency caching in `riso-quality.yml.jinja` using `actions/cache@v4`
- [x] T039 [P] [US3] Implement cache key generation with `runner.os`, Python version, and `hashFiles('**/uv.lock')` in `riso-quality.yml.jinja`
- [x] T040 [P] [US3] Add restore keys fallback for partial cache hits in `riso-quality.yml.jinja`
- [x] T041 [P] [US3] Implement pnpm dependency caching in `riso-quality.yml.jinja` (conditional on Node track)
- [x] T042 [P] [US3] Implement cache key generation with `hashFiles('**/pnpm-lock.yaml')` in `riso-quality.yml.jinja`
- [x] T043 [P] [US3] Add cache configuration to matrix workflow in `riso-matrix.yml.jinja`
- [x] T044 [P] [US3] Add cache hit/miss logging for debugging in workflow templates
- [x] T045 [P] [US3] Update `samples/default/baseline_quickstart_metrics.json` with cache performance targets
- [x] T046 [P] [US3] Document cache debugging procedures in `docs/quickstart.md.jinja`
- [x] T047 [P] [US3] Add cache hit rate tracking to `samples/metadata/module_success.json`

**Checkpoint**: Caching functional - CI runtime reduced from 6 minutes to 3 minutes on cache hits.

______________________________________________________________________

## Phase 6: User Story 4 - Artifact Collection and Retention (Priority: P3)

**Goal**: Upload test results, coverage reports, and quality logs as artifacts with 90-day retention for debugging and compliance auditing.

**Independent Test**: Trigger workflow, navigate to GitHub Actions artifacts section, verify downloadable artifacts exist with 90-day retention metadata.

### Implementation Tasks

- [x] T048 [P] [US4] Verify test results artifact upload in `riso-quality.yml.jinja` includes JUnit XML and coverage HTML
- [x] T049 [P] [US4] Verify quality logs artifact upload in `riso-quality.yml.jinja` includes ruff, mypy, pylint output
- [x] T050 [P] [US4] Ensure all artifact uploads use `retention-days: 90` in `riso-quality.yml.jinja`
- [x] T051 [P] [US4] Implement structured artifact naming with Python version and run ID in `riso-quality.yml.jinja`
- [x] T052 [P] [US4] Add `if: always()` to artifact uploads so they run even on failure in `riso-quality.yml.jinja`
- [x] T053 [P] [US4] Verify matrix workflow uploads per-version artifacts in `riso-matrix.yml.jinja`
- [x] T054 [P] [US4] Add artifact download instructions to `docs/quickstart.md.jinja`
- [x] T055 [P] [US4] Add artifact retention tracking to `samples/metadata/module_success.json`

**Checkpoint**: Artifacts available for 90 days - debugging and compliance requirements met.

______________________________________________________________________

## Phase 7: User Story 5 - Optional Node.js Track CI Integration (Priority: P3)

**Goal**: Add Node.js linting, type checking, and testing jobs that run in parallel with Python when `api_tracks` includes `node`.

**Independent Test**: Render full-stack sample with `api_tracks=['python', 'node']`, verify both Python and Node jobs appear and execute in parallel with independent status.

### Implementation Tasks

- [x] T056 [P] [US5] Add conditional Node.js quality job to `riso-quality.yml.jinja` (when `'node' in api_tracks`)
- [x] T057 [US5] Implement Node.js environment setup with Node 20 and corepack in `riso-quality.yml.jinja`
- [x] T058 [US5] Add pnpm dependency installation with frozen lockfile in `riso-quality.yml.jinja`
- [x] T059 [US5] Implement ESLint execution step in `riso-quality.yml.jinja`
- [x] T060 [US5] Implement TypeScript type checking step in `riso-quality.yml.jinja`
- [x] T061 [US5] Implement Vitest test execution step in `riso-quality.yml.jinja`
- [x] T062 [US5] Add Node.js test results artifact upload with 90-day retention in `riso-quality.yml.jinja`
- [x] T063 [US5] Set independent timeout for Node.js job (10 min standard, 20 min strict) in `riso-quality.yml.jinja`
- [x] T064 [P] [US5] Update `samples/full-stack/copier-answers.yml` to include `api_tracks=['python', 'node']`
- [x] T065 [P] [US5] Render full-stack sample and validate Node.js job generates in `riso-quality.yml`
- [x] T066 [US5] Run actionlint on rendered `samples/full-stack/render/.github/workflows/riso-quality.yml`
- [x] T067 [US5] Update `samples/full-stack/smoke-results.json` with Node.js CI status
- [x] T068 [P] [US5] Add Node.js track documentation to `docs/modules/workflows.md.jinja`

**Checkpoint**: Node.js projects receive same CI guarantees as Python - full-stack automation complete.

______________________________________________________________________

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finalize governance, documentation, and validation scripts.

- [x] T069 [P] Update `/Users/ww/dev/projects/riso/AGENTS.md` with GitHub Actions workflow patterns and required checks
- [x] T070 [P] Update `template/docs/upgrade-guide.md.jinja` with workflow migration instructions for copier updates
- [x] T071 [P] Create or update `.github/context/workflows.md` with workflow extension patterns
- [x] T072 Run context sync script `python scripts/ci/verify_context_sync.py` and commit any updates
- [x] T073 [P] Add optional dependency update workflow template at `template/files/shared/.github/workflows/riso-deps-update.yml.jinja` (FR-014)
- [x] T074 [P] Document environment variable customization options in `template/docs/modules/workflows.md.jinja`
- [x] T075 [P] Add branch protection setup instructions to `template/docs/quickstart.md.jinja`
- [x] T076 [P] Update `template/files/shared/module_catalog.json.jinja` with workflow module entry
- [x] T077 Validate all rendered workflows with actionlint across all samples in `samples/*/render/.github/workflows/`
- [x] T078 Run baseline quickstart validation `python scripts/ci/run_baseline_quickstart.py`
- [x] T079 Update `samples/metadata/module_success.json` with final workflow generation metrics
- [x] T080 Generate final smoke test report consolidating all workflow validation results
- [x] T081 [P] Document GitHub Actions free tier optimization strategies in `template/docs/modules/workflows.md.jinja` (fork limitations, aggressive caching, timeout tuning)

______________________________________________________________________

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)** → No dependencies - can start immediately
1. **Foundational (Phase 2)** → Depends on Setup (Phase 1) - **BLOCKS all user stories**
1. **User Story 1 (Phase 3)** → Depends on Foundational (Phase 2) - MVP baseline
1. **User Story 2 (Phase 4)** → Depends on Foundational (Phase 2) - Can run parallel with US1
1. **User Story 3 (Phase 5)** → Depends on US1 and US2 (modifies their workflows) - Must complete US1/US2 first
1. **User Story 4 (Phase 6)** → Depends on US1 (enhances artifact strategy) - Can integrate during US1 or after
1. **User Story 5 (Phase 7)** → Depends on Foundational (Phase 2) - Can run parallel with US1/US2
1. **Polish (Phase 8)** → Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies on other stories - MVP starting point
- **US2 (P2)**: Independent of US1 - can develop in parallel
- **US3 (P2)**: Enhances US1 and US2 workflows - must complete those first to add caching
- **US4 (P3)**: Enhances US1 artifacts - can integrate during US1 implementation
- **US5 (P3)**: Independent workflow job - can develop in parallel with US1/US2

### Within Each User Story

- Workflow template creation before validation
- Template validation before sample rendering
- Sample rendering before smoke test updates
- Documentation can proceed in parallel with implementation

### Parallel Opportunities

**Setup Phase**: T002, T003, T004 can run in parallel

**Foundational Phase**: T007, T008 can run in parallel after T005, T006 complete

**User Story 1**: After T009 completes, T010-T013, T018, T022-T023 can run in parallel. T014-T017 and T019-T021 follow sequentially.

**User Story 2**: After T024 completes, T033, T036-T037 can run in parallel. Matrix implementation T025-T032 must be sequential.

**User Story 3**: T038-T042 (caching implementation) can all run in parallel. T043-T047 (documentation and metrics) can run in parallel.

**User Story 4**: All artifact enhancement tasks T048-T055 can run in parallel.

**User Story 5**: After T056 completes, T064-T065, T068 can run in parallel. Node.js implementation T057-T063 and validation T066-T067 follow sequentially.

**Polish Phase**: T069-T071, T073-T076 can all run in parallel. T077-T080 must run sequentially at the end.

______________________________________________________________________

## Parallel Execution Examples

### User Story 1 (Main Quality Workflow)

```bash
# After foundational phase completes, launch in parallel:
Contributor A: T009-T011 (Create main quality workflow template)
Contributor B: T012-T013 (Add conditional module tests)
Contributor C: T022-T023 (Documentation updates)

# Then sequentially:
Contributor A: T014-T017 (Artifact uploads and error handling)
Contributor A: T019-T021 (Validation and smoke tests)
```

### User Story 2 (Matrix Testing)

```bash
# After T024 completes:
Contributor A: T025-T032 (Matrix implementation - sequential)
Contributor B: T036-T037 (Documentation - parallel)

# Final validation:
Contributor A: T033-T035 (Render and validate)
```

### User Story 3 (Caching)

```bash
# All caching implementation in parallel:
Contributor A: T038-T040 (Python caching)
Contributor B: T041-T042 (Node.js caching)
Contributor C: T043-T044 (Matrix caching)
Contributor D: T045-T047 (Documentation and metrics)
```

### Multiple Stories in Parallel (Team Strategy)

```bash
# After Foundational phase completes:
Team Alpha: User Story 1 (T009-T023) - MVP workflow
Team Beta: User Story 2 (T024-T037) - Matrix testing
Team Gamma: User Story 5 (T056-T068) - Node.js track

# Then:
Team Alpha: User Story 3 (T038-T047) - Add caching to existing workflows
Team Beta: User Story 4 (T048-T055) - Enhance artifact strategy
```

______________________________________________________________________

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004) - ~2 hours
1. Complete Phase 2: Foundational (T005-T008) - ~3 hours ⚠️ CRITICAL BLOCKER
1. Complete Phase 3: User Story 1 (T009-T023) - ~6 hours
1. **STOP and VALIDATE**:
   - Render default sample
   - Run actionlint validation
   - Trigger workflow in test repository
   - Verify quality checks run and artifacts upload
   - Check smoke-results.json for passing status
1. **MVP COMPLETE** - Developers can now see automated PR checks

**Total MVP Time**: ~11 hours

### Incremental Delivery (Recommended)

1. **Foundation** (Phases 1-2): Setup + Foundational → ~5 hours
1. **MVP** (Phase 3): User Story 1 → Test → Deploy → ~6 hours
1. **Matrix** (Phase 4): User Story 2 → Test → Deploy → ~4 hours
1. **Caching** (Phase 5): User Story 3 → Test → Deploy → ~3 hours
1. **Artifacts** (Phase 6): User Story 4 → Test → Deploy → ~2 hours
1. **Node.js** (Phase 7): User Story 5 → Test → Deploy → ~4 hours
1. **Polish** (Phase 8): Documentation and governance → ~2 hours

**Total Feature Time**: ~26 hours

### Parallel Team Strategy (3 developers)

**Day 1** (All together):

- Setup + Foundational (Phases 1-2) → 5 hours
- User Story 1 implementation (Phase 3) → 6 hours

**Day 2** (Parallel streams):

- Developer A: User Story 2 (Phase 4) → 4 hours
- Developer B: User Story 5 (Phase 7) → 4 hours
- Developer C: Start User Story 3 planning

**Day 3** (Sequential completion):

- Developer A: User Story 3 (Phase 5) → 3 hours (needs US1/US2 complete)
- Developer B: User Story 4 (Phase 6) → 2 hours
- Developer C: Polish (Phase 8) → 2 hours

**Total Parallel Time**: ~2.5 days vs 3.25 days sequential

______________________________________________________________________

## Validation Checkpoints

### After Setup (Phase 1)

- [ ] Workflow directory structure exists
- [ ] Validation scripts are executable
- [ ] Prompt definitions render correctly

### After Foundational (Phase 2)

- [ ] Pre-generation hook detects actionlint
- [ ] Post-generation hook validates workflow YAML
- [ ] Render matrix tracks workflow generation
- [ ] Module success schema includes workflow metrics

### After User Story 1 (MVP)

- [ ] `riso-quality.yml` generates in default sample
- [ ] actionlint reports zero errors
- [ ] Workflow includes retry logic
- [ ] Artifacts upload with 90-day retention
- [ ] Smoke results show workflow validation pass
- [ ] Documentation explains CI status viewing

### After User Story 2 (Matrix)

- [ ] `riso-matrix.yml` generates with 3 Python versions
- [ ] fail-fast is disabled
- [ ] Matrix summary job depends on all matrix jobs
- [ ] Per-version artifacts upload correctly
- [ ] Smoke results show matrix workflow pass

### After User Story 3 (Caching)

- [ ] Cache keys include lock file hashes
- [ ] Cache restoration logs show hit/miss status
- [ ] Second CI run shows \<3 minute duration
- [ ] Cache hit rate tracking shows ≥70%

### After User Story 4 (Artifacts)

- [ ] All artifacts have 90-day retention
- [ ] Artifacts upload even on workflow failure
- [ ] Artifact naming includes version and run ID
- [ ] Artifact metadata tracked in module success

### After User Story 5 (Node.js)

- [ ] Node.js job appears in full-stack sample
- [ ] Python and Node jobs run in parallel
- [ ] Node job skipped when api_tracks excludes 'node'
- [ ] Full-stack smoke results show both tracks

### After Polish (Final)

- [ ] All context files synchronized
- [ ] Upgrade guide includes workflow migration
- [ ] AGENTS.md documents required checks
- [ ] All samples validate successfully
- [ ] Module catalog includes workflow entry

______________________________________________________________________

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] labels**: Map tasks to specific user stories for traceability
- **Constitution compliance**: All workflows use `uv run` commands, 90-day retention, distinctive naming
- **Independent testing**: Each user story should be testable without others
- **Validation gates**: actionlint must pass before sample render is considered successful
- **Smoke tests**: Update after each story phase to track workflow generation health
- **Artifact strategy**: Implemented in US1, enhanced in US4 - can be done together if preferred
- **Caching strategy**: Must come after US1/US2 since it modifies their workflow templates

**Tasks Generated**: 81 tasks across 8 phases
**MVP Scope**: Phases 1-3 (T001-T023) = 23 tasks
**Parallel Opportunities**: 35 tasks marked [P] for parallel execution
**Estimated Completion Time**: 11 hours (MVP), 27 hours (full feature)
