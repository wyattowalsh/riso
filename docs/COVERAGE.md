# Code Coverage Guide

This document explains how code coverage works in the Riso project, how to generate coverage reports, and how to use Codecov.

## Table of Contents

- [What is Code Coverage?](#what-is-code-coverage)
- [Running Coverage Locally](#running-coverage-locally)
- [Understanding Coverage Reports](#understanding-coverage-reports)
- [Codecov Integration](#codecov-integration)
- [Coverage Requirements](#coverage-requirements)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## What is Code Coverage?

Code coverage measures what percentage of your code is executed during tests. It helps identify:
- **Untested code**: Functions and branches not covered by tests
- **Dead code**: Code that is never executed
- **Test quality**: How thoroughly your tests exercise the codebase

### Types of Coverage

1. **Line Coverage**: Percentage of lines executed
2. **Branch Coverage**: Percentage of conditional branches taken (if/else)
3. **Function Coverage**: Percentage of functions called
4. **Statement Coverage**: Percentage of statements executed

Riso tracks **line** and **branch** coverage.

## Running Coverage Locally

### Using uv (Recommended)

```bash
# Run tests with coverage
uv run pytest --cov=scripts --cov=template/hooks --cov-report=html --cov-report=xml --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Using the Quality Suite

```bash
# Run full quality suite (includes coverage)
uv run python scripts/ci/run_quality_suite.py

# With strict profile
QUALITY_PROFILE=strict uv run python scripts/ci/run_quality_suite.py
```

### Coverage Configuration

Coverage settings are in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["scripts", "template/hooks"]
branch = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.venv/*",
]

[tool.coverage.report]
precision = 2
skip_empty = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

## Understanding Coverage Reports

### Terminal Report

```
Name                                Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------
scripts/__init__.py                     0      0      0      0   100%
scripts/logging_config.py              45      5     12      2    88%
scripts/subprocess_security.py        125     15     38      4    87%
template/hooks/validation.py           89      8     22      3    90%
---------------------------------------------------------------------
TOTAL                                 259     28     72      9    88%
```

**Columns**:
- **Stmts**: Total statements
- **Miss**: Statements not executed
- **Branch**: Total branches
- **BrPart**: Branches partially covered
- **Cover**: Coverage percentage

### HTML Report

The HTML report (`htmlcov/index.html`) provides:
- File-by-file coverage breakdown
- Line-by-line highlighting:
  - ✅ **Green**: Executed
  - ❌ **Red**: Not executed
  - ⚠️ **Yellow**: Partially covered (branches)
- Missing line ranges
- Branch coverage details

### XML Report

The XML report (`coverage.xml`) is used for:
- CI/CD integration (GitHub Actions)
- Codecov upload
- Third-party tools

## Codecov Integration

### What is Codecov?

Codecov is a coverage analysis tool that:
- Tracks coverage over time
- Shows coverage in pull requests
- Provides detailed coverage visualization
- Enforces coverage requirements

### Setup

1. **Add Codecov to your repository**:
   - Go to https://codecov.io/
   - Sign in with GitHub
   - Select your repository

2. **Add Codecov token as GitHub secret**:
   - Settings → Secrets → Actions → New repository secret
   - Name: `CODECOV_TOKEN`
   - Value: Your Codecov upload token

3. **Coverage is automatically uploaded** via `.github/workflows/quality.yml`

### Codecov Dashboard

Visit `https://codecov.io/gh/<username>/<repo>` to view:

- **Overall coverage**: Project-wide coverage percentage
- **Coverage trends**: Coverage over time
- **Pull request comments**: Coverage impact of PRs
- **File browser**: File-by-file coverage
- **Flags**: Coverage by test suite (Python version, profile)

### Codecov Configuration

Configuration is in `codecov.yml`:

```yaml
coverage:
  status:
    project:
      default:
        target: 80%       # Target coverage
        threshold: 2%     # Allow 2% drop
    patch:
      default:
        target: 80%       # New code coverage
        threshold: 5%     # Allow 5% drop for patches
```

### Interpreting Codecov Comments

Codecov adds comments to pull requests:

```
Codecov Report
Coverage: 88.35% (+0.25%)
Files: 15 files (+2)
Lines: 1,234 lines (+45)
Branches: 234 branches (+12)

Files with missing coverage:
• scripts/new_feature.py: 75.00%
• template/hooks/new_hook.py: 82.50%

Status: ✅ Coverage increased
```

**Status indicators**:
- ✅ **Pass**: Coverage meets requirements
- ❌ **Fail**: Coverage below threshold
- ⚠️ **Warning**: Coverage decreased but within threshold

## Coverage Requirements

### Minimum Coverage

- **Overall project**: 80% coverage
- **Pull request changes**: 80% coverage
- **Threshold**: 2% decrease allowed

### Coverage by Component

| Component | Target Coverage | Notes |
|-----------|----------------|-------|
| Scripts | 85%+ | Core functionality |
| Hooks | 80%+ | Template hooks |
| CI Scripts | 75%+ | CI/CD automation |
| Templates | N/A | Jinja templates excluded |

### When to Exclude Code

Use `# pragma: no cover` for:

```python
# Debugging code
def debug_print(msg: str) -> None:  # pragma: no cover
    if DEBUG:
        print(msg)

# Type checking code
if TYPE_CHECKING:  # pragma: no cover
    from typing import SomeType

# Abstract methods
@abstractmethod
def must_implement(self) -> None:  # pragma: no cover
    raise NotImplementedError

# Main entry points
if __name__ == "__main__":  # pragma: no cover
    main()

# Defensive programming
def validate(value: int) -> None:
    if value < 0:
        raise ValueError("Value must be positive")
    # This should never happen
    if value > sys.maxsize:  # pragma: no cover
        raise OverflowError("Value too large")
```

## Best Practices

### Writing Testable Code

1. **Keep functions small**: Easier to test
2. **Minimize side effects**: Pure functions are easier to test
3. **Dependency injection**: Pass dependencies as arguments
4. **Avoid global state**: Use parameters and return values

### Improving Coverage

1. **Identify uncovered code**:
   ```bash
   uv run pytest --cov=scripts --cov-report=html
   open htmlcov/index.html
   ```

2. **Write tests for missing coverage**:
   - Red lines: Add tests that execute those lines
   - Yellow lines: Add tests for all branches (if/else)

3. **Test edge cases**:
   - Empty inputs
   - Boundary values
   - Error conditions
   - Different code paths

### Coverage Doesn't Mean Quality

⚠️ **Important**: 100% coverage doesn't mean bug-free code.

Coverage measures **execution**, not **correctness**:

```python
# 100% coverage but wrong implementation
def add(a: int, b: int) -> int:
    return a - b  # Bug!

# Test with 100% coverage
def test_add():
    result = add(2, 2)
    assert result == 4  # This will fail!
```

**Focus on**:
- Meaningful assertions
- Testing behavior, not implementation
- Edge cases and error handling
- Integration between components

## Troubleshooting

### Coverage Not Generated

**Problem**: No `coverage.xml` file created

**Solutions**:
```bash
# Ensure coverage is installed
uv sync --extra dev

# Run pytest with coverage flags
uv run pytest --cov=scripts --cov=template/hooks --cov-report=xml

# Check for pytest-cov plugin
uv run pytest --version
```

### Coverage Too Low

**Problem**: Coverage below target

**Solutions**:
1. Add tests for untested code
2. Remove dead code
3. Mark defensive code with `# pragma: no cover`
4. Check if test discovery is finding all tests

### Codecov Upload Fails

**Problem**: Codecov action fails in CI

**Solutions**:
1. Verify `CODECOV_TOKEN` is set in GitHub secrets
2. Check coverage.xml exists: `ls -la coverage.xml`
3. Review Codecov action logs
4. Set `fail_ci_if_error: false` to make upload optional

### Coverage Decreased in PR

**Problem**: PR shows coverage drop

**Solutions**:
1. Add tests for new code
2. Check if refactoring removed tests
3. Verify test discovery finds new test files
4. Review Codecov comment for specific files

### Branch Coverage Issues

**Problem**: Branch coverage lower than line coverage

**Solutions**:
```python
# Test both branches
def process(value: int) -> str:
    if value > 0:
        return "positive"
    else:
        return "non-positive"

# Test both paths
def test_process_positive():
    assert process(5) == "positive"

def test_process_non_positive():
    assert process(0) == "non-positive"
    assert process(-5) == "non-positive"
```

## References

- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Codecov documentation](https://docs.codecov.com/)
- [Testing Python Applications](https://realpython.com/python-testing/)
- [Writing Better Tests](https://martinfowler.com/articles/practical-test-pyramid.html)

## Coverage Checklist

Before committing:

- [ ] Tests pass locally: `uv run pytest`
- [ ] Coverage generated: `uv run pytest --cov --cov-report=html`
- [ ] Coverage meets target: Check `htmlcov/index.html`
- [ ] New code has tests: Review coverage report
- [ ] Edge cases tested: Boundary values, errors, empty inputs
- [ ] Meaningful assertions: Tests check correctness, not just execution
- [ ] No false coverage: Avoid tests that don't verify behavior

In pull requests:

- [ ] Coverage uploaded to Codecov
- [ ] Coverage change reviewed (Codecov comment)
- [ ] Failing coverage checks addressed
- [ ] Coverage regression justified and documented
