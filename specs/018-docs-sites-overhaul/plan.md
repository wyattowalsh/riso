# Implementation Plan: Documentation Sites Overhaul

**Branch**: `018-docs-sites-overhaul` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-docs-sites-overhaul/spec.md`

## Summary

Comprehensive enhancement of documentation site scaffolding in the Riso template, fixing critical Sphinx failures, adding extensive configuration options, implementing shared content transformation, and introducing interactive features. Primary focus on making all three documentation frameworks (Fumadocs, Sphinx-Shibuya, Docusaurus) production-ready with prompt-driven customization replacing hardcoded configurations.

## Technical Context

**Language/Version**: Python 3.11+ (template system), Node.js 20 LTS (for Fumadocs/Docusaurus), Bash/Zsh (automation scripts)  
**Primary Dependencies**:
- Jinja2 ≥3.1 (template rendering)
- Copier ≥9.0 (template engine)
- Sphinx ≥7.4 + Shibuya theme ≥2024.10 (Python docs)
- Fumadocs ≥13.0 + Next.js 15 (React docs)
- Docusaurus ≥3.5 (React docs alternative)
- Mermaid.js ≥10.0 (diagrams)
- uv ≥0.4 (Python environment management)
- pnpm ≥8 (Node package management)

**Storage**: File-based (template files, generated configs, documentation content)  
**Testing**: 
- pytest for template validation scripts
- Smoke tests for each docs variant (`samples/{variant}/smoke-results.json`)
- Link checking (sphinx-linkcheck, framework-specific tools)
- Accessibility validation (axe-core, pa11y)

**Target Platform**: Cross-platform (macOS, Linux, Windows via WSL)  
**Project Type**: Template/Scaffolding system (generates documentation sites)  
**Performance Goals**: 
- Template render: <60 seconds per variant
- Docs build: <90 seconds for <100 pages
- Link check: <5 minutes for typical project
- Search indexing: <30 seconds for local search

**Constraints**:
- Sphinx smoke tests currently at 0% pass rate (critical blocker)
- Must maintain backward compatibility with existing renders
- Content transformation must preserve semantic meaning across frameworks
- Interactive features must degrade gracefully without JavaScript

**Scale/Scope**:
- 3 documentation frameworks to support
- 7 new configuration prompts
- ~15 new/modified Jinja2 template files
- ~500 lines of content transformation logic
- ~10 sample renders to maintain

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research)

✅ **Module Sovereignty**: Documentation sites remain optional via `docs_site` prompt with `none` option; new configuration sub-prompts conditional on `docs_site != none`

✅ **Deterministic Generation**: All prompt-based configuration produces deterministic output; no timestamps or random values in generated docs config

✅ **Minimal Baseline**: New prompts only affect projects with `docs_site != none`; baseline (no docs) remains unchanged at <50 files

✅ **Quality Integration**: Documentation builds integrate with existing quality suite via FR-013; link checking, accessibility validation added as quality gates

✅ **Test-First Development**: Each user story has independent smoke tests; Sphinx fix (P1) verified by moving smoke tests from 0% → 100% pass rate

✅ **Documentation Standards**: New features documented in `docs/modules/docs-site.md.jinja`; upgrade guide includes migration paths between frameworks

✅ **Technology Consistency**: Uses approved stack (Python 3.11+/uv, Node 20/pnpm); extends existing GitHub Actions workflows; no new CI platforms

**Status**: ✅ Phase 1 Complete - All design artifacts generated

### Constitution Re-Check (Post-Design)

✅ **Module Sovereignty**: Design preserves optional nature; new prompts in contracts/prompts.yml are conditional on `docs_site != none`; no baseline impact when docs disabled

✅ **Deterministic Generation**: All transformation APIs produce deterministic output; no runtime randomness in contracts/transformation-api.md; prompt configurations fully reproducible

✅ **Minimal Baseline**: Baseline completely unaffected (verified in data-model.md); new features only active when `docs_site != none`; zero additional files when docs disabled

✅ **Quality Integration**: Validation APIs (contracts/validation-api.md) integrate with existing quality suite patterns; link checking and accessibility validation extend current pytest framework

✅ **Test-First Development**: quickstart.md emphasizes TDD workflow with Sphinx fix priority; each user story has independent smoke tests defined; transformation test script specified (T046)

✅ **Documentation Standards**: New module guide specified in contracts/; upgrade guide planned (framework-migration.md.jinja); all artifacts follow Jinja2 templating standards

✅ **Technology Consistency**: No new tool chain dependencies beyond approved stack; extends existing GitHub Actions workflows; uses Python 3.11+/uv and Node 20/pnpm per constitution

**Final Status**: ✅ PASS - Design fully aligns with all 7 constitution principles. No violations detected. Ready for implementation.

---

## Project Structure

### Documentation (this feature)

```text
specs/018-docs-sites-overhaul/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions and patterns
├── data-model.md        # Phase 1: Configuration entities and relationships
├── quickstart.md        # Phase 1: Developer onboarding for this feature
├── contracts/           # Phase 1: Template prompt schemas, transformation API
│   ├── prompts.yml      # Extended docs_site prompts with sub-options
│   ├── transformation-api.md  # Content transformation interface
│   └── validation-api.md      # Docs validation interface
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2: NOT created by this command
```

### Source Code (repository root)

```text
template/
├── copier.yml           # MODIFY: Add 7 new docs configuration prompts
├── files/
│   ├── python/
│   │   └── docs/        # MODIFY: Fix Sphinx Makefile, conf.py templates
│   ├── node/
│   │   └── docs/        # MODIFY: Enhance Fumadocs/Docusaurus configs
│   └── shared/
│       ├── docs/        # NEW: Shared content transformation system
│       │   ├── transformation/
│       │   │   ├── markdown_to_mdx.py.jinja
│       │   │   ├── markdown_to_rst.py.jinja
│       │   │   └── common.py.jinja
│       │   ├── validation/
│       │   │   ├── link_checker.py.jinja
│       │   │   ├── accessibility.py.jinja
│       │   │   └── common.py.jinja
│       │   ├── modules/
│       │   │   └── docs-site.md.jinja  # MODIFY: Comprehensive docs module guide
│       │   └── guidance/
│       │       └── framework-migration.md.jinja  # NEW: Migration between frameworks
│       └── .github/
│           └── workflows/
│               ├── riso-docs-build.yml.jinja  # NEW: Docs build workflow
│               └── riso-docs-validate.yml.jinja  # NEW: Link/accessibility validation

