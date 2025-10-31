# Quickstart: Code Quality Integration Suite

This document provides a guide to using the integrated code quality suite in your project.

## Overview

The project template now includes a comprehensive code quality suite that integrates Ruff, Mypy, and Pylint. This suite is designed to help you maintain high code quality, enforce coding standards, and catch potential issues early in the development process.

## Running the Quality Suite

A `make quality` command is available in the generated project's Makefile. This command will run the entire quality suite, including:

- **Ruff**: for linting and formatting.
- **Mypy**: for static type checking.
- **Pylint**: for additional code analysis.
- **pytest**: for running smoke tests.

Alternatively, you can use the `uv` command:

```bash
uv run task quality
```

## Quality Profiles

The quality suite can be configured with different profiles:

- **`standard` (default)**: A pragmatic set of rules that provides a good balance between strictness and developer convenience.
- **`strict`**: A more stringent set of rules for projects that require a higher level of code quality.

You can select the quality profile when you generate the project or by modifying the project's configuration.

## Customization

The configuration for each tool is located in the following files:

- `ruff.toml`
- `mypy.ini`
- `.pylintrc`

You can customize these files to tailor the quality suite to your project's specific needs.