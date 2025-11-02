# Implementation Plan: Changelog & Release Management

**Branch**: `014-changelog-release-management` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-changelog-release-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements automated changelog generation and release management for projects rendered from the Riso template. The system enforces conventional commit message format via Git hooks (installed automatically via post-clone script with manual fallback), generates semantic versions from commit history, produces categorized changelogs, creates GitHub Releases, and publishes artifacts to package registries (PyPI, npm, Docker Hub). Registry credentials are stored as GitHub Secrets with annual rotation reminders documented in project README. The complete release process must complete in under 10 minutes, with changelog generation under 30 seconds for repositories with up to 1000 commits.

Technical approach leverages semantic-release ecosystem with customizations for Riso's multi-language template context (Python + optional Node.js). Git hooks use commitlint/commitizen for validation. GitHub Actions workflows orchestrate the release process, integrating with existing riso-quality.yml and riso-matrix.yml workflows. Configuration is template-generated via Jinja2 with per-project customization through Copier prompts.

## Technical Context

**Language/Version**: Python 3.11+ (template baseline), Node.js 20 LTS (when api_tracks includes node)  
**Primary Dependencies**: semantic-release (changelog/version), commitlint (commit validation), commitizen (commit authoring), GitHub Actions marketplace actions (release creation, registry publishing)  
**Storage**: Git repository (commit history, tags), GitHub Secrets (registry credentials), generated files (CHANGELOG.md, package versions)  
**Testing**: pytest for Python validation scripts, smoke tests for rendered projects, integration tests for GitHub Actions workflows  
**Logging**: JSON-structured logs with INFO/DEBUG/ERROR levels, output to stdout and `.riso/logs/release-{timestamp}.log`, 30-day retention policy, correlation IDs for tracing multi-step operations across version calculation → changelog generation → artifact publishing  
**Target Platform**: GitHub-hosted repositories with GitHub Actions CI/CD, Linux runners for workflow execution  
**Project Type**: Template module - generates into rendered projects (both single-project and monorepo structures)  
**Performance Goals**: <30s changelog generation (1000 commits), <10min full release process (3 registries), <2min registry publishing  
**Constraints**: GitHub API rate limits (5000 req/hour authenticated), registry API timeouts, deterministic template generation, backward compatibility with existing Riso features  
**Scale/Scope**: Supports monorepo with independent package versioning, handles 1000+ commits per release cycle, manages 3+ concurrent registry publications

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research)

✅ **Module Sovereignty**: Feature controlled via `changelog_module=enabled` Copier prompt, fully optional, no impact on baseline template functionality. Documentation in `docs/modules/changelog-release.md.jinja`. Smoke tests in `samples/` variants.

✅ **Deterministic Generation**: All template files use Jinja2 with deterministic logic. No random values, timestamps, or system paths in generated code. Configuration files (.commitlintrc.yml, .releaserc.yml) generated from stable templates. Verified via render_matrix.py.

✅ **Minimal Baseline**: Feature is optional module - baseline project (<50 files) unaffected when disabled. When enabled, adds ~10 files (config, hooks, workflows). Core functionality uses established tools (semantic-release, commitlint) rather than custom implementations.

✅ **Quality Integration**: Generated Python scripts (hook installers, version validators) integrate with ruff/mypy/pylint/pytest. Workflows tested via riso-quality.yml. CI validates generated projects across Python 3.11/3.12/3.13.

✅ **Test-First Development**: Tests written before implementation (TDD discipline):

- Unit tests for commit message validation logic
- Smoke tests for git hook installation
- Integration tests for GitHub Actions workflows
- End-to-end tests for full release cycle

✅ **Documentation Standards**: Jinja2-templated documentation (`docs/modules/changelog-release.md.jinja`), quickstart guides, README sections with setup instructions, credential rotation schedule documented.

✅ **Technology Consistency**: Uses approved baseline (Python 3.11+, uv, GitHub Actions). Node.js 20 LTS with pnpm only when user enables node track. Integrates with existing riso-quality.yml/riso-matrix.yml workflows. No new tooling beyond semantic-release ecosystem.

