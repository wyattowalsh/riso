# Tasks: Documentation Sites Overhaul

**Input**: Design documents from `/specs/018-docs-sites-overhaul/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification. This implementation focuses on smoke tests and validation scripts per the existing quality framework.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Template system structure (from plan.md):

- `template/` - Copier template files
- `template/files/python/docs/` - Sphinx-specific templates
- `template/files/node/docs/` - Fumadocs/Docusaurus templates
- `template/files/shared/docs/` - Shared transformation logic
- `scripts/ci/` - CI validation scripts
- `samples/docs-*/` - Sample renders for testing

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for documentation overhaul

- [ ] T001 Create directory structure for shared documentation transformation system in template/files/shared/docs/
- [ ] T002 [P] Create directory structure for Python docs templates in template/files/python/docs/
- [ ] T003 [P] Create directory structure for Node docs templates in template/files/node/docs/
- [ ] T004 [P] Verify contracts directory exists and validate completeness of API specifications in specs/018-docs-sites-overhaul/contracts/ (prompts.yml, transformation-api.md, validation-api.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [FR-001] Add 7 new documentation configuration prompts to template/copier.yml (docs_theme_mode, docs_search_provider, docs_api_playground, docs_deploy_target, docs_versioning, docs_interactive_features, docs_quality_gates)
- [ ] T006 [P] [FR-009] Create shared transformation module base in template/files/shared/docs/transformation/common.py.jinja
- [ ] T007 [P] [FR-013] Create shared validation module base in template/files/shared/docs/validation/common.py.jinja
- [ ] T008 [FR-001] Update samples answer files with new documentation prompts in samples/docs-sphinx/copier-answers.yml, samples/docs-fumadocs/copier-answers.yml, samples/docs-docusaurus/copier-answers.yml
- [ ] T009 [FR-005] Create validation script framework in scripts/ci/validate_docs_config.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Sphinx Documentation Builds Successfully (Priority: P1) 🎯 MVP

**Goal**: Fix critical Sphinx failures - move smoke test pass rate from 0% to 100%

**Independent Test**: Render with `docs_site=sphinx-shibuya`, run `uv run make -f Makefile.docs docs` and `uv run make -f Makefile.docs linkcheck`, verify HTML output generates without errors

### Implementation for User Story 1

- [ ] T010 [P] [US1] [FR-002] Create Makefile.docs template with docs, linkcheck, doctest, clean-docs targets in template/files/python/docs/Makefile.docs.jinja
- [ ] T011 [P] [US1] [FR-003] Fix Sphinx conf.py template with sys.path modification for autodoc in template/files/python/docs/conf.py.jinja
- [ ] T012 [P] [US1] [FR-003] Add sphinx.ext.autodoc and sphinx.ext.napoleon extensions to conf.py template
- [ ] T013 [P] [US1] Configure Shibuya theme options with theme_mode support in conf.py template
- [ ] T014 [P] [US1] [FR-012] Add linkcheck retry configuration (3 attempts, 10s timeout) to conf.py template
- [ ] T015 [P] [US1] [FR-003] Configure autodoc_default_options in conf.py template
- [ ] T016 [US1] [FR-005] Update Sphinx sample render with fixed templates via ./scripts/render-samples.sh --variant docs-sphinx
- [ ] T017 [US1] [SC-003] Verify Sphinx docs build successfully in samples/docs-sphinx/render/ with uv run make -f Makefile.docs docs
- [ ] T018 [US1] [SC-003] [FR-012] Verify Sphinx linkcheck runs successfully in samples/docs-sphinx/render/ with uv run make -f Makefile.docs linkcheck
- [ ] T019 [US1] [SC-003] Update smoke-results.json to reflect 100% pass rate in samples/docs-sphinx/smoke-results.json
- [ ] T020 [US1] [SC-003] Run render_matrix.py to validate Sphinx smoke tests pass with uv run python scripts/ci/render_matrix.py

**Checkpoint**: At this point, Sphinx documentation should build successfully with 100% smoke test pass rate

---

## Phase 4: User Story 2 - Enhanced Documentation Configuration Options (Priority: P1)

**Goal**: Enable prompt-driven configuration for theme, search, API playground, and deployment without manual file editing

**Independent Test**: Render with extended prompts like `docs_theme_mode=dark`, `docs_search_provider=algolia`, `docs_deploy_target=vercel`, verify configuration files reflect choices

### Implementation for User Story 2

- [ ] T021 [P] [US2] [FR-001] Add docs_theme_mode conditional rendering to Sphinx conf.py template in template/files/python/docs/conf.py.jinja
- [ ] T022 [P] [US2] [FR-001] [FR-006] Add docs_theme_mode conditional rendering to Fumadocs next.config.mjs template in template/files/node/docs/fumadocs/next.config.mjs.jinja
- [ ] T023 [P] [US2] [FR-001] [FR-007] Add docs_theme_mode conditional rendering to Docusaurus config template in template/files/node/docs/docusaurus/docusaurus.config.ts.jinja
- [ ] T024 [P] [US2] [FR-010] Create search provider configuration templates for local search in template/files/shared/docs/search/local.config.jinja
- [ ] T025 [P] [US2] [FR-010] Create search provider configuration templates for Algolia in template/files/shared/docs/search/algolia.config.jinja
- [ ] T026 [P] [US2] [FR-010] Create search provider configuration templates for Typesense in template/files/shared/docs/search/typesense.config.jinja
- [ ] T027 [P] [US2] [FR-001] Create deployment configuration template for GitHub Pages in template/files/shared/docs/deploy/github-pages.yml.jinja
- [ ] T028 [P] [US2] [FR-001] Create deployment configuration template for Netlify in template/files/shared/docs/deploy/netlify.toml.jinja
- [ ] T029 [P] [US2] [FR-001] Create deployment configuration template for Vercel in template/files/shared/docs/deploy/vercel.json.jinja
- [ ] T030 [P] [US2] [FR-001] Create deployment configuration template for Cloudflare in template/files/shared/docs/deploy/cloudflare.toml.jinja
- [ ] T031 [P] [US2] [FR-011] Add API playground (Swagger/ReDoc) configuration to Sphinx conf.py when api_tracks includes python
- [ ] T032 [P] [US2] [FR-011] Add API playground configuration to Fumadocs when api_tracks includes node
- [ ] T033 [US2] [SC-005] Update sample answer files to test different configuration combinations in samples/docs-sphinx/copier-answers.yml, samples/docs-fumadocs/copier-answers.yml
- [ ] T034 [US2] [SC-001] Render all documentation variants with new prompts via ./scripts/render-samples.sh
- [ ] T035 [US2] [FR-005] [SC-005] Validate generated configuration files match prompt selections with uv run python scripts/ci/validate_docs_config.py
- [ ] T036 [US2] [SC-001] Update smoke tests to verify configuration options in samples/*/smoke-results.json

**Checkpoint**: At this point, all prompt-driven configuration options should work without manual file editing

---

## Phase 5: User Story 3 - Unified Documentation Content Management (Priority: P2)

**Goal**: Enable shared documentation content transformation across frameworks (Markdown → MDX/RST)

**Independent Test**: Update docs/modules/quality.md.jinja, re-render all three doc variants, verify identical content appears correctly formatted in each framework

### Implementation for User Story 3

- [ ] T037 [P] [US3] [FR-004] Implement AST-based Markdown parser with frontmatter extraction in template/files/shared/docs/transformation/common.py.jinja
- [ ] T038 [P] [US3] [FR-009] Implement Markdown to RST transformer in template/files/shared/docs/transformation/markdown_to_rst.py.jinja
- [ ] T039 [P] [US3] [FR-009] Implement Markdown to MDX transformer in template/files/shared/docs/transformation/markdown_to_mdx.py.jinja
- [ ] T040 [P] [US3] [FR-008] Implement Mermaid diagram transformation for Sphinx directives in markdown_to_rst.py.jinja
- [ ] T041 [P] [US3] [FR-009] Implement admonition transformation (Markdown → RST directives) in markdown_to_rst.py.jinja
- [ ] T042 [P] [US3] [FR-009] Implement code block transformation with language detection in markdown_to_rst.py.jinja
- [ ] T043 [P] [US3] [FR-009] Implement cross-reference transformation (Markdown links → RST :doc:) in markdown_to_rst.py.jinja
- [ ] T044 [P] [US3] [FR-004] [FR-009] Implement heading and frontmatter transformation (Markdown # → RST underlines, YAML → RST field list) in markdown_to_rst.py.jinja
- [ ] T045 [P] [US3] Add transformation error handling with file/line reporting per clarification Q1
- [ ] T046 [P] [US3] Create transformation test script in scripts/ci/test_content_transformation.py
- [ ] T047 [US3] Create shared module documentation in template/files/shared/docs/modules/docs-site.md.jinja
- [ ] T048 [US3] Create framework migration guide in template/files/shared/docs/guidance/framework-migration.md.jinja
- [ ] T049 [US3] Update quickstart documentation with transformation examples in docs/quickstart.md.jinja
- [ ] T050 [US3] Test transformation with sample content across all frameworks
- [ ] T051 [US3] Validate transformation preserves semantic meaning with uv run python scripts/ci/test_content_transformation.py

**Checkpoint**: At this point, shared documentation content should transform correctly across all three frameworks

---

## Phase 6: User Story 4 - Interactive Documentation Features (Priority: P2)

**Goal**: Enable Mermaid diagrams, API playgrounds, and interactive elements through prompt configuration

**Independent Test**: Render with `docs_interactive_features=enabled`, verify API playground, Mermaid diagrams render correctly in all frameworks

### Implementation for User Story 4

- [ ] T052 [P] [US4] [FR-008] Create shared Mermaid rendering utility in template/files/shared/docs/utilities/mermaid_renderer.py.jinja for Sphinx
- [ ] T053 [P] [US4] [FR-008] Create Mermaid configuration for Fumadocs in template/files/node/docs/fumadocs/mermaid.config.ts.jinja
- [ ] T054 [P] [US4] [FR-008] Create Mermaid configuration for Docusaurus in template/files/node/docs/docusaurus/mermaid.config.ts.jinja
- [ ] T055 [US4] [FR-008] [FR-011] Add automatic Mermaid theming based on docs_theme_mode to all framework configs
- [ ] T056 [P] [US4] [FR-008] Create test documentation page with sample Mermaid diagrams (flowchart, sequence, class) in template/files/shared/docs/examples/diagrams.md.jinja
- [ ] T057 [US4] [SC-007] Add Mermaid test cases to smoke tests in scripts/ci/smoke_test_docs.py
- [ ] T058 [P] [US4] [FR-011] Create shared link checker configuration in template/files/shared/docs/utilities/link_checker.py.jinja
- [ ] T059 [US4] [FR-011] Integrate link checker into Makefile.docs check target
- [ ] T060 [P] [US4] [FR-011] Create shared accessibility scanner configuration in template/files/shared/docs/utilities/a11y_scanner.py.jinja (using pa11y or axe-core)
- [ ] T061 [US4] [FR-011] Integrate accessibility scanner into Makefile.docs check target
- [ ] T062 [US4] [SC-008] Add link checker test cases to smoke tests in scripts/ci/smoke_test_docs.py
- [ ] T063 [US4] [SC-009] Add accessibility scanner test cases to smoke tests in scripts/ci/smoke_test_docs.py
- [ ] T064 [US4] Render samples and validate Mermaid/link checking/a11y features with ./scripts/render-samples.sh --variant docs-sphinx

**Checkpoint**: At this point, all documentation sites should support Mermaid diagrams, link checking, and accessibility scanning with zero manual configuration

---

## Phase 7: User Story 5 - Documentation Versioning and Multi-Version Support (Priority: P3)

**Goal**: Enable documentation versioning with version selector UI when docs_versioning=enabled

**Independent Test**: Render with `docs_versioning=enabled`, verify version selector scaffolding and configuration files are generated

### Implementation for User Story 5

- [ ] T065 [P] [US5] [FR-015] Create shared version dropdown component template in template/files/shared/docs/components/version_dropdown.jinja
- [ ] T066 [P] [US5] [FR-015] Integrate version dropdown into Sphinx sidebar via conf.py template
- [ ] T067 [P] [US5] [FR-015] Integrate version dropdown into Fumadocs layout component
- [ ] T068 [P] [US5] [FR-015] Integrate version dropdown into Docusaurus navbar component
- [ ] T069 [US5] [FR-015] Create version switcher configuration file template in template/files/shared/docs/versioning/versions.json.jinja
- [ ] T070 [US5] [FR-015] Add version detection logic to shared utilities in template/files/shared/docs/utilities/version_detector.py.jinja
- [ ] T071 [US5] [FR-015] Document version management workflow in docs/modules/versioning.md.jinja
- [ ] T072 [US5] [SC-010] Add version switcher test cases to smoke tests in scripts/ci/smoke_test_docs.py
- [ ] T073 [US5] Render samples with versioning enabled and validate version switcher UI with ./scripts/render-samples.sh

**Checkpoint**: At this point, all documentation sites should have a working version switcher UI with dropdown navigation

---

## Phase 8: Documentation Validation & Quality Gates

**Purpose**: Implement link checking, accessibility validation, and quality automation

- [ ] T074 [P] [FR-011] Implement link checker with exponential backoff retry logic (3 attempts, 1s→2s→4s delays) in template/files/shared/docs/validation/link_checker.py.jinja
- [ ] T075 [P] [FR-011] Implement accessibility validator using axe-core with WCAG 2.1 AA checking (non-blocking warnings per Q3) in template/files/shared/docs/validation/accessibility.py.jinja
- [ ] T076 [P] [FR-011] Implement image reference validator in template/files/shared/docs/validation/image_validator.py.jinja
- [ ] T077 [P] [FR-011] Implement cross-reference validator for Sphinx :doc: and :ref: in template/files/shared/docs/validation/cross_ref_validator.py.jinja
- [ ] T078 [P] [FR-012] Create GitHub Actions workflow for docs build in template/files/shared/.github/workflows/riso-docs-build.yml.jinja
- [ ] T079 [P] [FR-012] Create GitHub Actions workflow for docs validation in template/files/shared/.github/workflows/riso-docs-validate.yml.jinja
- [ ] T080 [FR-013] Update render_matrix.py to include documentation validation in smoke tests at scripts/ci/render_matrix.py
- [ ] T081 [FR-013] Update record_module_success.py to track documentation module success rates at scripts/ci/record_module_success.py
- [ ] T082 [FR-012] Add documentation validation to quality suite integration
- [ ] T083 [FR-011] [SC-008] Test link checking with retry logic on sample documentation
- [ ] T084 [FR-011] [SC-009] Test accessibility validation produces WCAG 2.1 AA warnings without blocking builds
- [ ] T085 [FR-012] Validate all documentation workflows in CI

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final documentation

- [ ] T086 [P] [FR-014] Create comprehensive module documentation guide in docs/modules/docs-site.md.jinja
- [ ] T087 [P] [FR-014] Create upgrade guide for documentation framework migrations in docs/upgrade-guide/018-docs-sites.md.jinja
- [ ] T088 [P] [FR-014] Update AGENTS.md with new documentation dependencies and technologies
- [ ] T089 [P] [FR-014] Update .github/copilot-instructions.md with documentation build commands
- [ ] T090 [FR-014] Add documentation examples to quickstart.md.jinja
- [ ] T091 [FR-014] Update constitution.md to document documentation standards (if needed)
- [ ] T092 [FR-013] Create comprehensive smoke tests for all documentation features (Mermaid, link checking, accessibility)
- [ ] T093 [FR-013] Create performance benchmarks for documentation builds (<5 seconds per SC-003)
- [ ] T094 [FR-013] Update samples/metadata/doc_publish.json with final validation metrics
- [ ] T095 [FR-013] [FR-014] Validate documentation completeness and upgrade guide completeness (FR-014)
- [ ] T096 [FR-013] [SC-004] Validate documentation builds complete in <5 seconds for projects with <100 Markdown source files (per SC-004)
- [ ] T097 [FR-013] Final smoke test run: uv run python scripts/ci/render_matrix.py
- [ ] T098 [FR-013] Final validation: All smoke tests pass for docs-sphinx, docs-fumadocs, docs-docusaurus variants
- [ ] T099 [FR-013] [SC-001] Final validation: Sphinx smoke test pass rate reaches 100% (from 0%)
- [ ] T100 [FR-013] Update feature implementation completion checklist in specs/018-docs-sites-overhaul/spec.md
- [ ] T091 Update README templates with documentation configuration instructions
- [ ] T092 Verify all sample renders build successfully with new configuration options
- [ ] T093 Run full quality suite on all documentation variants with make quality
- [ ] T094 Update module_success.json with documentation smoke test results
- [ ] T095 Validate quickstart.md instructions work end-to-end and upgrade guide completeness (FR-014)
- [ ] T096 Performance test: Verify documentation builds complete in <90 seconds for projects with <100 Markdown source files (per SC-004)
- [ ] T097 Performance test: Verify link checking completes in <5 minutes
- [ ] T098 Final validation: All smoke tests pass for docs-sphinx, docs-fumadocs, docs-docusaurus variants
- [ ] T099 Final validation: Sphinx smoke test pass rate reaches 100% (from 0%)
- [ ] T100 Update feature implementation completion checklist in specs/018-docs-sites-overhaul/spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - P1 priority (MVP)
- **User Story 2 (Phase 4)**: Depends on Foundational - P1 priority, can run parallel with US1
- **User Story 3 (Phase 5)**: Depends on Foundational - P2 priority, independent of US1/US2
- **User Story 4 (Phase 6)**: Depends on Foundational + US3 (transformation system) - P2 priority
- **User Story 5 (Phase 7)**: Depends on Foundational + US1/US2 - P3 priority (advanced feature)
- **Validation (Phase 8)**: Can start after Foundational, runs parallel with user stories
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Sphinx Fix)**: CRITICAL PATH - No dependencies on other stories, must complete first
- **User Story 2 (P1 - Configuration)**: Can run parallel with US1 - No dependencies on other stories
- **User Story 3 (P2 - Content Management)**: Independent - Requires transformation system foundation
- **User Story 4 (P2 - Interactive Features)**: Depends on US3 transformation system
- **User Story 5 (P3 - Versioning)**: Depends on US1/US2 working configurations

### Critical Path (MVP)

1. Phase 1: Setup (T001-T004)
2. Phase 2: Foundational (T005-T009) ⚠️ BLOCKS everything
3. **Phase 3: User Story 1** (T010-T020) 🎯 MVP - Sphinx must work
4. Validate: Sphinx smoke tests 0% → 100%

### Within Each User Story

- **US1**: Sphinx templates → render → test → validate smoke tests (sequential)
- **US2**: All configuration templates can be done in parallel (marked [P]) → render → validate
- **US3**: All transformation modules can be done in parallel (marked [P]) → test → validate
- **US4**: All interactive feature templates in parallel (marked [P]) → test → validate
- **US5**: All versioning templates in parallel (marked [P]) → document → test

### Parallel Opportunities

#### After Foundational Phase Completes

```text
┌─────────────────────────────────────────────────────┐
│ Foundational Phase Complete (T005-T009)             │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
    ▼             ▼             ▼              ▼
