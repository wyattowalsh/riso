# AGENTS.md

> AI coding agent instructions for **riso**. Human docs: [README.md](./README.md)

## Project Overview
<!-- agents-md:auto -->

Modular Copier-based project template for Python and Node.js applications.

- **Type**: Copier template project
- **Languages**: Python 3.11+ (primary), TypeScript, Node.js
- **Package Manager**: uv (Python), pnpm (Node.js)
- **License**: MIT

## Quick Reference
<!-- agents-md:auto -->

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Install all extras | `uv sync --all-extras` |
| Run tests | `uv run pytest` |
| Run tests (verbose) | `uv run pytest -v` |
| Run specific test | `uv run pytest tests/path/test_file.py::test_name` |
| Coverage | `uv run pytest --cov` |
| Lint (ruff) | `uv run ruff check .` |
| Format (ruff) | `uv run ruff format .` |
| Type check (ty) | `uv run ty check scripts template/hooks` |
| Static analysis | `uv run pylint scripts template/hooks tests` |
| Pre-commit (all) | `uv run pre-commit run --all-files` |
| Render samples | `./scripts/render-samples.sh` |
| Build docs | `uv run sphinx-build docs docs/_build` |
| Quality suite | `make quality` |

## Setup Commands
<!-- agents-md:auto -->

```bash
# Clone and setup
git clone https://github.com/wyattowalsh/riso.git
cd riso

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install --install-hooks

# Verify setup
uv run pytest tests/ -x -q
```

## Testing Instructions
<!-- agents-md:auto -->

- **Framework**: pytest with pytest-xdist (parallel), pytest-cov (coverage), pytest-randomly
- **Test paths**: `tests/`
- **Markers**: `slow`, `integration`, `unit`

```bash
# Run all tests (parallel by default)
uv run pytest

# Run specific test file
uv run pytest tests/unit/ci/test_render_matrix.py

# Run tests matching pattern
uv run pytest -k "test_validate"

# Run with coverage report
uv run pytest --cov=scripts --cov=template/hooks --cov-report=html

# Skip slow tests
uv run pytest -m "not slow"

# Run only integration tests
uv run pytest -m integration
```

## Pre-commit Hooks
<!-- agents-md:auto -->

Comprehensive pre-commit configuration with multi-stage hooks:

| Stage | Hooks | Purpose |
|-------|-------|---------|
| **pre-commit** | ruff (lint+format), ty, pylint, vulture, gitleaks, shellcheck, codespell, actionlint, mdformat, YAML/TOML/JSON checks | Code quality |
| **commit-msg** | commitlint, conventional-pre-commit | Commit format validation |
| **pre-push** | pytest, pip-audit | Full test suite + security |

```bash
# Install all hook types
uv run pre-commit install --install-hooks

# Run all hooks manually
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files

# Skip hooks (emergency only)
git commit --no-verify -m "emergency: bypass hooks"
```

## CI/CD Context
<!-- agents-md:auto -->

- **Platform**: GitHub Actions
- **Workflows**: `.github/workflows/quality.yml`

| Job | Triggers | Purpose |
|-----|----------|---------|
| `python-quality` | push, PR | Ruff, ty, pylint, pytest |
| `python-matrix` | push, PR | Python 3.11/3.12/3.13 matrix |
| `matrix-summary` | matrix complete | Block merge if any version fails |

**Required checks before merge**:
- `python-quality`
- `python-matrix / test-py311`
- `python-matrix / test-py312`
- `python-matrix / test-py313`
- `matrix-summary`

## CI Scripts Reference
<!-- agents-md:auto -->

