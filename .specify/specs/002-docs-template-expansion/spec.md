# Feature Specification: Expanded Documentation Template Options

**Feature Branch**: `002-docs-template-expansion`  
**Created**: 2025-10-29  
**Status**: Draft  
**Input**: User description: "enhanced + extended dev docs templating options (fumadocs + python sphinx shibuya + docusaurus)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Docs Variant Prompt Guides Baseline (Priority: P1)

A template maintainer selects a documentation framework during `copier copy` and receives scaffolding, quickstart commands, and automation wiring tailored to the chosen variant without manual edits.

**Why this priority**: Establishes a deterministic user experience where every render—baseline or optional—ships ready-to-run documentation.

**Independent Test**: Render the template three times (fumadocs, sphinx-shibuya, docusaurus), run the generated quickstart snippet, and confirm each build succeeds end-to-end with only documented dependencies.

**Acceptance Scenarios**:

1. **Given** the maintainer chooses `docs_site=fumadocs`, **When** the render completes and the quickstart script runs, **Then** the Next.js/Fumadocs dev server boots with the seeded docs navigation and passes linting.
2. **Given** the maintainer chooses `docs_site=docusaurus`, **When** automation executes sample regeneration, **Then** the generated CI job installs prerequisites and produces a static build artifact without retrying manual steps.

---

### User Story 2 - Python Teams Publish Shibuya Docs (Priority: P2)

A Python-focused team enables the Shibuya-themed Sphinx option and can run documentation builds through `uv` as part of the project’s quickstart and CI workflow.

**Why this priority**: Keeps the Python track first-class, ensuring generated examples and configuration align with `uv` workflows and the shared automation harness.

**Independent Test**: Render with `docs_site=sphinx-shibuya` and Python API enabled, execute `uv run make docs` (or generated equivalent), and verify HTML output, link checking, and theme assets succeed within CI.

**Acceptance Scenarios**:

1. **Given** the Shibuya docs variant is enabled, **When** maintainers run the documented build command locally, **Then** the Sphinx site renders without missing dependencies and outputs to the expected directory.
2. **Given** CI runs for a Shibuya-enabled render, **When** the docs job executes, **Then** it uploads the built site as an artifact and fails fast on broken references.

---

### User Story 3 - Front-end Orgs Rely on Docusaurus (Priority: P3)

A front-end-heavy organization selects the Docusaurus option to produce a documentation hub that matches their Node.js tooling expectations and supports module-level sub-sites.

**Why this priority**: Expands relevance beyond Python-only projects and unlocks a bias toward React/TypeScript documentation stacks.

**Independent Test**: Render with `docs_site=docusaurus` plus API modules, run `pnpm --filter docs-docusaurus build`, and verify navigation, search seed content, and deployed static assets behave as described.

**Acceptance Scenarios**:

1. **Given** Docusaurus is selected with both API tracks enabled, **When** the maintainer runs the generated build command, **Then** the site compiles, references both API docs, and surfaces module health badges pulled from smoke results.
2. **Given** a downstream consumer regenerates their project with no docs changes, **When** the comparator script runs, **Then** Docusaurus assets remain stable and regenerate without manual merges.

---

### Edge Cases

- How does the template behave when `docs_site=none` (or baseline default) is selected to skip documentation entirely while other doc-related modules remain disabled?
- What happens if maintainers enable a documentation framework whose runtime dependencies (Node.js, pnpm, uv) are missing on the render host?
- How are breaking theme upgrades (Fumadocs, Shibuya, Docusaurus) communicated and version-pinned to preserve reproducibility for existing renders?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (B)**: The template MUST expose a `docs_site` prompt with choices `fumadocs`, `sphinx-shibuya`, `docusaurus`, and `none`, defaulting to the organization-approved baseline and describing prerequisites for each option.
- **FR-002 (B)**: Each documentation choice MUST generate tailored quickstart commands, scripts, and README/quickstart documentation so teams can build, preview, and lint docs without additional setup.
- **FR-003 (B)**: Automation MUST extend `scripts/render-samples.sh` (and dependent CI jobs) to render and validate sample projects for every documentation variant on every change.
- **FR-004 (B)**: Governance MUST refuse merges when any docs variant fails its smoke build, static analysis, or context-sync checks, capturing evidence in `samples/**/smoke-results.json`.
- **FR-005 (O)**: Selecting `fumadocs` MUST scaffold a Next.js + Fumadocs workspace with navigation seeds, typed content examples, and pnpm tasks wired into CI.
- **FR-006 (O)**: Selecting `sphinx-shibuya` MUST scaffold a Python docs package using the Shibuya theme, `uv` environment management, and link-check integration.
- **FR-007 (O)**: Selecting `docusaurus` MUST scaffold a React/TypeScript docs workspace with localized config, search integration, and module documentation shells.
- **FR-008 (B)**: Template metadata, prompt reference docs, and upgrade guidance MUST document the new options, migration steps, and tooling expectations.
- **FR-009 (B)**: Optional documentation variants MUST compose cleanly with CLI, API, MCP, and shared-logic modules without introducing unused dependencies into the baseline render.
- **FR-010 (B)**: Render metadata (`samples/metadata/*.json`) MUST track which documentation variant generated each sample to support trend analysis and automation triage.

