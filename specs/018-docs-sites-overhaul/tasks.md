````markdown
---

description: "Task list for Documentation Sites Overhaul implementation"
---

# Tasks: Documentation Sites Overhaul

**Feature Branch**: `018-docs-sites-overhaul`  
**Input**: Design documents from `/specs/018-docs-sites-overhaul/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included as this is infrastructure code that requires validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project structure and tooling setup

- [ ] T001 Review design documents (plan.md, spec.md, research.md, data-model.md, contracts/) and understand feature scope
- [ ] T002 [P] Set up Python test infrastructure for transformation validation in tests/test_content_transformation.py
- [ ] T003 [P] Set up Python test infrastructure for docs validation in tests/test_docs_validation.py
- [ ] T004 Create shared documentation constants module in template/files/shared/docs/constants.py.jinja

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] Implement ContentFormat enum and base classes in template/files/shared/docs/transformation/common.py.jinja
- [ ] T006 [P] Implement TransformationError and TransformationResult classes in template/files/shared/docs/transformation/common.py.jinja
- [ ] T007 [P] Implement RetryConfig class in template/files/shared/docs/validation/common.py.jinja
- [ ] T008 [P] Implement BrokenLink and LinkCheckResult classes in template/files/shared/docs/validation/common.py.jinja
- [ ] T009 [P] Implement A11yWarning, A11yError, and AccessibilityResult classes in template/files/shared/docs/validation/common.py.jinja
- [ ] T010 Create CI validation script template in scripts/ci/validate_docs_config.py
- [ ] T011 Create CI transformation test script in scripts/ci/test_content_transformation.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Sphinx Documentation Builds Successfully (Priority: P1) 🎯 MVP

**Goal**: Fix Sphinx smoke tests (0% → 100%) with working Makefile targets and autodoc configuration

**Independent Test**: Render with `docs_site=sphinx-shibuya`, run `uv run make -f Makefile.docs docs` and `uv run make -f Makefile.docs linkcheck`, verify HTML output without errors

### Implementation for User Story 1

- [ ] T012 [US1] Create Makefile.docs template in template/files/python/docs/Makefile.docs.jinja with targets: docs, linkcheck, doctest, clean-docs
- [ ] T013 [US1] Fix Sphinx conf.py template in template/files/python/docs/conf.py.jinja with sys.path modification, autodoc/napoleon extensions, and Shibuya theme configuration
- [ ] T014 [US1] Add sphinxcontrib-mermaid extension configuration to conf.py.jinja
- [ ] T015 [US1] Configure Sphinx linkcheck settings in conf.py.jinja with retry=3, timeout=10, ignore patterns
- [ ] T016 [US1] Add conditional theme_mode configuration based on docs_theme_mode prompt in conf.py.jinja
- [ ] T017 [US1] Update docs-sphinx sample answers in samples/docs-sphinx/copier-answers.yml if needed
- [ ] T018 [US1] Test Sphinx render and build: run ./scripts/render-samples.sh --variant docs-sphinx
- [ ] T019 [US1] Verify smoke tests pass: check samples/docs-sphinx/smoke-results.json for 100% pass rate
- [ ] T020 [US1] Update render_matrix.py to validate Sphinx Makefile.docs targets exist in scripts/ci/render_matrix.py

**Checkpoint**: At this point, Sphinx documentation should build successfully (SC-003: 0% → 100% pass rate)

---

## Phase 4: User Story 2 - Enhanced Documentation Configuration Options (Priority: P1)

**Goal**: Add 7 new prompts to copier.yml for theme, search, API playground, deployment, versioning, interactive features

**Independent Test**: Render with extended prompts, verify configuration files reflect choices without placeholder comments

### Implementation for User Story 2

- [ ] T021 [P] [US2] Add docs_theme_mode prompt to template/copier.yml (choices: light, dark, auto; default: auto)
- [ ] T022 [P] [US2] Add docs_search_provider prompt to template/copier.yml (choices: none, local, algolia, typesense; default: local)
- [ ] T023 [P] [US2] Add docs_api_playground prompt to template/copier.yml (choices: disabled, swagger, redoc, both; default: disabled)
- [ ] T024 [P] [US2] Add docs_deploy_target prompt to template/copier.yml (choices: github-pages, netlify, vercel, cloudflare; default: github-pages)
- [ ] T025 [P] [US2] Add docs_versioning prompt to template/copier.yml (choices: disabled, enabled; default: disabled)
- [ ] T026 [P] [US2] Add docs_interactive_features prompt to template/copier.yml (choices: disabled, enabled; default: disabled)
- [ ] T027 [P] [US2] Implement Algolia search configuration template in template/files/shared/docs/search/algolia.config.jinja
- [ ] T028 [P] [US2] Implement Typesense search configuration template in template/files/shared/docs/search/typesense.config.jinja
- [ ] T029 [US2] Update Fumadocs next.config.mjs.jinja to use docs_search_provider and docs_theme_mode prompts in template/files/node/docs/fumadocs/next.config.mjs.jinja
- [ ] T030 [US2] Update Docusaurus docusaurus.config.js.jinja to use docs_search_provider and docs_theme_mode prompts in template/files/node/docs/docusaurus/docusaurus.config.js.jinja
- [ ] T031 [US2] Create GitHub Pages deployment workflow template in template/files/shared/.github/workflows/riso-docs-deploy-ghpages.yml.jinja
- [ ] T032 [P] [US2] Create Netlify deployment configuration template in template/files/shared/docs/deploy/netlify.toml.jinja
- [ ] T033 [P] [US2] Create Vercel deployment configuration template in template/files/shared/docs/deploy/vercel.json.jinja
- [ ] T034 [P] [US2] Create Cloudflare Pages deployment configuration template in template/files/shared/docs/deploy/wrangler.toml.jinja
- [ ] T035 [US2] Test prompt rendering with various combinations: run copier with custom answer files testing all prompt values
- [ ] T036 [US2] Update all sample answer files to include new prompts with appropriate defaults in samples/*/copier-answers.yml
- [ ] T037 [US2] Validate generated configs with scripts/ci/validate_docs_config.py

**Checkpoint**: At this point, all 7 new prompts should be functional (SC-004) and configuration files generated correctly

---

## Phase 5: User Story 3 - Unified Documentation Content Management (Priority: P2)

**Goal**: Implement Markdown → MDX/RST transformation system with AST-based conversion

**Independent Test**: Update shared docs, re-render all variants, verify content appears correctly formatted in all frameworks

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T038 [P] [US3] Test Markdown → RST heading conversion in tests/test_content_transformation.py::test_markdown_to_rst_headings
- [ ] T039 [P] [US3] Test Markdown → RST code block conversion in tests/test_content_transformation.py::test_markdown_to_rst_code_blocks
- [ ] T040 [P] [US3] Test Markdown → RST link conversion in tests/test_content_transformation.py::test_markdown_to_rst_links
- [ ] T041 [P] [US3] Test Markdown → RST list conversion in tests/test_content_transformation.py::test_markdown_to_rst_lists
- [ ] T042 [P] [US3] Test Markdown → MDX minimal transformation in tests/test_content_transformation.py::test_markdown_to_mdx_minimal
- [ ] T043 [P] [US3] Test Mermaid → RST directive conversion in tests/test_content_transformation.py::test_mermaid_to_rst
- [ ] T044 [P] [US3] Test transformation failure handling in tests/test_content_transformation.py::test_transformation_failure_halts_build
- [ ] T045 [P] [US3] Test frontmatter transformation (YAML → RST field lists) in tests/test_content_transformation.py::test_frontmatter_transformation

### Implementation for User Story 3

- [ ] T046 [US3] Implement ContentTransformer class with transform() method in template/files/shared/docs/transformation/common.py.jinja
- [ ] T047 [US3] Implement markdown_to_rst() transformation function in template/files/shared/docs/transformation/markdown_to_rst.py.jinja (AST-based)
- [ ] T048 [US3] Implement markdown_to_mdx() transformation function in template/files/shared/docs/transformation/markdown_to_mdx.py.jinja (minimal changes)
- [ ] T049 [US3] Implement frontmatter transformation for all formats (YAML ↔ RST field lists) in transformation modules
- [ ] T050 [US3] Implement Mermaid code block → RST directive transformation in markdown_to_rst.py.jinja
- [ ] T051 [US3] Implement admonition/callout transformation (Markdown → MDX Callout, RST directive) in transformation modules
- [ ] T052 [US3] Implement code tabs transformation (Markdown → Fumadocs Tabs, RST tabs directive) in transformation modules
- [ ] T053 [US3] Add transformation error handling with actionable messages (file:line format per FR-009) in common.py.jinja
- [ ] T054 [US3] Create transformation CLI tool in template/files/shared/docs/scripts/transform_content.py.jinja for manual transformations
- [ ] T055 [US3] Update render hooks to run transformations during template generation in template/hooks/post_gen_project.py
- [ ] T056 [US3] Test transformations work end-to-end: render all variants and verify content correctness
- [ ] T057 [US3] Run transformation test suite: uv run pytest tests/test_content_transformation.py -v

**Checkpoint**: At this point, shared content should transform correctly to all frameworks (SC-007)

---

## Phase 6: User Story 4 - Interactive Documentation Features (Priority: P2)

**Goal**: Enable Mermaid diagrams, API playgrounds, and interactive features through prompt configuration

**Independent Test**: Render with `docs_interactive_features=enabled`, verify Mermaid diagrams and API playground work

### Implementation for User Story 4

- [ ] T058 [P] [US4] Configure Mermaid plugin for Fumadocs in next.config.mjs.jinja (rehype-mermaid)
- [ ] T059 [P] [US4] Configure Mermaid plugin for Docusaurus in docusaurus.config.js.jinja (@docusaurus/theme-mermaid)
- [ ] T060 [P] [US4] Verify Mermaid already configured for Sphinx via sphinxcontrib-mermaid (T014)
- [ ] T061 [P] [US4] Create Swagger UI integration template for FastAPI in template/files/python/docs/api/swagger.py.jinja
- [ ] T062 [P] [US4] Create ReDoc integration template for FastAPI in template/files/python/docs/api/redoc.py.jinja
- [ ] T063 [P] [US4] Create Swagger UI integration template for Fastify in template/files/node/docs/api/swagger.ts.jinja
- [ ] T064 [P] [US4] Create ReDoc integration template for Fastify in template/files/node/docs/api/redoc.ts.jinja
- [ ] T065 [US4] Implement API playground configuration with CORS, auth, rate limiting (per FR-011) in API integration templates
- [ ] T066 [US4] Add graceful degradation for offline API playground (static schema with "API offline" notice per FR-011) in templates
- [ ] T067 [US4] Create code tabs component template for Fumadocs in template/files/node/docs/fumadocs/components/CodeTabs.tsx.jinja
- [ ] T068 [US4] Test Mermaid rendering: create test diagrams in sample docs and verify interactive SVGs
- [ ] T069 [US4] Test API playground: verify Swagger/ReDoc loads with editable payloads and working requests (SC-007)
- [ ] T070 [US4] Update module documentation to explain interactive features in docs/modules/docs-site.md.jinja

**Checkpoint**: At this point, interactive features (Mermaid, API playground) should work when enabled

---

## Phase 7: User Story 5 - Documentation Versioning (Priority: P3)

**Goal**: Add optional versioning support with framework-specific scaffolding

**Independent Test**: Render with `docs_versioning=enabled`, verify version selector appears and switches versions

### Implementation for User Story 5

- [ ] T071 [P] [US5] Create mike configuration template for Sphinx in template/files/python/docs/mike.yml.jinja
- [ ] T072 [P] [US5] Document mike workflow (mike deploy, mike set-default) in template/files/python/docs/VERSIONING.md.jinja
- [ ] T073 [P] [US5] Configure Docusaurus native versioning in docusaurus.config.js.jinja (versions array, version dropdown)
- [ ] T074 [P] [US5] Create Fumadocs version switcher component in template/files/node/docs/fumadocs/components/VersionSwitcher.tsx.jinja
- [ ] T075 [P] [US5] Document Fumadocs multi-version routing pattern in template/files/node/docs/fumadocs/VERSIONING.md.jinja
- [ ] T076 [US5] Add conditional versioning scaffolding based on docs_versioning prompt in templates
- [ ] T077 [US5] Test versioning with Sphinx: set up mike, deploy multiple versions, verify version selector
- [ ] T078 [US5] Test versioning with Docusaurus: run docs:version command, verify multiple versions build
- [ ] T079 [US5] Update upgrade guide to explain versioning setup in docs/upgrade-guide/018-docs-sites.md.jinja

**Checkpoint**: At this point, versioning should be functional when enabled (SC-008: <1s version switching)

---

## Phase 8: Documentation Validation & CI Integration

**Purpose**: Add link checking, accessibility validation, and CI workflows

### Tests for Validation

- [ ] T080 [P] Test link checking with retry logic in tests/test_docs_validation.py::test_link_check_with_retry
- [ ] T081 [P] Test accessibility validation in tests/test_docs_validation.py::test_accessibility_validation
- [ ] T082 [P] Test image validation in tests/test_docs_validation.py::test_image_validation
- [ ] T083 [P] Test cross-reference validation in tests/test_docs_validation.py::test_cross_reference_validation

### Implementation for Validation

- [ ] T084 [US2] Implement DocumentationValidator class in template/files/shared/docs/validation/validator.py.jinja
- [ ] T085 [US2] Implement validate_links() with exponential backoff retry (per clarification Q2) in validator.py.jinja
- [ ] T086 [US2] Implement validate_accessibility() using axe-core (non-blocking warnings per Q3) in validator.py.jinja
- [ ] T087 [US2] Implement validate_images() for missing image detection in validator.py.jinja
- [ ] T088 [US2] Implement validate_cross_references() for invalid internal links in validator.py.jinja
- [ ] T089 [US2] Create docs build CI workflow in template/files/shared/.github/workflows/riso-docs-build.yml.jinja
- [ ] T090 [US2] Create docs validation CI workflow in template/files/shared/.github/workflows/riso-docs-validate.yml.jinja
- [ ] T091 [US2] Add pytest-axe dependency for Python accessibility tests in template/files/python/pyproject.toml.jinja
- [ ] T092 [US2] Add @axe-core/cli dependency for Node accessibility tests in template/files/node/package.json.jinja
- [ ] T093 [US2] Update render_matrix.py to run link checking during smoke tests in scripts/ci/render_matrix.py
- [ ] T094 [US2] Update record_module_success.py to track docs validation metrics in scripts/ci/record_module_success.py
- [ ] T095 [US2] Run validation test suite: uv run pytest tests/test_docs_validation.py -v
- [ ] T096 [US2] Test CI workflows locally: verify docs build, link check, and accessibility validation jobs

**Checkpoint**: At this point, validation suite should be complete (SC-002: link checking <2% broken external links, SC-006: <5 min link check)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, optimization, and final quality checks

- [ ] T097 [P] Create comprehensive module documentation in docs/modules/docs-site.md.jinja explaining all features
- [ ] T098 [P] Create upgrade guide with migration paths in docs/upgrade-guide/018-docs-sites.md.jinja
- [ ] T099 [P] Document framework migration (Sphinx ↔ Fumadocs ↔ Docusaurus) in docs/guidance/framework-migration.md.jinja
- [ ] T100 [P] Add environment variable documentation for search/deployment credentials in module docs
- [ ] T101 Document build performance optimization tips (caching, incremental builds per FR-016) in module docs
- [ ] T102 Update AGENTS.md with new docs features and commands
- [ ] T103 Update copilot-instructions.md with docs technologies and patterns in .github/copilot-instructions.md
- [ ] T104 Add docs examples to quickstart.md template in docs/quickstart.md.jinja
- [ ] T105 Run full render matrix: uv run python scripts/ci/render_matrix.py
- [ ] T106 Verify all sample smoke tests pass: check samples/metadata/module_success.json for 100% docs success
- [ ] T107 Run quality suite on template code: make quality from repository root
- [ ] T108 Verify build times meet SC-004 (<90s for <100 pages): measure builds in samples/
- [ ] T109 Run quickstart validation commands from quickstart.md in multiple sample renders
- [ ] T110 Final constitution check: verify all 7 principles respected (Module Sovereignty, Deterministic Generation, etc.)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start immediately after Foundational - CRITICAL PATH
  - User Story 2 (P1): Can start immediately after Foundational - parallel with US1
  - User Story 3 (P2): Can start after Foundational - depends on T005-T011
  - User Story 4 (P2): Can start after US3 (depends on transformation system)
  - User Story 5 (P3): Can start after Foundational - independent of other stories
- **Validation (Phase 8)**: Can start after Foundational - parallel with user stories
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Sphinx Fix**: CRITICAL PATH - No dependencies on other stories
- **User Story 2 (P1) - Configuration Prompts**: No dependencies on other stories
- **User Story 3 (P2) - Content Transformation**: Depends on Foundational entities (T005-T009)
- **User Story 4 (P2) - Interactive Features**: Soft dependency on US3 (uses transformation system)
- **User Story 5 (P3) - Versioning**: No dependencies on other stories
- **Phase 8 - Validation**: No dependencies on user stories (can run in parallel)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (US3, Phase 8)
- Template files before integration/testing
- Individual features can run in parallel when marked [P]
- Story must be independently testable before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks marked [P] can run in parallel (T002, T003)

**Phase 2 (Foundational)**: All tasks marked [P] can run in parallel (T005-T009)

**Phase 3 (US1 - Sphinx)**: Sequential implementation, but T017-T019 can run as verification batch

**Phase 4 (US2 - Prompts)**: Many tasks can run in parallel:
- T021-T026: All prompt additions can run in parallel
- T027-T028: Search configurations can run in parallel
- T032-T034: Deployment configs can run in parallel

**Phase 5 (US3 - Transformation)**: Tests can all run in parallel (T038-T045), implementations are more sequential

**Phase 6 (US4 - Interactive Features)**:
- T058-T060: Mermaid configs can run in parallel
- T061-T064: API playground templates can run in parallel

**Phase 7 (US5 - Versioning)**: All tasks marked [P] can run in parallel (T071-T075)

**Phase 8 (Validation)**: Tests can all run in parallel (T080-T083), validations can run in parallel (T084-T088)

**Phase 9 (Polish)**: All documentation tasks marked [P] can run in parallel (T097-T100)

---

## Parallel Example: User Story 3 (Content Transformation)

```bash
# Launch all transformation tests together:
Task T038: "Test Markdown → RST heading conversion"
Task T039: "Test Markdown → RST code block conversion"
Task T040: "Test Markdown → RST link conversion"
Task T041: "Test Markdown → RST list conversion"
Task T042: "Test Markdown → MDX minimal transformation"
Task T043: "Test Mermaid → RST directive conversion"
Task T044: "Test transformation failure handling"
Task T045: "Test frontmatter transformation"