| Script | Purpose | Command |
|--------|---------|---------|
| `render_matrix.py` | Render all sample variants | `uv run python scripts/ci/render_matrix.py` |
| `record_module_success.py` | Aggregate smoke test results | `uv run python scripts/ci/record_module_success.py` |
| `check_quality_parity.py` | Ensure Makefile/uv tasks sync | `uv run python scripts/ci/check_quality_parity.py` |
| `verify_context_sync.py` | Verify context file sync | `uv run python scripts/ci/verify_context_sync.py` |
| `validate_workflows.py` | Validate GitHub workflows | `uv run python scripts/ci/validate_workflows.py` |
| `validate_dockerfiles.py` | Validate Dockerfiles | `uv run python scripts/ci/validate_dockerfiles.py` |
| `validate_release_configs.py` | Validate release configs | `uv run python scripts/ci/validate_release_configs.py` |

## Gotchas & Edge Cases
<!-- agents-md:auto -->

- **CRITICAL**: Always use `uv run` prefix for Python commands (never bare `python` or `pytest`)
- **Fixtures**: Test fixtures are in `conftest.py` files—check there for utilities
- **Parallel tests**: Tests run in parallel by default (`-n auto`); use `-n 0` for sequential
- **Pre-commit CI**: Some hooks are skipped in CI (ty-check, pylint, pytest, vulture, gitleaks)—they run in dedicated jobs
- **Jinja templates**: Template files in `template/files/` use `.jinja` extension
- **Sample renders**: Never manually edit `samples/*/render/`—regenerate with render script
- **Lock files**: Never manually edit `uv.lock` or `pnpm-lock.yaml`—use package manager commands

## Quickstart

### First-Time Setup

Bootstrap your development environment with all required tooling:

```bash
# Check what tools you have/need (dry-run)
./scripts/setup/setup.sh

# Install missing tools (with confirmation prompts)
./scripts/setup/setup.sh --install

# Non-interactive installation (CI/automation)
./scripts/setup/setup.sh --install --yes

# Or use Make targets
make bootstrap          # Interactive install
make setup-check        # Check-only (CI-friendly, exits 0 or 1)
```

**Windows (PowerShell):**
```powershell
.\scripts\setup\setup.ps1                  # Check (dry-run)
.\scripts\setup\setup.ps1 -Install         # Install with prompts
.\scripts\setup\setup.ps1 -Install -Yes    # Non-interactive
```

**CI/CD with GitHub token** (avoids rate limits):
```bash
export GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}"
./scripts/setup/setup.sh --install --yes
```

### Verify Environment

```bash
# Check all tools are present
make setup-check

# Verify version constants are synchronized
make verify-versions

# View setup logs (location printed after setup completes)
tail -f ~/.local/state/riso/setup_*.log
```

### Get Started with Template

Get started with the default template variant:

```bash
# Render the default sample
./scripts/render-samples.sh

# Navigate to the rendered project
cd samples/default/render

# Set up the environment and run quickstart
PACKAGE=$(awk -F': ' '$1=="package_name"{print $2}' ../copier-answers.yml)
uv sync
uv run python -m ${PACKAGE}.quickstart

# Run quality checks
make quality
# or, when make is unavailable
QUALITY_PROFILE=standard uv run task quality

# For Node.js tracks (when applicable)
pnpm install
pnpm run build
pnpm run test
pnpm run lint
```

## Scope & Ownership

- Riso is a Copier template plus automation helpers; render actual projects with `copier copy` or `scripts/render-samples.sh`.
- Template maintainers keep sample renders, automation scripts, and documentation synchronized; rendered projects must author their own AGENTS.md.
- Apply the "lean, link out" pattern—keep this file as the control plane and point to deeper docs like `docs/quickstart.md.jinja`.

## Required Tooling
- Python ≥3.11 with uv (`python3 --version`, `uv version`); hooks expect uv to manage virtual environments.
- Node.js 20 LTS and pnpm ≥8 (`node --version`, `pnpm --version`) for TypeScript/Fumadocs/Fastify tracks.
- Copier CLI (`copier --version`); `template/hooks/pre_gen_project.py` fails fast if any prerequisite is missing.
- Optional: set `COPIER_CMD` to point at a custom Copier binary when invoking automation.

## Repository Map