### Template Prompts & Variants

- **Prompt**: `docs_site` — **Type**: Baseline — **Default**: `fumadocs` (subject to maintainer confirmation) — **Implication**: Selects no-docs, Fumadocs (Next.js), Sphinx Shibuya, or Docusaurus scaffolds; toggles language-specific build scripts and dependencies.
- **Prompt**: `api_tracks` — **Type**: Optional — **Default**: `none` — **Implication**: When Python or Node APIs are enabled, injects corresponding doc API examples (FastAPI reference pages, Fastify snippets) into the selected documentation framework.
- **Variant Samples**: Extend `samples/docs-fumadocs/`, `samples/docs-sphinx/`, and `samples/docs-docusaurus/` renders with updated `metadata.json`, smoke logs, and documentation build artifacts; maintain `samples/default/` as the baseline evidence.

### Key Entities

- **DocumentationVariant**: Defines the selected documentation framework, required tooling, generated entrypoints, and CI job names.
- **DocumentationSampleEvidence**: Captures render metadata, smoke status, build durations, and artifact locations per variant to feed governance dashboards.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of documentation variants build successfully via the published quickstart commands on a fresh render within 8 minutes.
- **SC-002**: CI pipelines complete documentation smoke jobs for all variants with zero manual intervention in ≥98% of runs across a rolling 30-day window.
- **SC-003**: Downstream maintainers report <5% variance in docs setup steps versus the spec by monitoring support tickets tagged “docs setup”.
- **SC-004**: Documentation prompts and reference materials stay synchronized—automated diff checks detect and block drift in `.github/context/` and docs guides every release.

## Principle Compliance Evidence *(mandatory)*

- **Template Sovereignty**: Each framework’s scaffolding, configs, and datasets live in `template/files/**` with reference diffs captured via `copier` regeneration, ensuring downstream projects regenerate without manual merges.
- **Deterministic Generation**: `scripts/render-samples.sh` runs per-variant builds, recording `baseline_quickstart_metrics.json` and `smoke-results.json`; governance pipelines gate merges when any doc variant diverges.
- **Minimal Baseline, Optional Depth**: Default renders only include the chosen documentation stack; other frameworks remain opt-in modules that do not alter dependency footprints unless selected.
- **Documented Scaffolds**: Update `docs/quickstart.md.jinja`, `docs/modules/docs-site.md.jinja`, `docs/modules/sample-matrix.md.jinja`, and `docs/upgrade-guide.md.jinja` to describe workflows, migrations, and evidence expectations.
- **Automation-Governed Compliance**: Enhance `scripts/ci/render_matrix.py`, `scripts/ci/track_doc_publish.py`, and related GitHub Actions to publish variant metrics, failing builds whenever docs evidence or artifacts are outdated.

## Assumptions

- Node.js 20 LTS with pnpm ≥8 and Python 3.11 with `uv` remain the supported toolchains for doc builds; downstream teams can install missing runtimes when prompted.
- Only one documentation framework is active per render; switching frameworks requires re-rendering or applying upgrade guidance.
- Theme upgrades for Fumadocs, Shibuya, and Docusaurus can be version-pinned so automation remains deterministic between releases.

## Dependencies & External Inputs

- Official releases of Fumadocs, Sphinx Shibuya theme, and Docusaurus (including CLI tooling).
- Existing governance automation (`scripts/ci/*`, `.github/workflows/template-ci.yml`) that records smoke results and timing evidence.
- Maintainer-provided content seeds (example pages, module overviews) to populate new docs variants.

## Risks & Mitigations

- **Risk**: Divergent toolchains introduce flaky CI failures. **Mitigation**: Pin dependency versions and run cross-variant smoke builds in a matrix.
- **Risk**: Downstream teams hesitate to migrate between doc frameworks. **Mitigation**: Provide upgrade recipes and automated diff guidance in upgrade docs.
- **Risk**: Additional samples increase CI duration. **Mitigation**: Allow maintainers to run variant-specific subsets locally and parallelize docs jobs in GitHub Actions.

## Out of Scope

- Building custom themes or bespoke styling beyond configuring official Fumadocs, Shibuya, and Docusaurus starters.
- Managing content migration for downstream projects beyond documented upgrade steps.
- Integrating external search providers or analytics services; these can be layered after the template work completes.

