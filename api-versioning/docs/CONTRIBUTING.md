# Contributing to API Versioning Middleware

Thank you for your interest in contributing to the API Versioning middleware!

## Development Setup

### Prerequisites

- Python 3.11+ 
- uv (recommended) or pip
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/riso-template/api-versioning.git
cd api-versioning

# Install dependencies with uv
uv pip install -e ".[dev,all]"

# Or with pip
pip install -e ".[dev,all]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api_versioning --cov-report=html

# Run specific test file
pytest tests/unit/test_version.py -v

# Run benchmarks
pytest tests/performance/ --benchmark-only
```

### Code Quality

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type check
mypy src

# Run all quality checks
ruff check src tests && mypy src && pytest --cov
```

## Project Structure

```
api-versioning/
??? src/api_versioning/         # Source code
?   ??? core/                   # Core entities
?   ??? middleware/             # ASGI middleware
?   ??? handlers/               # Version-specific handlers
?   ??? security/               # Authentication & rate limiting
?   ??? monitoring/             # Performance metrics
?   ??? reliability/            # Hot-reload & circuit breakers
??? tests/                      # Test suite
?   ??? unit/                   # Unit tests
?   ??? integration/            # Integration tests
?   ??? performance/            # Performance benchmarks
??? examples/                   # Framework examples
??? docs/                       # Documentation
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints (Python 3.11+ syntax)
- Maximum line length: 100 characters
- Use dataclasses for data structures
- Prefer immutability (frozen dataclasses)

### Documentation

- All public APIs must have docstrings (Google style)
- Include examples in docstrings
- Update README when adding features
- Keep CHANGELOG.md current

### Testing

- Write tests for all new features
- Maintain >90% code coverage
- Include unit, integration, and performance tests
- Use descriptive test names

## Pull Request Process

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Implement your feature with tests
3. **Run quality checks**: Ensure all checks pass
4. **Commit**: Use clear, descriptive commit messages
5. **Push**: `git push origin feature/your-feature`
6. **Create PR**: Submit pull request with description

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] All quality checks pass
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)

## Commit Message Format

```
type(scope): brief description

Longer description if needed.

- Detail 1
- Detail 2

Closes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release commit
4. Tag release: `git tag v1.0.0`
5. Push: `git push && git push --tags`

## Getting Help

- **Documentation**: See README.md and docs/
- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