# All tests should FAIL initially, then implement transformations sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T011) - CRITICAL
3. Complete Phase 3: User Story 1 - Sphinx Fix (T012-T020)
4. **STOP and VALIDATE**: Test Sphinx independently (0% → 100% smoke tests)
5. Deploy/demo if ready

**Estimated effort**: ~15 tasks, ~2-3 days for 1 developer

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~10 tasks)
2. Add User Story 1 (Sphinx Fix) → Test independently → Demo (MVP! SC-003) (~9 tasks)
3. Add User Story 2 (Configuration Prompts) → Test independently → Demo (SC-004) (~17 tasks)
4. Add User Story 3 (Content Transformation) → Test independently → Demo (SC-007) (~20 tasks)
5. Add User Story 4 (Interactive Features) → Test independently → Demo (~13 tasks)
6. Add User Story 5 (Versioning) → Test independently → Demo (SC-008) (~9 tasks)
7. Add Phase 8 (Validation) → Test independently → Demo (SC-002, SC-006) (~17 tasks)
8. Complete Polish → Final validation (~14 tasks)

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

- **Developer A**: User Story 1 (Sphinx Fix) - CRITICAL PATH
- **Developer B**: User Story 2 (Configuration Prompts) - HIGH VALUE
- **Developer C**: Foundational tests + Validation infrastructure (Phase 8)