```
riso/
├── .claude/                       # Claude Code configuration
│   ├── prompts/                   # Claude prompt templates
│   └── skills/                    # AI agent skills
│       ├── agents-md-manager/     # AGENTS.md sync & management
│       └── mcp-installer/         # MCP server installation
├── .github/
│   ├── workflows/                 # CI/CD workflows
│   └── context/                   # Canonical context snippets (synced)
├── src/
│   └── riso/                      # Python package (automation helpers)
├── template/                      # Copier payload
│   ├── files/
│   │   ├── python/                # Python project template files
│   │   ├── node/                  # Node.js project template files
│   │   └── shared/                # Shared across variants
│   │       ├── .claude/skills/    # Skills for rendered projects
│   │       ├── .github/           # CI workflow templates
│   │       └── quality/           # Quality suite templates
│   ├── hooks/                     # Pre/post generation hooks
│   │   ├── pre_gen_project.py     # Validates tooling (runs before render)
│   │   └── post_gen_project.py    # Writes metadata (runs after render)
│   └── prompts/                   # Copier prompt definitions
├── scripts/
│   ├── render-samples.sh          # Primary render automation
│   ├── setup/                     # Dev environment setup
│   │   ├── setup.sh               # Bash setup (macOS/Linux/WSL)
│   │   └── setup.ps1              # PowerShell setup (Windows)
│   └── ci/                        # CI automation scripts
├── samples/                       # Rendered sample projects
│   ├── default/                   # Default variant
│   │   ├── copier-answers.yml     # Answer file
│   │   └── render/                # Rendered output (gitignored except AGENTS.md)
│   └── metadata/                  # Aggregated metrics
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── docs/                          # Sphinx documentation source
├── specs/                         # GitHub Spec Kit workspace
├── web/                           # Web frontend (if applicable)
├── pyproject.toml                 # Python project config
└── .pre-commit-config.yaml        # Pre-commit hook configuration
```

**Key Paths**:
- `template/hooks/` – Validation and initialization logic (security-critical)
- `scripts/ci/` – CI automation scripts
- `.github/context/` – Must stay in sync with `template/files/shared/.github/context/`
- `scripts/render-samples.sh` – Primary automation entry point
- `template/copier.yml` – Copier template definition
- `pyproject.toml` – Project metadata and dependencies

## Build & Test Parity

**Local development:**

```bash
# From repo root - render and test template
./scripts/render-samples.sh
cd samples/default/render
uv sync
make quality
```

**CI workflows:** GitHub Actions workflows automatically run quality checks on PRs and commits to main. Rendered projects include:

- **`riso-quality.yml`**: Main quality workflow running ruff, ty, pylint, pytest with retry logic and artifact uploads (90-day retention)
- **`riso-matrix.yml`**: Matrix testing across Python 3.11, 3.12, 3.13 with fail-fast disabled and per-version artifacts

**Required branch protection checks:**
- `python-quality` - Main quality suite (ruff, ty, pylint, pytest)
- `python-matrix / test-py311` - Python 3.11 compatibility
- `python-matrix / test-py312` - Python 3.12 compatibility
- `python-matrix / test-py313` - Python 3.13 compatibility
- `matrix-summary` - Overall matrix status (blocks merge if any version fails)

**CI features:**
- Dependency caching with 70%+ hit rate target (uv.lock and pnpm-lock.yaml hashing)
- Retry logic with exponential backoff (3 attempts)
- Conditional Node.js job when `api_tracks` includes `node`
- Profile-based timeouts (10min standard, 20min strict)
- Cache hit/miss logging for debugging

**Viewing CI status:**
```bash
# In rendered project with GitHub remote
gh run list --limit 5
gh run view <run-id> --log
```

## Code Quality

Quality tools run via `make quality` or `uv run task quality` in rendered projects:

