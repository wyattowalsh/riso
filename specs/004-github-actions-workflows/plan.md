# Implementation Plan: GitHub Actions CI/CD Workflows

**Branch**: `004-github-actions-workflows` | **Date**: 2025-10-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-github-actions-workflows/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement comprehensive GitHub Actions workflow templates that automate testing, quality checks, building, and deployment for rendered projects. The solution includes matrix builds for Python versions (3.11, 3.12, 3.13), parallel job execution for Python and Node.js tracks, intelligent caching strategies using lock file hashes, and artifact management with 90-day retention. Workflows use distinctive names (`riso-quality.yml`, `riso-matrix.yml`) to avoid conflicts with custom workflows and respect existing quality profiles from feature 003.

## Technical Context

**Language/Version**: YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering)  
**Primary Dependencies**: GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`), actionlint (workflow validation), existing quality tools from feature 003  
**Storage**: Workflow artifacts (JUnit XML, coverage reports, logs) stored in GitHub Actions artifact storage with 90-day retention  
**Testing**: Rendered workflow validation via actionlint, integration testing via actual workflow execution in sample renders, smoke tests for workflow generation  
**Target Platform**: GitHub-hosted runners (ubuntu-latest), optimized for free tier (2000 minutes/month private repos, unlimited public)  
**Project Type**: Template composition - workflows are Jinja2 templates that render into downstream projects  
**Performance Goals**: <3 minutes CI runtime on cache hits, <6 minutes on cache misses, <8 minutes for full matrix builds, 70%+ cache hit rate  
**Constraints**: 10-minute timeout (standard profile), 20-minute timeout (strict profile), must respect GitHub Actions free tier limits  
**Scale/Scope**: Workflows must support Python 3.11-3.13 matrix, optional Node.js track, conditional module validation (CLI, API, MCP, docs), 2-5 workflow files per rendered project

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. UV-Managed Python Execution ✅
- Workflows execute quality checks via `uv run pytest`, `uv run ruff`, `uv run mypy`
- No direct `python` or `pytest` invocations in workflow YAML
- Compliance: All Python commands properly wrapped with `uv run`

### II. Automation-Governed Quality ✅
- Workflows are deterministic with fixed tool versions
- Single-attempt validation via actionlint before render
- Evidence tracked: artifacts uploaded with 90-day retention, durations logged
- No network dependencies beyond GitHub Actions marketplace actions
- Respects `quality_profile` (standard/strict) from feature 003

### III. Template Composition Over Inheritance ✅
- Workflows generated conditionally based on module selection (`api_tracks`, `cli_module`, etc.)
- Uses distinctive naming (`riso-quality.yml`, `riso-matrix.yml`) to avoid conflicts
- No hidden dependencies - workflows explicitly check module presence before execution
- Jinja2 conditionals handle module-specific logic

### IV. Documentation Synchronization ✅
- Workflow documentation added to rendered project README
- Quickstart docs updated with CI status viewing instructions
- Upgrade guide updated for workflow template changes
- Extension patterns documented for downstream customization

### V. Evidence-Driven Governance ✅
- Workflow generation logged in smoke-results.json
- Artifact upload success tracked per SC-006 (98%+ success rate)
- CI runtime metrics tracked per SC-002 (<3min cache hit, <6min cache miss)
- Module success rates include CI automation health

**Status**: ✅ PASS - No constitution violations. All principles adhered to.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
template/
├── files/
│   └── shared/
│       └── .github/
│           └── workflows/
│               ├── riso-quality.yml.jinja       # Main quality workflow (US1)
│               ├── riso-matrix.yml.jinja        # Matrix build workflow (US2)
│               ├── riso-cache.yml.jinja         # Cache management utilities (US3)
│               └── riso-deps-update.yml.jinja   # Optional dependency updates (FR-014)
├── hooks/
│   ├── pre_gen_project.py                       # Validate actionlint availability
│   └── post_gen_project.py                      # Validate generated workflows
└── prompts/
    └── ci_platform.yml.jinja                    # New prompt for CI platform selection

scripts/
├── ci/
│   ├── validate_workflows.py                    # Workflow YAML validation helper
│   └── render_matrix.py                         # Update to track workflow generation
└── hooks/
    └── workflow_validator.py                    # actionlint wrapper for hooks

samples/
├── default/
│   ├── render/
│   │   └── .github/
│   │       └── workflows/                       # Rendered workflows for testing
│   └── smoke-results.json                       # Updated with workflow validation
└── full-stack/
    ├── render/
    │   └── .github/
    │       └── workflows/                       # Rendered workflows with Node.js track
    └── smoke-results.json

docs/
├── quickstart.md.jinja                          # Updated with CI status viewing
└── upgrade-guide.md.jinja                       # Updated with workflow migration
```

**Structure Decision**: This feature uses the template composition pattern. Workflow files are Jinja2 templates that render into the `.github/workflows/` directory of downstream projects. The distinctive naming convention (`riso-*.yml`) prevents conflicts with custom workflows. Validation happens at two stages: (1) pre-generation via actionlint availability check, and (2) post-generation via actual workflow YAML validation. Sample renders include both Python-only (default) and Python+Node (full-stack) configurations to test conditional logic.

## Complexity Tracking

**No violations**. All constitution principles are fully adhered to:

- UV-managed Python execution maintained in workflows via `uv run` commands
- Quality automation is deterministic with single-attempt validation
- Template composition pattern used for workflow generation
- Documentation synchronized across template and rendered projects
- Evidence-driven governance via artifact uploads and smoke test tracking

