# Contributing to Riso

Thank you for your interest in contributing to Riso! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/riso.git
   cd riso
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/wyattowalsh/riso.git
   ```

## Development Setup

### Prerequisites

- Python ≥3.11
- Node.js 20 LTS (for Node/TypeScript templates)
- pnpm ≥8
- uv (Python dependency manager)
- Copier ≥9.1.0
- Git

### Initial Setup

```bash
# Install Python dependencies
uv sync --extra dev --extra security --extra docs

# Install pre-commit hooks
uv run pre-commit install

# Verify installation
uv run pytest tests/
```

### Optional Tools

- `mise` - for automatic tool provisioning
- `actionlint` - for GitHub Actions workflow validation

## Making Changes

### Branch Naming Convention

- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
git commit -m "feat(template): add Jupyter notebook module with full stack"
git commit -m "fix(hooks): fix subprocess injection vulnerability in pre_gen_project"
git commit -m "docs(readme): update installation instructions"
```

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes** thoroughly:
   ```bash
   # Run quality checks
   uv run python scripts/ci/run_quality_suite.py

   # Run tests
   uv run pytest tests/ -v

   # Test template rendering
   ./scripts/render-samples.sh
   ```

4. **Commit your changes** with descriptive commit messages

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub with:
   - Clear title following conventional commits format
   - Detailed description of changes
   - Link to related issues
   - Screenshots/examples if applicable
   - Checklist of completed items

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventional commits
- [ ] No merge conflicts with main
- [ ] Pre-commit hooks pass
- [ ] CHANGELOG.md updated (for significant changes)

## Coding Standards

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints for all functions
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting
- Use `mypy` for type checking
- Document all public functions with docstrings

**Example:**
```python
from typing import Dict, List

def validate_config(config: Dict[str, str]) -> List[str]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation error messages (empty if valid)

    Raises:
        ValueError: If config is None or empty
    """
    if not config:
        raise ValueError("Config cannot be empty")

    errors: List[str] = []
    # Validation logic...
    return errors
```

### JavaScript/TypeScript

- Use 2 spaces for indentation
- Follow Prettier formatting
- Use ESLint for linting
- Prefer `const` over `let`, avoid `var`
- Use TypeScript strict mode

### Templates (Jinja)

- Use 2 spaces for indentation
- Place logic in macros when reusable
- Comment complex conditional logic
- Test all template branches

### Shell Scripts

- Use `#!/usr/bin/env bash` shebang
- Set `set -euo pipefail` for safety
- Quote variables: `"$variable"`
- Use meaningful variable names

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/automation/sync_test.py -v

# Run with coverage
uv run pytest tests/ --cov=scripts --cov=template --cov-report=html

# Run sync test
uv run python tests/automation/sync_test.py --threshold 15
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names
- Include docstrings for complex tests
- Use fixtures for common setup
- Aim for >80% code coverage

**Example:**
```python
import pytest
from pathlib import Path

def test_template_renders_successfully(tmp_path: Path):
    """Test that default template renders without errors."""
    # Arrange
    destination = tmp_path / "test-project"

    # Act
    result = render_template(destination)

    # Assert
    assert result.exit_code == 0
    assert (destination / "pyproject.toml").exists()
```

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Smoke tests**: Test template rendering
- **Sync tests**: Verify make/uv task parity

## Documentation

### Types of Documentation

1. **Code Documentation**
   - Docstrings for all public functions
   - Inline comments for complex logic
   - Type hints for clarity

2. **User Documentation**
   - README.md for project overview
   - AGENTS.md for development workflow
   - Module-specific guides in `docs/modules/`

3. **API Documentation**
   - Auto-generated from docstrings
   - Located in `docs/api/`

### Building Documentation

```bash
# Install docs dependencies
uv sync --extra docs

# Build Sphinx docs
uv run sphinx-build docs dist/docs

# Serve docs locally
uv run python -m http.server -d dist/docs
```

### Documentation Standards

- Use Markdown for general docs
- Use reStructuredText for Sphinx docs
- Include code examples
- Keep examples up-to-date
- Link to related documentation

## Development Workflow

### Typical Development Cycle

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes** and **test locally**

4. **Run pre-commit checks**:
   ```bash
   uv run pre-commit run --all-files
   ```

5. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add my feature"
   git push origin feature/my-feature
   ```

6. **Create Pull Request**

7. **Address review feedback**

8. **Merge** after approval

## Specification-Driven Development

Riso follows a specification-driven approach:

1. Features are documented in `specs/NNN-feature-name/`
2. Each spec includes:
   - `spec.md` - Requirements and acceptance criteria
   - `plan.md` - Implementation roadmap
   - `tasks.md` - Actionable work items
   - `research.md` - Research notes
   - `contracts/` - Contract specifications

3. Reference existing specs for examples

## Release Process

Releases are managed by project maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v0.x.0 -m "Release v0.x.0"`
4. Push tag: `git push origin v0.x.0`
5. GitHub Actions creates release automatically

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/wyattowalsh/riso/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wyattowalsh/riso/discussions)
- **Documentation**: [Docs](docs/)

## Recognition

Contributors are recognized in:
- Release notes
- CHANGELOG.md
- GitHub contributors page

Thank you for contributing to Riso! 🎉
