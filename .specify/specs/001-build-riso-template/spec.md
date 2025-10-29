# Feature Specification: Riso Template Foundation

**Feature Branch**: `001-build-riso-template`  
**Created**: 2025-10-29  
**Status**: Draft  
**Input**: User description: "`Riso` is the ultimate GH copier-based project template. it has an optional: cli (typer), api (node and/or python), mcp (FastMCP>=2.0.0), docs site (fumadocs or shibuya sphinx), and logic. it should allow for monorepos (apps/ and packages/ as well as single package repos. it should use the latest community-driven best practices ./.github/context/"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Baseline Render Works (Priority: P1)

A template consumer scaffolds the default project with no optional modules and completes the published quickstart without manual fixes.

**Why this priority**: Validates that the minimal configuration is ready for production teams and demonstrates deterministic output.

**Independent Test**: Render the baseline template into an empty directory, run the documented setup script, and confirm all smoke tests pass.

**Acceptance Scenarios**:

1. **Given** an empty workspace, **When** the consumer renders the template using default answers, **Then** dependencies install successfully and the quickstart task completes end-to-end.
2. **Given** a freshly rendered baseline project, **When** a regeneration check compares template source to output, **Then** no drift is detected.

---

### User Story 2 - Optional Modules Compose (Priority: P2)

A maintainer enables any combination of optional capabilities (CLI, API, MCP, docs, shared logic) and verifies they interoperate without conflicts.

**Why this priority**: Ensures teams can layer advanced tooling without bloating the default scaffold.

**Independent Test**: Produce scripted renders that toggle each module individually and in combined scenarios, then run the module-specific smoke checks listed in documentation.

**Acceptance Scenarios**:

1. **Given** a render with CLI and docs modules enabled, **When** the contributor runs the generated command workflows and documentation preview, **Then** both succeed and reference only committed files.
2. **Given** a render with both API tracks and shared logic enabled, **When** platform tests execute, **Then** each service passes on its own and shared code remains synchronized.

---

### User Story 3 - Multi-Layout Support (Priority: P3)

A team chooses between single-package layout and monorepo layout (apps/ + packages/) without rework.

**Why this priority**: Supports varied team structures while keeping governance consistent.

**Independent Test**: Render the template twice—once in single-package mode and once in monorepo mode—and confirm that tooling, documentation, and automation adjust accordingly.

**Acceptance Scenarios**:

1. **Given** monorepo mode is selected, **When** the render completes, **Then** shared tooling applies uniformly and each app/package can run its quickstart independently.
2. **Given** single-package mode is selected, **When** the render completes, **Then** no monorepo scaffolding leaks into the project and governance checks still pass.

---

### User Story 4 - Governance Automation Protects Releases (Priority: P4)

Maintainers rely on automated checks to confirm every template change still honors constitutional principles.

**Why this priority**: Guarantees long-term trust in the template as contributors and options expand.

**Independent Test**: Propose a template change, trigger CI, and confirm the pipeline blocks merge until sample regeneration, documentation updates, and policy validations succeed.

**Acceptance Scenarios**:

1. **Given** a pull request that modifies template prompts, **When** CI runs, **Then** it regenerates all declared samples and fails if updated artifacts are missing.
2. **Given** a scheduled governance review job, **When** it executes, **Then** it reports compliance status for each principle and raises issues for any automation gaps.

---

### Edge Cases

- How does a render behave when every optional module is selected while single-package layout is chosen (ensuring footprint remains manageable)?
- What happens if the host machine lacks tooling referenced by `.github/context/` (e.g., Node or Python not installed) during render time?
- How are upgrades handled when `.github/context/` best practices introduce breaking workflow changes for downstream teams?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (B)**: System MUST deliver a baseline render that installs, lints, tests, and documents itself using only the resources described in the quickstart guide.
- **FR-002 (B)**: System MUST apply automated governance checks (render drift, documentation sync, policy review) on every change before merge.
- **FR-003 (B)**: System MUST offer layout prompts that produce either a single-package project or a monorepo with dedicated `apps/` and `packages/` directories while preserving identical governance hooks.
- **FR-004 (B)**: System MUST publish upgrade guidance for existing projects, including how to run template updates and reconcile prompt changes.
- **FR-005 (O)**: System MUST provide an optional command interface module aligned with the CLI standards defined in `.github/context/`, including usage documentation and smoke validations.
- **FR-006 (O)**: System MUST provide optional service modules covering both JavaScript-based and Python-based APIs, each with independent runbooks, tests, and documentation.
- **FR-007 (O)**: System MUST provide an optional machine-controller protocol (MCP) integration module that includes sample tools, contracts, and verification steps.
- **FR-008 (O)**: System MUST provide optional documentation site variants covering both lightweight and full-knowledge-base experiences with build and deploy guidance.
- **FR-009 (O)**: System MUST provide an optional shared logic module that can be consumed by other modules without forcing unused dependencies.
- **FR-010 (B)**: System MUST synchronize `.github/context/` best-practice workflows into the generated project and expose a process to keep future updates aligned.
- **FR-011 (B)**: System MUST declare template semantic versioning, compatibility matrix, and supported optional module combinations within template metadata.

