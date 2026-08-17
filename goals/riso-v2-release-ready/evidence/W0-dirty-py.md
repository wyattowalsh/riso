# W0-T01a — Dirty-tree map, lane PY

- Task: `W0-T01a`
- Wave: W0 / group W0A
- Lane: PY
- Exclusive write root: `template/files/python/**`
- Verify: every dirty `template/files/python/**` path owned; keep-or-drop vs `plan.md`; `samples/*/render/` write count = 0
- Status: **green**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (workspace root; `.git` present) |
| Branch | `main` (launch porcelain: `git rev-parse --abbrev-ref HEAD` → `main`; `main...origin/main [ahead 34, behind 1]`) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| Filter | keep only `template/files/python/**` |

Commands required by the mission: `git status --short` and `git diff --name-only`.

This worker has no shell (`run_terminal_command` not in the tool list). Porcelain is **not invented**: it is the live `git status --short` / `git diff --name-only` / `git ls-files --others --exclude-standard` capture from parent session `019ffa08-aa06-7ee2-ade5-356d0569fc81` (`terminal/call-26af77c5-f17a-446f-adc1-4733deddad6b-232.log`), cross-checked against:

- launch snapshot `019ff9d6` `call-2b37110c-…-83.log` (`main`, ahead 34 / behind 1)
- parent `call-2da8d941-…-63.log` (`git status --short \| head -200` — same PY `M`/`D` prefix)
- later `call-6935198d-…-126.log` (DESIGN/mpl/plotly exist; SaaS `runtime/{nextjs,remix}` restored)
- current worktree `list_dir` / `read_file` / `grep` (this task)

No git mutation. Branch not changed.

## Matching dirty paths (PY filter)

`git status --short` ∩ `template/files/python/**`.

### Tracked modified (`M`) — 51 (captured porcelain) + 1 post-capture

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `template/files/python/coverage.cfg.jinja` | **KEEP** — CLI/coverage gates; not flatten |
| `M` | `template/files/python/docs/_static/css/components.css` | **KEEP** — DESIGN tokens polish (PY-T06) |
| `M` | `template/files/python/docs/_static/css/custom.css` | **KEEP** — DESIGN tokens polish (PY-T06) |
| `M` | `template/files/python/docs/_static/css/design-tokens.css` | **KEEP** — DESIGN tokens polish (PY-T06) |
| `M` | `template/files/python/docs/_static/css/lucide-icons.css` | **KEEP** — DESIGN tokens polish (PY-T06) |
| `M` | `template/files/python/docs/conf.py.jinja` | **KEEP** — Sphinx + mpl/plotly wiring (PY-T06) |
| `M` | `template/files/python/pyproject.toml.jinja` | **KEEP** current polish (ty in `quality`; `httpx` stays in `api_python_test`). **W2 will add** `hypothesis` + `respx` to `test` (PY-T01/T02). No `python_files` widening here. |
| `M` | `template/files/python/src/{{ package_name }}/cli/__init__.py.jinja` | **KEEP** — CLI feature-gate (`cli_module` + `python` in `cli_languages`) |
| `M` | `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/__init__.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/example_async.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/init.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/list.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/plugin.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/quickstart.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/version.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/__init__.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja` | **KEEP** — `BaseCommand.execute()` validate-then-run (plan keep / PY-T07) |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/exceptions.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/formatter.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/prompts.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/plugins/README.md.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/cli/plugins/example_plugin.py.jinja` | **KEEP** — same CLI gate |
| `M` | `template/files/python/src/{{ package_name }}/codegen/EXAMPLES.md.jinja` | **KEEP** — mypy → ty wording (PY-T05) |
| `M` | `template/files/python/src/{{ package_name }}/codegen/README.md.jinja` | **KEEP** — mypy → ty wording (PY-T05) |
| `M` | `template/files/python/src/{{ package_name }}/config.py.jinja` | **KEEP** — notebook extra / settings cleanup |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/__init__.py.jinja` | **KEEP** — dual-gate empty stub when GraphQL off |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/mutations/__init__.py.jinja` | **KEEP** — dual-gate |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/queries/__init__.py.jinja` | **KEEP** — dual-gate |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/subscriptions/__init__.py.jinja` | **KEEP** — dual-gate |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/types/__init__.py.jinja` | **KEEP** — dual-gate |
| `M` | `template/files/python/src/{{ package_name }}/quickstart.py.jinja` | **KEEP** — Jinja-gated quickstart |
| `M` | `template/files/python/tests/codegen/fixtures/sample_templates/python-microservice/template.yml` | **KEEP** — mypy → ty in fixture |
| `M` | `template/files/python/tests/conftest.py.jinja` | **KEEP** — CLI tests gated on python CLI |
| `M` | `template/files/python/tests/graphql/__init__.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_auth.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_complexity.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_dataloaders.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_errors.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_mutations.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_playground.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_queries.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/graphql/test_subscriptions.py.jinja` | **KEEP** — dual-gate tests |
| `M` | `template/files/python/tests/test_cli_commands.py.jinja` | **KEEP** — CLI test gate |
| `M` | `template/files/python/tests/test_cli_config.py.jinja` | **KEEP** — CLI test gate |
| `M` | `template/files/python/tests/test_cli_formatters.py.jinja` | **KEEP** — CLI test gate |
| `M` | `template/files/python/tests/test_cli_plugins.py.jinja` | **KEEP** — CLI test gate |
| `M` | `template/files/python/tests/test_quickstart.py.jinja` | **KEEP** — Jinja-gated quickstart tests |
| `M` | `template/files/python/tests/test_cli.py.jinja` | **KEEP** — `BaseCommand.execute()` tests (PY-T07). Not in the 019ffa08 porcelain; present in worktree after that capture. Treat as dirty keep. |

