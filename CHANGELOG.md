# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive Python testing stack with 30+ pytest plugins
  - hypothesis for property-based testing
  - pytest-xdist for parallel test execution
  - pytest-cov for coverage reporting
  - pytest-asyncio for async testing
  - pytest-benchmark for performance testing
  - And many more plugins for enhanced testing capabilities

- Complete Jupyter/notebook stack integration
  - JupyterLab 4.2+ with modern extensions
  - jupyter-ai for AI-powered assistance
  - jupyterlab-lsp for language server protocol support
  - papermill for notebook parameterization
  - nbqa for quality checking notebooks
  - jupytext for notebook-as-code workflows
  - And 15+ additional Jupyter extensions

- Pre-commit configuration with comprehensive hooks
  - Ruff for Python linting and formatting
  - mypy for type checking
  - Bandit for security scanning
  - detect-secrets for secret detection
  - actionlint for GitHub Actions validation
  - Shell script validation with shellcheck
  - Dockerfile linting with hadolint

- Security scanning in CI/CD
  - Bandit security analysis
  - Safety dependency vulnerability scanning
  - Automated security reports in GitHub Actions

- Complete project metadata in pyproject.toml
  - Authors, keywords, classifiers
  - Project URLs (homepage, repository, docs, issues)
  - Comprehensive dependency groups (dev, security, docs, jupyter)

- Essential project documentation
  - CONTRIBUTING.md with detailed contribution guidelines
  - CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
  - SECURITY.md with vulnerability reporting process
  - .editorconfig for consistent editor settings

### Changed

- Updated GitHub Actions to latest versions
  - actions/checkout@v4 (was v3)
  - actions/setup-python@v5 (was v4)
  - actions/upload-artifact@v4 (maintained)
  - Added pip caching for faster CI runs

- Expanded Python version testing matrix to 3.11, 3.12, 3.13

- Enhanced CI/CD workflows
  - Added security job with Bandit and Safety
  - Improved coverage reporting with artifact uploads
  - Added quality profile matrix (standard, strict)
  - Extended artifact retention to 90 days

- Updated template pyproject.toml with comprehensive testing dependencies

### Fixed

- Python version consistency (now correctly requires >=3.11)

### Security

- Added security scanning tools (Bandit, Safety)
- Implemented secret detection in pre-commit hooks
- Added security policy and vulnerability reporting process
- Documented security best practices for template users

## [0.1.0] - 2025-10-30

### Added

- Initial release of Riso template system
- Modular Copier-based template with 15 feature specifications
- Optional modules:
  - CLI (Typer)
  - API (FastAPI/Fastify)
  - GraphQL (Strawberry)
  - MCP (FastMCP)
  - WebSockets
  - Documentation (Fumadocs/Sphinx/Docusaurus)
  - SaaS Starter (14-option technology matrix)
  - Code generation tools
  - Changelog and release management

- Quality assurance infrastructure
  - Ruff, mypy, pylint for Python
  - pytest with coverage
  - Make and uv task sync testing
  - GitHub Actions workflows

- Comprehensive documentation
  - Sphinx-based maintainer docs
  - Specification-driven development workflow
  - Module-specific guides

- Sample projects
  - 12+ sample configurations
  - Smoke test framework
  - Multiple layout options (single-package, monorepo)

### Documentation

- AGENTS.md for development workflow
- Specification templates in .specify/
- Module documentation in docs/modules/
- GitHub context files for LLM assistance

[Unreleased]: https://github.com/wyattowalsh/riso/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/wyattowalsh/riso/releases/tag/v0.1.0
