# W2-PY — generated Python test extras + keep list

- Tasks: `PY-T01`, `PY-T02`, `PY-T03`, `PY-T04`, `PY-T05`, `PY-T06`, `PY-T07`, `PY-T08`, `PY-JOIN`
- Wave: W2 / lane PY
- Deps: `W1-OUT`
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (no checkout / stash / reset / commit)
- Exclusive writes: `template/files/python/**`
- Also allowed: this file; `goals/riso-v2-release-ready/evidence/W2-PY-*`; `goals/riso-v2-release-ready/residuals/PY.md` (not written — no residual)
- `samples/*/render/**` writes: **0**
- Status: **green**

## Contract

Generated Python `[dependency-groups] test` includes `hypothesis` and `respx`, with one shipped test each. `httpx` stays in `api_python_test`. ty/ruff/uv remain; mypy is not default. DESIGN / mpl / plotly / `custom.js.jinja` and `BaseCommand.execute()` stay. pytest collects `test_*.py` / `*_test.py` only (no `.jinja`).

| Task | Result |
| --- | --- |
| PY-T01 | `hypothesis>=6.165.5` in `[dependency-groups] test` |
| PY-T02 | `respx>=0.23.1` in same `test` group (one writer with T01); `httpx>=0.25.0` remains in `api_python_test` |
| PY-T03 | `template/files/python/tests/test_hypothesis.py.jinja` ships `@given` tests |
| PY-T04 | `template/files/python/tests/test_respx.py.jinja` ships an HTTP mock |
| PY-T05 | `rg -i mypy template/files/python` empty; quality extra is `ty` |
| PY-T06 | DESIGN tokens / mpl / plotly / `custom.js.jinja` present (kept, not rewritten) |
| PY-T07 | `BaseCommand.execute()` validate-then-run + `test_cli.py.jinja` kept |
| PY-T08 | explicit `python_files = ["test_*.py", "*_test.py"]` — no `.jinja` collection |
| PY-JOIN | 152 jinja OK; `docs-sphinx` + `cli-docs` `ok: true` |

## T01 / T02 — test extra (one writer)

`template/files/python/pyproject.toml.jinja`:

```toml
[dependency-groups]
test = [
  "pytest>=8.4.2",
  "hypothesis>=6.165.5",
  "respx>=0.23.1",
]
```

`api_python_test` unchanged:

```toml
api_python_test = [
  "httpx>=0.25.0",
  "pytest-asyncio>=0.21.0",
]
```

Pins are latest PyPI stables as of 2026-08-13 (`hypothesis` 6.165.5, `respx` 0.23.1). `respx` depends on `httpx>=0.25.0` (same floor as `api_python_test`). No new languages/runtimes/vendors.

## T03 — shipped hypothesis test

`template/files/python/tests/test_hypothesis.py.jinja` always ships (not gated on API/CLI). `pytest.importorskip("hypothesis")` if the test extra is missing.

- `test_run_heartbeat_is_stable` — `@given` over `importlib.import_module(PACKAGE_NAME).run` (`PACKAGE_NAME = "{{ package_name }}"`; skips if unrendered)
- `test_hyphen_join_round_trips_ascii_tokens` — `@given` on a pure helper
- Unrendered file is valid Python (`AST_OK`); idle-gate can parse it without SyntaxError.

## T04 — shipped respx test

`template/files/python/tests/test_respx.py.jinja` always ships. Mocks `https://example.test/health` via `@respx.mock` + `httpx.get` (no network).

Isolated smoke (temp src layout, not `samples/*/render/`):

```text
PYTHONPATH=<tmp>/src uv run --with hypothesis --with 'respx>=0.23.1' --with httpx pytest <tmp>/tests -q -n 0
...                                                                      [100%]
3 passed in 0.22s
```

## T05 — ty/ruff/uv remain; mypy not default

```text
rg -n -i 'mypy' template/files/python
(no mypy matches)
```

Quality extra still `ruff` + `ty` + `pylint`. `tasks/quality.py.jinja` runs `ty check`, not mypy.

## T06 — keep DESIGN / mpl / plotly / custom.js.jinja

| Path | Present |
| --- | --- |
| `docs/_static/css/design-tokens.css` | yes |
| `docs/_static/js/custom.js.jinja` | yes |
| `docs/_static/js/riso-plotly-template.json` | yes |
| `docs/_static/mpl/riso.mplstyle` | yes |
| `docs/conf.py.jinja` `apply_riso_plotly_template` / mplstyle loader | yes |

Not rewritten this wave.

## T07 — keep `BaseCommand.execute()`

`src/{{ package_name }}/cli/core/base.py.jinja` still validates then `run()`. `tests/test_cli.py.jinja` still has `test_base_command_execute_runs_handler` and `test_base_command_execute_requires_handler`. Not rewritten this wave.

## T08 — pytest collection

```toml
[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
```

This is pytest's default pair made explicit (keeps `tests/smoke_test.py`). Mission “`test_*.py` only” means **no `.jinja` widening** (idle-gate hack stays dropped). `test_hypothesis.py.jinja` / `test_respx.py.jinja` do **not** match those globs.

## PY-JOIN

```text
find template/files/python -name '*.jinja' -print0 | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
Validated 152 Jinja template(s): all OK
```

```text
uv run riso validate --answers-file samples/docs-sphinx/copier-answers.yml --json
{"ok": true, ... "valid": true, "errors": []}

uv run riso validate --answers-file samples/cli-docs/copier-answers.yml --json
{"ok": true, ... "valid": true, "errors": []}
```

Warnings only: `_commit` / `_src_path` unknown answer keys (Copier bookkeeping; not removed remaps). Sample answers were not edited (PLATFORM lock).

Logs: `W2-PY-join.txt`, `W2-PY-validate-docs-sphinx.json`, `W2-PY-validate-cli-docs.json`.

## Not this lane

- `copier.yml` / hooks / answers remaps (COORD / CLI)
- `samples/**/copier-answers.yml` (PLATFORM)
- `samples/*/render/**` (never hand-edit)
- `uv.lock` / `pnpm-lock.yaml`
- `riso-mcp` not reintroduced
