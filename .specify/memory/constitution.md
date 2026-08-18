# Riso Template Constitution

> Governance principles for the Riso project template system.

## Core Principles

### I. Template Quality First

All template output must be production-ready. Generated projects should:

- Pass all quality checks (ruff, ty, pylint, pytest) without modification
- Include proper documentation and type hints
- Follow established patterns for the chosen technology stack
- Be immediately runnable after generation

### II. Modular Composition

Features are implemented as composable modules:

- Modules must be independently testable
- Module combinations must not create conflicts
- Each module has clear boundaries and responsibilities
- Shared logic is extracted to common packages

### III. Test-Driven Development

Testing is non-negotiable:

- Template changes require corresponding test updates
- Maintainer CI coverage floor is 70% (`just ci-full`); rendered Python packages enforce 90%
- Integration tests verify module combinations
- CI must pass before merging

### IV. Documentation Parity

Documentation stays synchronized:

- Template docs match generated project docs
- Changes to one require updates to the other
- All public APIs are documented
- Examples are tested and verified

### V. Backwards Compatibility

Breaking changes are managed carefully:

- Semantic versioning for template releases
- Migration guides for breaking changes
- Deprecation warnings before removal
- Clear upgrade paths documented

## Development Standards

### Code Style

- Python: Ruff for linting, Black formatting via Ruff
- TypeScript: ESLint + Prettier
- YAML/Jinja: Consistent indentation (2 spaces)
- Commit messages: Conventional Commits format

### Review Process

- All changes require PR review
- CI must pass before merge
- Breaking changes require maintainer approval
- Security issues are prioritized

### Quality Gates

- Ruff check must pass
- ty typecheck must pass (not mypy)
- Pylint score ≥9.0
- Maintainer test coverage ≥70%; rendered Python packages ≥90%
- No security vulnerabilities (pip-audit)

## Governance

- This constitution supersedes all other practices
- Amendments require documentation and maintainer approval
- All PRs must verify compliance with these principles
- Exceptions must be documented and justified

**Version**: 1.0.1 | **Ratified**: 2024-12-23 | **Last Amended**: 2026-08-18
