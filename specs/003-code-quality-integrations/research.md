# Research Log: Code Quality Integration Suite

## Auto-Healing Python Quality Tooling

### Decision: Attempt a single `uv` install for missing Ruff/Mypy/Pylint binaries before aborting
- **Rationale**: Keeps renders deterministic while unblocking first-time users; `uv` already manages Python interpreters and pinning, so leveraging it prevents manual setup stalls.
- **Alternatives Considered**:
  - Immediate failure: preserves strictness but increases friction for clean environments and CI warm starts.
  - Silent skip: would let lint/type drift go unnoticed and violate governance.

## Auto-Healing Node Quality Tooling

### Decision: Use `corepack pnpm install` once when Node API tracks are enabled and pnpm is missing
- **Rationale**: Mirrors the Python experience, keeps optional Node quality checks useful out of the box, and respects pnpm’s recommended installation path via corepack.
- **Alternatives Considered**:
  - Manual install requirement: simpler implementation but burdens downstream teams and CI with extra provisioning steps.
  - Bundling pnpm in repo: increases maintenance cost and risks stale binaries.

## CI Parallelization Strategy

### Decision: Split quality workflows into per-tool jobs with shared caches and aggregate status
- **Rationale**: Parallel lanes keep strict profiles within the 6-minute CI budget while surfacing failures per tool; caching avoids duplicate installs across jobs.
- **Alternatives Considered**:
  - Single monolithic job: simpler YAML but prone to breaching CI timeouts when strict profiles are enabled.
  - Nightly strict runs only: reduces PR latency but delays detection of regressions until after merge.

## Quality Profile Defaults

### Decision: Ship `quality_profile=standard` as the default baseline with `strict` as opt-in
- **Rationale**: Standard mode meets success criteria and keeps quickstarts fast; teams can opt into strict once comfortable with noise and runtime.
- **Alternatives Considered**:
  - Strict-by-default: maximizes coverage but risks noisy onboarding and longer runtimes.
  - Variant-dependent defaults: adds branching complexity and reduces predictability of generated advice.

## Evidence Retention Policy

### Decision: Retain quality artifacts (logs, coverage, JUnit) for 90 days in CI storage
- **Rationale**: Aligns with quarterly governance reviews and provides enough history for regressions without overwhelming storage.
- **Alternatives Considered**:
  - 30-day retention: insufficient for quarterly audits and long investigations.
  - Rolling overwrite on next success: minimizes storage but eliminates historical evidence needed for compliance.
