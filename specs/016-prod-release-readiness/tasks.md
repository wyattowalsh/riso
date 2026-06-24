# Tasks: Production Release Readiness

## Phase 1: Research And Design

- [x] R001 [P] Capture external release, docs, skills, and package references.
- [x] R002 [P] Record the no-legacy-answer decision.
- [x] R003 [P] Define release gate classes and evidence fields.
- [x] R004 [P] Define maintainer-only skill placement and mirror policy.
- [x] D001 [P] Write canonical answer schema contract.
- [x] D002 [P] Write release gate schema contract.
- [x] D003 [P] Write data model and quickstart artifacts.

## Phase 2: Parallel Implementation

- [ ] T001 [P] Remove active legacy answer keys from template prompts.
- [ ] T002 [P] Add fail-fast validation for removed answer keys.
- [ ] T003 [P] Remove post-gen pre-commit installation side effects.
- [ ] T004 [P] Migrate checked sample answers to canonical keys.
- [ ] T005 [P] Update render scripts and metadata to canonical keys.
- [ ] T006 [P] Update MCP tools/resources/prompts to canonical keys.
- [ ] T007 [P] Update web wizard/store/presets to canonical keys.
- [ ] T008 [P] Fix docs warnings and stale answer-key examples.
- [ ] T009 [P] Align pnpm and release workflow blocking gates.
- [ ] T010 [P] Add maintainer-only release-readiness skill.

## Phase 3: Validation

- [ ] V001 Validate no active removed-key references remain.
- [ ] V002 Validate skill mirror and frontmatter.
- [ ] V003 Run focused hook/template/render tests.
- [ ] V004 Run docs `sphinx-build -W`.
- [ ] V005 Run MCP focused tests.
- [ ] V006 Run web lint/tests/build/e2e.
- [ ] V007 Run full Python quality and tests.
- [ ] V008 Run render matrix.
- [ ] V009 Run package build, metadata, install smoke, and dry-run release.
- [ ] V010 Update `tmp/riso-prod-ready-release-todo.md` with final evidence.

