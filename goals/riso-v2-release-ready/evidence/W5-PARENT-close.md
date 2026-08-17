# W5 parent close — live gaps implemented before/during closeout workflow

Date: 2026-08-14
Branch: main
No tag / commit / push / PyPI. No `samples/*/render/**` hand-edits.

Live audit (five explore agents) found several residuals stale and several product holes still open. Parent implemented the exclusive-lock product holes below so the `riso-v2-release-ready-closeout` workflow can skip already-fixed items.

## Implemented

| Lock | Change |
| --- | --- |
| COORD `template/copier.yml` | Dropped unrooted `_exclude` `README.md`, `config/`, `hooks/`, `samples/`, `prompts/`. Those gitignore-anywhere patterns were dropping `electron/README.md`, `go/internal/config/**`, `node/saas/config/**`, `scripts/hooks/**`. `"specs/"` was already gone. |
| GATES quality templates | GHA CLI/MCP pytest now `working-directory: python`. Rust MCP `working-directory: rust/mcp`. Circle + GitLab `cd python` for CLI + MCP pytest (old `tests/test_mcp.py` PAY-P0-06 still lived there). |
| GATES container workflows | `riso-container-build.yml.jinja` omits `scan` when no API languages (default sample); summary `needs` is `hadolint` then. `riso-container-publish.yml.jinja` omits `publish-ghcr` + empty matrix when no API languages. |
| PY | Added `template/files/python/tests/test_mcp.py.jinja` (import smoke for top-level `mcp` package). |
| HOOKS tests | `test_removes_empty_openspec_dir` asserts `"openspec" in EMPTY_SCAFFOLD_DIRS` and cleanup removes the empty dest dir. |
| DOCS | Generated upgrade-guide `mcp_language` value-rules now mention already-list keep + drop empties + `node`/`js` alias. |
| DOCS just | `just docs-build` is now `uv run --group docs sphinx-build -W -b html docs docs/_build`. |

## Already green (not re-implemented)

- Apply-then-reject 8-key remap SSOT + CLI migrate/update + hooks + generation_gates
- Integration leftover tests use `saas_auth=firebase`
- Jinja validator walks dirs
- Fumadocs `output: 'export' as const`
- `EMPTY_SCAFFOLD_DIRS` includes `openspec`
- hypothesis + respx extras + shipped tests
- Generated Node 20 / maintainer Node 22
- SaaS nextjs + remix runtimes unflattened
- electron-store ESM exclude
- Sample answers have no leftover removed keys
- `samples/metadata/render_matrix.json` exists (37 variants; 34 smoke-failed on stale dests)

## Left for official scripts / review pair

- Restore `samples/default/render` via `./scripts/render-samples.sh` (never hand-create). Required for `just validate-agents`.
- Re-render other dests so empty `openspec/` shells are removed by post_gen and README/config/hooks files copy.
- Two consecutive dry review passes (W5-R01 / W5-R03) after the ladder.
- Rewrite `ASSURANCE.md` from live commands.

## Commands

```text
uv run pytest tests/unit/hooks/test_post_gen_project.py::TestCleanupEmptyScaffoldDirs -q -n 0
# 3 passed
uv run python scripts/ci/validate_jinja_templates.py <touched jinja>
# 6 OK
uv run ruff format --check <five named files>
# 5 files left unchanged
```