┌───────┐    ┌───────┐    ┌───────┐    ┌──────────┐
│  US1  │    │  US2  │    │ Phase │    │   US3    │
│(T010- │    │(T021- │    │   8   │    │ (start   │
│ T020) │    │ T036) │    │(T074- │    │  after   │
│       │    │       │    │ T085) │    │  US1/2)  │
└───────┘    └───────┘    └───────┘    └──────────┘
```

#### Within User Story 2 (Configuration)

- T021-T030 (all configuration templates) can run in parallel
- T031-T032 (API playground configs) can run in parallel
- Then T033-T036 (render and validate) run sequentially

#### Within User Story 3 (Transformation)

- T037-T044 (all transformer implementations) can run in parallel
- T046 (test script) in parallel with T047-T049 (documentation)
- Then T050-T051 (test and validate) run sequentially

#### Within User Story 4 (Interactive)

- T052-T054 (Mermaid configs) in parallel
- T055-T060 (API playground and code tabs) in parallel
- Then T061-T064 (test and validate) run sequentially

---

## Parallel Example: User Story 1 (Critical Path)

```bash
# These Sphinx template tasks can run in parallel:
T010: "Create Makefile.docs template"
T011: "Fix Sphinx conf.py template"
T012: "Add autodoc extensions"
T013: "Configure Shibuya theme"
T014: "Add linkcheck retry config"
T015: "Configure autodoc options"

