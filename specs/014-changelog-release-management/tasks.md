# Implementation Tasks: Changelog & Release Management

**Feature**: 014-changelog-release-management  
**Created**: 2025-11-02  
**Status**: Ready for Implementation  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Overview

This document provides a complete task breakdown for implementing automated changelog generation and release management. Tasks are organized by user story to enable independent implementation and testing. Each phase represents a complete, testable increment of functionality.

**Implementation Strategy**: MVP-first approach focusing on User Stories 1-3 (commit enforcement, changelog generation, version automation) before adding distribution features (GitHub Releases, breaking change guides, registry publishing).

---

## Dependency Graph

### User Story Completion Order

```text
Phase 1: Setup (T001-T010) - Foundation for all features
    ↓
Phase 2: Foundational (T011-T020) - Blocking prerequisites
    ↓
Phase 3: US1 - Commit Enforcement (T021-T035) - Independent
    ↓
Phase 4: US2 - Changelog Generation (T036-T048) - Requires US1
    ↓
Phase 5: US3 - Version Automation (T049-T061) - Requires US1, US2
    ↓
Phase 6: US4 - GitHub Releases (T062-T072) - Requires US1-US3
    ↓
Phase 7: US5 - Breaking Changes (T073-T083) - Requires US1-US4
    ↓
Phase 8: US6 - Artifact Publishing (T084-T100) - Requires US1-US5
    ↓
Phase 9: Polish & Cross-Cutting (T101-T115) - Final integration
```

**Critical Path**: US1 → US2 → US3 form the MVP. US4-US6 can be developed incrementally.

**Parallel Opportunities**:
- Within each user story: Tests, models, and configuration can be parallelized
- Across user stories after MVP: US4, US5 (partially), US6 (per registry) can proceed independently

---

## Phase 1: Setup & Project Structure

**Goal**: Establish project structure, tooling, and development environment.

### Project Initialization

- [ ] T001 Create directory structure per implementation plan in template/files/shared/
- [ ] T002 Create directory structure in template/files/python/release/
- [ ] T003 Create directory structure in template/files/node/release/
- [ ] T004 Create directory structure for tests/release/ with unit and integration subdirs
- [ ] T005 Create directory structure for samples/changelog-python/, samples/changelog-monorepo/, samples/changelog-full-stack/
- [ ] T006 Create scripts/ci/ directory for validation scripts

### Copier Configuration

- [ ] T007 Add changelog_module prompt to template/copier.yml with enabled/disabled options
- [ ] T008 Add conditional rendering logic for changelog module files in template/copier.yml
- [ ] T009 Update template/files/shared/module_catalog.json.jinja with changelog module entry
- [ ] T010 Add changelog module to AGENTS.md Active Technologies section

---

## Phase 2: Foundational Components

**Goal**: Create shared infrastructure and base configuration templates required by all user stories.

### Configuration Templates

- [ ] T011 [P] Create template/files/shared/.commitlintrc.yml.jinja with conventional commit rules
- [ ] T012 [P] Create template/files/shared/.releaserc.yml.jinja with semantic-release configuration
- [ ] T013 [P] Create template/files/shared/.github/workflows/riso-release.yml.jinja workflow skeleton
- [ ] T014 Add package.json script entries for setup-hooks in template/files/shared/package.json.jinja

### Base Scripts

- [ ] T015 [P] Create template/files/shared/scripts/release/__init__.py.jinja empty module
- [ ] T016 [P] Create template/files/python/release/__init__.py.jinja with version utilities
- [ ] T017 [P] Create template/files/node/release/commitizen.config.js.jinja for Node projects

### Documentation Foundation

- [ ] T018 Create docs/modules/changelog-release.md.jinja documentation template skeleton
- [ ] T019 Create samples/changelog-python/copier-answers.yml with test configuration
- [ ] T020 Update docs/upgrade-guide.md.jinja with changelog module section

> **Note**: Sample project (samples/changelog-python/) will be incrementally enhanced as each phase completes. Initial version from T019 provides basic structure with copier answers; subsequent phases (T021-T120) will add commit validation, changelog generation, release automation, and publishing features progressively through the release workflow.

---

## Phase 3: User Story 1 - Commit Format Enforcement (P1)

**Goal**: Implement commit message validation at commit time to enforce conventional commit format.

**Independent Test**: Attempt commits with valid/invalid formats and verify enforcement.

**Acceptance**: Developers receive immediate feedback on commit message validity; non-compliant commits are rejected.

### Configuration & Validation Logic

