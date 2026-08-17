# W5 CLOSE-PY — generated Python payload close

- Wave: **CLOSE-PY**
- Lane: **PY**
- Date: 2026-08-14
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive write roots: `template/files/python/**`, this file, `residuals/PY.md`
- `samples/*/render/**` writes: **0**
- No commit / tag / push / PyPI. No `uv.lock` / `pnpm-lock.yaml`. Maintainer `riso-mcp` not reintroduced.
- Status: **residualed** — lock P0/P1 templates are fixed; official Sphinx smoke still needs COORD/PLATFORM (just-only dests have no `python/Makefile`)

## Contract (live, re-read)

- Generated `[dependency-groups] test` keeps `hypothesis>=6.165.5` and `respx>=0.23.1`.
- Shipped tests remain: `python/tests/test_hypothesis.py.jinja` (`@given`) and `python/tests/test_respx.py.jinja` (`@respx.mock`).
- `httpx` stays in `api_python_test` only.
- Quality extra stays `ruff` + `ty` + `pylint`. `rg -i mypy template/files/python` empty.
- `python/tests/test_mcp.py.jinja` still ships under `mcp_module` + python (GHA dest path `python/tests/test_mcp.py` is foreign-tree and already correct).
- Official Sphinx docs smoke (`scripts/render-samples.sh` L169–173) is `uv run make linkcheck` from `python_cwd`.

## Confirmed P0/P1 in this lock

| id | Live before | This session |
| --- | --- | --- |
| PAY-P0-linkcheck / MS-P0-sphinx-linkcheck | `python/Makefile.jinja` and `python/justfile.jinja` had no `linkcheck` | Recipe added, gated on `docs_module=enabled` + `docs_framework=sphinx-shibuya`: `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck` |
| PAY-P1-ruff-conf-release | `docs/conf.py.jinja` imported `yaml` after `warnings.filterwarnings` (E402); `release/models.py.jinja` `(str, Enum)` (UP042) + nested `validate_scope` (SIM102); dest `release/__init__.py` unused `Optional` (F401) | Hoisted `yaml`; `collections.abc.Iterable`; `StrEnum`; collapsed `if`; `str \| None` / dropped unused `Optional`; unused `date`/`Version` imports removed from `changelog.py.jinja` |
| PAY-P1-pylint-cli-placeholder / MS-P1-pylint-placeholder | Disabled-CLI `__main__.py` L3 = 105 cols | Wrapped to ≤100 |
| changelog-monorepo C0301 | `plugin_manager.py` docstring 101/100 with `changelog_monorepo` | Wrapped entry-point line; `plugin.py` info line split |

Foreign (not edited): `PAY-P1-gha-uv-root` (`template/files/.github/workflows/riso-quality.yml.jinja`); `quality/{justfile,makefile}.quality.jinja` linkcheck (PLATFORM); `copier.yml` Makefile exclude (COORD); `scripts/render-samples.sh` smoke argv (PLATFORM).

## Commands

```text
find template/files/python -name '*.jinja' -print0 | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 153 Jinja template(s): all OK

uv run pytest tests/unit/test_task_runner_templates.py -q -n 0 --tb=line
# 11 passed

# Throwaway Jinja render (not samples/*/render):
# ruff check docs/conf.py + release/ --select E,F,I,W,B,C4,UP,SIM --ignore E203,E266,E501
# All checks passed!
# pylint --max-line-length=100 --disable=all --enable=line-too-long on wrapped CLI files
# 10.00/10, no C0301
# make -n linkcheck → uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck
```

## Keep (not rewritten)

- `pyproject.toml.jinja` test extra: hypothesis + respx; `httpx` in `api_python_test`
- `tests/test_hypothesis.py.jinja`, `tests/test_respx.py.jinja`, `tests/test_mcp.py.jinja`
- DESIGN / mpl / plotly / `custom.js.jinja` / `BaseCommand.execute()`
- Generated Node floor untouched (not this lock)

## Residual

`residuals/PY.md` R1 — default `task_runner=just` excludes `python/Makefile` (`copier.yml` L1910). Official smoke still calls `make linkcheck`. After official re-render, makefile-runner dests get the new target; just-only Sphinx dests (`docs-sphinx`, `changelog-python`) still have no Makefile. PY cannot change `copier.yml` or `render-samples.sh`.
