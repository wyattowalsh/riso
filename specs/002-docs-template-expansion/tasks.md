---

description: "Task list template for feature implementation"
---

# Tasks: Expanded Documentation Template Options

**Input**: Design documents from `/.specify/specs/002-docs-template-expansion/` (legacy symlink available at `specs/002-docs-template-expansion/`)
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Focus on docs smoke commands baked into quickstart and CI; add unit tests only where automation requires.

**Constitution Gates**: Regenerate template samples, refresh documentation, and prove CI automation before closing the feature.

**Organization**: Tasks are grouped by user story so each increment remains independently testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish directories and sample stubs needed by all documentation variants.

- [ ] T001 Create documentation sample scaffolds in `samples/docs-fumadocs/`, `samples/docs-sphinx/`, and `samples/docs-docusaurus/` with placeholder `copier-answers.yml` entries.
- [ ] T002 [P] Establish shared guidance directory structure in `template/files/shared/docs/guidance/` for variant-specific README snippets.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide prompt options, tooling automation, CI matrix, and governance plumbing required by every story.

- [ ] T003 Update `template/copier.yml` to expose `docs_site` choices (`fumadocs`, `sphinx-shibuya`, `docusaurus`, `none`) with Fumadocs as default.
- [ ] T004 [P] Refresh `template/prompts/options.yml.jinja` descriptions to document prerequisites and implications for all documentation variants.
- [ ] T005 Implement tooling auto-provision and `docs_site=none` handling in `template/hooks/pre_gen_project.py` (mise + uv install, fail-fast logging).
- [ ] T006 [P] Extend `template/hooks/post_gen_project.py` to emit post-render guidance for selected documentation variant and opt-out messaging.
- [ ] T007 Add template-managed `.mise.toml.jinja` under `template/files/shared/` pinning Node.js 20 and pnpm ≥8 alongside README instructions.
- [ ] T008 Wire `ToolchainProvisioningAttempt` logging in hooks and ensure schema compliance using `template/hooks/pre_gen_project.py` + `template/files/shared/logic/__init__.py.jinja`.
- [ ] T009 Expand `scripts/render-samples.sh` to render docs variants, execute variant-specific commands, capture metrics, and upload smoke logs.
- [ ] T010 [P] Update `scripts/ci/render_matrix.py` to include docs permutations and stream module success data for documentation variants.
- [ ] T011 [P] Enhance `scripts/ci/track_doc_publish.py` to record artifact URLs, expirations, and checksum metadata for every docs run.
- [ ] T012 Adjust `scripts/ci/record_module_success.py` to aggregate pass/fail counts for documentation modules.
- [ ] T013 Update `.github/workflows/template-ci.yml` and `template/files/shared/.github/workflows/template-ci.yml.jinja` with docs matrix jobs using `actions/upload-artifact@v4`.
- [ ] T014 [P] Extend `scripts/automation/render_client.py` and related metadata clients to surface new documentation variant results.
- [ ] T015 Seed documentation opt-out behavior in `template/files/shared/docs/guidance/none.md.jinja` (links from README/upgrade guide).
- [ ] T016 Refresh `samples/default/copier-answers.yml` to align with new prompt defaults and add placeholder metadata entries in `samples/metadata/*.json` for docs variants.

**Checkpoint**: Foundation ready—user story development may now proceed.

---

## Phase 3: User Story 1 – Docs Variant Prompt Guides Baseline (Priority: P1) 🎯 MVP

**Goal**: Default render offers Fumadocs Next.js documentation with tailored quickstart commands and CI automation.

**Independent Test**: Render baseline (`docs_site=fumadocs`), run generated pnpm dev/build/lint commands, and confirm docs artifact uploads in CI logs.

### Implementation for User Story 1

