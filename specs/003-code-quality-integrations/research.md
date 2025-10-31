# Research: Code Quality Integration Suite

This document summarizes the best practices and decisions for the technologies used in the code quality integration suite.

## Ruff

- **Decision**: Use `ruff.toml` for configuration. Combine linting and formatting. Integrate with pre-commit hooks and CI/CD.
- **Rationale**: Ruff is an all-in-one tool that is extremely fast. A dedicated `ruff.toml` is cleaner than mixing it with `pyproject.toml` when the configuration is extensive. Pre-commit hooks and CI/CD integration enforce quality gates automatically.
- **Alternatives considered**: Flake8, Black, isort, Pylint (Ruff can replace all of these).

## Mypy

- **Decision**: Use `mypy.ini` or `pyproject.toml` for a strict default configuration. Integrate with pre-commit hooks and CI/CD.
- **Rationale**: Strict typing catches errors early. A configuration file ensures consistency. Pre-commit and CI integration automate the checks.
- **Alternatives considered**: Pyright (another popular type checker).

## Pylint

- **Decision**: Use `.pylintrc` or `pyproject.toml` for configuration. Integrate with pre-commit hooks and CI/CD.
- **Rationale**: Pylint provides a different set of checks than Ruff and can be used to enforce more stylistic or complex rules.
- **Alternatives considered**: Using only Ruff (which can replace some of Pylint's functionality).

## pytest

- **Decision**: Use a dedicated `tests/` directory with a `conftest.py` for shared fixtures. Use `pytest.ini` or `pyproject.toml` for configuration. Integrate with CI/CD for automated testing and coverage reporting.
- **Rationale**: This is a standard and well-established structure for pytest projects. It promotes organized, readable, and maintainable tests.
- **Alternatives considered**: `unittest` (built-in, but less feature-rich than pytest).

## uv

- **Decision**: Use `pyproject.toml` for dependency definition and commit `uv.lock` to version control. Use `uv sync` in CI/CD for fast and reproducible builds.
- **Rationale**: `uv` is a modern, high-performance package manager that ensures reproducible environments and speeds up CI/CD pipelines.
- **Alternatives considered**: `pip` + `virtualenv` (slower, less integrated).

## pnpm

- **Decision**: Use `pnpm-workspace.yaml` for monorepo setup. Integrate with pre-commit hooks and CI/CD. Use the `workspace:` protocol for internal packages.
- **Rationale**: `pnpm` is efficient for monorepos, saving disk space and providing fast installations. The `workspace:` protocol simplifies internal dependency management.
- **Alternatives considered**: `npm`, `yarn` (pnpm is generally faster and more efficient for monorepos).