- **Linting:** ruff (configuration in `pyproject.toml`)
- **Type checking:** ty (configuration in `pyproject.toml` under `[tool.ty]`)
- **Static analysis:** pylint (configuration in `pyproject.toml`)
- **Testing:** pytest with coverage (configuration in `pytest.ini` and `coverage.cfg`)
- **Profiles:** `QUALITY_PROFILE=standard` (default) or `QUALITY_PROFILE=strict` for enhanced checks

**Test patterns:**
```python
# tests/test_hooks.py
import pytest
from riso.hooks import validate_tooling

def test_validate_tooling_success():
    """Test that validation passes with all tools present."""
    result = validate_tooling()
    assert result.success is True

@pytest.fixture
def mock_config():
    """Provide test configuration fixture."""
    return {"variant": "default", "force": False}

class TestRenderConfig:
    def test_init(self, mock_config):
        """Test configuration initialization."""
        assert mock_config["variant"] == "default"
```

**TypeScript test patterns (for Node.js tracks):**
```typescript
// packages/api-node/tests/health.test.ts
import { describe, it, expect } from 'vitest';
import { createApp } from '../src/app';

describe('Health endpoint', () => {
  it('should return 200 OK', async () => {
    const app = createApp();
    const response = await app.inject({ method: 'GET', url: '/health' });
    expect(response.statusCode).toBe(200);
  });
});
```

Quality suite implementation:

- `template/files/shared/quality/makefile.quality.jinja` – Makefile targets
- `template/files/shared/quality/uv_tasks/quality.py.jinja` – uv task definitions
- `scripts/ci/check_quality_parity.py` – ensures Makefile and uv tasks stay synchronized
- `scripts/ci/run_quality_suite.py` – CI orchestration script

**Critical Convention:** All Python commands MUST use `uv run` prefix (never bare `python` or `pytest`). This ensures consistent virtual environment usage across local development, CI/CD workflows, and rendered projects. Examples:
- ✅ `uv run pytest tests/`
- ✅ `uv run python -m mypackage.cli`
- ✅ `uv run task quality`
- ❌ `python -m pytest` (incorrect)
- ❌ `pytest tests/` (incorrect)

## Code Style

**Languages & Frameworks:**
- **Python:** 3.11+ (managed via uv)
- **Node.js:** 20 LTS with pnpm ≥8
- **TypeScript:** 5.6+ (strict mode)
- **Template Engine:** Jinja2 + Copier ≥9.0

**Formatters & Linters:**
- Python: ruff (format + lint), ty (type checking), pylint (static analysis)
- TypeScript/Node: ESLint + Prettier
- YAML: yamllint for workflow validation

**Indentation & Formatting:**
- Python: 4 spaces (enforced by ruff)
- TypeScript/JavaScript: 2 spaces (enforced by Prettier)
- YAML: 2 spaces
- Jinja: Match target file format
- Line length: 88 chars (Python), 100 chars (TypeScript)

**Import Order (Python):**
1. Standard library (`import os`, `from pathlib import Path`)
2. Third-party (`import pytest`, `from pydantic import BaseModel`)
3. Local (`from riso.hooks import validate`)

**Naming Conventions:**
- Python modules: `snake_case` (`render_samples.py`)
- Python classes: `PascalCase` (`AnalysisResult`)
- Jinja templates: `snake_case.ext.jinja` (`pyproject.toml.jinja`)
- Shell scripts: `kebab-case.sh` (`render-samples.sh`)

**Example (Python):**
```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RenderConfig:
    """Configuration for template rendering."""

    variant: str
    output_dir: Path
    force: bool = False

    def validate(self) -> None:
        """Validate configuration before rendering."""
        if not self.output_dir.parent.exists():
            raise ValueError(f"Parent directory does not exist: {self.output_dir.parent}")
```

**Example (Jinja template):**
```jinja
{# template/files/python/pyproject.toml.jinja #}
[project]
name = "{{ package_name }}"
version = "{{ version }}"
requires-python = ">={{ python_version }}"

{% if cli_module == "enabled" %}
[project.scripts]
{{ package_name }} = "{{ package_name }}.cli:app"
{% endif %}
```

