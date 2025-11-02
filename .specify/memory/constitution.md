<!--
Sync Impact Report - Constitution v1.0.0
========================================
Version Change: [TEMPLATE] → 1.0.0
Rationale: Initial constitution ratification for Riso template project

Changes:
- Added all core principles (Module Sovereignty, Deterministic Generation, Minimal Baseline, Quality Integration, Test-First Development, Documentation Standards, Technology Consistency)
- Added Template Constraints section
- Added Development Workflow section
- Established governance rules and versioning policy

Templates Requiring Updates:
✅ plan-template.md - Constitution Check section aligns with these principles
✅ spec-template.md - Requirements align with optional modules and quality gates
✅ tasks-template.md - Test-first approach reflected in task organization

Follow-up TODOs:
- None - all placeholders filled with project-specific values
-->

# Riso Template Constitution

## Core Principles

### I. Module Sovereignty

Every feature is an optional, self-contained module controlled by Copier prompts. Modules MUST NOT be required for baseline template functionality. Each module MUST include:

- Clear activation flag in `copier.yml` (e.g., `graphql_api_module=enabled`)
- Independent documentation in `docs/modules/{module}.md.jinja`
- Smoke tests in `samples/` proving standalone functionality
- No dependencies on other optional modules unless explicitly documented

**Rationale**: Users should get only what they need. A minimal project should remain minimal. Features that bloat the baseline violate user trust and template usability.

### II. Deterministic Generation

The same Copier answers MUST produce identical output across renders. All template logic MUST be:

- Pure (no random values, timestamps, or system-dependent paths in generated code)
- Reproducible (same `copier-answers.yml` → same file tree and content)
- Idempotent (re-rendering with same answers produces no diff)
- Validated (CI checks confirm determinism via `render_matrix.py`)

**Rationale**: Reproducibility is essential for debugging, testing, and version control. Non-deterministic templates break trust and make automation impossible.

### III. Minimal Baseline

The default template render (all optional modules disabled) MUST produce a working project with:

- Python 3.11+ package structure managed via uv
- Basic quality tooling (ruff, mypy, pylint, pytest)
- README with quickstart instructions
- No unnecessary dependencies or boilerplate

Size constraints:

- Baseline project: <50 files
- Core dependencies: <10 production packages
- Install time: <30 seconds on modern hardware

**Rationale**: Template bloat drives users away. Every file and dependency must justify its existence in the baseline.

### IV. Quality Integration

All generated code MUST integrate with the quality suite (ruff, mypy, pylint, pytest). Quality checks MUST:

- Pass on baseline renders (`QUALITY_PROFILE=standard make quality`)
- Support strict mode for production (`QUALITY_PROFILE=strict`)
- Execute in CI via `riso-quality.yml` and `riso-matrix.yml` workflows
- Enforce Python 3.11, 3.12, 3.13 compatibility

Configuration files:

- `pyproject.toml` - Tool configurations
- `.github/workflows/riso-quality.yml` - Main quality workflow
- `.github/workflows/riso-matrix.yml` - Multi-version testing

**Rationale**: Quality gates prevent regressions and ensure professional output. Generated projects should follow best practices by default.

### V. Test-First Development

Tests MUST be written before implementation. The red-green-refactor cycle is NON-NEGOTIABLE:

1. Write tests that define expected behavior (RED - tests fail)
2. Implement minimal code to make tests pass (GREEN - tests succeed)
3. Refactor for clarity and performance (REFACTOR - tests still pass)

Test requirements:

- Unit tests for all modules (`tests/{module}/`)
- Smoke tests for template rendering (`samples/{variant}/smoke-results.json`)
- Integration tests for cross-module functionality
- Coverage targets: 80% minimum (standard), 95% target (strict)

**Rationale**: TDD catches bugs early, improves design, and provides living documentation. Tests define the contract.

### VI. Documentation Standards

Generated projects MUST include comprehensive, auto-updated documentation:

- `README.md` with quickstart, architecture, and module overview
- `docs/quickstart.md` for step-by-step setup
- `docs/modules/{feature}.md` for each optional module
- `AGENTS.md` for development workflow and automation

Documentation MUST:

- Be generated from Jinja2 templates (`*.md.jinja`)
- Include working code examples
- Link to external resources for deep dives
- Stay synchronized with code via CI checks

**Rationale**: Undocumented code is unusable code. Documentation as code ensures accuracy and maintainability.

### VII. Technology Consistency

All features MUST use the approved technology baseline:

- **Python**: 3.11+ managed via uv (not pip, poetry, or conda)
- **Node.js**: 20 LTS with pnpm ≥8 (when Node track enabled)
- **Quality**: ruff + mypy + pylint + pytest (no alternatives)
- **CI**: GitHub Actions (no CircleCI, Travis, etc.)
- **Containers**: Docker with multi-stage builds (when container module enabled)

New dependencies require justification:

- Production dependency: Must solve real user problem
- Development dependency: Must improve DX or quality
- Version constraints: Pin major version, allow minor/patch updates