- [ ] T017 [P] [US1] Scaffold Fumadocs Next.js workspace files (`package.json.jinja`, `next.config.mjs.jinja`, `postcss.config.cjs`, `tailwind.config.ts`) under `template/files/node/docs/fumadocs/`.
- [ ] T018 [P] [US1] Provide seeded MDX pages, navigation, and theme overrides in `template/files/node/docs/fumadocs/content/` and `app/` directories.
- [ ] T019 [US1] Update `template/files/node/pnpm-workspace.yaml.jinja` (and related `template/files/node/shared-config/logic.ts.jinja` if needed) to register the Fumadocs package.
- [ ] T020 [P] [US1] Add README snippets for Fumadocs variant to `template/files/shared/docs/guidance/fumadocs.md.jinja` and reference them from hooks/post-gen outputs.
- [ ] T021 [US1] Expand `docs/quickstart.md.jinja` and `docs/modules/docs-site.md.jinja` with Fumadocs commands, tooling expectations, and troubleshooting notes.
- [ ] T022 [P] [US1] Capture Fumadocs prompt answers in `samples/docs-fumadocs/copier-answers.yml` and align `samples/default/copier-answers.yml` with the new default selection.
- [ ] T023 [US1] Document variant in `docs/modules/sample-matrix.md.jinja` and update governance guidance in `docs/modules/governance.md.jinja` for artifact evidence.
- [ ] T024 [US1] Populate `samples/docs-fumadocs/metadata.json` and `samples/metadata/render_matrix.json` with Fumadocs timing + artifact placeholders.
- [ ] T025 [US1] Ensure hooks/post-gen quickstart messages surface pnpm commands for Fumadocs (validate in `template/hooks/post_gen_project.py`).

**Checkpoint**: Baseline render delivers working Fumadocs docs and CI automation evidence.

---

## Phase 4: User Story 2 – Python Teams Publish Shibuya Docs (Priority: P2)

**Goal**: Python-focused renders enable Sphinx Shibuya docs with uv-managed builds and link checking.

**Independent Test**: Render with `docs_site=sphinx-shibuya`, run `uv run make docs` and `uv run make linkcheck`, confirm CI artifact and link check status in smoke logs.

### Implementation for User Story 2

- [ ] T026 [P] [US2] Add optional Sphinx dependencies and extras to `template/files/python/pyproject.toml.jinja` gated on `docs_site` prompt.
- [ ] T027 [P] [US2] Scaffold Shibuya configuration (`conf.py.jinja`, `index.rst`, theme overrides, makefiles) under `template/files/python/docs/sphinx-shibuya/`.
- [ ] T028 [US2] Provide uv-aware build scripts and README snippets in `template/files/shared/docs/guidance/sphinx-shibuya.md.jinja` and hook output.
- [ ] T029 [P] [US2] Update `docs/modules/docs-site.md.jinja` and `docs/quickstart.md.jinja` with Sphinx commands, tooling prerequisites, and troubleshooting.
- [ ] T030 [US2] Capture Shibuya prompt answers within `samples/docs-sphinx/copier-answers.yml` and create `samples/docs-sphinx/metadata.json` for smoke evidence.
- [ ] T031 [US2] Extend `samples/metadata/render_matrix.json`, `module_success.json`, and `doc_publish.json` with Sphinx entries and thresholds.
- [ ] T032 [US2] Verify `scripts/render-samples.sh` and docs matrix jobs run `uv` commands for this variant (adjust command mapping if needed).

**Checkpoint**: Sphinx Shibuya variant builds and uploads artifacts deterministically.

---

## Phase 5: User Story 3 – Front-end Orgs Rely on Docusaurus (Priority: P3)

**Goal**: React/TypeScript teams render Docusaurus 3.9 docs with DocSearch v4 integration and module health surfacing.

**Independent Test**: Render with `docs_site=docusaurus` plus API modules, run `pnpm --filter docs-docusaurus build`, verify artifact upload and module health badges in generated site.

### Implementation for User Story 3

- [ ] T033 [P] [US3] Scaffold Docusaurus workspace (`package.json.jinja`, `docusaurus.config.ts.jinja`, `sidebars.ts`, scripts) under `template/files/node/docs/docusaurus/`.
- [ ] T034 [P] [US3] Seed DocSearch v4 config, MDX landing pages, and health badge placeholders within `template/files/node/docs/docusaurus/docs/`.
- [ ] T035 [US3] Update `template/files/node/pnpm-workspace.yaml.jinja` and monorepo configs to include the Docusaurus package and shared TypeScript settings.
- [ ] T036 [P] [US3] Document Docusaurus usage in `template/files/shared/docs/guidance/docusaurus.md.jinja`, `docs/modules/docs-site.md.jinja`, and `docs/quickstart.md.jinja`.
- [ ] T037 [US3] Populate `samples/docs-docusaurus/copier-answers.yml` and create `samples/docs-docusaurus/metadata.json` with smoke placeholders.
- [ ] T038 [US3] Extend `samples/metadata/render_matrix.json`, `module_success.json`, and `doc_publish.json` with Docusaurus results and artifact links.
- [ ] T039 [US3] Ensure CI matrix includes DocSearch env vars/secrets scaffolding in `.github/workflows/template-ci.yml` and sample metadata.

