# Testing Strategy

This playbook keeps the template and rendered projects aligned on quality
expectations. Coverage floors are **not** the same in both trees:

- **Maintainer repo** (`riso/`): `--cov-fail-under=70` via `just ci-full`.
- **Rendered Python packages**: generated `coverage.cfg` currently selects 90%
  with a Python CLI and 85% otherwise; explicit CI arguments can impose 90%.

Treat the floor that applies to the tree you are changing as
non-negotiable—changes that reduce coverage must ship with offsetting test
cases or written justification in the PR description and code comments.

## Targets and thresholds

- **Unit tests:** maintainer jobs use `pytest --cov --cov-fail-under=70`.
  Rendered Python packages use `--cov-fail-under=90` on the 3.11–3.13 matrix.
  Missing lines must be justified in code comments or skipped with explicit
  reasons.
- **Integration:** Exercise FastAPI/Fastify endpoints, database paths, and
  background tasks with deterministic fixtures. Capture evidence in
  `tests/integration/` and wire them into CI by default. Emit coverage data via
  `coverage run -m pytest tests/integration` and combine with unit runs.
- **E2E & CLI:** Smoke the Typer CLI and optional MCP tools with real inputs;
  prefer black-box flows using example payloads in `tests/e2e/`. Capture
  coverage with `coverage run -m pytest tests/e2e` when practical so UI/CLI
  pathways count toward the floor.
- **Artifacts:** Keep `coverage.xml`, JUnit XML, and log bundles under artifact
  retention (90 days) for auditability.

## Commands to run

### Maintainer repo (`riso/` root)

```bash
just quality
uv run pytest --cov --cov-report=term-missing --cov-fail-under=70
```

### Inside a rendered Python package

```bash
# Render + sync env
./scripts/render-samples.sh --variant api-python \
  --answers samples/api-python/copier-answers.yml
cd samples/api-python/render/python
uv sync --group quality --group test --group api_python --group api_python_test

# Fast feedback (lint + type + unit tests + coverage)
just quality
# or `make quality` when task_runner=makefile|both
# or, when no aggregator is present
QUALITY_PROFILE=standard uv run task quality

# Coverage visualization with the package's configured hard gate
uv run pytest --cov --cov-config=coverage.cfg --cov-report=term-missing --cov-report=xml

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
- Keep Vitest and Python coverage reports separate. `coverage combine` accepts
  coverage.py data files, not Node LCOV reports; combine cross-language reports
  only with a reporting service that explicitly supports both formats.

## Generated runtime qualification

A successful render establishes that Copier emitted a project. Qualify each
enabled runtime with its own compiler and tools, and record the actual toolchain
version separately from a declared minimum version. A compiler-only `go test`
result reporting `[no test files]` does not establish behavioral coverage.

For a TypeScript MCP workspace, run these commands from the rendered root after
installing its dependencies with the declared pnpm version:

```bash
pnpm --filter ./node/mcp --fail-if-no-match run typecheck
pnpm --filter ./node/mcp --fail-if-no-match run build
pnpm --filter ./node/mcp --fail-if-no-match run test
pnpm --filter ./node/mcp --fail-if-no-match run lint
pnpm audit
```

The MCP package currently requires at least 22.19 on Node 22. A workspace with release
automation also has to satisfy semantic-release's declared Node range. Check the
generated `engines` field rather than treating all Node 22 patch versions as
equivalent.

The Fastify workspace's test tooling requires at least 22.12 on Node 22. Its health
tests run inside the process; also run the workspace's `typecheck` and `build`
scripts, since a passing Vitest run does not check the production type build.
Verify the built package entry with Node after `pnpm --filter api-node --prod deploy <output>` for both plain and shared-logic builds.

When the Python API selects GraphQL or WebSocket support, the sample renderer
runs the corresponding `tests/graphql/` or `tests/websocket/` suite with its
dependency group. Check both GraphQL entry points and an in-memory WebSocket
handshake when changing the routes. The sample renderer also runs generated
quality with the sample's declared profile, including strict branch coverage.

For Python MCP, run `uv run --group mcp python -m <package>.mcp --help` from
`render/python/` and qualify an installed copy outside the source tree. The
generated server lives under the project package and imports the separate MCP SDK.
Choose a Python package name other than `mcp`. The Riso CLI and wizard enforce
this; when using Copier directly, choose a project name that produces a different
package name.

In an enabled Go module, run `go work edit -json`, `gofmt -l .`, `go build ./...`,
`go test ./...`, and `go vet ./...`. Formatter output must be empty. The Go MCP
project is a nested module under `go/mcp/`; check it separately. Keep the
generated workspace enabled during qualification.

In each enabled Rust crate, run the following. Run the MCP crate under
`rust/mcp/` separately. The selected build toolchain and Cargo's `rust-version`
minimum serve different purposes; testing a newer compiler does not prove that
minimum.

```bash
cargo fmt --all -- --check
cargo check --all-targets
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
```

For Fumadocs, use the `docs-fumadocs` workspace's `lint`, `typecheck`, and `build`
scripts and audit its complete workspace dependency graph. Check the full-feature
variant as well as the default, since OpenAPI, math, and diagram features add
different dependency consumers.

Keep partial sample results separate from full-matrix acceptance. Disabled,
unavailable, or unimplemented checks must remain explicit skips; they cannot be
reported as passed runtime qualification.

## Matrix and parity

- Run the quality matrix locally via `uv run python scripts/ci/run_quality_suite.py`
  to mirror CI behavior.
- Ensure dependency groups in `pyproject.toml` resolve on Python 3.11, 3.12, and
  3.13; misaligned deps often surface as coverage drops.
- Keep Node tracks (Fastify, docs-fumadocs) green by running `pnpm --filter` test
  targets when the `api_languages` or docs options are enabled.

## Reporting and triage

- Coverage deltas should be called out in PR descriptions with references to
  `coverage.xml` and failing lines from `--cov-report=term-missing` (or
  `coverage html` when debugging locally).
- Flaky tests must be quarantined with a linked issue; avoid `@pytest.mark.flaky`
  without an owner or remediation plan.
- Integration and e2e suites should log sample payloads and response codes to
  help reproduce failures in CI artifacts.

## Enforcement and dashboards

- Require coverage jobs as mandatory branch protection checks. Maintainer CI
  enforces `--cov-fail-under=70`; rendered packages enforce `--cov-fail-under=90`.
  Keep matrix jobs mandatory so cross-version regressions are visible.
- Publish coverage summaries in PR descriptions or status comments (e.g., via
  `python-summarize-coverage` action or `gh api` uploads) so reviewers can act on
  deltas without downloading artifacts.
- When coverage dips, link to the exact uncovered lines and create follow-up
  issues if remediation exceeds the current PR scope.
