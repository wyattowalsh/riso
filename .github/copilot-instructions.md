# riso Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-30

## Active Technologies
- YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering) + GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`, `nick-fields/retry@v3`, `docker/setup-buildx-action@v3`, `docker/build-push-action@v5`, `aquasecurity/trivy-action@0.20.0`), actionlint (workflow validation), hadolint (Dockerfile linting), Trivy (container security scanning), existing quality tools from feature 003 (004-github-actions-workflows, 005-container-deployment)
- Workflow artifacts (JUnit XML, coverage reports, logs, container images, SBOMs, scan results) stored in GitHub Actions artifact storage with 90-day retention (004-github-actions-workflows, 005-container-deployment)
- Matrix testing across Python 3.11, 3.12, 3.13 with fail-fast disabled and per-version artifacts (004-github-actions-workflows)
- Container registries: GitHub Container Registry (ghcr.io, OIDC default), Docker Hub (optional), AWS ECR (optional) with semantic versioning (latest, v1.2.3, v1.2, v1, SHA) (005-container-deployment)
- Python 3.11 (uv-managed), optional Node.js 20 LTS + ruff, mypy, pylint, pytest, coverage, optional eslint + typescript (003-code-quality-integrations)
- Python 3.11+ (managed via uv, consistent with template baseline) + Typer ≥0.20.0, Loguru (logging), Rich (formatting), tomli/tomllib (TOML parsing) (009-typer-cli-scaffold)
- TOML configuration files (config.toml or .app-name.toml in project directory) (009-typer-cli-scaffold)
- Python 3.11+ (consistent with Riso template baseline, managed via uv) + Strawberry GraphQL ≥0.200.0, FastAPI ≥0.104.0 (ASGI integration), uvicorn (ASGI server), pydantic ≥2.0.0 (data validation) (007-graphql-api-scaffold)
- Pluggable resolver pattern - supports any data source (PostgreSQL via async SQLAlchemy recommended, but also REST APIs, in-memory, etc.) (007-graphql-api-scaffold)
- Python 3.11+ + FastAPI ≥0.104.0 (WebSocket support), websockets library, pydantic ≥2.0.0 (008-websockets-scaffold)
- In-memory connection registry (default), optional Redis for multi-server (documented pattern) (008-websockets-scaffold)
- Python 3.11+ (template baseline), Node.js 20 LTS (when api_tracks includes node) + semantic-release (changelog/version), commitlint (commit validation), commitizen (commit authoring), GitHub Actions marketplace actions (release creation, registry publishing) (014-changelog-release-management)
- Git repository (commit history, tags), GitHub Secrets (registry credentials), generated files (CHANGELOG.md, package versions) (014-changelog-release-management)
- Python 3.11+ (uv-managed), optional Node.js 20 LTS (when api_tracks includes node) (016-conventional-commit-tooling)
- Version-controlled configuration files (.commitlintrc.yml, pyproject.toml), local log files (optional) (016-conventional-commit-tooling)

## Project Structure

```text
template/files/shared/.github/workflows/
  riso-quality.yml.jinja
  riso-matrix.yml.jinja
scripts/ci/
  validate_workflows.py
scripts/hooks/
  workflow_validator.py
docs/modules/
  workflows.md.jinja
```

## Commands

# Validate workflow templates
python scripts/ci/validate_workflows.py template/files/shared/.github/workflows/

# Render samples with workflows
./scripts/render-samples.sh

# Check workflow generation in rendered project
cd samples/default/render
ls -la .github/workflows/

# Validate rendered workflows with actionlint
actionlint .github/workflows/riso-*.yml

## Code Style

Python 3.11 (uv-managed), optional Node.js 20 LTS: Follow standard conventions

## Recent Changes
- 016-conventional-commit-tooling: Added Python 3.11+ (uv-managed), optional Node.js 20 LTS (when api_tracks includes node)
- 016-conventional-commit-tooling: Added Python 3.11+ (uv-managed), optional Node.js 20 LTS (when api_tracks includes node)
- 014-changelog-release-management: Added Python 3.11+ (template baseline), Node.js 20 LTS (when api_tracks includes node) + semantic-release (changelog/version), commitlint (commit validation), commitizen (commit authoring), GitHub Actions marketplace actions (release creation, registry publishing)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
