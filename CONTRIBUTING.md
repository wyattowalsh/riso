# Contributing to Riso

Thank you for your interest in contributing to Riso! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Getting Started

### Prerequisites

- Python ≥3.11 with [uv](https://github.com/astral-sh/uv)
- Node.js 20 LTS with [pnpm](https://pnpm.io/) ≥8
- [Copier](https://copier.readthedocs.io/) ≥9.1.0
- Git

### Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/riso.git
   cd riso
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Render a sample to test:
   ```bash
   ./scripts/render-samples.sh --variant default
   ```

4. Run quality checks:
   ```bash
   uv run task quality
   ```

## Development Workflow

### Branch Naming

- `feat/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring
- `test/description` - Test additions/changes

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes

3. Run quality checks:
   ```bash
   uv run task quality
   ```

4. Run tests:
   ```bash
   uv run pytest tests/
   ```

5. Commit with conventional commits:
   ```bash
   git commit -m "feat: add amazing feature"
   ```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code style changes (formatting)
- `refactor` - Code refactoring
- `test` - Test additions/changes
- `chore` - Maintenance tasks

**Examples:**
```
feat(api): add rate limiting support
fix(cli): resolve argument parsing error
docs: update installation instructions
```

## Quality Standards

### Code Style

- **Python**: Ruff for linting and formatting
- **TypeScript**: ESLint + Prettier
- **YAML/Jinja**: 2-space indentation

### Testing Requirements

- All new code must have tests
- Maintain ≥80% coverage for scripts
- Use pytest markers for slow tests

### Type Hints

- Use modern Python type hints (`dict`, `list`, `|`)
- All public functions must be typed

## Pull Request Process

1. Ensure all quality checks pass
2. Update documentation if needed
3. Add tests for new functionality
4. Fill out the PR template
5. Request review from maintainers

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No security vulnerabilities introduced

## Reporting Issues

### Bug Reports

Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages/logs

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered

## Getting Help

- Open an issue for questions
- Check existing issues first
- Be patient and respectful

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