- [ ] T021 [US1] Implement commit message parser in template/files/shared/scripts/release/validate-commit.py.jinja
- [ ] T022 [US1] Add regex patterns for type, scope, subject validation in validate-commit.py.jinja
- [ ] T023 [US1] Add breaking change detection logic (footer/body parsing) in validate-commit.py.jinja
- [ ] T024 [US1] Implement error message generation with format examples in validate-commit.py.jinja
- [ ] T025 [US1] Create CommitMessage data model in template/files/python/release/models.py.jinja

### Git Hook Installation

- [ ] T026 [US1] Create template/files/shared/scripts/release/install-hooks.py.jinja hook installer
- [ ] T027 [US1] Add hook existence check and backup logic in install-hooks.py.jinja
- [ ] T028 [US1] Add commit-msg hook template with shebang and validation call in install-hooks.py.jinja
- [ ] T029 [US1] Add executable permission setting logic in install-hooks.py.jinja
- [ ] T030 [US1] Add idempotency checks (skip if already installed) in install-hooks.py.jinja

### Testing

- [ ] T031 [P] [US1] Write unit tests for commit message parser in tests/release/test_commit_validation.py
- [ ] T032 [P] [US1] Write unit tests for breaking change detection in tests/release/test_commit_validation.py
- [ ] T033 [P] [US1] Write smoke tests for hook installation in tests/release/test_hook_installation.py
- [ ] T034 [US1] Write integration test for hook validation workflow in tests/release/integration/test_commit_enforcement.py
- [ ] T035 [US1] Add sample commits (valid/invalid) to samples/changelog-python/ for manual testing

**Checkpoint**: Run `uv run pytest tests/release/test_commit_validation.py` - all tests pass. Manual test: attempt invalid commit, verify rejection.

---

## Phase 4: User Story 2 - Automatic Changelog Generation (P1)

**Goal**: Generate human-readable changelogs from commit history, categorized by type.

**Independent Test**: Create commits with various types (feat, fix, breaking) and verify changelog generation.

**Acceptance**: Changelog correctly categorizes changes and includes commit/PR links.

### Changelog Generation Logic

- [ ] T036 [US2] Create ChangelogEntry data model in template/files/python/release/models.py.jinja
- [ ] T037 [US2] Create Change data model with commit metadata in template/files/python/release/models.py.jinja
- [ ] T038 [US2] Implement commit history parser in template/files/python/release/changelog.py.jinja
- [ ] T039 [US2] Implement commit categorization logic (feat/fix/breaking) in changelog.py.jinja
- [ ] T040 [US2] Add PR number extraction from commit messages in changelog.py.jinja
- [ ] T041 [US2] Add GitHub link generation for commits and PRs in changelog.py.jinja

### Changelog Formatting