Once US1 and US2 are complete:
- **Developer A**: User Story 3 (Content Transformation)
- **Developer B**: User Story 4 (Interactive Features) - depends on US3
- **Developer C**: User Story 5 (Versioning) - independent

---

## Success Criteria Checklist

Track progress against spec.md success criteria:

- [ ] **SC-001**: 100% of docs variants build successfully on first render (validate with render_matrix.py)
- [ ] **SC-002**: Link checking completes with 0 broken internal links, <2% broken external links (validate with link checker)
- [ ] **SC-003**: Sphinx smoke tests achieve 100% pass rate (currently 0% - PRIMARY GOAL for US1)
- [ ] **SC-004**: Build time <90 seconds for <100 pages (measure in samples/)
- [ ] **SC-005**: 95% of users customize through prompts only (post-launch survey)
- [ ] **SC-006**: Search results <200ms local, <500ms hosted (p95 latency)
- [ ] **SC-007**: API playgrounds execute 98% of valid requests (test corpus of 50+ scenarios)
- [ ] **SC-008**: Version switching <1 second (measure time from selection to render)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story (US1-US5) for traceability
- Each user story should be independently completable and testable
- Tests marked with "Write FIRST, ensure they FAIL" follow TDD workflow
- Commit after each task or logical group for incremental progress
- Stop at any checkpoint to validate story independently
- **Critical Path**: Phase 1 → Phase 2 → User Story 1 (Sphinx fix) is the MVP
- Sphinx fix is the highest priority as it's currently at 0% pass rate (spec.md clarification)

---

**Total Tasks**: 110  
**MVP Tasks** (Setup + Foundational + US1): 20 tasks  
**Task Breakdown**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US1 - Sphinx Fix): 9 tasks ← MVP COMPLETE HERE
- Phase 4 (US2 - Configuration): 17 tasks
- Phase 5 (US3 - Transformation): 20 tasks
- Phase 6 (US4 - Interactive): 13 tasks
- Phase 7 (US5 - Versioning): 9 tasks
- Phase 8 (Validation): 17 tasks
- Phase 9 (Polish): 14 tasks

**Parallel Opportunities**: ~40 tasks marked [P] can run in parallel within their phases

**Estimated Timeline** (1 developer, sequential):
- MVP (Phases 1-3): 2-3 days
- Full Feature (All phases): 2-3 weeks

**Estimated Timeline** (3 developers, parallel):
- MVP (Phases 1-3): 1-2 days
- Full Feature (All phases): 1-1.5 weeks

````