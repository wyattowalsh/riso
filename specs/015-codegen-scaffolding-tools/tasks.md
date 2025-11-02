# Tasks: Code Generation and Scaffolding Tools

**Feature Branch**: `015-codegen-scaffolding-tools`  
**Input**: Design documents from `/specs/015-codegen-scaffolding-tools/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, all paths use the Riso template structure:
- Python source: `template/files/python/src/{{package_name}}/codegen/`
- Tests: `template/files/python/tests/codegen/`
- Documentation: `template/files/shared/docs/modules/`
- Integration: `template/copier.yml` for module flag

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create directory structure per plan.md in template/files/python/src/{{package_name}}/codegen/
- [ ] T002 Add dependencies to template/files/python/pyproject.toml.jinja (jinja2, typer, rich, merge3, gitpython, pydantic, loguru)
- [ ] T003 [P] Create __init__.py files for all codegen subpackages (templates/, generation/, updates/, quality/)
- [ ] T004 [P] Create test directory structure in template/files/python/tests/codegen/
- [ ] T005 [P] Create fixtures directory with sample templates in template/files/python/tests/codegen/fixtures/sample_templates/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and configuration that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create VariableType enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T007 Create TemplateType enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T008 Create OverwriteMode enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T009 Create QualityStatus enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T010 [P] Create VariableDefinition model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T011 [P] Create Template model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T012 [P] Create Project model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T013 [P] Create Module model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T014 Create FilePattern value object in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T015 Create Dependency value object in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T016 Create HookConfiguration value object in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T017 Setup Jinja2 Environment with configuration from research.md in template/files/python/src/{{package_name}}/codegen/engine.py
- [ ] T018 Create TemplateLoader class in template/files/python/src/{{package_name}}/codegen/templates/loader.py
- [ ] T019 Create CacheManager class in template/files/python/src/{{package_name}}/codegen/templates/cache.py
- [ ] T020 Create CLI app skeleton with Typer in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T021 Setup Rich console for terminal output in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T022 Create base test fixtures in template/files/python/tests/codegen/conftest.py (tmp_path, sample_template, mock_env)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Project Boilerplate (Priority: P1) 🎯 MVP

**Goal**: Enable developers to quickly create a new project with consistent structure using `scaffold new PROJECT_NAME`

**Independent Test**: Run `scaffold new test-project`, verify directory created with files, run quality checks, confirm tests pass

### Implementation for User Story 1

- [ ] T023 [P] [US1] Implement template size validation (100MB limit, 50MB warning) in template/files/python/src/{{package_name}}/codegen/templates/validator.py
- [ ] T024 [P] [US1] Implement template metadata loading (template.yml parsing) in template/files/python/src/{{package_name}}/codegen/templates/loader.py
- [ ] T025 [P] [US1] Implement variable collection with interactive prompts in template/files/python/src/{{package_name}}/codegen/generation/variables.py
- [ ] T026 [P] [US1] Implement variable validation (pattern, choices, required) in template/files/python/src/{{package_name}}/codegen/generation/variables.py
- [ ] T027 [US1] Implement Generator class with Jinja2 rendering in template/files/python/src/{{package_name}}/codegen/generation/generator.py (depends on T023-T026)
- [ ] T028 [US1] Implement atomic file operations (all-or-nothing generation) in template/files/python/src/{{package_name}}/codegen/generation/atomic.py
- [ ] T029 [US1] Implement file permission preservation in template/files/python/src/{{package_name}}/codegen/generation/atomic.py
- [ ] T030 [US1] Implement binary file handling (copy without rendering) in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T031 [US1] Implement pre-generation hooks execution in template/files/python/src/{{package_name}}/codegen/generation/hooks.py
- [ ] T032 [US1] Implement post-generation hooks execution in template/files/python/src/{{package_name}}/codegen/generation/hooks.py
- [ ] T033 [US1] Implement quality validation (syntax, ruff, mypy) in template/files/python/src/{{package_name}}/codegen/quality/checker.py
- [ ] T034 [US1] Implement warning/error reporting (warn-but-allow) in template/files/python/src/{{package_name}}/codegen/quality/reporter.py
- [ ] T035 [US1] Implement .scaffold-metadata.json generation in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T036 [US1] Implement `scaffold new` command with all options in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T037 [US1] Add Rich progress bars for generation in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T038 [US1] Add dry-run mode support in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T039 [US1] Add interactive/non-interactive mode handling in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T040 [US1] Add existing directory detection and overwrite prompt in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T041 [P] [US1] Write unit tests for VariableDefinition validation in template/files/python/tests/codegen/test_models.py
- [ ] T042 [P] [US1] Write unit tests for Template model validation in template/files/python/tests/codegen/test_models.py
- [ ] T043 [P] [US1] Write unit tests for template loading in template/files/python/tests/codegen/test_templates/test_loader.py
- [ ] T044 [P] [US1] Write unit tests for size validation in template/files/python/tests/codegen/test_templates/test_validator.py
- [ ] T045 [P] [US1] Write unit tests for variable collection in template/files/python/tests/codegen/test_generation/test_variables.py
- [ ] T046 [P] [US1] Write unit tests for Jinja2 generation in template/files/python/tests/codegen/test_generation/test_generator.py
- [ ] T047 [P] [US1] Write unit tests for atomic operations in template/files/python/tests/codegen/test_generation/test_atomic.py
- [ ] T048 [P] [US1] Write unit tests for quality checker in template/files/python/tests/codegen/test_quality/test_checker.py
- [ ] T049 [US1] Write integration test for full project generation in template/files/python/tests/codegen/integration/test_new_project.py
- [ ] T050 [US1] Write CLI test for `scaffold new` command in template/files/python/tests/codegen/test_cli.py

**Checkpoint**: User Story 1 complete - can generate projects from templates independently

---

## Phase 4: User Story 2 - Add Feature Modules (Priority: P2)

**Goal**: Enable developers to add feature modules to existing projects using `scaffold add MODULE_TYPE MODULE_NAME`

**Independent Test**: Generate a project (US1), run `scaffold add api users`, verify module files created, imports updated, project still builds/tests pass

### Implementation for User Story 2

- [ ] T051 [P] [US2] Create ModuleType enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T052 [P] [US2] Implement project metadata loading (.scaffold-metadata.json) in template/files/python/src/{{package_name}}/codegen/templates/loader.py
- [ ] T053 [P] [US2] Implement module template discovery in template/files/python/src/{{package_name}}/codegen/templates/registry.py
- [ ] T054 [US2] Implement dependency addition (pyproject.toml update) in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T055 [US2] Implement import statement addition in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T056 [US2] Implement configuration file merging in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T057 [US2] Implement module conflict detection (existing module check) in template/files/python/src/{{package_name}}/codegen/templates/validator.py
- [ ] T058 [US2] Implement `scaffold add` command with all options in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T059 [US2] Add module type validation and suggestions in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T060 [US2] Add project detection (find .scaffold-metadata.json) in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T061 [US2] Update .scaffold-metadata.json with module info in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T062 [P] [US2] Write unit tests for Module model in template/files/python/tests/codegen/test_models.py
- [ ] T063 [P] [US2] Write unit tests for project metadata loading in template/files/python/tests/codegen/test_templates/test_loader.py
- [ ] T064 [P] [US2] Write unit tests for dependency updates in template/files/python/tests/codegen/test_generation/test_generator.py
- [ ] T065 [P] [US2] Write unit tests for import additions in template/files/python/tests/codegen/test_generation/test_generator.py
- [ ] T066 [US2] Write integration test for module addition in template/files/python/tests/codegen/integration/test_add_module.py
- [ ] T067 [US2] Write CLI test for `scaffold add` command in template/files/python/tests/codegen/test_cli.py

**Checkpoint**: User Story 2 complete - can add modules to existing projects independently

---

## Phase 5: User Story 3 - Customize Templates (Priority: P3)

**Goal**: Enable teams to define organization-specific templates using `scaffold new PROJECT --template CUSTOM_TEMPLATE`

**Independent Test**: Create custom template directory with template.yml, run `scaffold new project --template ./custom`, verify custom patterns appear in output

### Implementation for User Story 3

- [ ] T068 [P] [US3] Create RegistryType enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T069 [P] [US3] Create TemplateRegistry model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T070 [P] [US3] Implement local template directory scanning in template/files/python/src/{{package_name}}/codegen/templates/registry.py
- [ ] T071 [P] [US3] Implement Git repository template fetching in template/files/python/src/{{package_name}}/codegen/templates/registry.py
- [ ] T072 [P] [US3] Implement HTTP(S) template downloading in template/files/python/src/{{package_name}}/codegen/templates/registry.py
- [ ] T073 [US3] Implement template caching in ~/.scaffold/templates/ in template/files/python/src/{{package_name}}/codegen/templates/cache.py
- [ ] T074 [US3] Implement template version tracking in template/files/python/src/{{package_name}}/codegen/templates/cache.py
- [ ] T075 [US3] Implement `scaffold list` command with filtering in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T076 [US3] Implement `scaffold info TEMPLATE` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T077 [US3] Add --template option support to `scaffold new` in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T078 [US3] Add template search by name/description in template/files/python/src/{{package_name}}/codegen/templates/registry.py
- [ ] T079 [US3] Implement Rich table output for template list in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T080 [US3] Add JSON/YAML output format option in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T081 [P] [US3] Write unit tests for TemplateRegistry model in template/files/python/tests/codegen/test_models.py
- [ ] T082 [P] [US3] Write unit tests for template fetching in template/files/python/tests/codegen/test_templates/test_registry.py
- [ ] T083 [P] [US3] Write unit tests for template caching in template/files/python/tests/codegen/test_templates/test_cache.py
- [ ] T084 [P] [US3] Write CLI tests for `scaffold list` in template/files/python/tests/codegen/test_cli.py
- [ ] T085 [P] [US3] Write CLI tests for `scaffold info` in template/files/python/tests/codegen/test_cli.py

**Checkpoint**: User Story 3 complete - can use custom templates from multiple sources

---

## Phase 6: User Story 4 - Update Generated Code (Priority: P4)

**Goal**: Enable developers to update projects when templates evolve using `scaffold update` with merge support

**Independent Test**: Generate project from old template, modify files, update template, run `scaffold update`, verify improvements applied, conflicts marked, custom changes preserved

### Implementation for User Story 4

- [ ] T086 [P] [US4] Create MergeStrategy enum in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T087 [P] [US4] Create MergeResult model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T088 [P] [US4] Create ConflictRegion model in template/files/python/src/{{package_name}}/codegen/models.py
- [ ] T089 [P] [US4] Implement three-way merge using merge3 in template/files/python/src/{{package_name}}/codegen/updates/merger.py
- [ ] T090 [P] [US4] Implement conflict marker insertion (<<<<<<, =======, >>>>>>>) in template/files/python/src/{{package_name}}/codegen/updates/merger.py
- [ ] T091 [P] [US4] Implement conflict detection and parsing in template/files/python/src/{{package_name}}/codegen/updates/conflict.py
- [ ] T092 [US4] Implement template version comparison in template/files/python/src/{{package_name}}/codegen/updates/differ.py
- [ ] T093 [US4] Implement base version retrieval from cache in template/files/python/src/{{package_name}}/codegen/templates/cache.py
- [ ] T094 [US4] Implement file-by-file update orchestration in template/files/python/src/{{package_name}}/codegen/updates/differ.py
- [ ] T095 [US4] Implement unresolved conflict validation in template/files/python/src/{{package_name}}/codegen/updates/conflict.py
- [ ] T096 [US4] Implement `scaffold update` command with merge strategies in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T097 [US4] Add --dry-run support for updates in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T098 [US4] Add --strategy option (three_way, ours, theirs) in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T099 [US4] Add conflict summary reporting with file paths and line numbers in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T100 [US4] Add user guidance for conflict resolution in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T101 [US4] Update project metadata with new template version in template/files/python/src/{{package_name}}/codegen/generation/generator.py
- [ ] T102 [P] [US4] Write unit tests for MergeResult model in template/files/python/tests/codegen/test_models.py
- [ ] T103 [P] [US4] Write unit tests for three-way merge in template/files/python/tests/codegen/test_updates/test_merger.py
- [ ] T104 [P] [US4] Write unit tests for conflict detection in template/files/python/tests/codegen/test_updates/test_conflict.py
- [ ] T105 [P] [US4] Write unit tests for version comparison in template/files/python/tests/codegen/test_updates/test_differ.py
- [ ] T106 [US4] Write integration test for clean merge (no conflicts) in template/files/python/tests/codegen/integration/test_update_project.py
- [ ] T107 [US4] Write integration test for conflicted merge in template/files/python/tests/codegen/integration/test_update_project.py
- [ ] T108 [US4] Write CLI test for `scaffold update` command in template/files/python/tests/codegen/test_cli.py

**Checkpoint**: User Story 4 complete - can update projects with merge support

---

## Phase 7: User Story 5 - Generate from API Specs (Priority: P3)

**Goal**: Enable API-first development by generating code from OpenAPI/GraphQL schemas using `scaffold generate-api SPEC_FILE`

**Independent Test**: Provide sample openapi.yaml, run `scaffold generate-api openapi.yaml`, verify FastAPI routes/models generated, types match spec, code imports successfully

### Implementation for User Story 5

- [ ] T109 [P] [US5] Implement OpenAPI parser (extract endpoints, models, types) in template/files/python/src/{{package_name}}/codegen/generation/api_parser.py
- [ ] T110 [P] [US5] Implement GraphQL schema parser in template/files/python/src/{{package_name}}/codegen/generation/api_parser.py
- [ ] T111 [US5] Implement FastAPI code generator from OpenAPI in template/files/python/src/{{package_name}}/codegen/generation/api_generator.py
- [ ] T112 [US5] Implement GraphQL client generator in template/files/python/src/{{package_name}}/codegen/generation/api_generator.py
- [ ] T113 [US5] Implement type-safe model generation with Pydantic in template/files/python/src/{{package_name}}/codegen/generation/api_generator.py
- [ ] T114 [US5] Implement validation logic generation from schema constraints in template/files/python/src/{{package_name}}/codegen/generation/api_generator.py
- [ ] T115 [US5] Implement `scaffold generate-api` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T116 [US5] Add --language option (python, typescript) in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T117 [US5] Add --type option (server, client) in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T118 [US5] Add designated areas for custom business logic (no-overwrite regions) in template/files/python/src/{{package_name}}/codegen/generation/api_generator.py
- [ ] T119 [P] [US5] Write unit tests for OpenAPI parsing in template/files/python/tests/codegen/test_generation/test_api_parser.py
- [ ] T120 [P] [US5] Write unit tests for GraphQL parsing in template/files/python/tests/codegen/test_generation/test_api_parser.py
- [ ] T121 [P] [US5] Write unit tests for FastAPI generation in template/files/python/tests/codegen/test_generation/test_api_generator.py
- [ ] T122 [US5] Write integration test for OpenAPI → FastAPI in template/files/python/tests/codegen/integration/test_generate_api.py
- [ ] T123 [US5] Write CLI test for `scaffold generate-api` in template/files/python/tests/codegen/test_cli.py

**Checkpoint**: User Story 5 complete - can generate code from API specifications

---

## Phase 8: Additional Commands & Features

**Purpose**: Supporting commands for cache management and configuration

- [ ] T124 [P] Implement `scaffold cache list` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T125 [P] Implement `scaffold cache update` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T126 [P] Implement `scaffold cache clear` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T127 [P] Implement `scaffold config get` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T128 [P] Implement `scaffold config set` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T129 [P] Implement `scaffold config list` command in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T130 Implement configuration file loading (~/.scaffold/config.yml) in template/files/python/src/{{package_name}}/codegen/engine.py
- [ ] T131 Add shell completion installation in template/files/python/src/{{package_name}}/codegen/cli.py
- [ ] T132 [P] Write CLI tests for cache commands in template/files/python/tests/codegen/test_cli.py
- [ ] T133 [P] Write CLI tests for config commands in template/files/python/tests/codegen/test_cli.py

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, integration, and final quality improvements

- [ ] T134 [P] Create user documentation in template/files/shared/docs/modules/codegen-scaffolding.md.jinja
- [ ] T135 [P] Add examples to documentation (project generation, module addition, updates)
- [ ] T136 [P] Create template metadata schema documentation in template/files/shared/docs/modules/codegen-scaffolding.md.jinja
- [ ] T137 Add codegen_module flag to template/copier.yml with enabled/disabled choices
- [ ] T138 Wrap all codegen files with {% if codegen_module == 'enabled' %} conditionals
- [ ] T139 Create sample answer file for testing in samples/codegen-enabled/copier-answers.yml
- [ ] T140 Test rendering with codegen_module=enabled via ./scripts/render-samples.sh
- [ ] T141 Test rendering with codegen_module=disabled via ./scripts/render-samples.sh
- [ ] T142 [P] Add logging throughout all modules using Loguru in template/files/python/src/{{package_name}}/codegen/
- [ ] T143 [P] Add comprehensive docstrings to all classes and functions
- [ ] T144 [P] Add type hints to all function signatures
- [ ] T145 Run quality checks (ruff, mypy, pylint) and fix violations
- [ ] T146 Verify 80%+ test coverage with pytest-cov
- [ ] T147 Update AGENTS.md with codegen_module documentation
- [ ] T148 Update .github/copilot-instructions.md with codegen patterns
- [ ] T149 Validate against all spec requirements (FR-001 through FR-024)
- [ ] T150 Validate against all success criteria (SC-001 through SC-010)
- [ ] T151 Run quickstart.md validation (generate test project, add module, update)
- [ ] T152 Performance profiling (ensure <30s project generation)
- [ ] T153 Create upgrade guide for existing projects in docs/upgrade-guide/015-codegen-scaffolding.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (Generate Project) - Priority P1 - Can start after Foundational
  - US2 (Add Modules) - Priority P2 - Can start after Foundational (may integrate with US1)
  - US3 (Custom Templates) - Priority P3 - Can start after Foundational (extends US1)
  - US4 (Update Projects) - Priority P4 - Can start after Foundational (extends US1)
  - US5 (API Specs) - Priority P3 - Can start after Foundational (builds on US1)
- **Additional Commands (Phase 8)**: Depends on US3 completion (cache/config for templates)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - pure project generation
- **User Story 2 (P2)**: Builds on US1 - requires project detection and metadata
- **User Story 3 (P3)**: Extends US1 - adds template sources and discovery
- **User Story 4 (P4)**: Extends US1 - adds update/merge to existing projects
- **User Story 5 (P3)**: Builds on US1 - API spec as input source for generation

### Within Each User Story

- Tests written first (when present) - must FAIL before implementation
- Data models before services
- Services before CLI commands
- Core functionality before CLI integration
- Unit tests before integration tests

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003, T004, T005 can run in parallel (different directories)

**Phase 2 (Foundational)**: Tasks T006-T016 (models), T017-T021 (infrastructure) can run in parallel within groups

**User Story 1**: Tasks T023-T026 (validation/variables), T031-T032 (hooks), T033-T034 (quality), T041-T048 (unit tests) can run in parallel within groups

**User Story 2**: Tasks T051-T053 (models/discovery), T062-T065 (unit tests) can run in parallel

**User Story 3**: Tasks T068-T072 (models/fetching), T081-T085 (tests) can run in parallel

**User Story 4**: Tasks T086-T091 (merge models/logic), T102-T105 (unit tests) can run in parallel

**User Story 5**: Tasks T109-T110 (parsers), T119-T121 (unit tests) can run in parallel

**Phase 8**: All cache/config commands (T124-T129, T132-T133) can run in parallel

**Phase 9**: Documentation tasks (T134-T136), logging/docs (T142-T144) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch validation and variable tasks together:
Task T023: "Implement template size validation in validator.py"
Task T024: "Implement template metadata loading in loader.py"
Task T025: "Implement variable collection in variables.py"
Task T026: "Implement variable validation in variables.py"

# Launch quality and hook tasks together:
Task T031: "Implement pre-generation hooks in hooks.py"
Task T032: "Implement post-generation hooks in hooks.py"
Task T033: "Implement quality validation in checker.py"
Task T034: "Implement warning/error reporting in reporter.py"

# Launch all unit tests together:
Task T041: "Unit tests for VariableDefinition in test_models.py"
Task T042: "Unit tests for Template model in test_models.py"
Task T043: "Unit tests for template loading in test_loader.py"
Task T044: "Unit tests for size validation in test_validator.py"
Task T045: "Unit tests for variable collection in test_variables.py"
Task T046: "Unit tests for Jinja2 generation in test_generator.py"
Task T047: "Unit tests for atomic operations in test_atomic.py"
Task T048: "Unit tests for quality checker in test_checker.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Complete Phase 1**: Setup (T001-T005) - ~1 hour
2. **Complete Phase 2**: Foundational (T006-T022) - ~4 hours
3. **Complete Phase 3**: User Story 1 (T023-T050) - ~10 hours
4. **STOP and VALIDATE**: Test project generation independently
5. **Deploy/Demo**: Working project generator

**Total MVP**: ~15 hours, ~2 days

### Incremental Delivery (Recommended)

1. **Foundation** (Phase 1 + 2): Setup + models/infrastructure → ~5 hours
2. **US1** (Phase 3): Add project generation → Test independently → **Demo MVP!** → ~10 hours
3. **US2** (Phase 4): Add module addition → Test independently → Demo enhancement → ~6 hours
4. **US3** (Phase 5): Add custom templates → Test independently → Demo flexibility → ~5 hours
5. **US4** (Phase 6): Add update/merge → Test independently → Demo updates → ~8 hours
6. **US5** (Phase 7): Add API generation → Test independently → Demo API-first → ~5 hours
7. **Polish** (Phase 8 + 9): Commands + docs + integration → ~6 hours

**Total Feature**: ~45 hours, ~6 days (includes all 5 user stories)

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Story 1 (P1) - Core project generation
- **Developer B**: User Story 2 (P2) + User Story 3 (P3) - Modules + custom templates
- **Developer C**: User Story 4 (P4) + User Story 5 (P3) - Updates + API generation

Then merge and complete Phase 8 + 9 together.

**Total Time (parallel)**: ~20 hours, ~3 days

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 17 tasks (BLOCKING)
- **Phase 3 (US1 - Generate Project)**: 28 tasks (MVP)
- **Phase 4 (US2 - Add Modules)**: 17 tasks
- **Phase 5 (US3 - Custom Templates)**: 18 tasks
- **Phase 6 (US4 - Update Projects)**: 23 tasks
- **Phase 7 (US5 - API Specs)**: 15 tasks
- **Phase 8 (Additional Commands)**: 10 tasks
- **Phase 9 (Polish)**: 20 tasks

**Total**: 153 tasks

**MVP Subset** (Phase 1 + 2 + 3): 50 tasks

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability and independent testing
- Each user story designed to be independently completable and testable
- Foundational phase (Phase 2) MUST complete before any user story work begins
- Stop at any user story checkpoint to validate functionality independently
- Follow TDD approach - write tests, watch them fail, implement, watch them pass
- Commit after each task or logical group of related tasks
- Quality checks (ruff, mypy, pylint) should pass at each checkpoint
- Target 80%+ test coverage for all modules