## Security

**Secrets management:**

- Never commit secrets to the repository
- Use environment variables for sensitive configuration
- Rendered projects should implement `.env` files (gitignored by default)

**Production safety:**

- Pre-generation hook (`template/hooks/pre_gen_project.py`) validates required tooling and fails fast on missing dependencies
- Post-generation hook writes metadata to `.riso/post_gen_metadata.json` for audit trails
- Quality checks must pass before merging changes

**Security-critical paths:**

- `template/hooks/` – validation and initialization logic
- `scripts/ci/verify_context_sync.py` – ensures shared context files remain synchronized

## Git Workflow

**Branches:**
- `main` — Production-ready, protected
- `feature/*` — New features
- `fix/*` — Bug fixes
- `docs/*` — Documentation updates

**Commits:** Conventional Commits format:
```
feat(template): add WebSocket module scaffold
fix(hooks): handle missing uv gracefully
docs(agents): update repository map with directory tree
refactor(ci): consolidate quality check scripts
```

**Pull Requests:**
- Require passing CI checks (quality + matrix tests)
- Squash merge to main
- Delete branch after merge

## Python Execution Convention
**CRITICAL**: All Python scripts MUST be executed via `uv run python` to ensure proper virtual environment isolation and dependency management. Never invoke Python directly (`python`, `python3`, or `python3.11`). This applies to all automation scripts, CI workflows, and local development commands.

## Render & Validate Default Variant
```bash
./scripts/render-samples.sh
cd samples/default/render
PACKAGE=$(awk -F': ' '$1=="package_name"{print $2}' ../copier-answers.yml)
uv sync
uv run python -m ${PACKAGE}.quickstart
make quality
# or, when make is unavailable
QUALITY_PROFILE=standard uv run task quality
```
- The render writes metrics to `samples/default/baseline_quickstart_metrics.json` and smoke logs to `samples/default/smoke-results.json`.
- The quality suite logs tool durations to `.riso/quality-durations.json`; CI archives the full log bundle with 90-day retention.

## Render Specific Variant
```bash
./scripts/render-samples.sh --variant full-stack --answers samples/full-stack/copier-answers.yml
```
- Output lands in `samples/<variant>/render`; inspect `<variant>/smoke-results.json` for module statuses and `<variant>/metadata.json` for configuration.

## Aggregate & Governance Checks
- `uv run python scripts/ci/render_matrix.py` – render every `samples/*/copier-answers.yml`, update metadata, and recompute module success.
- `uv run python scripts/ci/record_module_success.py` – regenerate `samples/metadata/module_success.json` from existing smoke logs.
- `uv run python scripts/ci/run_quality_suite.py --profile {standard|strict}` – execute make/uv quality lanes and emit artifacts consumed by `.github/workflows/quality-matrix.yml`.
- `uv run python scripts/ci/run_baseline_quickstart.py` – refresh command timing evidence for downstream documentation.
- `uv run python scripts/ci/verify_context_sync.py` – ensure shared `.github/context` files stay byte-identical between template and repo.

## Module Validation Matrix (run inside a rendered project root)
- `cli_module=enabled`
  ```bash
  uv run python -m ${PACKAGE}.cli --help
  uv run pytest tests/test_cli.py
  ```
- `api_tracks` includes `python`
  ```bash
  uv run pytest tests/test_api_fastapi.py
  uv run uvicorn ${PACKAGE}.api.main:app --host 0.0.0.0 --port 8000
  ```
- `api_tracks` includes `node`
  ```bash
  pnpm install
  pnpm --filter api-node test
  pnpm --filter api-node run dev
  ```
- `mcp_module=enabled`
  ```bash
  uv run python -c "from shared.mcp import tooling; print(tooling.list_tools())"
  ```
- `docs_site=fumadocs`
  ```bash
  pnpm install
  pnpm --filter docs-fumadocs build
  pnpm --filter docs-fumadocs run dev
  ```