# Then these run sequentially:
T016: "Update Sphinx sample render" (depends on T010-T015)
T017: "Verify docs build" (depends on T016)
T018: "Verify linkcheck" (depends on T016)
T019: "Update smoke-results.json" (depends on T017-T018)
T020: "Run render_matrix.py" (depends on T019)
```

---

## Parallel Example: User Story 2 (Configuration)

```bash
# All configuration templates in parallel:
T021: "Sphinx theme config"
T022: "Fumadocs theme config"
T023: "Docusaurus theme config"
T024: "Local search template"
T025: "Algolia search template"
T026: "Typesense search template"
T027: "GitHub Pages deploy config"
T028: "Netlify deploy config"
T029: "Vercel deploy config"
T030: "Cloudflare deploy config"

# API playground configs in parallel:
T031: "Sphinx API playground"
T032: "Fumadocs API playground"

# Then sequentially:
T033: "Update sample answers"
T034: "Render all variants"
T035: "Validate configs"
T036: "Update smoke tests"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Sphinx Fix)

**Critical Path to MVP**:

1. ✅ Complete Phase 1: Setup (T001-T004)
2. ✅ Complete Phase 2: Foundational (T005-T009) - BLOCKING
3. 🎯 Complete Phase 3: User Story 1 (T010-T020) - Sphinx Fix
4. **STOP and VALIDATE**:
   - Sphinx smoke test pass rate: 0% → 100%
   - Run `uv run make -f Makefile.docs docs` successfully
   - Run `uv run make -f Makefile.docs linkcheck` successfully
