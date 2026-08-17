# W4-A01 — accepted-fact map

> **Stale-doc (2026-08-14 W5-CLOSE).** Do not use this table as live closeout.
> Live map: [`W5-CLOSE-fact-map.md`](./W5-CLOSE-fact-map.md) (24 green / 1 residual).
> Historical command logs below remain useful only as W4 artifacts.

- Task: `W4-A01`
- Wave: W4
- Lane: GOAL
- Date (UTC): 2026-08-14
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive writes: `goals/riso-v2-release-ready/**` only
- `samples/*/render/**` writes this task: **0**
- Report: `goals/riso-v2-release-ready/ASSURANCE.md`
- Source facts: `facts.md` / `facts.meta.json` (25 accepted)

**facts_covered = 21** · **facts_residual = 4** · **sum = 25**

Live command bundle: `W4-A01-quality.txt`, `W4-A01-validate.txt`, `W4-A01-ladder.txt`, `W4-A01-pytest-agents.txt`.

Remap contract (not re-implemented here): apply then reject; no dest overwrite; idempotent; no dual-path.

| # | id | Verdict | Owner if residual | Command / proof | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `fact-goal-kind` | green | — | `git tag -l 'v2.0.0' '2.0.0'` empty; no commit/push/PyPI this session | this file; ASSURANCE | Evidence-ready closeout only |
| 2 | `fact-hard-major` | green | — | W0 keep/drop + W2 lane joins; no new language/runtime/vendor added | `W0-keep-drop.md`, W2-*-join | Existing tracks only |
| 3 | `fact-runtime-floors` | green | — | generated `mise.toml.jinja` `python = "3.11"` `node = "20"` | `W2-MISE-join.md` | Maintainer Node 22 not raised onto generated floor |
| 4 | `fact-tooling-canon` | green | — | PY extras + WEB store `task_runner=just`; Makefile via `task_runner` | `W2-PY.md`, `W2-WEB-join.md`, `W1-C01-extras.md` | pydantic/loguru/typer; Playwright/Vitest where already present |
| 5 | `fact-mise` | green | — | always-on generated `mise.toml.jinja`; maintainer `.mise.toml` unchanged | `W2-MISE-join.md`, `coord-outbox/mise-always.md` | Dual `mise.toml` / `.mise.toml.jinja` noted, not blocking |
| 6 | `fact-openspec` | green | — | `openspec_extra` default `disabled`; exclude unless enabled | `W1-C01-extras.md`, `W2-OPENSPEC.md` | Related COORD residuals do not flip the default-off fact |
| 7 | `fact-hypothesis-respx` | green | — | extras + shipped tests | `W2-PY.md` | `test_hypothesis.py.jinja`, `test_respx.py.jinja` |
| 8 | `fact-super-migrate` | green | — | `uv run pytest tests/unit/test_cli/test_migrate.py tests/unit/test_cli/test_remap.py tests/unit/test_cli/test_update.py -q -n 0` → **98 passed** | `W4-A01-ladder.txt`, `W2-CLI-tasks.md` | JOIN integration tests residualed separately (`residuals/CLI.md`) |
| 9 | `fact-no-legacy-answers` | green | — | `check_removed_key_ssot.py` leftover scan + 37/37 validate + leftover `rg` empty | `W4-A01-ladder.txt`, `W4-A01-validate.txt` | Rendered `.copier-answers.yml` also clean |
| 10 | `fact-surfaces-lockstep` | green | — | 3-way SSOT + migrate + WEB twin + v2 docs | `W3-PL-T10-ssot.txt`, `W2-WEB-join.md`, `W4-D01.md`, `W4-D04.md` | Payload GHA path leftovers are refine items, not key-SSOT drift |
| 11 | `fact-dirty-tree` | green | — | keep/drop vs `plan.md`; flatten absent at `node/saas` root | `W0-keep-drop.md`, `W2-SAAS-summary.md` | runtime/{nextjs,remix} present |
| 12 | `fact-wave-order` | green | — | evidence prefixes W0 / W1 / W2 / W3 / W4 | `plan.md`, `plan.taskgraph.json`, `evidence/` | A01 is last W4 join |
| 13 | `fact-write-locks` | green | — | this session GOAL-only; `git status --short -- 'samples/*/render'` empty | ASSURANCE path-lock | Official `render_matrix` may write dest trees; never hand-edit |
| 14 | `fact-correctness-first` | green | — | electron-store `externalizeDepsPlugin({exclude})`; ESLint 9; no clang/lld | `W2-DESKTOP-join.md` | 58 pytest (electron + new-template) |
| 15 | `fact-refine-stop` | **residual** | GOAL | two consecutive no-new-P0/P1 reviews **and** ladder green | `residuals/GOAL.md` R1; `W4-R03-gates.md` | On-disk R01/R02 absent; PAY-P0-06 still live; quality/jinja/agents red |
| 16 | `fact-just-quality` | **residual** | PLATFORM (format) + GOAL (integration tests) | `just quality` | `W4-A01-quality.txt`, `W4-A01-pytest-agents.txt`, `residuals/PLATFORM.md` R1 | lint format fail (5 files); ty 0; pytest 2 failed / 1064 passed |
| 17 | `fact-sample-validate` | green | — | 37 × `uv run riso validate --answers-file … --json` | `W4-A01-validate.txt`; W3-S0…S5 jsonl | TOTAL=37 OK=37 FAIL=0 |
| 18 | `fact-jinja` | **residual** | PLATFORM | official `uv run python scripts/ci/validate_jinja_templates.py template/files` | `W4-A01-ladder.txt`, `W3-PL-T04-jinja.txt`, `residuals/PLATFORM.md` R3 | Official argv exit 1 (`Not a file`); `find\|xargs` 799 OK |
| 19 | `fact-context-agents` | **residual** | PLATFORM | `verify_context_sync.py` (0) + `just validate-agents` (1) | `W4-A01-ladder.txt`, `W4-A01-pytest-agents.txt`, `residuals/PLATFORM.md` R4 | default render dest missing after failed matrix variant |
| 20 | `fact-render-matrix` | green | — | `uv run python scripts/ci/render_matrix.py` wrote JSON | `samples/metadata/render_matrix.json`; `W3-PL-T06.log` | 37 variants; 3 ok / 34 failed smoke; **must not residual** |
| 21 | `fact-docs-w` | green | — | `uv run --group docs sphinx-build -W -b html docs docs/_build/html` | `W4-A01-ladder.txt`, `W4-PL-T08-sphinx.txt` | exit 0; `guides/v2-migration.html` present |
| 22 | `fact-release-validators` | green | — | skill + workflows + release-configs | `W4-A01-ladder.txt` (all exit 0) | W3 PL-T07 log stale (mirror + missing dest) |
| 23 | `fact-migration-docs` | green | — | page + CHANGELOG Unreleased 2.0.0 + no tag | `W4-D01.md`, `W4-D03.md`, `W4-D04.md` | 8 remaps named; `git tag` empty |
| 24 | `fact-no-riso-mcp` | green | — | `rg -n riso-mcp src/riso template` | `W4-A01-ladder.txt` | `src/riso` empty; 2 template prohibition hits → JSON `riso_mcp_clean=false` |
| 25 | `fact-evidence` | green | — | this map + `ASSURANCE.md` | `goals/riso-v2-release-ready/ASSURANCE.md` | Residuals carry owner / command / redacted log |