- `shared_logic=enabled`
  ```bash
  uv run python -c "from shared.logic import summarize_payload; print(summarize_payload({'service': 'shared', 'status': 'ok'}))"
  ```

## Key Artifacts & Logs
- `samples/<variant>/smoke-results.json` – per-module pass/fail/skip reasoning from render scripts.
- `samples/metadata/render_matrix.json` – inventory of rendered variants and latest smoke outcomes.
- `samples/metadata/module_success.json` – aggregated success rates per module for trend tracking.
- `.riso/post_gen_metadata.json` (inside renders) – rendered-at timestamp and module selections.

## References
- Quickstart playbook: `docs/quickstart.md.jinja`
- Automation: `scripts/render-samples.sh`, `scripts/hooks/post-init.sh`
- Module catalog: `template/files/shared/module_catalog.json.jinja`

## Git Workflow & Commits
<!-- agents-md:auto -->

**Branches:**
- `main` — Production-ready, protected
- `feature/*` — New features
- `fix/*` — Bug fixes
- `docs/*` — Documentation updates
- `claude/*` — AI-assisted development branches

**Commit format** (Conventional Commits):
```
feat(template): add WebSocket module scaffold
fix(hooks): handle missing uv gracefully
docs(agents): update repository map
refactor(ci): consolidate quality scripts
test(hooks): add validation edge cases
```

**Pull request workflow:**
1. Create feature branch from `main`
2. Run `uv run pre-commit run --all-files` before committing
3. Ensure all CI checks pass
4. Squash merge to main
5. Delete branch after merge

## Boundaries
<!-- agents-md:auto -->

### ✅ Always Do
- Run `uv run pre-commit run --all-files` before committing
- Use `uv run` prefix for all Python commands
- Update tests when modifying functionality
- Keep template and repo context files in sync
- Follow conventional commit format
- Run quality checks before pushing (`make quality`)

### ❓ Ask First
- Adding new dependencies to `pyproject.toml`
- Modifying CI workflow files (`.github/workflows/`)
- Changing Copier prompt definitions (`template/prompts/`)
- Updating pre/post generation hooks
- Adding new sample variants
- Modifying `.pre-commit-config.yaml`

### 🚫 Never Touch
- `.env*` files (secrets, gitignored)
- `samples/*/render/` directories (generated—regenerate via script)
- `node_modules/`, `.venv/`, `__pycache__/` (managed by tools)
- `.riso/post_gen_metadata.json` (auto-generated)
- `uv.lock`, `pnpm-lock.yaml` (modify via package manager only)
- `dist/`, `build/`, `.next/` (build outputs)
- GitHub Actions secrets or repository settings

### ⚠️ Avoid
- Running bare `python` or `pytest`—always use `uv run`
- Manually editing rendered sample directories
- Committing secrets, API keys, or credentials
- Skipping CI checks or force-pushing to main
- Duplicating content between AGENTS.md and pointer files

<!-- MANUAL ADDITIONS START -->
### Docs Site Maintenance
- Primary maintainer docs live in `docs/` (Shibuya Sphinx). Build locally with `uv sync --group docs` + `uv run sphinx-build docs docs/_build`.
- Keep the template copy at `template/files/python/docs/` in lockstep; changes to navigation or config must be mirrored.
- Doc dependencies are defined in the `docs` dependency group inside `template/files/python/pyproject.toml.jinja`.
- For rendered projects with `docs_site=sphinx-shibuya`, CI runs `uv run sphinx-build docs dist/docs`.

### Claude Code Skills
Two AI agent skills are installed at both project and template levels:

| Skill | Location | Purpose |
|-------|----------|---------|
| `agents-md-manager` | `.claude/skills/agents-md-manager/` | AGENTS.md as SSOT with platform sync |
| `mcp-installer` | `.claude/skills/mcp-installer/` | Universal MCP server management |

