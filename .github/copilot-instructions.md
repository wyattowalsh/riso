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
- 009-typer-cli-scaffold: Added Python 3.11+ (managed via uv, consistent with template baseline) + Typer ≥0.20.0, Loguru (logging), Rich (formatting), tomli/tomllib (TOML parsing)
- 004-github-actions-workflows: Added YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering) + GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`), actionlint (workflow validation), existing quality tools from feature 003

- 003-code-quality-integrations: Added Python 3.11 (uv-managed), optional Node.js 20 LTS + ruff, mypy, pylint, pytest, coverage, optional eslint + typescrip

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