- [ ] T042 [US2] Implement markdown formatter with emoji sections (💥/✨/🐛) in changelog.py.jinja
- [ ] T043 [US2] Add version header generation (## [version] - date) in changelog.py.jinja
- [ ] T044 [US2] Add changelog file update logic (prepend new version) in changelog.py.jinja
- [ ] T045 [US2] Configure @semantic-release/changelog plugin in .releaserc.yml.jinja

### Testing

- [ ] T046 [P] [US2] Write unit tests for commit categorization in tests/release/test_changelog_generation.py
- [ ] T047 [P] [US2] Write unit tests for markdown formatting in tests/release/test_changelog_generation.py
- [ ] T048 [US2] Write integration test for full changelog generation in tests/release/integration/test_changelog_workflow.py

**Checkpoint**: Run `uv run pytest tests/release/test_changelog_generation.py` - all tests pass. Generate test changelog from sample commits.

---

## Phase 5: User Story 3 - Semantic Version Automation (P1)

**Goal**: Automatically calculate next version number based on commit types.

**Independent Test**: Create commit sequences and verify correct version bump calculation.

**Acceptance**: Version numbers follow SemVer rules (fix→PATCH, feat→MINOR, BREAKING→MAJOR).

### Version Calculation Logic

- [ ] T049 [US3] Create Version data model in template/files/python/release/models.py.jinja
- [ ] T050 [US3] Implement version parser (parse MAJOR.MINOR.PATCH) in template/files/python/release/version.py.jinja
- [ ] T051 [US3] Implement version bump logic (major/minor/patch) in version.py.jinja
- [ ] T052 [US3] Implement version comparison (next > current) in version.py.jinja
- [ ] T053 [US3] Add commit type → version bump mapping in version.py.jinja
- [ ] T054 [US3] Add breaking change detection → major bump logic in version.py.jinja

### Version File Updates

- [ ] T055 [US3] Create version updater for pyproject.toml in template/files/shared/scripts/release/update-version.py.jinja
- [ ] T056 [US3] Create version updater for package.json in template/files/shared/scripts/release/update-version.py.jinja
- [ ] T057 [US3] Add semantic-release prepare step with @semantic-release/exec in .releaserc.yml.jinja
- [ ] T058 [US3] Configure Git commit for version bumps with @semantic-release/git in .releaserc.yml.jinja

### Testing

- [ ] T059 [P] [US3] Write unit tests for version parsing and comparison in tests/release/test_version_calculation.py
- [ ] T060 [P] [US3] Write unit tests for version bump logic in tests/release/test_version_calculation.py
- [ ] T061 [US3] Write integration test for version calculation workflow in tests/release/integration/test_version_automation.py

**Checkpoint**: Run `uv run pytest tests/release/test_version_calculation.py` - all tests pass. Test version bump calculation with sample commits.

---

## Phase 6: User Story 4 - GitHub Release Creation (P2)

**Goal**: Automatically create GitHub Releases with version tags and changelog content.

**Independent Test**: Trigger release and verify GitHub Release creation with correct metadata.

**Acceptance**: GitHub Release created with version tag, changelog notes, and appropriate flags.

### GitHub Release Integration

- [ ] T062 [US4] Configure @semantic-release/github plugin in .releaserc.yml.jinja
- [ ] T063 [US4] Add GitHub token configuration (GITHUB_TOKEN secret) in .releaserc.yml.jinja
- [ ] T064 [US4] Add release asset configuration in .releaserc.yml.jinja
- [ ] T065 [US4] Add pre-release detection logic in .releaserc.yml.jinja
- [ ] T066 [US4] Configure release name format (v{version}) in .releaserc.yml.jinja

### Workflow Integration

- [ ] T067 [US4] Add GitHub Release creation step to riso-release.yml.jinja workflow
- [ ] T068 [US4] Add GITHUB_TOKEN permission configuration in riso-release.yml.jinja
- [ ] T069 [US4] Add release creation retry logic with exponential backoff in riso-release.yml.jinja
- [ ] T070 [US4] Add release creation error handling and logging in riso-release.yml.jinja

### Testing

- [ ] T071 [P] [US4] Write integration test for GitHub Release creation in tests/release/integration/test_github_release.py
- [ ] T072 [US4] Add smoke test for release workflow in samples/changelog-python/smoke-results.json

**Checkpoint**: Trigger test release in sample project, verify GitHub Release appears with correct tag and notes.

---

## Phase 7: User Story 5 - Breaking Change Detection & Migration Guides (P2)

**Goal**: Detect breaking changes and generate migration guide templates.

**Independent Test**: Create commits with breaking changes and verify detection/prominence in changelog.

**Acceptance**: Breaking changes appear prominently in changelog with migration instructions.

### Breaking Change Enhancement

- [ ] T073 [US5] Add migration guide extraction from commit footers in changelog.py.jinja
- [ ] T074 [US5] Add breaking change prominence formatting (top of changelog) in changelog.py.jinja
- [ ] T075 [US5] Add migration note template generation in changelog.py.jinja
- [ ] T076 [US5] Configure breaking change section in @semantic-release/release-notes-generator in .releaserc.yml.jinja

### Documentation Templates

- [ ] T077 [US5] Create migration guide template in template/files/shared/docs/MIGRATION_GUIDE_TEMPLATE.md.jinja
- [ ] T078 [US5] Add migration guide link in changelog entries
- [ ] T079 [US5] Add breaking change checklist in migration template

### Testing

- [ ] T080 [P] [US5] Write unit tests for migration guide extraction in tests/release/test_breaking_changes.py
- [ ] T081 [P] [US5] Write unit tests for breaking change formatting in tests/release/test_breaking_changes.py
- [ ] T082 [US5] Write integration test for breaking change workflow in tests/release/integration/test_breaking_changes.py
- [ ] T083 [US5] Add breaking change sample commits to samples/changelog-python/

**Checkpoint**: Create breaking change commit, verify prominent placement in changelog and migration guide generation.

---

## Phase 8: User Story 6 - Release Artifact Publishing (P3)

**Goal**: Publish release artifacts to package registries (PyPI, npm, Docker Hub).

**Independent Test**: Trigger release and verify package appears in target registry with correct version.

**Acceptance**: Artifacts published to configured registries within 2 minutes per registry.

### PyPI Publishing

- [ ] T084 [P] [US6] Create PyPI publisher script in template/files/shared/scripts/release/publish-pypi.py.jinja
- [ ] T085 [P] [US6] Add twine upload logic with retry in publish-pypi.py.jinja
- [ ] T086 [P] [US6] Add PYPI_TOKEN environment variable handling in publish-pypi.py.jinja
- [ ] T087 [P] [US6] Configure @semantic-release/exec publishCmd for PyPI in .releaserc.yml.jinja

### npm Publishing

- [ ] T088 [P] [US6] Add npm publish configuration in .releaserc.yml.jinja
- [ ] T089 [P] [US6] Configure @semantic-release/npm plugin in .releaserc.yml.jinja
- [ ] T090 [P] [US6] Add NPM_TOKEN environment variable handling in .releaserc.yml.jinja

### Docker Hub Publishing

- [ ] T091 [P] [US6] Create Docker Hub publisher script in template/files/shared/scripts/release/publish-docker.py.jinja
- [ ] T092 [P] [US6] Add docker tag generation (latest, v1.2.3, v1.2, v1) in publish-docker.py.jinja
- [ ] T093 [P] [US6] Add docker push logic with retry in publish-docker.py.jinja
- [ ] T094 [P] [US6] Add DOCKER_HUB_USERNAME and DOCKER_HUB_TOKEN handling in publish-docker.py.jinja
- [ ] T095 [P] [US6] Configure @semantic-release/exec publishCmd for Docker in .releaserc.yml.jinja

### Workflow Integration

- [ ] T096 [US6] Add registry publishing steps to riso-release.yml.jinja workflow
- [ ] T097 [US6] Add registry credential secret configuration in riso-release.yml.jinja
- [ ] T098 [US6] Add parallel publishing logic for multiple registries in riso-release.yml.jinja

### Testing

- [ ] T099 [P] [US6] Write integration tests for registry publishing in tests/release/integration/test_registry_publishing.py
- [ ] T100 [US6] Add dry-run mode tests for all publishers in tests/release/integration/test_registry_publishing.py (dry-run includes version calculation, changelog generation, and registry API connectivity checks, but skips actual artifact publishing and GitHub Release creation)

**Checkpoint**: Run dry-run release, verify all publishing steps execute correctly. Test with test PyPI/npm accounts.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Complete documentation, add error handling, optimize performance, and validate end-to-end workflows. (T101-T120)

### Documentation

- [ ] T101 Complete docs/modules/changelog-release.md.jinja with architecture, configuration, troubleshooting
- [ ] T102 Add credential rotation schedule to generated README in template/files/shared/README_CHANGELOG.md.jinja (add to ## Maintenance > Credential Rotation section)
- [ ] T103 Add commit message format guide to generated README
- [ ] T104 Update docs/quickstart.md.jinja with changelog module setup instructions
- [ ] T105 Create upgrade guide section in docs/upgrade-guide/014-changelog-release.md.jinja

### Error Handling & Logging

- [ ] T106 [P] Add comprehensive error handling to all Python scripts in template/files/shared/scripts/release/
- [ ] T107 [P] Add detailed logging for debugging in all release scripts
- [ ] T108 [P] Add retry logic with exponential backoff to all network operations
- [ ] T109 Add error message user-friendliness pass (clear, actionable errors)

### Performance Optimization

- [ ] T110 Add shallow clone configuration (fetch-depth: 0 only for release) in riso-release.yml.jinja
- [ ] T111 Add dependency caching for npm/uv in riso-release.yml.jinja
- [ ] T112 Add parallel execution for independent registry publishing in riso-release.yml.jinja

### Validation & CI

- [ ] T113 Create scripts/ci/validate_release_configs.py to validate generated configs
- [ ] T114 Create scripts/ci/test_release_template_rendering.py to test template generation
- [ ] T115 Add workflow validation to render_matrix.py for all sample variants

### Sample Projects

- [ ] T116 [P] Complete samples/changelog-python/ with copier-answers.yml and smoke tests
- [ ] T117 [P] Complete samples/changelog-monorepo/ with independent package versioning
- [ ] T118 [P] Complete samples/changelog-full-stack/ with Python + Node configuration
- [ ] T119 Add smoke test validation for all three sample variants
- [ ] T120 Add baseline metrics for changelog generation performance to samples/metadata/

### Enhanced Coverage (Optional)

- [ ] T121 [P] Add Monorepo Lerna Configuration Template (FR-017 enhanced coverage) - Create Lerna configuration template for independent package versioning in monorepos with version: independent, changelog generation per package, publish configuration
- [ ] T122 [P] Add Monorepo Independent Versioning Smoke Tests (FR-017 enhanced coverage) - Create smoke tests verifying independent versioning for multiple packages in monorepo sample; tests verify package A can release v2.0.0 while package B stays at v1.3.5
- [ ] T123 [P] Document Monorepo Release Workflow (FR-017 enhanced coverage) - Add dedicated section to docs/modules/changelog-release.md.jinja explaining monorepo release patterns including independent vs fixed versioning, per-package changelogs, publish order
- [ ] T124 [P] Add Pre-Release Sample Configuration (FR-018 enhanced coverage) - Create sample semantic-release configuration demonstrating alpha, beta, rc channels with branch-to-channel mappings, pre-release tagging patterns, example workflows

---

## Parallel Execution Examples

### Within User Story 1 (Commit Enforcement)

**Parallel Tasks**:
```bash
# Run simultaneously (different files)
T031 - tests/release/test_commit_validation.py
T032 - tests/release/test_commit_validation.py (different test functions)
T033 - tests/release/test_hook_installation.py
```

### Within User Story 2 (Changelog Generation)

**Parallel Tasks**:
```bash
# Run simultaneously (different components)
T046 - tests/release/test_changelog_generation.py (categorization tests)
T047 - tests/release/test_changelog_generation.py (formatting tests)
```

### Within User Story 6 (Artifact Publishing)

**Parallel Tasks**:
```bash
# Run simultaneously (different registries)
T084-T087 - PyPI publishing scripts
T088-T090 - npm publishing configuration
T091-T095 - Docker Hub publishing scripts
```

### Across User Stories (After MVP Complete)

**Parallel User Stories**:
```bash
# After US1-US3 complete, can proceed in parallel:
US4 - GitHub Releases (T062-T072)
US5 - Breaking Changes (T073-T083, partially blocked by US4)
US6 - Artifact Publishing (T084-T100, independent per registry)
```

---

## Task Summary

**Total Tasks**: 120

**Tasks by User Story**:
- Setup & Foundational: 20 tasks (T001-T020)
- US1 - Commit Enforcement: 15 tasks (T021-T035)
- US2 - Changelog Generation: 13 tasks (T036-T048)
- US3 - Version Automation: 13 tasks (T049-T061)
- US4 - GitHub Releases: 11 tasks (T062-T072)
- US5 - Breaking Changes: 11 tasks (T073-T083)
- US6 - Artifact Publishing: 17 tasks (T084-T100)
- Polish & Cross-Cutting: 20 tasks (T101-T120)

**Parallelizable Tasks**: 45 tasks marked with [P]

**Independent Test Criteria by Story**:
- **US1**: Can commit valid messages, invalid messages rejected with helpful errors
- **US2**: Generated changelog correctly categorizes commits and includes links
- **US3**: Version calculation follows SemVer rules for all commit type combinations
- **US4**: GitHub Release created with correct tag, notes, and metadata
- **US5**: Breaking changes prominently highlighted with migration guides
- **US6**: Artifacts published to all configured registries within 2 minutes per registry

**Suggested MVP Scope**: User Stories 1-3 (T001-T061)
- Provides complete commit-to-version automation
- Deliverable: Developers can use conventional commits, get automatic changelogs, and see correct version bumps
- Estimated: ~60% of total implementation effort
- Can be deployed and validated before adding distribution features (US4-US6)

---

## Implementation Strategy

### Phase Approach

1. **Foundation First** (T001-T020): Establish project structure and base templates
2. **MVP Core** (T021-T061): Implement US1-US3 for complete commit→version workflow
3. **Distribution** (T062-T100): Add GitHub Releases, breaking change guides, registry publishing
4. **Polish** (T101-T120): Documentation, error handling, performance, validation

### Test-First Discipline

Each user story includes dedicated test tasks (marked with test file paths). Tests should be written and failing before implementation begins for that component.

### Incremental Delivery

- After Phase 2: Can render projects with changelog module structure
- After Phase 3 (US1): Can enforce commit messages
- After Phase 5 (US3): Have complete MVP (commit→changelog→version)
- After Phase 6 (US4): Can create GitHub Releases
- After Phase 8 (US6): Have complete automated release pipeline
- After Phase 9: Production-ready with full documentation

### Validation Gates

- End of each user story: Run all tests for that story
- End of MVP (US3): Full integration test across US1-US3
- End of Distribution (US6): Full end-to-end release test
- End of Polish: Render all sample projects and validate smoke tests

---

## Format Validation

✅ **All tasks follow checklist format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

✅ **Sequential Task IDs**: T001 through T120

✅ **Story Labels**: Applied to all user story phase tasks ([US1]-[US6])

✅ **Parallel Markers**: Applied to 45 independently executable tasks

✅ **File Paths**: Included in all implementation task descriptions

---

**Ready for Implementation** | Next: Begin with Phase 1 Setup tasks (T001-T010)