**agents-md-manager** — Manages AGENTS.md files across AI coding platforms:
```bash
# Detect all agent files in codebase
uv run python .claude/skills/agents-md-manager/detect.py .

# Analyze AGENTS.md quality (scores against 6-area framework)
uv run python .claude/skills/agents-md-manager/analyze.py AGENTS.md

# Sync AGENTS.md → all platform pointer files
uv run python .claude/skills/agents-md-manager/sync.py .

# Migrate deprecated formats (.cursorrules → .cursor/rules/)
uv run python .claude/skills/agents-md-manager/migrate.py .
```

**mcp-installer** — Research, install, and sync MCP servers:
```bash
# Search MCP registries
uv run python -m scripts.research --query "github" --cwd .claude/skills/mcp-installer

# Install MCP server to Claude Code
uv run python -m scripts.cli install github --cwd .claude/skills/mcp-installer

# Sync servers across all AI interfaces
uv run python -m scripts.sync --from claude-code --to all --cwd .claude/skills/mcp-installer

# Validate MCP configuration
uv run python -m scripts.validate --interface claude-code --cwd .claude/skills/mcp-installer
```

Rendered projects inherit these skills via `template/files/shared/.claude/skills/`.
<!-- MANUAL ADDITIONS END -->

## Boundaries

### Always Do
- Run `make quality` or `uv run task quality` before committing
- Use `uv run` prefix for all Python commands
- Update tests when modifying functionality
- Keep template and repo context files in sync (`scripts/ci/verify_context_sync.py`)
- Follow conventional commit format

### Ask First
- Adding new dependencies to `pyproject.toml`
- Modifying CI workflow files (`.github/workflows/`)
- Changing Copier prompt definitions (`template/prompts/`)
- Updating pre/post generation hooks
- Adding new sample variants

### Never Touch
- `.env*` files (secrets, gitignored)
- `samples/*/render/` directories (generated output, recreate via render script)
- `node_modules/`, `.venv/`, `__pycache__/` (managed by tools)
- `.riso/post_gen_metadata.json` (auto-generated)
- `uv.lock`, `pnpm-lock.yaml` (modify via package manager commands only)
- Files in `dist/`, `build/`, `.next/` (build outputs)
- GitHub Actions secrets or repository settings

### Avoid
- Do not run bare `python` or `pytest` commands—always use `uv run` prefix
- Do not manually edit rendered sample directories—regenerate instead
- Do not commit secrets, API keys, or credentials
- Do not skip CI checks or force-push to main
- Do not duplicate content between AGENTS.md and platform pointer files

## Recent Changes

