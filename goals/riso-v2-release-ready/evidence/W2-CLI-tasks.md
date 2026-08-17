# W2-CLI — apply-then-reject call sites + migrate

- Lane: **CLI**
- Wave: W2
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset / commit)
- Exclusive writes: `src/riso/**`, `tests/unit/test_cli/**`, this evidence, `residuals/CLI.md`
- `samples/*/render/**` writes: **0**
- Remap SSOT (`src/riso/core/removed_answer_keys.py`) **not re-edited** (W1-OUT closed)

## Contract

`apply_then_reject_removed_keys` is the choke point (`src/riso/core/answers.py`): **apply remaps then reject leftovers**. No dest overwrite. Idempotent second apply. Unmapped values stay on the old key and fail closed with the same leftover error shape.

## Tasks

| ID | Status | What |
| --- | --- | --- |
| CLI-T10 | green | `resolve_answers` apply then reject |
| CLI-T11 | green | `validate_and_raise` apply then reject (mutates to remapped) |
| CLI-T12 | green | `riso update` remaps `.copier-answers.yml`, preview in `remap`, writes unless `--dry-run`, then Copier |
| CLI-T13 | green | `riso recopy` apply then reject on provided + merged existing (dry-run) |
| CLI-T14 | green | `riso diff` apply then reject (copy via resolve; update/recopy via merge) |
| CLI-T15 | green | `validate_answers_for_generation` applies remaps before leftover/saas/language errors; `_collect_saas_selected` still does not read leftover `saas_auth` |
| CLI-T16 | green | `riso migrate DEST\|--answers-file [--dry-run] [--json]` |
| CLI-T17 | green | `--skip-post-gen` remains in `_GLOBAL_FLAGS` (`test_global_flags_keep_skip_post_gen`) |
| CLI-T18 | green | Fixtures `tests/unit/test_cli/fixtures/remap/` (8 keys + mixed + leftover + already_canonical) loaded by `test_remap.py` + `test_migrate.py` |

## `riso migrate`

```text
uv run riso migrate DEST|--answers-file PATH [--dry-run] [--json]
```

- Exactly one of DEST (reads `DEST/.copier-answers.yml`) or `--answers-file`.
- Preview ops; write unless `--dry-run`.
- Exit 0 when already canonical (`ops` empty).
- Leftover / unmapped value: `ValidationFailedError`, no write.

`--json` is the global flag. Command is listed on `uv run riso --help`. Subcommand help (`--dry-run`, `--answers-file`) verified via Typer `CliRunner` (`test_migrate_help_lists_flags`). Entrypoint `uv run riso migrate --help` still hoists `--help` into `_GLOBAL_FLAGS` (pre-existing normalize); not changed.

## Verify (unit)

```text
uv run pytest tests/unit/test_cli/ -q -n 0
============================= 228 passed in 14.25s =============================
```

`uv run ruff check` + `uv run ty check` on CLI write roots: passed.

## Not this slice

`tests/integration/**` is outside the exclusive write lock. Two JOIN tests still assert reject-before-remap on remappable `api_tracks=python` — see `residuals/CLI.md`.
