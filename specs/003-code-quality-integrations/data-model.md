# Data Model: Code Quality Integration Suite

This document defines the key entities for the code quality integration suite.

## QualitySuite

Describes the set of tools enabled for a render, their severity levels, and expected runtime budgets.

- **Attributes**:
  - `tools`: List of enabled tools (e.g., Ruff, Mypy, Pylint, pytest, ESLint).
  - `severity_levels`: Configuration for the severity of issues to report for each tool.
  - `runtime_budgets`: Expected maximum runtime for each tool.

## QualityRunEvidence

Captures per-tool exit codes, durations, and artifact locations.

- **Attributes**:
  - `ci_run_id`: The unique identifier for the CI run.
  - `check_name`: The name of the specific quality check (e.g., `ruff-lint`).
  - `exit_code`: The exit code of the tool.
  - `duration`: The duration of the tool's execution.
  - `artifact_location`: The path to the generated artifact (e.g., log file, coverage report).
- **Primary Key**: `ci_run_id` + `check_name`

## QualityProfileSelection

Represents the selected quality profile option.

- **Attributes**:
  - `profile_name`: The name of the selected profile (e.g., `standard`, `strict`).
  - `configuration_overrides`: A map of configuration overrides for the selected profile.
  - `ci_matrix_entries`: A list of CI matrix entries for the selected profile.