**Status**: ✅ **PASS** - No constitution violations. Feature aligns with all core principles.

## Project Structure

### Documentation (this feature)

```text
specs/014-changelog-release-management/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Data structures and entities
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/           # Phase 1: Configuration file schemas
│   ├── commitlint-config.schema.json
│   ├── semantic-release-config.schema.json
│   └── release-workflow.schema.json
├── checklists/          # Quality validation
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Phase 2: Implementation task breakdown (created by /speckit.tasks)
```

### Source Code (template files - repository root)

```text
template/files/
├── shared/
│   ├── .github/
│   │   └── workflows/
│   │       └── riso-release.yml.jinja           # Main release workflow
│   ├── .commitlintrc.yml.jinja                  # Commit message linting config
│   ├── .releaserc.yml.jinja                     # semantic-release configuration
│   ├── scripts/
│   │   └── release/
│   │       ├── install-hooks.py.jinja           # Git hook installation script
│   │       ├── validate-commit.py.jinja         # Commit message validator
│   │       └── publish-artifacts.py.jinja       # Multi-registry publisher
│   └── docs/
│       └── modules/
│           └── changelog-release.md.jinja        # Module documentation
├── python/
│   └── release/
│       ├── __init__.py.jinja
│       ├── version.py.jinja                      # Version utilities
│       └── changelog.py.jinja                    # Changelog generation helpers
└── node/
    └── release/
        ├── commitizen.config.js.jinja            # Commitizen config (when node track enabled)
        └── package-version.js.jinja              # npm version sync script

tests/
└── release/
    ├── test_commit_validation.py                 # Unit tests for commit validation
    ├── test_version_calculation.py               # Unit tests for version logic
    ├── test_changelog_generation.py              # Unit tests for changelog
    ├── test_hook_installation.py                 # Smoke tests for hook setup
    └── integration/
        ├── test_release_workflow.py              # Integration test for full release
        └── test_registry_publishing.py           # Integration test for registries

scripts/ci/
├── validate_release_configs.py                   # CI validation for release configs
└── test_release_template_rendering.py            # Render validation

samples/
├── changelog-python/                              # Python-only project with changelog
│   ├── copier-answers.yml
│   └── smoke-results.json
├── changelog-monorepo/                            # Monorepo with independent versioning
│   ├── copier-answers.yml
│   └── smoke-results.json
└── changelog-full-stack/                          # Python + Node with changelog
    ├── copier-answers.yml
    └── smoke-results.json
```

**Structure Decision**: Template module pattern - feature files live in `template/files/shared/` for cross-language support, with language-specific extensions in `template/files/python/` and `template/files/node/`. Generated projects include release scripts, workflows, and configuration files. Monorepo support via semantic-release's workspace plugins. Testing infrastructure validates both template rendering and generated project functionality.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No complexity violations - constitution check passed all principles.*

---

## Post-Design Constitution Re-evaluation

After completing Phase 0 (Research) and Phase 1 (Design & Contracts), re-validating all principles with design-level evidence:

### ✅ Principle 1: Module Sovereignty
**Status**: PASS (Verified Post-Design)

**Evidence**:
- Module fully optional via `changelog_module=enabled/disabled` Copier prompt (copier.yml)
- No baseline modifications - all files rendered conditionally via Jinja2 `{% if changelog_module == "enabled" %}`
- Git hooks installed via opt-in scripts (`uv run setup-hooks`, `pnpm run setup-hooks`), not automatic
- Workflow dependencies explicit: riso-release.yml only generated when changelog_module=enabled

**Design Validation**: Configuration files (.commitlintrc.yml, .releaserc.yml) scoped to project root, do not conflict with existing tools. Hook installation is manual/scripted, not forced during copier generation.

### ✅ Principle 2: Deterministic Generation
**Status**: PASS (Verified Post-Design)

**Evidence**:
- All configuration files templated with explicit Jinja2 variables (package_name, project_slug, api_tracks)
- Commit types, changelog format, tag format all configurable via .releaserc.yml template
- No runtime environment lookups - registry credentials via GitHub Secrets (documented in README)
- Version calculation follows strict SemVer 2.0.0 rules (fix→PATCH, feat→MINOR, BREAKING→MAJOR)