**Rationale**: Consistency reduces cognitive load and ensures ecosystem compatibility. Tool churn wastes time and breaks workflows.

## Template Constraints

### File Organization

All template files MUST follow this structure:

```text
template/files/
├── python/          # Python-specific modules (conditional)
├── node/            # Node-specific modules (conditional)
├── shared/          # Cross-language shared files
├── tests/           # Test templates
└── docs/            # Documentation templates
```

Path conventions:

- Jinja2 templates: `*.py.jinja`, `*.md.jinja`, etc.
- Conditional includes: `{% if module_enabled %}...{% endif %}`
- Package namespace: `{{package_name}}.{module_name}`

### Copier Integration

All features MUST be controlled via `template/copier.yml`:

```yaml
# Feature example
feature_module:
  type: str
  help: "Enable feature module?"
  default: disabled
  choices:
    - enabled
    - disabled
```

Prompts MUST:

- Have clear help text
- Default to safe/minimal option
- Use consistent naming (`{name}_module`, `{name}_enabled`)
- Group related options

### CI/CD Requirements

Generated workflows MUST:

- Use GitHub Actions with marketplace actions
- Cache dependencies (uv, pnpm) with 70%+ hit rate
- Retry flaky tests (3 attempts with exponential backoff)
- Upload artifacts (test reports, coverage, logs) with 90-day retention
- Support matrix testing across Python versions (3.11, 3.12, 3.13)

Workflow naming:

- `riso-quality.yml` - Main quality suite
- `riso-matrix.yml` - Multi-version testing
- `riso-{feature}.yml` - Feature-specific workflows

## Development Workflow

### Feature Development Process

1. **Specification** (speckit.specify):
   - Create feature spec in `specs/{number}-{name}/spec.md`
   - Define user stories with acceptance criteria
   - List functional requirements and success criteria

2. **Clarification** (speckit.clarify):
   - Resolve ambiguities through Q&A
   - Document decisions in spec's Clarifications section

3. **Planning** (speckit.plan):
   - Create implementation plan in `plan.md`
   - Run constitution check (verify alignment with these principles)
   - Design data models and contracts

4. **Task Breakdown** (speckit.tasks):
   - Generate task list in `tasks.md`
   - Organize by user story for independent implementation
   - Mark parallel tasks with [P] flag

5. **Analysis** (speckit.analyze):
   - Validate consistency across spec, plan, tasks
   - Check requirement coverage and ambiguities
   - Verify constitution alignment

6. **Implementation** (speckit.implement):
   - Execute tasks following test-first discipline
   - Mark completed tasks with [X]
   - Validate at each checkpoint

### Code Review Requirements

All PRs MUST:

- Pass quality suite (`make quality`)
- Pass matrix tests (Python 3.11, 3.12, 3.13)
- Include tests for new functionality
- Update documentation for user-facing changes
- Pass constitution compliance check

Review checklist:

- [ ] Constitution principles followed
- [ ] Deterministic generation verified
- [ ] Minimal baseline preserved
- [ ] Quality gates pass
- [ ] Tests written first
- [ ] Documentation updated

### Complexity Justification

Features adding complexity MUST justify necessity:

| Concern | Required Justification |
|---------|----------------------|
| New dependency | Why existing tools insufficient? |
| Breaking change | Migration path defined? |
| Performance cost | Benchmarks show acceptable overhead? |
| API surface expansion | User value clearly demonstrated? |

Constitution review: Features that contradict principles require amendment proposal.

## Governance

### Amendment Procedure

1. **Proposal**: Open issue with `constitution-amendment` label
2. **Discussion**: Minimum 7-day comment period
3. **Impact Analysis**: Document affected features and migration path
4. **Approval**: Maintainer consensus required
5. **Implementation**: Update constitution + propagate to templates
6. **Versioning**: Increment version per semantic rules

### Versioning Policy

Constitution versions follow semantic versioning:

- **MAJOR (X.0.0)**: Principle removal, redefinition, or backward-incompatible governance change
- **MINOR (0.X.0)**: New principle added or existing principle materially expanded
- **PATCH (0.0.X)**: Clarifications, wording improvements, typo fixes

Version history in commit messages: `docs: amend constitution to vX.Y.Z (summary)`

### Compliance Review

All features MUST pass constitution check before merge:

```text
Constitution Check: ✅ PASS / ❌ FAIL

Principles verified:
✅ Module Sovereignty - Feature is optional via copier.yml
✅ Deterministic Generation - Render produces consistent output
✅ Minimal Baseline - No baseline bloat introduced
✅ Quality Integration - Integrates with ruff/mypy/pylint/pytest
✅ Test-First Development - Tests written before implementation
✅ Documentation Standards - Jinja-templated docs included
✅ Technology Consistency - Uses approved tech stack
```

Non-compliance blocks merge. Exceptions require maintainer approval and must be documented in `plan.md` with mitigation strategy.

### Living Document

This constitution is a living document. Feedback welcome via issues. Principles should evolve with project needs while maintaining core values.

**Version**: 1.0.0 | **Ratified**: 2025-11-01 | **Last Amended**: 2025-11-01
