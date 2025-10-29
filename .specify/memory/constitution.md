<!--
Sync Impact Report
- Version change: N/A → 1.0.0
- Modified principles: Added I. Template Sovereignty; Added II. Deterministic Generation; Added III. Minimal Baseline, Optional Depth; Added IV. Documented Scaffolds; Added V. Automation-Governed Compliance
- Added sections: Template Architecture Constraints; Delivery Workflow & Review
- Removed sections: None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
  - ⚠ .specify/templates/commands/* (directory absent; add command guidance when commands are introduced)
- Follow-up TODOs: None
-->

# Riso Constitution

## Core Principles

### I. Template Sovereignty
All repository behavior MUST be expressed through the copier template so every rendered project remains identical.
- Template artifacts (Jinja templates, `copier.yml`, hook scripts) are the single source of truth for generated files.
- Manual edits applied to generated example projects MUST be mirrored back into the template before merge.
- Each change MUST include a `copier diff` (or equivalent evidence) proving that regenerated outputs match the template.
Rationale: This prevents configuration drift across downstream projects and keeps scaffolding reviewable.

### II. Deterministic Generation
The template MUST render deterministically across supported environments.
- Default answers MUST render without warnings on macOS, Linux, and Windows CI targets.
- A golden sample project under `samples/` (or equivalent) MUST be regenerated and validated in CI whenever prompts or hooks change.
- Hooks and scripts MUST be idempotent and avoid external side effects such as network calls or host-specific paths.
Rationale: Deterministic output ensures new projects can trust the scaffold and enables reproducible debugging.

### III. Minimal Baseline, Optional Depth
The default project MUST remain lightweight while advanced capabilities stay opt-in.
- Baseline renders MUST include only what is required to run the documented quickstart end-to-end.
- New capabilities MUST be guarded by descriptive prompts with documented defaults and backwards-compatible migrations.
- Optional modules MUST compose without forcing unrelated stacks, services, or credentials into the baseline.
Rationale: Teams adopt the template faster when the core stays small and optional layers remain modular.

### IV. Documented Scaffolds
Every scaffolded asset MUST ship with authoritative documentation generated alongside the code.
- `docs/` MUST contain a template quickstart that mirrors the default render and is updated with every change.
- Each prompt MUST be described in reference docs covering purpose, defaults, side effects, and CI/CD implications.
- Runtime guidance MUST state how to upgrade existing projects with `copier update` and how to resolve breaking changes.
Rationale: Paired documentation reduces onboarding friction and keeps downstream teams self-sufficient.

### V. Automation-Governed Compliance
Quality gates MUST be automated so constitutional compliance cannot be bypassed.
- CI pipelines MUST execute template linting (`copier lint` or equivalent), render smoke tests, and policy checks on every merge.
- Release notes MUST summarize principle impacts and link to the latest golden sample diff.
- Compliance reviews MUST block merges until automation proves all principles remain satisfied.
Rationale: Automated enforcement keeps the template trustworthy even as contributors and projects change.

## Template Architecture Constraints

- `copier.yml` MUST declare the template semantic version, minimum supported copier version, and default answers for every prompt.
- Hooks under `hooks/` MUST be cross-platform, self-contained, and unit-tested where logic exceeds trivial shell scripting.
- Template files MUST avoid hard-coded organization identifiers; use prompts or computed values to support broad reuse.
- Generated projects MUST include linting, testing, and formatting scripts that succeed immediately after rendering.

These constraints keep the scaffold portable and production-ready upon first render.

## Delivery Workflow & Review

1. Open a design discussion referencing the relevant spec and identify which principles are affected.
2. Produce an implementation plan that documents template files touched, render validation strategy, and documentation obligations.
3. Run `copier copy --defaults --pretend` and a full `copier copy` into `samples/` to capture diffs for review.
4. Update documentation (quickstart, prompt reference, upgrade guide) in the same change set.
5. Ensure CI runs succeed on regenerated samples and attach evidence (logs or artifacts) to the review.
6. Secure maintainer approval sign-off explicitly acknowledging principle compliance before merge.

## Governance

- This constitution supersedes all other process documents governing the template; conflicts MUST be resolved in favor of this file.
- Amendments require an RFC linked to this document, majority maintainer approval, and successful regeneration of all declared samples.
- Version updates MUST follow semantic versioning (MAJOR: breaking principle scope or default render behavior; MINOR: adding principles or governance obligations; PATCH: clarifications and non-obligatory refinements).
- Ratification and amendments MUST update the version line and Sync Impact Report at the top of this file.
- A compliance review MUST occur at least quarterly or before each tagged release to confirm automation still enforces every principle.

**Version**: 1.0.0 | **Ratified**: 2025-10-29 | **Last Amended**: 2025-10-29