5. **MVP COMPLETE** - Sphinx documentation is functional

**Why this MVP**: Sphinx is currently at 0% smoke test pass rate (critical blocker). Fixing this unblocks Python teams and demonstrates immediate value.

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + Foundational → Foundation ready
2. **MVP** (Phase 3): User Story 1 → Sphinx works → Deploy/Demo 🎯
3. **Enhanced Configuration** (Phase 4): User Story 2 → Prompt-driven config → Deploy/Demo
4. **Content Management** (Phase 5): User Story 3 → Shared content transforms → Deploy/Demo
5. **Interactive Features** (Phase 6): User Story 4 → Mermaid + API playgrounds → Deploy/Demo
6. **Versioning** (Phase 7): User Story 5 → Multi-version support → Deploy/Demo
7. **Quality Gates** (Phase 8): Validation → CI integration → Deploy/Demo
8. **Polish** (Phase 9): Documentation + final validation → Release

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Week 1**: Team completes Setup + Foundational together (T001-T009)
2. **Week 2** (once Foundational done):
   - Developer A: User Story 1 (T010-T020) - PRIORITY
   - Developer B: User Story 2 (T021-T036)
   - Developer C: Phase 8 Validation (T074-T085)
3. **Week 3**:
   - Developer A: User Story 3 (T037-T051)
   - Developer B: User Story 4 (T052-T064)
   - Developer C: Documentation (T086-T091)
