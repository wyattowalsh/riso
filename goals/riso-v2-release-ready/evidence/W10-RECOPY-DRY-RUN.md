# W10-RECOPY-DRY-RUN

- Date (UTC): 2026-08-18T15:06:58Z
- Cwd: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `89882ff`
- Python: `uv run` only
- Product dry-run: still calls `compute_diff` (`src/riso/cli/commands/recopy.py`)
- `samples/*/render/**` writes: **0**
- No commit.

## Change

`tests/integration/test_riso_cli.py::test_recopy_dry_run_json` no longer recopies `samples/default/render` (300s `config.timeout` inside `compute_diff` → `copier.run_copy` of the full dest).

- Tiny tmp dest + `.copier-answers.yml` (`project_name: Demo`, `cli_module: enabled`, `cli_languages: [python]`) — same shape as `tests/unit/test_cli/test_recopy.py`.
- `_run_cli` now has an explicit timeout (default **60s**); recopy dry-run passes `timeout=60`. Hung `uv run` is killed as a process group.
- Remaining full-dest slow tests (`copy` / `diff` / `update`) pass `timeout=300` so the helper default does not clip them.
- `@pytest.mark.slow` dropped on this test (tiny dest).
- Test kept (not skipped/deleted). `compute_diff` not disabled; unit tests still patch it.

`src/riso/cli/commands/recopy.py` and `tests/unit/test_cli/test_recopy.py` match HEAD (sibling skip-preview / `preview_engine: remap` was reverted; dry-run still calls `compute_diff`).

## Verify

| Command                                                                                                                                                                                     |  Exit | Notes                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----: | ------------------------------------------------------------------------------------------- |
| `uv run pytest tests/integration/test_riso_cli.py::test_recopy_dry_run_json tests/unit/test_cli/test_recopy.py tests/unit/test_saas_template_clients.py::TestRecopyIntegrationDest -q -n 0` | **0** | **9 passed** in 6.87s. Live `compute_diff` on tiny dest; dest-lock forbids official render. |
| `uv run pytest tests/unit/test_cli/test_update.py tests/unit/test_saas_template_clients.py -q -n 0`                                                                                         | **0** | **24 passed** in 0.11s                                                                      |
| `ruff check` on exclusive surfaces + dest-lock                                                                                                                                              | **0** | All checks passed                                                                           |

**Not run (forbidden this session):** commit / tag / push / stash / reset; dest hand-edits; `render_matrix.py`.