**Design Validation**: semantic-release configuration deterministic - same commits + config = same version. Hook installation script idempotent (checks existing hooks before writing). Workflow YAML static, no dynamic job generation.

### ✅ Principle 3: Minimal Baseline
**Status**: PASS (Verified Post-Design)

**Evidence**:
- Node.js 20 LTS required only when changelog_module=enabled AND api_tracks includes node
- Python 3.11+ already baseline - no new interpreter requirement
- commitlint/semantic-release installed as devDependencies (package.json) when Node track enabled
- For Python-only projects: uses @semantic-release/exec with Python scripts (no Node runtime dependency except semantic-release CLI)

**Design Validation**: Dependency footprint minimal - commitlint (6 deps), semantic-release (12 deps including plugins), commitizen (4 deps). Total ~150MB npm install. Python-only mode defers to existing uv environment.

### ✅ Principle 4: Quality Integration
**Status**: PASS (Verified Post-Design)

**Evidence**:
- riso-release.yml depends on riso-quality.yml (needs: [quality] gate)
- Commit message validation (commitlint) runs pre-push via Git hooks
- Release workflow conditional on quality checks passing
- Test suite includes commit validation unit tests, version calculation tests, changelog generation tests

**Design Validation**: Quality gates enforced at three levels: (1) pre-commit hook validates format, (2) CI quality workflow validates code, (3) release workflow blocks on quality pass. Integration tests validate end-to-end release flow including registry publishing.

### ✅ Principle 5: Test-First Development
**Status**: PASS (Verified Post-Design)

**Evidence**:
- Test structure defined in plan.md before implementation: test_commit_validation.py, test_version_calculation.py, test_changelog_generation.py
- Contract schemas (commitlint-config.schema.json, semantic-release-config.schema.json) provide test fixtures for configuration validation
- Sample projects (changelog-python, changelog-monorepo, changelog-full-stack) serve as smoke tests

**Design Validation**: tests/release/ directory includes unit tests (commit/version/changelog) and integration tests (release workflow, registry publishing). Smoke tests validate template rendering + module activation + first release cycle.

### ✅ Principle 6: Documentation Standards
**Status**: PASS (Verified Post-Design)

**Evidence**:
- quickstart.md: Developer onboarding with setup, first commit, first release walkthroughs
- docs/modules/changelog-release.md.jinja: Comprehensive module documentation (architecture, configuration, troubleshooting)
- Inline examples in contract schemas (commitlint-config, semantic-release-config)
- README sections: credential rotation schedule, commit message format, monorepo conventions

**Design Validation**: Documentation covers three audiences: (1) template maintainers (plan.md, research.md, data-model.md), (2) rendered project developers (quickstart.md, module docs), (3) end users (README commit format guide, troubleshooting).

### ✅ Principle 7: Technology Consistency
**Status**: PASS (Verified Post-Design)

**Evidence**:
- Python 3.11+ baseline - consistent with Features 003/004/005/007/008/009
- Node.js 20 LTS - consistent with Feature 002 (docs templates)
- GitHub Actions - extends existing riso-quality.yml/riso-matrix.yml workflows (Feature 004)
- uv package management - consistent with all Python features
- pnpm for Node - consistent with Feature 002 (Fumadocs/Docusaurus)

**Design Validation**: No new technology paradigms introduced. semantic-release (Node) + commitlint (Node) + Python scripts (version updates, publishing) follows established pattern from Feature 002 (mixed Python/Node tracks). Git hooks via Python scripts consistent with uv-first approach.

---

**Post-Design Conclusion**: All 7 constitution principles remain satisfied after detailed design. No complexity violations detected. Feature integrates cleanly with existing workflows (Feature 004), quality tools (Feature 003), and container publishing (Feature 005). Ready for task breakdown (Phase 2).

---

## Phase 1 Completion Report

**Status**: ✅ COMPLETE (2025-11-02)

### Generated Artifacts

