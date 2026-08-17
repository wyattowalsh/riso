# Residual — Lane PY (W5 CLOSE-PY)

## Summary

CLOSE-PY fixed every confirmed P0/P1 whose file sits in `template/files/python/**` (linkcheck recipes, ruff conf/release, pylint ≤100). Official Sphinx dest smoke cannot go green from this lock alone: smoke still runs `uv run make linkcheck` while default `task_runner=just` excludes `python/Makefile`.

`samples/*/render/**` writes this lane: **0**.

## Residuals

### R1 — Sphinx smoke still calls `make linkcheck` on just-only dests

| Field | Value |
| --- | --- |
| **task_id** | PAY-P0-linkcheck-smoke |
| **owner** | PLATFORM (`scripts/render-samples.sh`) + COORD (`template/copier.yml` exclude) |
| **status** | open (environmental; PY recipe is in-tree) |
| **command** | After official re-render: either keep `uv run make linkcheck` and stop excluding `python/Makefile` when `docs_framework=sphinx-shibuya`, or change smoke to `just linkcheck` / `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck` from `python_cwd` |
| **blocking reason** | `copier.yml` L1910: `{% if task_runner in ['just', 'none'] %}python/Makefile{% endif %}`. Default `task_runner=just`. `docs-sphinx` and `changelog-python` omit `task_runner`. Smoke (`render-samples.sh` L169–173) is still `["uv", "run", "make", "linkcheck"]`. PY added `linkcheck` on `python/Makefile.jinja` and `python/justfile.jinja` only. `quality/{justfile,makefile}.quality.jinja` is PLATFORM lock. |
| **redacted log** | Historical matrix: `docs-sphinx` / `changelog-python` docs `returncode=2` `No rule to make target 'linkcheck'`. Throwaway render: `make -n linkcheck` → `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck`. |
| **fix** | COORD: do not exclude `python/Makefile` when Sphinx is on (or PLATFORM: stop invoking `make` on just-only dests). Official re-render via `render-samples.sh` / `render_matrix.py`. Never hand-edit `samples/*/render/**`. Optional: add the same recipe on `quality/justfile.quality.jinja` / `quality/makefile.quality.jinja`. |
| **evidence** | `goals/riso-v2-release-ready/evidence/W5-CLOSE-PY.md` |

## Closed in this lane (not residual)

- PAY-P1-ruff-conf-release (conf E402 / models UP042+SIM102 / unused Optional)
- PAY-P1-pylint-cli-placeholder / MS-P1-pylint-placeholder (disabled-CLI docstring)
- changelog-monorepo `plugin_manager` C0301
- hypothesis + respx extras and shipped tests kept
- `python/tests/test_mcp.py.jinja` kept
