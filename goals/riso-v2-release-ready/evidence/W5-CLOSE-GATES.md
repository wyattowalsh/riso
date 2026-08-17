# W5-CLOSE-GATES

Date: 2026-08-14
Branch: `main`
HEAD: `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
Cwd: `/Users/ww/dev/projects/riso`
No commit / tag / push / PyPI. `samples/*/render/**` written only via `./scripts/render-samples.sh`.

## Lock verdict

Exclusive-root P0/P1 are closed in template/scripts. Official dests for `rust-api` / `go-api` no longer emit `needs: []` or an empty publish matrix. `just validate-agents` is green after restoring `samples/default/render` via the official script.

Environmental leftovers (NODE fumadocs smoke, dest `mise.toml` trust, stale non-rerendered dest quality.yml, Circle/GitLab dest-root `uv`) are in `residuals/GATES.md`.

## Live re-verify (before edit)

| Item | Live |
| --- | --- |
| `riso-container-build.yml.jinja` | Already omitted `scan` unless `api_module == enabled` and python/node in `api_languages`. Summary `needs: [hadolint]` otherwise. |
| `riso-container-publish.yml.jinja` | Already omitted `publish-ghcr` under the same guard. |
| Stale dests | `samples/rust-api/render` and `samples/go-api/render` still had `needs: []` / empty `matrix.target` until official re-render. |
| `riso-quality.yml.jinja` | Dest-root `uv sync` + `uv run task quality` (PAY-P1 live). |
| `render-samples.sh` | Bootstrap errors only wrote `.riso/bootstrap-status.json` and continued (MS-P1 live). |
| `validate_jinja_templates.py` | Directory walk already present (`rglob("*.jinja")`). |
| `just quality` | `quality: lint typecheck test ssot` (unchanged). |
| Skill mirrors | 5/5 `.agents` ↔ `.claude` byte-identical (unchanged). |
| `samples/default/render` | Absent before this wave. |

## Changes

| File | Change |
| --- | --- |
| `template/files/.github/workflows/riso-quality.yml.jinja` | `working-directory: python` on `uv sync`; `uv --directory python run task quality` inside nick-fields/retry; artifacts under `python/`. |
| `scripts/render-samples.sh` | `bootstrap_render_dependencies` returns 1 on uv/pnpm error; `render_variant` exits 1. |
| `tests/unit/test_github_workflow_templates.py` | Render rust/go/disabled/python/node; forbid `needs: []` / empty matrix; assert python/ uv. |
| `tests/unit/ci/test_validate_jinja_templates.py` | Official dir-walk argv. |
| `tests/unit/ci/test_render_samples_variant_names.py` | Bootstrap fail-closed source contract. |
| `tests/integration/test_rendered_workflows.py` | actionlint also covers `rust-api` and `go-api`. |

Container jinja was already gated; dests were stale. Re-rendered via official script only.

## Commands

```text
uv run python scripts/ci/validate_jinja_templates.py template/files
# Validated 803 Jinja template(s): all OK  exit 0

uv run python scripts/ci/validate_release_readiness_skill.py
# Release readiness skill mirror is valid.  exit 0

uv run python scripts/ci/check_removed_key_ssot.py
# ok: 3-way key+op parity; zero leftover sample keys  exit 0

uv run pytest tests/unit/test_github_workflow_templates.py \
  tests/unit/ci/test_validate_jinja_templates.py \
  tests/unit/ci/test_render_samples_variant_names.py \
  tests/unit/ci/test_validate_release_readiness_skill.py -q -n 0
# 19 passed

./scripts/render-samples.sh --variant rust-api --answers samples/rust-api/copier-answers.yml
# copy ok; dest workflows omit scan/publish-ghcr
# bootstrap FAIL: mise dest mise.toml untrusted → pnpm  (RUST_EXIT:1)

./scripts/render-samples.sh --variant go-api --answers samples/go-api/copier-answers.yml
# same dest workflow shape; bootstrap FAIL mise trust  (GO_EXIT:1)

./scripts/render-samples.sh --variant default --answers samples/default/copier-answers.yml
# dest restored; AGENTS.md present; fumadocs smoke FAIL sitemap.xml + output:export  (DEFAULT_EXIT:1)

just validate-agents
# template + dest AGENTS + agent-smoke 6/6 × 4  VALIDATE_AGENTS_EXIT:0

actionlint samples/{rust-api,go-api}/render/.github/workflows/riso-container-*.yml
# ACTIONLINT_EXIT:0

uv run pytest tests/integration/test_rendered_workflows.py \
  tests/unit/test_github_workflow_templates.py -q -n 0
# 26 passed
```

## Dest proof (official script only)

`samples/rust-api/render/.github/workflows/riso-container-build.yml`:

- no `scan` job
- `summary.needs: [hadolint]`
- no `needs: []`

`samples/go-api/render/.github/workflows/riso-container-publish.yml`:

- no `publish-ghcr` job
- `summary` has no `needs` (valid)
- no empty `matrix.target`

`samples/default/render/AGENTS.md`: present. Container workflows excluded (`api_module: disabled`).

`samples/api-python/render/.github/workflows/riso-quality.yml`: still dest-root `uv sync` (not re-rendered this wave).

## Not done / not this lock

- Did not make `just validate-agents` or other release gates non-blocking.
- Did not start or kill `render_matrix.py`.
- Did not edit `template/copier.yml`, Circle/GitLab jinja, Fumadocs payloads, or dest files by hand.
- Generated Node floor remains 20. OpenSpec extra stays off by default.