**Checkpoint**: Docusaurus variant compiles, publishes DocSearch-enabled artifacts, and surfaces module health in docs.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Align documentation, evidence, and release readiness across all variants.

- [ ] T040 [P] Sync documentation upgrades in `docs/upgrade-guide.md.jinja`, `docs/modules/sample-matrix.md.jinja`, and `docs/modules/governance.md.jinja` with final commands and remediation steps.
- [ ] T041 Refresh `samples/README.md` to describe new documentation samples and smoke evidence expectations.
- [ ] T042 [P] Run `scripts/render-samples.sh` for default and each docs variant, update `samples/**/baseline_quickstart_metrics.json`, and capture artifact links.
- [ ] T043 [P] Execute `scripts/ci/render_matrix.py`, `scripts/ci/record_module_success.py`, and `scripts/ci/track_doc_publish.py` locally to regenerate `samples/metadata/*.json`.
- [ ] T044 Document doc-site opt-out remediation in `template/files/shared/docs/guidance/none.md.jinja` and align README checkpoints where referenced.
- [ ] T045 Finalize `AGENTS.md` and `.specify/memory/constitution.md` notes if new tooling integrations require context updates.
- [ ] T046 Generate `copier diff` evidence for default and each docs variant, storing outputs under `samples/**/copier-diff.txt` before release sign-off.
- [ ] T047 Implement support-ticket variance tracking in `scripts/compliance/checkpoints.py` (recording results to `samples/metadata/support_tickets.json`) to enforce the <5% threshold.
- [ ] T048 Update `docs/modules/governance.md.jinja` and `docs/upgrade-guide.md.jinja` with instructions for reviewing support-ticket metrics each release.
- [ ] T049 Extend `scripts/ci/track_doc_publish.py` to emit warnings when documentation artifacts are within 14 days of expiry and log status to `samples/metadata/doc_publish.json`.
- [ ] T050 Document artifact-expiry alert handling in `docs/modules/governance.md.jinja` and `samples/README.md`.

---

## Dependencies & Execution Order

- **Phase Order**: Setup → Foundational → US1 → US2 → US3 → Polish. Each phase depends on completion of its predecessor.
- **Story Independence**: US1 delivers the MVP baseline; US2 and US3 rely on foundational work and build atop US1 assets but remain independently testable after their prerequisites finish.
- **Shared Files**: `template/hooks/pre_gen_project.py`, `template/hooks/post_gen_project.py`, `scripts/render-samples.sh`, `scripts/ci/render_matrix.py`, `scripts/ci/track_doc_publish.py`, and `.github/workflows/template-ci.yml` evolve across phases—apply changes sequentially to avoid conflicts.
- **Automation Flow**: `scripts/render-samples.sh` feeds `samples/metadata/*.json` and docs artifacts; ensure scripts are updated before wiring variant-specific automation.

## Parallel Execution Examples

- **US1 (P1)**: T017–T024 can proceed in parallel across the Next.js app, content seeds, and documentation updates once foundational tasks finish.
- **US2 (P2)**: T026–T031 split between dependency wiring, Sphinx config, and metadata updates while another contributor adjusts automation commands in T032.
- **US3 (P3)**: T033–T039 divide into package scaffolding, DocSearch integration, and CI wiring with minimal overlap when sequencing workspace edits.

## Implementation Strategy

- **MVP First**: Complete Phases 1–2, deliver US1 (T017–T025), and validate Fumadocs quickstart plus artifact uploads to establish a releasable MVP.
- **Incremental Delivery**: Layer US2 to unlock Sphinx docs, then US3 for Docusaurus; after each story, regenerate samples and confirm CI evidence before proceeding.
- **Parallel Teams**: After foundational work, distribute engineers per story using the parallel examples while coordinating shared automation files through code review.
- **Validation Cadence**: After each story, run `scripts/render-samples.sh`, CI helper scripts, and artifact checks to capture deterministic evidence prior to merge.
