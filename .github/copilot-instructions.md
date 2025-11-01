# riso Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-30

## Active Technologies
- YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering) + GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`, `nick-fields/retry@v3`), actionlint (workflow validation), existing quality tools from feature 003 (004-github-actions-workflows)
- Workflow artifacts (JUnit XML, coverage reports, logs) stored in GitHub Actions artifact storage with 90-day retention (004-github-actions-workflows)
- Matrix testing across Python 3.11, 3.12, 3.13 with fail-fast disabled and per-version artifacts (004-github-actions-workflows)

- Python 3.11 (uv-managed), optional Node.js 20 LTS + ruff, mypy, pylint, pytest, coverage, optional eslint + typescript (003-code-quality-integrations)

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
- 004-github-actions-workflows: Added YAML (GitHub Actions workflow syntax), Python 3.11+ (for validation scripts), Jinja2 (for template rendering) + GitHub Actions marketplace actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`), actionlint (workflow validation), existing quality tools from feature 003

- 003-code-quality-integrations: Added Python 3.11 (uv-managed), optional Node.js 20 LTS + ruff, mypy, pylint, pytest, coverage, optional eslint + typescrip

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
