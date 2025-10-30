# Quality Automation Overview

- Unified command: `make quality` (or `uv run task quality` if `make` is unavailable)
- Tools: Ruff, Mypy, Pylint, pytest (via coverage), optional ESLint/TypeScript when `api_tracks` enables Node.
- Profiles: `quality_profile=standard` by default, `strict` enables Mypy strict mode and extended Ruff linting.
- Evidence: `.riso/quality-durations.json` plus CI workflow `.github/workflows/quality-matrix.yml` upload artifacts (90-day retention).
- Governance: `scripts/ci/run_quality_suite.py`, `scripts/ci/check_quality_parity.py`, and updated `render_matrix.json` capture quality state.
