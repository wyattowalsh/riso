# Testing Strategy

This playbook keeps **{{ project_name }}** aligned with the Riso template's
quality expectations. The baseline policy is **≥90% unit test coverage** with
explicit integration and end-to-end (e2e) evidence for every critical surface.
Treat the coverage floor as non-negotiable—changes that reduce coverage must
ship with offsetting test cases or written justification in the PR description
and code comments.

## Targets and thresholds

- **Unit tests:** `pytest --cov --cov-fail-under=90` must report ≥90% line
  coverage across Python packages (per job in the Python 3.11–3.13 matrix).
  Missing lines must be justified in code comments or skipped with explicit
  reasons.
- **Integration:** Exercise API endpoints, database paths, and background tasks
  with deterministic fixtures. Capture evidence in `tests/integration/` and wire
  them into CI by default. Emit coverage data via `coverage run -m pytest
  tests/integration` and combine with unit runs.
- **E2E & CLI:** Smoke the Typer CLI and optional MCP tools with real inputs;
  prefer black-box flows using example payloads in `tests/e2e/`. Capture
  coverage with `coverage run -m pytest tests/e2e` when practical so UI/CLI
  pathways count toward the floor.
- **Artifacts:** Keep `coverage.xml`, JUnit XML, and log bundles under artifact
  retention (90 days) for auditability.

## Commands to run

```bash
uv sync

# Fast feedback (lint + type + unit tests + coverage)
make quality
# or
QUALITY_PROFILE=standard uv run task quality

# Explicit coverage visualization with hard gate
uv run pytest --cov --cov-report=term-missing --cov-report=xml --cov-fail-under=90

# Integration and e2e passes with coverage emitted for combination
uv run coverage run -m pytest tests/integration
uv run coverage run -m pytest tests/e2e
uv run coverage combine
uv run coverage xml
```

## Coverage hygiene

- Avoid giant fixtures: prefer factory helpers and shared fixtures in
  `tests/conftest.py` to keep runtime low while covering branches.
- Mark slow tests with `@pytest.mark.slow` and include them in CI at least once
  per day; keep a smoke subset (`-m "not slow"`) for PRs.
- Validate CLI help text and option parsing with snapshot-style assertions so
  Typer changes stay tracked.
- When excluding lines (e.g., platform guards), add inline comments explaining
  the rationale and confirm coverage stays above the floor.
- Prefer `coverage.lcov` generation when Node tracks are enabled so browsers
  (Vitest) and Python data can be combined via `coverage combine` and reported
  through a single Cobertura file.

## Matrix and parity

- Run the quality matrix locally via `uv run python scripts/ci/run_quality_suite.py`
  to mirror CI behavior.
- Ensure dependency groups in `pyproject.toml` resolve on Python 3.11, 3.12, and
  3.13; misaligned deps often surface as coverage drops.
- Keep Node tracks (Fastify, docs-fumadocs) green by running `pnpm --filter` test
  targets when the `api_tracks` or docs options are enabled.

## Reporting and triage

- Coverage deltas should be called out in PR descriptions with references to
  `coverage.xml` and failing lines from `--cov-report=term-missing` (or
  `coverage html` when debugging locally).
- Flaky tests must be quarantined with a linked issue; avoid `@pytest.mark.flaky`
  without an owner or remediation plan.
- Integration and e2e suites should log sample payloads and response codes to
  help reproduce failures in CI artifacts.

## Enforcement and dashboards

- Require coverage jobs as mandatory branch protection checks. The default lane
  already enforces `--cov-fail-under=90`; keep matrix jobs mandatory so
  cross-version regressions are visible.
- Publish coverage summaries in PR descriptions or status comments (e.g., via
  `python-summarize-coverage` action or `gh api` uploads) so reviewers can act on
  deltas without downloading artifacts.
- When coverage dips, link to the exact uncovered lines and create follow-up
  issues if remediation exceeds the current PR scope.
