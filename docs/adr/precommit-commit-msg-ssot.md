# ADR: Pre-commit and Commit-msg Single Source of Truth

**Status:** Accepted\
**Date:** 2026-06-24\
**Decision gate:** DG-1 Option A

## Context

Rendered Riso projects had fragmented hook installation:

- `.pre-commit-config.yaml` lived under `quality/`, so `pre-commit install` without `--config` did not discover it.
- `make hooks` existed only in `quality/makefile.quality`, not at the project root.
- `commit-msg` was installed for `strict` in Makefiles but for `changelog_module OR strict` in the Jinja template defaults.
- Three commit-msg paths coexisted: pre-commit `commitlint`, `install-hooks.py`, and `scripts/hooks/commit-msg.sh`.
- Maintainer repo duplicated commit-msg validation (`commitlint` + `conventional-pre-commit`).

## Decision

1. **Config location:** Ship `.pre-commit-config.yaml` at the **rendered project root**. Keep other quality artifacts in `quality/`.
1. **Install SSOT:** `make hooks` from the root `Makefile`, which delegates to `quality/makefile.quality`.
1. **Commit-msg SSOT:** One `commitlint` local hook in `.pre-commit-config.yaml` (`stages: [commit-msg]`). Remove `conventional-pre-commit` from maintainer and template configs.
1. **Hook-type install rule:** Install `commit-msg` when `changelog_module == 'enabled' OR quality_profile == 'strict'`; install `pre-push` only for `strict`.
1. **Legacy installer:** `scripts/release/install-hooks.py` is deprecated (prints warning, exit 0). `pnpm run setup-hooks` and `package.json` call `make hooks`.
1. **Fallback script:** `scripts/hooks/commit-msg.sh` tries `pnpm exec commitlint`, then `npx commitlint`, then a conventional-commit pattern check.

## Consequences

### Positive

- `pre-commit install` works without `--config` in rendered projects.
- Post-gen metadata records `"install_command": "make hooks"` consistently.
- Maintainer and template hook pins stay aligned via shared patterns and `scripts/ci/hooks_catalog.yaml`.

### Negative / follow-ups

- Rendered `AGENTS.md` and upgrade docs must reference `make hooks`, not raw `pre-commit install` or `install-hooks.py`.
- `scripts/ci/render_precommit_configs.py` gates sample renders for layout regression.

## Verification

```bash
uv run pre-commit validate-config
uv run python scripts/ci/render_precommit_configs.py --all
uv run pytest tests/test_precommit.py tests/integration/test_rendered_precommit.py -q
```