**Phase 0: Research (research.md)**
- 8 research sections covering all technical unknowns
- Tooling decisions: commitlint + commitizen + semantic-release ecosystem
- Hook strategy: Python script via `uv/pnpm run setup-hooks`
- Credential approach: GitHub Secrets with annual rotation
- Changelog format: Standard semantic-release with emoji sections
- Monorepo strategy: Independent versioning via @semantic-release/monorepo
- CI/CD design: Dedicated riso-release.yml workflow
- Performance plan: Caching + shallow clones + parallel publishing

**Phase 1: Design & Contracts**

1. **data-model.md** (10 entities)
   - CommitMessage (Conventional Commits format)
   - Version (SemVer 2.0.0 with calculation rules)
   - ChangelogEntry (categorized changes)
   - Change (commit metadata with PR links)
   - ReleaseConfiguration (workflow settings)
   - CommitTypeConfig, Asset, PluginConfiguration, MonorepoConfig, PackageConfig
   - Entity relationships and state transitions
   - Validation rules and performance considerations

2. **contracts/commitlint-config.schema.json** (103 lines)
   - JSON Schema validating .commitlintrc.yml files
   - Defines commit types (feat, fix, docs, etc.)
   - Scope restrictions and subject length limits
   - Rule configuration with severity levels

3. **contracts/semantic-release-config.schema.json** (90 lines)
   - JSON Schema validating .releaserc.yml files
   - Branches, tag format, plugin configuration
   - Python (@semantic-release/exec) and npm plugin support
   - Changelog, Git, GitHub integration

4. **contracts/release-workflow.schema.json** (246 lines)
   - JSON Schema validating .github/workflows/riso-release.yml files
   - Workflow triggers (push, workflow_dispatch)
   - Job structure with quality dependencies
   - Environment variable definitions (GITHUB_TOKEN, PYPI_TOKEN, NPM_TOKEN, DOCKER_HUB_*)
   - Step validation (checkout, setup-node, setup-python, semantic-release)

5. **quickstart.md** (350+ lines)
   - Developer onboarding guide
   - Setup instructions (hook installation, GitHub Secrets)
   - Commit message format reference
   - First release walkthrough
   - Troubleshooting section
   - Advanced configuration examples

### Post-Design Constitution Check

All 7 principles verified with design-level evidence:
- ✅ Module Sovereignty: Optional via Copier prompt, no baseline modifications
- ✅ Deterministic Generation: All configs templated, no runtime lookups
- ✅ Minimal Baseline: Node.js only when Node track enabled
- ✅ Quality Integration: Release depends on quality workflow
- ✅ Test-First Development: Test structure defined before implementation
- ✅ Documentation Standards: Quickstart + module docs + inline examples
- ✅ Technology Consistency: Aligns with Features 002/003/004/005

### Agent Context Updates

Updated `.github/copilot-instructions.md`:
- Added commitlint ≥18.0.0, semantic-release ≥23.0.0 to Active Technologies
- Documented @semantic-release/* plugin ecosystem
- Registered Git hook installation pattern (`uv/pnpm run setup-hooks`)
- Noted GitHub Secrets credential management with annual rotation
- Listed performance targets (<30s/1000 commits, <10min release, <2min per registry)

### Next Steps

**Command**: `/speckit.tasks`

**Purpose**: Generate `tasks.md` with implementation task breakdown organized by user story.

**Expected Deliverables**:
- Task breakdown for each of 6 user stories (P1: commit enforcement, P1: changelog generation, P1: version automation, P2: GitHub releases, P2: breaking changes, P3: artifact publishing)
- Tasks organized by implementation order with dependencies marked
- Parallel tasks flagged with [P] for concurrent execution
- Test-first discipline enforced (write tests before implementation)
- Checkpoints for validation after each user story

**File Paths**:
- Feature Directory: `/Users/ww/dev/projects/riso/specs/014-changelog-release-management/`
- Implementation Plan: `/Users/ww/dev/projects/riso/specs/014-changelog-release-management/plan.md`
- Specification: `/Users/ww/dev/projects/riso/specs/014-changelog-release-management/spec.md`
- Branch: `014-changelog-release-management`

---

**Planning Phase Complete** ✅  
Ready for task breakdown and implementation.