- 015-claude-code-skills: Added AI agent skills for Claude Code at project and template levels—`agents-md-manager` (AGENTS.md SSOT with detection, analysis, platform sync, migration) and `mcp-installer` (universal MCP server research, installation, cross-interface sync, validation). Skills located in `.claude/skills/` and propagate to rendered projects via `template/files/shared/.claude/skills/`.
- 014-changelog-release-management: Added automated changelog generation and release management with conventional commit enforcement via Git hooks (commitlint ≥18.0.0), semantic versioning automation (semantic-release ≥23.0.0), human-readable changelog generation with categorized changes (💥/✨/🐛 sections), GitHub Release creation, breaking change detection with migration guide templates, multi-registry publishing (PyPI via twine, npm via @semantic-release/npm, Docker Hub), monorepo support with independent package versioning, pre-release versions (alpha, beta, rc), release completion <10min, comprehensive logging with correlation IDs, GitHub Actions workflow (riso-release.yml), credential management via GitHub Secrets with annual rotation, comprehensive docs (changelog-release.md, quickstart, upgrade guide)
- 008-websockets-scaffold: Added WebSocket real-time communication module with connection lifecycle management, heartbeat/ping-pong mechanism (30s interval, 60s timeout), room-based broadcasting with <100ms latency (p95), FastAPI authentication integration, rate limiting (100 msg/60s window, configurable), backpressure handling with bounded queues, structured error responses, pytest fixtures, support for 10K+ concurrent connections with <10MB/1K conn memory overhead, comprehensive docs (websockets.md, quickstart, upgrade guide)
- 005-container-deployment: Added Docker/docker-compose support with multi-stage Dockerfiles (Python 3.11-slim-bookworm, Node 20-alpine), docker-compose orchestration (API/docs/databases), GitHub Actions workflows (riso-container-build.yml with hadolint/Trivy, riso-container-publish.yml with semantic versioning), container validation (render_matrix.py, record_module_success.py), health endpoints (FastAPI/Fastify /health), security hardening (UID 1000:1000, HEALTHCHECK, SBOM/provenance), registry support (ghcr.io OIDC, Docker Hub, AWS ECR), comprehensive documentation (containers.md, context guide, upgrade guide)
- 004-github-actions-workflows: Added GitHub Actions CI/CD workflows with quality checks (ruff, ty, pylint, pytest), matrix testing across Python 3.11/3.12/3.13, retry logic with exponential backoff, dependency caching, artifact uploads with 90-day retention, and conditional Node.js job support
- 003-code-quality-integrations: Added unified quality suite (ruff, ty, pylint, pytest, coverage) with standard/strict profiles, auto-healing tool provisioning, parallelized CI jobs, and 90-day artifact retention
- 002-docs-template-expansion: Added Python 3.11 (uv-managed), Node.js 20 LTS, TypeScript 5.6, POSIX shell + Fumadocs (Next.js 15), Sphinx 7.4 + Shibuya theme, Docusaurus 3, pnpm ≥8, mise 2024.9+, uv ≥0.4

## Active Technologies

- Changelog & Release Management: commitlint ≥18.0.0 + @commitlint/config-conventional ≥18.0.0 (commit validation), semantic-release ≥23.0.0 (version automation), @semantic-release/changelog ≥6.0.3 (changelog generation), @semantic-release/commit-analyzer ≥11.1.0 (commit analysis), @semantic-release/exec ≥6.0.3 (custom scripts), @semantic-release/git ≥10.0.1 (Git operations), @semantic-release/github ≥9.2.6 (GitHub Releases), @semantic-release/npm ≥11.0.2 (npm publishing), commitizen ≥4.3.0 + cz-conventional-changelog ≥3.3.0 (interactive commits), twine (PyPI publishing), Git hooks (commit-msg validation), GitHub Secrets (credential management), Pydantic v2 (data models), Python 3.11+ (automation scripts) (014-changelog-release-management)
- WebSocket communication: FastAPI ≥0.104.0 WebSocket support, websockets ≥14.0 library, python-jose ≥3.3.0 for JWT authentication, Pydantic v2 for message validation, asyncio for concurrent connection handling, Redis pub/sub pattern for multi-server broadcasting (documented, optional), Prometheus metrics integration via prometheus_client (optional) (008-websockets-scaffold)
- YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering) + GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`, `nick-fields/retry@v3`, `docker/setup-buildx-action@v3`, `docker/build-push-action@v5`, `aquasecurity/trivy-action@0.20.0`), actionlint (workflow validation), hadolint (Dockerfile linting), Trivy (container security scanning), existing quality tools from feature 003 (004-github-actions-workflows, 005-container-deployment)
- Workflow artifacts (JUnit XML, coverage reports, logs, container images, SBOMs, scan results) stored in GitHub Actions artifact storage with 90-day retention (004-github-actions-workflows, 005-container-deployment)
- Matrix testing across Python 3.11, 3.12, 3.13 with fail-fast disabled and per-version artifacts (004-github-actions-workflows)
- Container registries: GitHub Container Registry (ghcr.io, OIDC default), Docker Hub (optional), AWS ECR (optional) with semantic versioning (latest, v1.2.3, v1.2, v1, SHA) (005-container-deployment)
- Python 3.11 (uv-managed), optional Node.js 20 LTS + ruff, ty, pylint, pytest, coverage, optional eslint + typescript (003-code-quality-integrations)