scripts/ci/
├── validate_docs_config.py     # NEW: Validate generated docs configurations
├── test_content_transformation.py  # NEW: Test Markdown → MDX/RST conversion
└── render_matrix.py            # MODIFY: Add docs validation to smoke tests

samples/
├── docs-fumadocs/
│   ├── render/              # MODIFY: Update with new prompts
│   └── smoke-results.json   # UPDATE: Enhanced validation
├── docs-sphinx/
│   ├── render/              # FIX: Make smoke tests pass (currently failing)
│   └── smoke-results.json   # UPDATE: 0% → 100% pass rate
└── docs-docusaurus/
    ├── render/              # MODIFY: Update with new prompts
    └── smoke-results.json   # UPDATE: Enhanced validation

docs/
├── modules/
│   └── docs-site.md.jinja   # MODIFY: Document new configuration options
└── upgrade-guide/
    └── 018-docs-sites.md.jinja  # NEW: Migration and configuration guide
```

**Structure Decision**: Template system (Option 1 variant) with both shared transformation logic and framework-specific implementations. Shared content lives in `template/files/shared/docs/` with framework-specific templates in `template/files/{python|node}/docs/`. This allows code reuse while respecting framework-specific requirements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations detected - this section intentionally left blank.*

## Phase 0: Outline & Research

### Research Tasks

Documented in `research.md` (completed 2025-11-02):

1. **Sphinx Makefile Patterns** - ✅ Complete
   - Decision: Generate separate `Makefile.docs` to avoid target collisions
   - Rationale: Prevents conflicts with Python build targets

2. **Content Transformation Strategies** - ✅ Complete
   - Decision: AST-based transformation using Python `markdown` library
   - Rationale: Preserves semantic structure, pure Python dependency

3. **Mermaid Integration Patterns** - ✅ Complete
   - Decision: Framework-native plugins with RST-only transformation
   - Rationale: Leverages native framework support, minimal transformation needed

4. **Search Provider Integration** - ✅ Complete
   - Decision: Default to local search; prompt-driven external providers
   - Rationale: Zero-cost default, opt-in for external services

5. **Accessibility Validation Tools** - ✅ Complete
   - Decision: axe-core (pytest-axe for Python, @axe-core/cli for Node)
   - Rationale: Industry standard, dual Python/Node support

6. **Documentation Versioning Patterns** - ✅ Complete
   - Decision: Opt-in via prompt with framework-specific scaffolding
   - Rationale: Advanced feature, adds build complexity

7. **Link Checking Retry Logic** - ✅ Complete
   - Decision: Sphinx built-in retry + custom script for Node frameworks
   - Rationale: 3 retries with exponential backoff handles transient failures

**Status**: ✅ Phase 0 Complete - All research questions answered

## Phase 1: Design & Contracts

### Artifacts Generated

All Phase 1 artifacts completed (2025-11-02):

1. **data-model.md** - ✅ Complete
   - Entities: DocumentationConfiguration, ContentTransformationRule, TransformationResult, DocumentationBuildArtifact, ValidationResults, RetryConfig
   - Relationships: Configuration → Rules, Configuration → Artifacts, Artifacts → Validation
   - State machines: Configuration workflow, Transformation pipeline

2. **contracts/prompts.yml** - ✅ Complete
   - 7 new documentation configuration prompts
   - Help text with cost/feature details
   - Conditional rendering based on `docs_site` selection

3. **contracts/transformation-api.md** - ✅ Complete
   - ContentTransformer interface
   - Transformation rules (Markdown ↔ MDX ↔ RST)
   - Failure modes per clarification Q1 (halt build immediately)
   - Usage examples and implementation notes

4. **contracts/validation-api.md** - ✅ Complete
   - DocumentationValidator interface
   - Link checking with exponential backoff (per clarification Q2)
   - Accessibility validation (WCAG 2.1 AA warnings non-blocking per Q3)
   - Usage examples and CI integration patterns

5. **quickstart.md** - ✅ Complete
   - Developer onboarding guide
   - Critical path: Fix Sphinx first (P1)
   - TDD workflow examples
   - Debugging tips and common commands

**Status**: ✅ Phase 1 Complete - All design artifacts generated

### Constitution Re-Check (Post-Design)

✅ **Module Sovereignty**: Design preserves optional nature; no baseline impact confirmed

✅ **Deterministic Generation**: All APIs produce deterministic output; no runtime randomness

✅ **Minimal Baseline**: Baseline unaffected; new features only active when `docs_site != none`

✅ **Quality Integration**: Validation APIs integrate with existing quality suite patterns

✅ **Test-First Development**: Quickstart emphasizes TDD workflow; smoke tests define success

✅ **Documentation Standards**: New docs module guide planned; upgrade guide specified

✅ **Technology Consistency**: No new tool chain dependencies; extends existing workflows

**Final Status**: ✅ PASS - Design aligns with constitution principles.

---

## Implementation Notes

### Priority Order (from spec)

1. **P1: Sphinx Fixes** (User Story 1) - CRITICAL PATH
   - Generate `Makefile.docs` template with correct targets
   - Fix `conf.py` template with autodoc configuration
   - Verify smoke tests move from 0% → 100% pass rate

2. **P1: Configuration Prompts** (User Story 2) - HIGH VALUE
   - Add 7 new prompts to `template/copier.yml`
   - Implement conditional rendering logic
   - Update sample answer files

3. **P2: Content Management** (User Story 3) - INFRASTRUCTURE
   - Implement AST-based transformation system
   - Create Markdown → MDX/RST converters
   - Add comprehensive unit tests

4. **P2: Interactive Features** (User Story 4) - ENHANCEMENTS
   - Mermaid diagram integration
   - Code tabs implementation
   - API playground scaffolding

5. **P3: Versioning** (User Story 5) - ADVANCED FEATURE
   - Optional versioning scaffold
   - Framework-specific patterns
   - Version switcher components

### Risk Mitigation Strategies

1. **Framework Divergence**:
   - Establish canonical Markdown subset in research phase ✅
   - Document transformation rules in contracts/ ✅
   - Test all transformations with unit tests (Phase 2)

2. **Sphinx Makefile Conflicts**:
   - Use separate `Makefile.docs` to avoid collisions ✅
   - Prefix all targets with `docs-` for clarity ✅
   - Test with `uv run make -f Makefile.docs <target>` (Phase 2)

3. **Search Provider Costs**:
   - Default to local search (no external costs) ✅
   - Document provider limits in prompt help text ✅
   - Provide cost estimation in generated README (Phase 2)

### Success Validation

Feature complete when:

- [ ] Sphinx smoke tests achieve 100% pass rate (SC-003)
- [ ] All 7 new prompts functional in copier.yml (SC-004)
- [ ] Content transformation passes test suite (SC-007)
- [ ] Link checking with retry logic operational (SC-006)
- [ ] Accessibility validation reports WCAG 2.1 AA warnings (SC-008)
- [ ] All sample renders build successfully (SC-001, SC-002)
- [ ] Documentation updated (module guide, upgrade guide)
- [ ] Constitution check passes (all principles respected) ✅

---

## Next Phase: Task Breakdown

**Ready for**: `/speckit.tasks` command

This plan provides complete Phase 0 (research) and Phase 1 (design) artifacts. The next step is to run `/speckit.tasks` to break down the implementation into concrete, actionable tasks with acceptance criteria and test cases.

**Plan Version**: 1.0  
**Created**: 2025-11-02  
**Status**: ✅ Ready for Task Generation
