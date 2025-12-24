# Riso Template Constitution

> Governance principles for the Riso project template system.

## Core Principles

### I. Template Quality First

All template output must be production-ready. Generated projects should:
- Pass all quality checks (ruff, mypy, pylint, pytest) without modification
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
- Rendered projects must achieve ≥90% test coverage
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
- Mypy strict mode must pass
- Pylint score ≥9.0
- Test coverage ≥90%
- No security vulnerabilities (pip-audit)

## Governance

- This constitution supersedes all other practices
- Amendments require documentation and maintainer approval
- All PRs must verify compliance with these principles
- Exceptions must be documented and justified

**Version**: 1.0.0 | **Ratified**: 2024-12-23 | **Last Amended**: 2024-12-23
