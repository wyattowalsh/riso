# Tasks: Conventional Commit Tooling Integration

**Feature**: 016-conventional-commit-tooling  
**Input**: Design documents from `/specs/016-conventional-commit-tooling/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT explicitly requested in the specification, so this implementation follows a validation-first approach with smoke tests rather than full TDD (acceptable deviation from Constitution Principle V with documented justification).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Python Execution**: All Python commands MUST use `uv run` prefix per AGENTS.md convention (never bare `python` or `pytest`).

---

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and template structure for commit tooling module

- [ ] T001 Create template directory structure for commit tooling module in template/files/shared/
- [ ] T002 [P] Create Python package structure in template/files/python/{package_name}/commit_tooling/
- [ ] T003 [P] Create Node.js scripts structure in template/files/node/scripts/
- [ ] T004 [P] Add commit_tooling_module option to template/copier.yml with default=disabled
- [ ] T005 Create sample configuration files directory in samples/cli-docs/ for testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core validation and configuration infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create configuration schema in specs/016-conventional-commit-tooling/contracts/config-schema.yaml (already exists, validate completeness)
- [ ] T007 Implement Python configuration loader in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T008 Implement Python configuration validator with JSON Schema support in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T009 Create default .commitlintrc.yml template in template/files/shared/.commitlintrc.yml.jinja
- [ ] T010 Implement structured logging system in template/files/python/{package_name}/commit_tooling/logger.py.jinja
- [ ] T011 Create commit message parser in template/files/python/{package_name}/commit_tooling/parser.py.jinja
- [ ] T012 Implement base ValidationRule class in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T013 Implement ValidationRuleSet class in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T014 Create __init__.py with module exports in template/files/python/{package_name}/commit_tooling/__init__.py.jinja

**Checkpoint**: Foundation ready - validation infrastructure complete, user story implementation can now begin

---

## Phase 3: User Story 1 - Automated Commit Message Validation (Priority: P1) 🎯 MVP

**Goal**: Automatically validate commit messages against conventional commit format, rejecting invalid commits with helpful error messages

**Independent Test**: Make a commit with invalid message (e.g., "fixed bug") → verify rejection with error. Make valid commit (e.g., "fix: resolve login timeout") → verify success.

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement type-enum validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T016 [P] [US1] Implement subject-max-length validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T017 [P] [US1] Implement subject-empty validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T018 [P] [US1] Implement body-leading-blank validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T019 [P] [US1] Implement footer-leading-blank validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T020 [US1] Create CommitValidator class in template/files/python/{package_name}/commit_tooling/validator.py.jinja
- [ ] T021 [US1] Implement merge and revert commit detection (skip validation for "Merge" or "Revert" prefix) in template/files/python/{package_name}/commit_tooling/validator.py.jinja
- [ ] T022 [US1] Implement breaking change detection ("!" or "BREAKING CHANGE:") in template/files/python/{package_name}/commit_tooling/parser.py.jinja
- [ ] T023 [US1] Create Git commit-msg hook script template in template/files/shared/.git-hooks/commit-msg.jinja
- [ ] T024 [US1] Implement hook error formatting with suggestions in template/files/shared/.git-hooks/commit-msg.jinja
- [ ] T025 [US1] Add --no-verify bypass documentation in hook script comments
- [ ] T026 [US1] Create smoke test for validation in samples/cli-docs/smoke-test-commit-validation.sh

**Checkpoint**: Basic validation works - commits are automatically validated, invalid commits rejected

---

## Phase 4: User Story 3 - Cross-Platform Hook Installation (Priority: P1)

**Goal**: Automatically install Git commit-msg hooks during project setup on macOS, Linux, and Windows

**Independent Test**: Run setup-hooks command on fresh clone → verify .git/hooks/commit-msg exists and is executable → test that commit validation works

**Note**: This is P1 because User Story 1 (validation) depends on hooks being installed

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create Python hook installation script in template/files/shared/scripts/setup-hooks.py.jinja
- [ ] T028 [P] [US3] Create Node.js hook installation script in template/files/node/scripts/setup-hooks.js.jinja
- [ ] T029 [US3] Implement hook installation logic (copy, chmod 755) in setup-hooks.py.jinja
- [ ] T030 [US3] Implement backup mechanism for existing hooks in setup-hooks.py.jinja
- [ ] T031 [US3] Add Git hooks directory detection in setup-hooks.py.jinja
- [ ] T032 [US3] Implement graceful degradation with warning display in setup-hooks.py.jinja
- [ ] T033 [US3] Create recovery instructions text for failed installation in setup-hooks.py.jinja
- [ ] T034 [US3] Add installation verification (test hook with sample message) in setup-hooks.py.jinja
- [ ] T035 [US3] Create uv task entry for install-hooks in template/files/shared/quality/uv_tasks/commit_tooling.py.jinja
- [ ] T036 [US3] Create Makefile target for install-hooks in template/files/shared/quality/makefile.commit-tooling.jinja
- [ ] T037 [US3] Add post-render hook integration in template/hooks/post_gen_project.py to suggest running install-hooks
- [ ] T038 [US3] Create smoke test for hook installation in samples/cli-docs/smoke-test-hook-install.sh

**Checkpoint**: Hooks install automatically, validation runs on every commit

---

## Phase 5: User Story 2 - Guided Commit Message Authoring (Priority: P2)

**Goal**: Provide interactive CLI tool for guided commit message creation, preventing errors before validation

**Independent Test**: Run guided commit command → follow prompts to select type, scope, description → verify generated message matches conventional commit format

### Implementation for User Story 2

- [ ] T039 [P] [US2] Create guided authoring CLI entry point in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T040 [P] [US2] Implement type selection prompt in template/files/python/{package_name}/commit_tooling/prompts.py.jinja
- [ ] T041 [P] [US2] Implement scope selection prompt with autocomplete threshold (>10 scopes) in template/files/python/{package_name}/commit_tooling/prompts.py.jinja
- [ ] T042 [P] [US2] Implement subject input prompt with live character count in template/files/python/{package_name}/commit_tooling/prompts.py.jinja
- [ ] T043 [P] [US2] Implement body input prompt (optional) in template/files/python/{package_name}/commit_tooling/prompts.py.jinja
- [ ] T044 [P] [US2] Implement breaking change prompt in template/files/python/{package_name}/commit_tooling/prompts.py.jinja
- [ ] T045 [P] [US2] Implement footer/issues prompt in template/files/python/{package_name}/commit_tooling/prompts.py.jinja
- [ ] T046 [US2] Implement fuzzy search for scopes using Levenshtein distance (max edit distance 2) with <100ms response time for 50 scopes in template/files/python/{package_name}/commit_tooling/autocomplete.py.jinja
- [ ] T047 [US2] Implement commit message preview and confirmation in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T048 [US2] Integrate with Git commit execution in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T049 [US2] Add --type and --scope command-line options for pre-selection in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T050 [US2] Add --dry-run option for preview without committing in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T051 [US2] Create uv task entry for commit command in template/files/shared/quality/uv_tasks/commit_tooling.py.jinja
- [ ] T052 [US2] Create Makefile target for commit command in template/files/shared/quality/makefile.commit-tooling.jinja
- [ ] T053 [US2] Create Node.js commitizen wrapper in template/files/node/scripts/commit.js.jinja (for Node.js projects)
- [ ] T054 [US2] Create smoke test for guided authoring in samples/cli-docs/smoke-test-guided-commit.sh

**Checkpoint**: Guided authoring prevents errors, developers can create valid commits interactively

---

## Phase 6: User Story 4 - Python-Only Project Support (Priority: P2)

**Goal**: Support commit validation in Python-only projects without requiring Node.js installation

**Independent Test**: Render Python-only project (no Node.js in api_tracks) → run hook installation → make commit → verify validation works without Node.js

### Implementation for User Story 4

- [ ] T055 [US4] Add Python-only detection logic in template/files/shared/scripts/setup-hooks.py.jinja
- [ ] T056 [US4] Implement Python-based validation backend selection in template/files/shared/.git-hooks/commit-msg.jinja
- [ ] T057 [US4] Create pure Python commitlint rule parser subset (type-enum, subject-max-length, subject-empty, body-leading-blank, footer-leading-blank) in template/files/python/{package_name}/commit_tooling/parser.py.jinja
- [ ] T058 [US4] Add fallback to Python validation in hook script when Node.js unavailable
- [ ] T059 [US4] Document Python-only mode in template/files/shared/.commitlintrc.yml.jinja comments
- [ ] T060 [US4] Add Python-only project to samples (samples/python-cli/ if not exists) for smoke testing
- [ ] T061 [US4] Create smoke test for Python-only validation in samples/python-cli/smoke-test-python-only.sh

**Checkpoint**: Python-only projects work without Node.js dependency

---

## Phase 7: User Story 5 - Configuration Customization (Priority: P3)

**Goal**: Allow project maintainers to customize commit types, scopes, and validation rules

**Independent Test**: Edit .commitlintrc.yml to add custom type (e.g., "perf") → commit with that type → verify validation passes. Use undefined type → verify validation catches error.

### Implementation for User Story 5

- [ ] T062 [P] [US5] Implement scope-enum validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T063 [P] [US5] Implement subject-case validation rule in template/files/python/{package_name}/commit_tooling/rules.py.jinja
- [ ] T064 [P] [US5] Implement custom type loading from config in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T065 [P] [US5] Implement custom scope loading from config in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T066 [US5] Add scope count validation (max 50) in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T067 [US5] Add custom type validation (max 20) in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T068 [US5] Create CLI init command for config generation in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T069 [US5] Implement --profile option (standard/strict) for init command in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T070 [US5] Implement --scopes option for init command in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T071 [US5] Create strict profile configuration template in template/files/shared/.commitlintrc.strict.yml.jinja
- [ ] T072 [US5] Add scope descriptions support in prompt configuration
- [ ] T073 [US5] Create smoke test for custom configuration in samples/cli-docs/smoke-test-custom-config.sh

**Checkpoint**: Projects can customize types, scopes, and rules to match their conventions

---

## Phase 8: CLI Tooling & Diagnostics

**Purpose**: Complete CLI interface with all commands from contracts/cli-commands.md

- [ ] T074 [P] Create CLI validate command in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T075 [P] Create CLI config command (--show, --validate, --list-scopes, --list-types) in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T076 [P] Create CLI doctor command with diagnostics checks in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T077 [US2] Implement --json output option for all CLI commands in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T078 Add global options (--verbosity, --config, --profile) to CLI in template/files/python/{package_name}/commit_tooling/cli.py.jinja
- [ ] T079 Implement environment variable support (COMMIT_TOOLING_*) in template/files/python/{package_name}/commit_tooling/config.py.jinja
- [ ] T080 Create CLI entry point in template/files/python/pyproject.toml.jinja scripts section
- [ ] T081 Add uv task entries for all CLI commands in template/files/shared/quality/uv_tasks/commit_tooling.py.jinja
- [ ] T082 Add Makefile targets for all CLI commands in template/files/shared/quality/makefile.commit-tooling.jinja

---

## Phase 9: CI Integration

**Purpose**: Enable commit validation in CI/CD pipelines

- [ ] T083 Create GitHub Actions workflow template in template/files/shared/.github/workflows/riso-commit-validation.yml.jinja
- [ ] T084 Implement batch commit validation (validate all commits in PR) in workflow
- [ ] T085 Add conditional rendering based on commit_tooling_module in workflow template
- [ ] T086 Implement validation report artifact upload (90-day retention) in workflow
- [ ] T087 Add PR comment integration for validation failures in workflow
- [ ] T088 Create pre-push hook template (optional) in template/files/shared/.git-hooks/pre-push.jinja
- [ ] T089 Document CI integration in docs/modules/commit-tooling.md.jinja
- [ ] T090 Add CI validation smoke test to samples/cli-docs/

---

## Phase 10: Documentation & Templates

**Purpose**: User-facing documentation and quickstart guides

- [ ] T091 [P] Create module documentation in docs/modules/commit-tooling.md.jinja
- [ ] T092 [P] Add commit tooling section to docs/quickstart.md.jinja
- [ ] T093 [P] Create upgrade guide in docs/upgrade-guide/016-commit-tooling.md.jinja
- [ ] T094 [P] Add commit tooling examples to README.md.jinja template
- [ ] T095 Update AGENTS.md with commit tooling commands and workflows
- [ ] T096 Update .github/copilot-instructions.md with conventional commit patterns
- [ ] T097 Create commit message examples in template/files/shared/.gitmessage.jinja (nice-to-have, non-blocking)
- [ ] T098 Add troubleshooting section to documentation with common issues
- [ ] T099 Document Python-only vs Node.js mode differences
- [ ] T100 Create sample configurations for monorepo projects

---

## Phase 11: Testing & Validation

**Purpose**: Comprehensive smoke tests and validation across project types

- [ ] T101 Update samples/cli-docs/copier-answers.yml to enable commit_tooling_module
- [ ] T102 Update samples/default/copier-answers.yml to enable commit_tooling_module
- [ ] T103 Update samples/full-stack/copier-answers.yml to enable commit_tooling_module
- [ ] T104 Create render_matrix.py integration for commit tooling validation
- [ ] T105 Update record_module_success.py to track commit_tooling status
- [ ] T106 Create comprehensive smoke test suite in scripts/ci/test_commit_tooling.py
- [ ] T107 Test hook installation on macOS, Linux, Windows (via CI matrix)
- [ ] T108 Test Python-only projects without Node.js
- [ ] T109 Test Node.js projects with commitlint/commitizen
- [ ] T110 Test custom configuration with 50 scopes (performance validation)
- [ ] T111 Test guided authoring autocomplete with >10 scopes
- [ ] T112 Test graceful degradation scenarios (missing config, failed install)
- [ ] T113 Validate hook performance (<500ms target, <1000ms max)
- [ ] T114 Validate autocomplete performance (<100ms for 50 scopes)
- [ ] T115 Run quickstart.md validation steps

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and quality improvements

- [ ] T116 [P] Add type hints to all Python modules
- [ ] T117 [P] Add docstrings to all public functions and classes
- [ ] T118 Run ruff linting on all generated code
- [ ] T119 Run mypy type checking on all Python modules
- [ ] T120 Run pylint static analysis
- [ ] T121 Optimize hook script for startup time (<500ms)
- [ ] T122 Add caching for configuration (60s TTL, mtime invalidation)
- [ ] T123 Implement logging verbosity levels (normal/verbose/debug)
- [ ] T124 Add performance metrics to smoke test reports
- [ ] T125 Review and update all error messages for clarity
- [ ] T126 Ensure all file paths use absolute paths consistently
- [ ] T127 Validate template rendering with copier-answers combinations
- [ ] T128 Update module_catalog.json.jinja with commit_tooling entry
- [ ] T129 Create release notes for feature 016
- [ ] T130 Final review of all contracts against implementation

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)**: No dependencies - can start immediately
2. **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories
3. **User Story 1 - Validation (Phase 3)**: Depends on Phase 2
4. **User Story 3 - Hook Installation (Phase 4)**: Depends on Phase 2 and Phase 3 (needs validation to install)
5. **User Story 2 - Guided Authoring (Phase 5)**: Depends on Phase 2, can run parallel with Phase 3/4
6. **User Story 4 - Python-Only (Phase 6)**: Depends on Phase 3, Phase 4
7. **User Story 5 - Customization (Phase 7)**: Depends on Phase 2, Phase 3
8. **CLI Tooling (Phase 8)**: Depends on Phase 2, 3, 4, 5
9. **CI Integration (Phase 9)**: Depends on Phase 3 (validation)
10. **Documentation (Phase 10)**: Can start after Phase 2, complete after all user stories
11. **Testing (Phase 11)**: Depends on all user story phases
12. **Polish (Phase 12)**: Depends on all previous phases

### User Story Dependencies

- **US1 (Validation)**: Independent after Foundational (Phase 2)
- **US3 (Hook Install)**: Depends on US1 (needs validation to install hooks)
- **US2 (Guided Authoring)**: Independent after Foundational, integrates with US1 validation
- **US4 (Python-Only)**: Depends on US1 and US3 (extends validation and installation)
- **US5 (Customization)**: Depends on US1 (extends validation rules)

### Critical Path (MVP)

For minimum viable product, complete in order:

1. Phase 1: Setup
2. Phase 2: Foundational (T006-T014)
3. Phase 3: User Story 1 - Validation (T015-T026)
4. Phase 4: User Story 3 - Hook Installation (T027-T038)
5. Phase 10: Basic Documentation (T091-T094)
6. Phase 11: Basic Testing (T101-T106)

**MVP Checkpoint**: At this point, basic commit validation works automatically

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T007, T010, T011, T012 can run in parallel (different files)

**Within Phase 3 (User Story 1)**:
- T015-T019 (validation rules) can all run in parallel (same file, different functions)

**Within Phase 4 (User Story 3)**:
- T027, T028 can run in parallel (Python vs Node.js implementations)

**Within Phase 5 (User Story 2)**:
- T039-T045 (prompt implementations) can run in parallel (different functions)

**Within Phase 7 (User Story 5)**:
- T062-T065 (rule and config extensions) can run in parallel

**Within Phase 8 (CLI)**:
- T074-T076 (CLI commands) can run in parallel (different functions)

**Within Phase 10 (Documentation)**:
- T091-T094 can all run in parallel (different files)

**Within Phase 12 (Polish)**:
- T116-T117 can run in parallel (documentation tasks)

---

## Parallel Example: Phase 3 (User Story 1)

```bash
# Launch all validation rules in parallel:
Task T015: "Implement type-enum validation rule"
Task T016: "Implement subject-max-length validation rule"
Task T017: "Implement subject-empty validation rule"
Task T018: "Implement body-leading-blank validation rule"
Task T019: "Implement footer-leading-blank validation rule"

