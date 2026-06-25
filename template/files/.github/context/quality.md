# Quality Automation Overview

- Unified command: `make quality` (or `uv run task quality` if `make` is unavailable)
- Tools: Ruff, ty, Pylint, pytest (via coverage), optional ESLint/TypeScript when `api_languages` enables Node.
- Profiles: `quality_profile=standard` by default, `strict` enables ty strict checks and extended Ruff linting.
- Evidence: `.riso/quality-durations.json` plus rendered workflow `riso-quality.yml` artifact uploads (90-day retention).
- Governance: `scripts/ci/run_quality_suite.py`, `scripts/ci/check_quality_parity.py`, `scripts/ci/render_precommit_configs.py`, and updated `render_matrix.json` capture quality state.
- Pre-commit (rendered projects): `.pre-commit-config.yaml` at repo root; install via `make hooks` (see `docs/adr/precommit-commit-msg-ssot.md`).