### Template Prompts & Variants

- **Prompt**: `project_layout` — **Type**: Baseline — **Default**: `single-package` — **Implication**: Selects between single-package structure and monorepo structure with shared tooling and documentation notes.
- **Prompt**: `cli_module` — **Type**: Optional — **Default**: `disabled` — **Implication**: Adds command entrypoints, CLI usage docs, and associated tests.
- **Prompt**: `api_tracks` — **Type**: Optional — **Default**: `none` — **Implication**: Enables one or both API service tracks with environment setup and testing instructions.
- **Prompt**: `mcp_module` — **Type**: Optional — **Default**: `disabled` — **Implication**: Introduces MCP integration scaffolds, sample tools, and verification scripts.
- **Prompt**: `docs_site` — **Type**: Optional — **Default**: `starter-guide` — **Implication**: Chooses between lightweight quickstart docs and full documentation site with deployment workflow.
- **Prompt**: `shared_logic` — **Type**: Optional — **Default**: `disabled` — **Implication**: Generates a reusable core package/module with integration notes for other components.
- **Variant Samples**: Update `samples/default` (baseline), `samples/cli-docs`, `samples/api-monorepo`, and `samples/full-stack` to demonstrate representative prompt combinations with linked render evidence.

### Key Entities *(include if feature involves data)*

- **Template Module Definition**: Captures name, description, dependencies, and validation steps for each optional capability.
- **Sample Project Artifact**: Stores rendered outputs for baseline and key variants, including verification logs and documentation snapshots.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of baseline renders complete all quickstart checks in under 10 minutes across macOS, Linux, and Windows environments.
- **SC-002**: Optional module render permutations achieve a 98% success rate in nightly automation runs, with failures triaged within one business day.
- **SC-003**: Documentation build pipeline publishes updated prompt reference and upgrade guidance within 24 hours of a template merge.
- **SC-004**: Governance automation blocks 100% of merges lacking regenerated samples, updated docs, or policy attestations (zero manual overrides per quarter).

## Principle Compliance Evidence *(mandatory)*

- **Template Sovereignty**: Document which template files (prompts, hooks, metadata) encode each capability and attach regeneration diffs for every sample.
- **Deterministic Generation**: Define the render matrix (platforms, prompt combinations) and link to automated test evidence stored with sample artifacts.
- **Minimal Baseline, Optional Depth**: Explain how the baseline remains lightweight, and show the gating prompts and compatibility map for optional add-ons.
- **Documented Scaffolds**: List the documentation deliverables (quickstart, prompt reference, upgrade guide) and assign responsible owners for updates.
- **Automation-Governed Compliance**: Outline CI jobs enforcing linting, render tests, docs checks, and policy reviews, including failure-handling workflow.

## Assumptions

- Optional modules will align with the recommended tooling catalog captured in `.github/context/`, with final toolkit confirmations handled during planning.
- Downstream teams expect both single-package and monorepo layouts to be viable without additional scaffolding beyond what the template provides.
- Governance automation budgets allow the addition of render permutations without impacting overall CI cycle-time targets.

## Dependencies & External Inputs

- `.github/context/` files supply curated best practices that must be kept in sync with the template.
- Organizational release notes and upgrade channels must distribute template version changes to downstream projects.

## Out of Scope

- Defining the exact implementation details for each optional module (to be handled during planning and implementation phases).
- Creating bespoke variants beyond the standard combinations captured in the samples directory.
- Managing downstream project migrations beyond providing documented upgrade guidance.