4. **Week 4**:
   - Developer A: User Story 5 (T065-T073)
   - Developer B: Final validation (T092-T099)
   - Developer C: Polish (remaining tasks)

Stories complete and integrate independently.

---

## Success Metrics

Track progress against spec.md success criteria:

- [ ] **SC-001**: 100% of documentation variants build successfully on first render
  - Validated by: T092, T098
  
- [ ] **SC-002**: Link checking <2% broken external links after 3 retries
  - Validated by: T083
  
- [ ] **SC-003**: Sphinx smoke tests 0% → 100% pass rate
  - Validated by: T019, T020, T099
  
- [ ] **SC-004**: Documentation builds <90 seconds for <100 pages
  - Validated by: T096
  
- [ ] **SC-005**: 95% of users customize via prompts without file editing
  - Validated by: T035, T092
  
- [ ] **SC-006**: Search returns results <200ms (local) <500ms (hosted)
  - Validated by: T062 (manual testing)
  
- [ ] **SC-007**: API playgrounds execute 98% of valid requests
  - Validated by: T062
  
- [ ] **SC-008**: Version switching <1 second
  - Validated by: T071

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Commit after each task** or logical group for atomic changes
- **Stop at any checkpoint** to validate story independently
- Focus on **User Story 1 first** (Sphinx fix) - it's the critical blocker at 0% pass rate
- Transformation system (US3) is foundation for interactive features (US4)
- Versioning (US5) is advanced feature - can be deferred if needed

---

**Total Tasks**: 100 tasks across 9 phases

**Tasks by Priority**:

- P1 (Critical): User Story 1 (11 tasks) + User Story 2 (16 tasks) = 27 tasks
- P2 (High Value): User Story 3 (15 tasks) + User Story 4 (13 tasks) = 28 tasks
- P3 (Advanced): User Story 5 (9 tasks) = 9 tasks
- Infrastructure: Setup (4) + Foundational (5) + Validation (12) + Polish (15) = 36 tasks

**Parallel Opportunities**: 55 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phase 1-3 (Setup + Foundational + User Story 1) = 24 tasks to achieve Sphinx 0% → 100% pass rate

**Status**: ✅ Ready for implementation - Start with T001