## Residual fact detail

### `fact-just-quality`

```text
just quality
# ruff check: All checks passed
# ruff format --check: Would reformat 5 files; recipe lint failed exit 1
# ty / pytest / ssot not reached

uv run pytest tests -q --tb=no -n auto
# 2 failed, 1064 passed, 5 skipped
# FAILED tests/integration/test_riso_cli.py::test_validate_rejects_removed_key
# FAILED tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker
```

### `fact-jinja`

```text
uv run python scripts/ci/validate_jinja_templates.py template/files
# Jinja template validation failed (1 error(s)):
#   template/files: Not a file
# jinja_official_exit:1

find template/files -type f -name '*.jinja' -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 799 Jinja template(s): all OK
```

### `fact-context-agents`

```text
uv run python scripts/ci/verify_context_sync.py   # exit 0
just validate-agents
# agents-ecosystem: all checks passed
# Quality parity checks passed.
# agents-ecosystem: render missing AGENTS.md: samples/default/render
# exit 1
# samples/default/render does not exist (matrix default render_status=failed)
```

### `fact-refine-stop`

Required: two consecutive review passes with **no new P0/P1** on payloads / CLI / wizard / docs / gates, **and** the official ladder green.

- On disk: `W4-R03-gates.md` only (gates: no new P0/P1 vs pass 1).
- Missing: `evidence/W4-R01*`, `evidence/W4-R02*`.
- Live template still has PAY-P0-06 (`uv run pytest tests/test_mcp.py` in `riso-quality.yml.jinja`).
- Official ladder not fully green (quality, official jinja argv, validate-agents).

## Counts

| class | n |
| --- | ---: |
| green | 21 |
| residual | 4 |
| blocked (`render_matrix` missing) | 0 |
| total accepted facts | 25 |
