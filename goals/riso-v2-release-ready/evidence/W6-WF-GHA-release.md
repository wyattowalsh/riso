# W6-WF-GHA-release — dest-root `uv` in `riso-release.yml`

- Wave: W6 / GATES payload workflow
- Task: close `PAY-P1-gha-release-uv-root`
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87`
- Exclusive writes: `template/files/.github/workflows/riso-release.yml.jinja`, this file
- `samples/*/render/**` writes: **0**
- Commits / tags / pushes: **0**
- Status: **source-closed**

## Finding (W6-R03)

`template/files/.github/workflows/riso-release.yml.jinja` quality job always ran dest-root `uv sync` / `uv run task quality` (was L58–62). Canonical pyproject is `python/pyproject.toml` (`post_gen` `cleanup_legacy_root_pyproject`). Same class as closed `PAY-P1-gha-uv-root`. Official `changelog-python` ships this workflow.

Same dest-root `uv` also lived in the `release` job (was L99–100 `uv sync`; L124–125 `uv run python`), already gated on API Python.

## Change

Match `riso-quality.yml.jinja` / `riso-matrix.yml.jinja`:

1. Gate quality-job Python setup + `uv` on the same Python-track condition as matrix (`cli`/`api`/`mcp` python **or** sphinx).
1. Install: `working-directory: python` + `uv sync`.
1. Quality: `uv --directory python run task quality`.
1. Non-Python changelog dests: keep `jobs.quality` (release `needs: [quality]`) with a no-op echo. No dest-root `uv`.
1. Release-job Python install / version verify: same `working-directory` / `uv --directory python`. Publish gate stays `api_module` + python (not broadened).

## Live (source)

| Path                         | After                                                                                                  |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| Quality job, Python track    | L46 gate; L60–61 `working-directory: python` / `uv sync`; L64 `uv --directory python run task quality` |
| Quality job, no Python track | L66–67 echo only; no `uv sync` / `setup-python`                                                        |
| Release job, API Python      | L105–107 `working-directory: python` / `uv sync`; L131–132 `uv --directory python run python`          |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/.github/workflows/riso-release.yml.jinja
# Validated 1 Jinja template(s): all OK
# throwaway jinja render (not dest): python-track → 2× working-directory: python,
#   3× uv --directory python; both uv sync steps have working-directory: python
# no-python (fumadocs) → quality steps checkout + echo; uv sync absent
git status --short -- 'samples/*/render/**'   # empty
```

## Residuals (not this lock)

| Residual                                                                            | Disposition                                    |
| ----------------------------------------------------------------------------------- | ---------------------------------------------- |
| Official `samples/changelog-*/render/.github/workflows/riso-release.yml` dest-stale | PLATFORM re-render only; do not hand-edit dest |
| Release-job Python still API-only (CLI/MCP/sphinx without API)                      | pre-existing publish gate; not dest-root `uv`  |
| Workflow still emits on `changelog_module` even if `ci_platform != github-actions`  | pre-existing; out of this P1                   |

## Path lock

| Class                                   | Count                                                         |
| --------------------------------------- | ------------------------------------------------------------- |
| Product write                           | 1 — `template/files/.github/workflows/riso-release.yml.jinja` |
| Evidence                                | this file                                                     |
| `samples/*/render/**`                   | 0                                                             |
| Lockfile / secret / commit / tag / push | 0                                                             |

## Verdict

```yaml
id: PAY-P1-gha-release-uv-root
status: source-closed
files:
  - template/files/.github/workflows/riso-release.yml.jinja
summary: >
  Changelog release quality no longer dest-root uv. Python track uses
  working-directory: python and uv --directory python; non-python dests
  keep a no-op quality job. Release-job uv follows the same cwd.
```
