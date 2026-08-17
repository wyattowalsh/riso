# W5-AUDIT — payloads-py

- Lane: `payloads-py`
- Mode: **read-only** (this file only; no product edits)
- Date: 2026-08-14
- Repo: `/Users/ww/dev/projects/riso` (workspace = maintainer root)
- Branch: stay on current (`.git/HEAD` hook-denied this session)
- `samples/*/render/**` writes: **0**
- `uv.lock` / `pnpm-lock.yaml` / commit / tag / push: **none**

## Contract (re-read, not ASSURANCE)

From `goal.md` / `facts.md` / `plan.md` PY-T01–T05:

- Generated Python `[dependency-groups] test` includes `hypothesis` and `respx` with one shipped test each.
- ty/ruff/uv remain; **mypy is not default**.
- Sphinx generated Makefile/just must expose `linkcheck` **if smoke runs it**.
- PAY-P0-06: generated quality workflow pytest path must resolve to `python/tests/test_mcp.py`, not repo-root `tests/test_mcp.py`.

P0/P1 = still-open implementation gaps. `stale` = residual docs already fixed in tree. `closed` = verified-good (recorded as strengths unless needed in the table).

## Live inspection

| Check | Live result |
| --- | --- |
| `template/files/python/pyproject.toml.jinja` `test` extra | `hypothesis>=6.165.5`, `respx>=0.23.1` (L36–39). Quality extra is `ruff` + `ty` + `pylint` (no mypy). `httpx` stays in `api_python_test`. |
| Shipped hypothesis test | `template/files/python/tests/test_hypothesis.py.jinja` — `@given` + `importorskip("hypothesis")`. Also present in `samples/docs-sphinx/render/python/tests/`. |
| Shipped respx test | `template/files/python/tests/test_respx.py.jinja` — `@respx.mock` + `httpx.get("https://example.test/health")`. |
| `rg -i mypy template/files/python` | **empty**. Mentions elsewhere are “ty, not mypy” (`AGENTS.md.jinja`, `DESIGN.md.jinja`, catalog). |
| Smoke Sphinx command | `scripts/render-samples.sh` L169–173: `docs_cwd = python_cwd`, `["uv", "run", "make", "linkcheck"]`. |
| Generated make/just `linkcheck` | **absent**. `python/Makefile.jinja` PHONY/forward list has no `linkcheck`. `python/justfile.jinja` only imports `quality/justfile.quality`. Quality make/just have no `linkcheck` recipe. Default `task_runner=just` **excludes** `python/Makefile` (`copier.yml` L1910). |
| Matrix confirmation | `samples/metadata/render_matrix.json`: `changelog-python` + `docs-sphinx` docs smoke `returncode=2`, stderr `make: *** No rule to make target 'linkcheck'. Stop.` |
| PAY-P0-06 GHA | `template/files/.github/workflows/riso-quality.yml.jinja` L77–82: `working-directory: python` then `uv run pytest tests/test_mcp.py -v` → dest path **`python/tests/test_mcp.py`**. |
| Shipped MCP test | `template/files/python/tests/test_mcp.py.jinja` exists (gated on `mcp_module` + python). |
| Circle / GitLab leftover | `cd python` then `uv run pytest tests/test_mcp.py` (same dest path). |

## Findings

| id | severity | file | issue | fix |
| --- | --- | --- | --- | --- |
| PAY-P0-linkcheck | **P0** | `template/files/python/Makefile.jinja` (+ `justfile.jinja`, `quality/{makefile,justfile}.quality.jinja`) | Official smoke runs `uv run make linkcheck` from `python/`. Generated make/just do not define `linkcheck`. Default just-only renders have **no** Makefile. Matrix docs smoke is red on `docs-sphinx` and `changelog-python`. | Add a `linkcheck` recipe on the generated runner smoke actually invokes: `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck` (cwd = python package). Forward it from `python/Makefile.jinja` **and** `quality/justfile.quality.jinja` / `python/justfile.jinja`. If `task_runner=just` keeps excluding Makefile, either still ship a Makefile when `docs_framework=sphinx-shibuya` **or** hand off a smoke-command change to gates (`just linkcheck` / bare `sphinx-build`). Do not hand-edit `samples/*/render/**`. |
| PAY-P0-06 | **stale** | `template/files/.github/workflows/riso-quality.yml.jinja` | `residuals/GOAL.md` / `ASSURANCE.md` still claim GHA runs repo-root `uv run pytest tests/test_mcp.py`. Live job uses `working-directory: python` + `tests/test_mcp.py` (and `test_mcp.py.jinja` now ships). | No payload edit. GOAL residual/ASSURANCE should drop “PAY-P0-06 still live”. |
| PAY-P1-gha-uv-root | **P1** | `template/files/.github/workflows/riso-quality.yml.jinja` | `uv sync` (L53–56) and `uv run task quality` (L65–67) still run at dest root. Canonical `pyproject.toml` is `python/pyproject.toml` (post_gen deletes leftover root pyproject). Test steps already `working-directory: python`. | Set `working-directory: python` on install + quality steps (same as CLI/MCP tests), or `uv --directory python sync` / `uv --directory python run task quality`. |
| PAY-P1-ruff-conf-release | **P1** | `template/files/python/docs/conf.py.jinja`, `template/files/python/release/models.py.jinja` | `just quality` (`quality/justfile.quality.jinja` `ruff check` with no paths) fails generated smoke: `docs/conf.py` E402 (`import yaml` after `warnings.filterwarnings`, L12–19); `release/models.py` UP042 `class CommitType(str, Enum)` (L16) + SIM102 nested `if` in `validate_scope`. Confirmed in `changelog-python` `quality_just` smoke. | Move third-party imports above statements (or per-file-ignore `docs/conf.py` E402). Use `enum.StrEnum` and collapse the nested `if`. Keep `httpx` in `api_python_test` only. |
| PAY-P1-pylint-cli-placeholder | **P1** | `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja` | Disabled-CLI placeholder docstring L3 is 105 cols. `docs-sphinx` (`cli_module=disabled`) `quality_uv_task` smoke: pylint C0301 on `cli/__main__.py:3`. | Wrap the “Re-render the template…” line to ≤100 cols. |

## Strengths (verified-good)

- PY-T01/T02: `test` extra has `hypothesis` + `respx`; `httpx` remains in `api_python_test`.
- PY-T03/T04: one shipped `@given` test and one `@respx.mock` HTTP test; both render in `samples/docs-sphinx/render/python/tests/`.
- PY-T05: no mypy default under `template/files/python/**`; typecheck is `ty`.
- PAY-P0-06 dest path is correct in live GHA (`python/` + `tests/test_mcp.py`); `test_mcp.py.jinja` is present.
- Circle/GitLab now `cd python` before the same pytest path (old leftover class is not live).
- `BaseCommand.execute()` validate-then-run still present; DESIGN / mpl / plotly / `custom.js.jinja` kept.

## Not this lane

- Changing `scripts/render-samples.sh` smoke argv (gates).
- Hand-editing `samples/*/render/**`.
- Residual ledger edits (`residuals/GOAL.md`, `ASSURANCE.md`).

## Verdict

One **P0** remains: Sphinx smoke `make linkcheck` has no generated target (and default just-only trees have no Makefile). PAY-P0-06 is **stale**. Hypothesis/respx extras + tests and no-mypy default are **green**.