# Then proceed with dependent tasks sequentially:
Task T020: "Create CommitValidator class" (depends on T015-T019)
Task T021: "Implement merge commit detection" (depends on T020)
```

---

## Implementation Strategy

### MVP First (Critical Path)

**Goal**: Get basic validation working as quickly as possible

1. ✅ Phase 1: Setup (5 tasks, ~1 hour)
2. ✅ Phase 2: Foundational (9 tasks, ~4 hours)
3. ✅ Phase 3: User Story 1 (12 tasks, ~6 hours)
4. ✅ Phase 4: User Story 3 (12 tasks, ~4 hours)
5. ✅ Phase 10: Basic docs (4 tasks, ~2 hours)
6. ✅ Phase 11: Basic testing (6 tasks, ~3 hours)

**Total MVP Time**: ~20 hours

**MVP Deliverables**:
- Commit validation works automatically
- Hooks install on project setup
- Invalid commits are rejected with helpful errors
- Basic documentation available

### Incremental Delivery

After MVP, add features incrementally:

1. **Iteration 2**: User Story 2 (Guided Authoring)
   - Phase 5: ~8 hours
   - Value: Prevents errors before validation
   
2. **Iteration 3**: User Story 4 (Python-Only Support)
   - Phase 6: ~4 hours
   - Value: Removes Node.js dependency for Python projects

3. **Iteration 4**: User Story 5 (Customization)
   - Phase 7: ~6 hours
   - Value: Projects can adapt to their conventions

4. **Iteration 5**: Complete tooling
   - Phase 8: CLI commands (~4 hours)
   - Phase 9: CI integration (~4 hours)
   - Phase 10: Complete docs (~4 hours)
   - Phase 11: Comprehensive testing (~8 hours)
   - Phase 12: Polish (~6 hours)

### Parallel Team Strategy

With 3 developers after Foundational phase:

- **Developer A**: User Story 1 + User Story 3 (validation + hooks) - Critical path
- **Developer B**: User Story 2 (guided authoring) - Independent
- **Developer C**: Documentation + CI integration - Independent

All can work simultaneously after Phase 2 completes.

---

## Success Metrics

Per spec.md Success Criteria:

- **SC-001**: 95% of commits follow format → Validate via git log analysis after deployment
- **SC-002**: Install in <2 minutes → Measure in smoke tests (T106-T115)
- **SC-003**: Reject invalid commits in <1 second → Validate in T113 (target <500ms)
- **SC-004**: 80% error reduction with guided authoring → Compare pre/post metrics
- **SC-005**: 100% install success across platforms → CI matrix in T107
- **SC-006**: Python-only validation works → Validate in T108
- **SC-007**: CI catches 100% invalid commits → Validate in Phase 9 tests
- **SC-008**: Customize in <5 minutes → Test in T073
- **SC-009**: Tool startup <500ms → Validate in T113
- **SC-010**: Valid commits in 10 minutes for new users → Validate with quickstart.md

---

## Notes

- All Python code must use `uv run` prefix (per AGENTS.md convention)
- Hook scripts must be cross-platform (Python for portability)
- Configuration files use YAML (human-readable, comments allowed)
- Graceful degradation is required for failed installations (FR-023)
- Scope limit is 50 (FR-025), type limit is 20 (FR-024)
- Autocomplete activates at >10 scopes (FR-026)
- All tasks include exact file paths for clarity
- Jinja2 templates enable conditional rendering based on copier.yml options
- No tests explicitly requested, so using smoke tests for validation

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 9 tasks
- **Phase 3 (US1 - Validation)**: 12 tasks
- **Phase 4 (US3 - Hook Install)**: 12 tasks
- **Phase 5 (US2 - Guided Authoring)**: 16 tasks
- **Phase 6 (US4 - Python-Only)**: 7 tasks
- **Phase 7 (US5 - Customization)**: 12 tasks
- **Phase 8 (CLI Tooling)**: 9 tasks
- **Phase 9 (CI Integration)**: 8 tasks
- **Phase 10 (Documentation)**: 10 tasks
- **Phase 11 (Testing)**: 15 tasks
- **Phase 12 (Polish)**: 15 tasks

**Total Tasks**: 130

**Parallel Tasks**: 35 tasks marked [P] (27% can run in parallel)

**MVP Tasks**: 42 tasks (Phases 1, 2, 3, 4, + basic docs/testing)

---

**Status**: ✅ Ready for Implementation

**Next Step**: Begin Phase 1 (Setup) or run `/speckit.kickoff` to create GitHub issue and start development