---

## Phase 0: Research ✅

**Status**: Complete  
**Output**: `research.md` (see above)

**Key Decisions**:

1. **Workflow naming**: `riso-` prefix prevents conflicts
2. **Cache strategy**: Lock file hash + OS/Python version prefix
3. **Matrix configuration**: Python 3.11-3.13, fail-fast disabled
4. **Retry logic**: 3 attempts with exponential backoff
5. **Parallelization**: Python and Node jobs always parallel
6. **Artifact retention**: 90 days per constitution
7. **Validation**: actionlint in post-generation hook
8. **Quality profiles**: Integrated with feature 003 settings
9. **Module conditionals**: Jinja2 conditionals for module-specific checks
10. **Timeout configuration**: 10 min standard, 20 min strict

---

## Phase 1: Design & Contracts ✅

**Status**: Complete  
**Outputs**: `data-model.md`, `contracts/`, `quickstart.md`, `.github/copilot-instructions.md` (updated)

**Entities Defined**:

- `WorkflowConfiguration` - Generated workflow YAML files
- `JobDefinition` - Individual jobs within workflows
- `MatrixStrategy` - Matrix build configuration
- `StepDefinition` - Individual steps within jobs
- `RetryConfiguration` - Retry behavior for transient failures
- `CacheManifest` - Cache key patterns and restoration strategies
- `MatrixBuildResult` - Per-version execution outcomes
- `ArtifactMetadata` - Uploaded artifact metadata
- `WorkflowValidationReport` - actionlint validation results

**Contracts Created**:

- `riso-quality.contract.md` - Main quality workflow specification
- `riso-matrix.contract.md` - Matrix testing workflow specification

**Agent Context Updated**:

- Added GitHub Actions patterns to `.github/copilot-instructions.md`
- Technologies: YAML, Python 3.11+, Jinja2
- Frameworks: GitHub Actions marketplace actions, actionlint
- Storage: GitHub Actions artifact storage (90-day retention)

---

## Phase 2: Implementation Tasks

**Status**: Pending - requires `/speckit.tasks` command

**Expected Task Phases** (preview):

1. **Setup**: Create workflow template scaffolding
2. **Foundational**: Implement workflow generation and validation hooks
3. **User Story 1**: Main quality workflow with retry logic and artifact uploads
4. **User Story 2**: Matrix testing across Python versions
5. **User Story 3**: Cache configuration with lock file hashing
6. **User Story 4**: Artifact collection and retention
7. **User Story 5**: Conditional Node.js track integration
8. **Polish**: Documentation updates, smoke tests, governance tracking, free tier optimization

**Estimated Implementation Time**: 16-20 hours

---

## Success Criteria Validation

| ID | Criterion | Validation Method |
|----|-----------|-------------------|
| SC-001 | 95% renders have passing workflows in <5 min | Smoke tests track first-push workflow status |
| SC-002 | CI completes in <3 min (cache hit), <6 min (cache miss) | `MatrixBuildResult.duration_seconds` tracking |
| SC-003 | Matrix builds complete in <8 min | Sum of parallel job durations |
| SC-004 | 70%+ cache hit rate, 50%+ install time reduction | `CacheManifest` hit rate aggregation |
| SC-005 | 100% failures have actionable error messages | Manual review of workflow output formatting |
| SC-006 | 98%+ artifact uploads succeed with 90-day retention | `ArtifactMetadata` upload success tracking |
| SC-007 | 90%+ satisfaction in "works out of box" metric | Support ticket analysis (feature 003 pattern) |

---

## Risk Mitigation Status

| Risk | Mitigation Strategy | Implementation Status |
|------|---------------------|----------------------|
| Excessive Actions minutes consumption | 10/20 min timeouts, aggressive caching | ✅ Designed in contracts |
| Confusing matrix PR status | Clear job naming, summary aggregation | ✅ Designed in matrix workflow |
| Cache invalidation failures | Lock file hash keys, manual clear docs | ✅ Designed in cache manifest |
| Template workflow conflicts | Distinctive `riso-` prefix, extension docs | ✅ Designed in research |
| Node.js jobs doubling runtime | Parallel execution, independent timeouts | ✅ Designed in contracts |

---

## Integration Points

### Feature 003 (Code Quality Integrations)

- **Dependencies**: Workflows execute quality commands defined in feature 003
- **Quality profiles**: Workflows respect `quality_profile` setting
- **Tool commands**: `uv run task quality` invoked in workflow steps
- **Evidence format**: Artifacts match quality tool output expectations

### Feature 001 (Build Riso Template)

- **Template structure**: Workflows live in `template/files/shared/`
- **Rendering logic**: Copier handles Jinja2 template rendering
- **Module catalog**: Workflows check module catalog for conditional execution
- **Sample renders**: Workflows validated in default and full-stack samples

### Feature 002 (Docs Template Expansion)

- **Documentation**: Quickstart updated with CI viewing instructions
- **Upgrade guide**: Workflow migration patterns documented
- **Context sync**: Workflow automation added to shared context files

---

## Next Steps

1. **Run `/speckit.tasks`** to decompose implementation into executable tasks
2. **Execute tasks** following task dependency order (Setup → Foundational → User Stories → Polish)
3. **Validate each phase** via smoke tests and success criteria checks
4. **Update governance** (AGENTS.md, context files, module success tracking)
5. **Prepare PR** with all artifacts and evidence

**Planning Complete**: 2025-10-30  
**Branch**: `004-github-actions-workflows`  
**Next Command**: `/speckit.tasks`
