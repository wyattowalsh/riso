# Riso Template Constitution

## Core Principles

### I. Template Sovereignty

The template directory (`template/`) is the single source of truth for all generated project artifacts.

**Requirements**:
- All template files (prompts, hooks, metadata) live in `template/copier.yml`, `template/prompts/`, `template/hooks/`, `template/files/**`
- Shared context assets mirrored in `.github/context/` must stay synchronized
- Every template change requires regenerating `samples/**` renders
- Proof of sovereignty via `copier diff` evidence attached to all template modifications
- No manual edits to rendered projects should be necessary for baseline functionality

**Validation**:
- CI jobs verify sample renders match template source
- `scripts/ci/verify_context_sync.py` ensures `.github/context/` stays synchronized
- Pull requests blocked until samples regenerated and `copier diff` clean

### II. Deterministic Generation

Template rendering must be reproducible, idempotent, and platform-independent.

**Requirements**:
- Same prompt answers always produce identical output across macOS/Linux/Windows
- Hooks remain side-effect free (no network calls, no filesystem mutations outside render target)
- Sample renders (`default`, `cli-docs`, `api-monorepo`, `full-stack`) regenerated on every template change
- Baseline timing metrics captured via `scripts/ci/run_baseline_quickstart.py`
- Module success rates tracked via `scripts/ci/record_module_success.py`
- Documentation SLA status monitored via `scripts/ci/track_doc_publish.py`

**Validation**:
- Render matrix executes across platforms in CI
- Smoke tests validate module combinations deterministically
- Performance regression detection for render times
- Zero tolerance for non-deterministic template logic

### III. Minimal Baseline, Optional Depth

The default render must be lightweight and production-ready; complexity is opt-in via prompts.

**Requirements**:
- Baseline keeps only uv-managed Python 3.11+ quickstart (pytest, ruff, mypy, pylint)
- Optional modules (CLI, API, MCP, docs, shared logic) stay behind explicit prompts
- `cli_module`, `api_tracks`, `mcp_module`, `docs_site`, `shared_logic` all default to disabled/minimal
- Each module documents compatibility matrix and dependencies
- No module should bloat the baseline render with unused tooling or dependencies

**Validation**:
- Baseline render completes in <10 minutes including smoke tests
- Default sample has minimal dependency footprint (Python stdlib + uv essentials)
- Optional module activation measured against baseline performance budget
- ≥98% module success rate across all permutations

### IV. Documented Scaffolds

Every rendered project includes comprehensive, executable documentation.

**Requirements**:
- `docs/quickstart.md.jinja` provides step-by-step setup and validation commands
- Module-specific docs (`docs/modules/*.md.jinja`) cover architecture, usage, troubleshooting
- `.github/context/*.md` files provide extension patterns and customization guidance
- Upgrade guide (`docs/upgrade-guide.md.jinja`) documents breaking changes and migration paths
- All documentation validated via render smoke tests

**Validation**:
- Quickstart commands execute successfully in freshly rendered projects
- Documentation links resolve correctly (no 404s)
- Code examples in docs run without modification
- Troubleshooting sections address common failure modes identified via user feedback

### V. Automation-Governed Compliance

CI/CD pipelines enforce constitutional compliance before merging any changes.

**Requirements**:
- `.github/workflows/template-ci.yml` runs lint/tests, render matrix, docs build, baseline timing checks
- Governance automation enforces ≥98% module success-rate threshold
- Documentation publish SLA verification (<15 min from merge to deployment)
- Quality gates block merge on: lint failures, failed smoke tests, missing sample regeneration, broken docs
- Compliance checkpoints post to automation API for audit trails

**Validation**:
- All template PRs pass full render matrix before merge
- Branch protection enforces required CI checks
- Failed renders produce actionable error messages with reproduction steps
- Compliance dashboard shows historical trends for success rates and performance

## Quality Standards

### Code Quality

**Python**:
- All Python code executed via `uv run python` (never bare `python` or `python3`)
- Ruff linting with zero errors (warnings acceptable with justification)
- MyPy type checking with strict mode
- Pylint static analysis (configurable rules in `pyproject.toml`)
- Pytest coverage ≥80% for new modules

**Node.js**:
- ESLint + TypeScript strict mode for all Node projects
- Prettier formatting enforced
- Vitest for unit testing with coverage reports

**Templates**:
- Jinja2 templates validated for syntax correctness
- Conditional logic tested across all prompt combinations
- Hadolint linting for Dockerfiles (zero errors required)

### Security Standards

- No secrets committed to repository
- `.env` files gitignored by default in rendered projects
- Pre-generation hooks validate required tooling and fail fast
- Post-generation hooks write audit metadata to `.riso/post_gen_metadata.json`
- Container images scanned with Trivy/Grype (zero HIGH/CRITICAL vulnerabilities)
- Non-root execution (UID 1000:1000) for all containerized services

### Performance Standards

- Baseline render completes in <10 minutes (local development)
- Optional module permutations complete in <15 minutes
- Docker builds: Python <3min, Node <5min on GitHub Actions standard runners
- Container images: Python <500MB, Node <300MB, docs <200MB
- docker-compose services achieve healthy status in <30 seconds

## Development Workflow

### Feature Implementation

1. **Specification Phase** (`/speckit.specify`):
   - Create feature spec with user stories, requirements, success criteria
   - Document principle compliance evidence
   - Define functional and non-functional requirements

2. **Clarification Phase** (`/speckit.clarify`):
   - Identify ambiguities via coverage analysis
   - Ask sequential clarification questions
   - Integrate answers into spec before proceeding

3. **Planning Phase** (`/speckit.plan`):
   - Generate implementation plan with technical context
   - Create data model, contracts, research documents
   - Validate constitution check passes all gates
   - Produce executable quickstart guide

4. **Task Breakdown** (`/speckit.tasks`):
   - Generate phased task list organized by user story
   - Mark parallel tasks, dependencies, checkpoints
   - Estimate effort and define independent test criteria

5. **Analysis Phase** (`/speckit.analyze`):
   - Detect inconsistencies, ambiguities, coverage gaps
   - Validate constitution alignment
   - Remediate issues before implementation

6. **Implementation** (`/speckit.implement`):
   - Execute tasks following phased approach
   - Validate after each checkpoint
   - Regenerate samples and update documentation

### Review Process

- All template changes require PR with regenerated samples
- CI must pass full render matrix (all 4 sample variants)
- Documentation updates required for user-facing changes
- `copier diff` evidence attached to prove template sovereignty
- At least one maintainer approval required for merge

## Governance

### Amendment Process

Constitution changes require:
1. RFC document proposing change with rationale
2. Impact analysis on existing features
3. Migration plan for affected projects
4. Maintainer consensus (≥2 approvals)
5. Version bump and ratification date update

### Compliance Verification

- All PRs/reviews must verify principle compliance
- Constitutional violations block merge (non-negotiable)
- Complexity additions must be justified against minimal baseline principle
- Performance regressions require explicit approval and documentation

### Conflict Resolution

When specifications conflict with constitution:
1. Constitution authority is non-negotiable
2. Adjust spec/plan/tasks to align with principles
3. If principle itself needs change, follow amendment process
4. Never dilute, reinterpret, or silently ignore constitutional requirements

**Version**: 1.0.0 | **Ratified**: 2025-10-29 | **Last Amended**: 2025-11-01