### Tracked deleted (`D`) — 4 (renames to `.jinja`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `D` | `template/files/python/docs/guides/quickstart.md` | **KEEP the rename** — replaced by `quickstart.md.jinja` (Copier must render) |
| `D` | `template/files/python/docs/guides/testing-strategy.md` | **KEEP the rename** — replaced by `testing-strategy.md.jinja` |
| `D` | `template/files/python/docs/index.md` | **KEEP the rename** — replaced by `index.md.jinja` |
| `D` | `template/files/python/docs/tools/index.md` | **KEEP the rename** — replaced by `tools/index.md.jinja` |

Worktree confirm: those four `.md` paths are **absent**; the `.jinja` replacements exist.

### Untracked (`??`) — captured + post-capture

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `??` | `template/files/python/docs/_static/js/riso-plotly-template.json` | **KEEP** — plan keep / PY-T06 |
| `??` | `template/files/python/docs/_static/mpl/` → leaf `riso.mplstyle` | **KEEP** — plan keep / PY-T06 |
| `??` | `template/files/python/docs/guides/quickstart.md.jinja` | **KEEP** — pair of `D` quickstart.md |
| `??` | `template/files/python/docs/guides/testing-strategy.md.jinja` | **KEEP** — pair of `D` testing-strategy.md |
| `??` | `template/files/python/docs/index.md.jinja` | **KEEP** — pair of `D` index.md |
| `??` | `template/files/python/docs/tools/index.md.jinja` | **KEEP** — pair of `D` tools/index.md |
| `??` | `template/files/python/docs/_static/js/custom.js.jinja` | **KEEP** — plan keep `custom.js.jinja`. Not in 019ffa08 porcelain (DESIGN residual still saw `custom.js`); worktree now has only the `.jinja` file. |

`git status --short` directory form for mpl is `?? template/files/python/docs/_static/mpl/`. `git ls-files --others` leaf: `template/files/python/docs/_static/mpl/riso.mplstyle`.

### `git diff --name-only` ∩ PY

Tracked `M` + `D` only (untracked omitted). Same 55 tracked paths as the `M`/`D` tables (51 captured `M` + 4 `D`; plus `tests/test_cli.py.jinja` if still modified vs index).

## Counts

| Class | Count |
| --- | ---: |
| Captured `M` | 51 |
| Post-capture `M` (`test_cli.py.jinja`) | 1 |
| `D` | 4 |
| Captured `??` leaves | 6 |
| Post-capture `??` (`custom.js.jinja`) | 1 |
| **PY dirty owned** | **63** |
| Unowned PY dirty | **0** |
| `samples/*/render/` in this filter | **0** |

## plan.md keep / drop (PY)

`plan.md` “What stays from the dirty tree” + W2 PY tasks:

| Item | Decision | Why |
| --- | --- | --- |
| DESIGN tokens / mpl / plotly / `custom.js.jinja` | **KEEP** | explicit keep list; PY-T06 |
| `BaseCommand.execute()` validate+run | **KEEP** | explicit keep list; PY-T07; `base.py.jinja` + `test_cli.py.jinja` |
| pytest `python_files` = `test_*.py` only | **KEEP** | do **not** teach pytest to collect `.jinja`; generated `pyproject.toml.jinja` has `testpaths = ["tests"]` only — no `.jinja` collection hack |
| `hypothesis` + `respx` in `[dependency-groups] test` | **not in dirty tree yet** | current `test = ["pytest>=8.4.2"]` only; W2 PY-T01/T02 add them; `httpx` already in `api_python_test` |
| ty/ruff/uv remain; mypy not default | **KEEP** | PY-T05; codegen docs already moving mypy → ty |
| Idle-gate pytest collection hack (root `conftest` / widen `python_files` to `.jinja`) | **DROP** | plan “what stays dropped”; not a `template/files/python/**` path |
| SaaS Next/Remix flatten | **N/A to PY** | stays dropped; SAAS lane |
| Hand-edit `samples/*/render/**` | **DROP / forbid** | hard forbid |

## `samples/*/render/` write count

**0**

- Filter is `template/files/python/**` only — no `samples/**` path matches.
- Current `samples/*/` listings have `copier-answers.yml` (and some metadata) only; **no** `render/` directories present.
- This task wrote only this evidence file.

## SAAS runtime confirm (mission extra)

Not PY write roots. Confirmed present for W0-T01c / W2 SAAS-T01/T02:

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** (`app/`, `lib/`, `middleware.ts.jinja`, `next.config.js.jinja`, …) |
| `template/files/node/saas/runtime/remix` | **yes** (`app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `remix.config.js.jinja`) |

## W2 PY follow-through (no W0 rewrite)

- PY-T01/T02 — add `hypothesis` and `respx` to `pyproject.toml.jinja` `test` extra (one writer).
- PY-T03/T04 — ship one hypothesis test + one respx HTTP mock.
- PY-T05 — `rg mypy` only in “not mypy” docs.
- PY-T06–T08 — keep DESIGN/mpl/plotly/`custom.js.jinja`, `BaseCommand.execute()`, pytest `test_*.py` only.

No PY residual. No files outside `goals/riso-v2-release-ready/evidence/W0-dirty-py.md` written.
