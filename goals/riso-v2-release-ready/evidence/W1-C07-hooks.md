# W1-C07 — Hooks apply then reject leftovers

- Task: `W1-C07`
- Wave: W1
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset)
- Exclusive writes: `template/hooks/pre_gen_project.py`, `template/hooks/post_gen_project.py`, `tests/unit/hooks/test_pre_gen_project.py`, `tests/unit/hooks/test_post_gen_project.py` (companion; leftover reject test now uses unmapped `saas_auth`), this file
- `samples/*/render/**` writes: **0**
- Status: **green**

## Contract

`apply_removed_key_remaps` (from `lib.removed_answer_keys`) then reject leftovers. No dest overwrite when the dest key is already set. Drop the old key after a successful apply. Second apply is a no-op. Unmapped values stay on the old key so reject stays fail-closed. No dual-path aliases after remap.

## Hook choke point

Both hooks import `REMOVED_ANSWER_KEYS` and `apply_removed_key_remaps` from `lib.removed_answer_keys` (W1-M02 twin already exported).

| Hook | Apply | Then reject leftovers |
| --- | --- | --- |
| `pre_gen_project.py` | `_apply_removed_key_remaps` mutates Copier context in place | `_reject_leftover_removed_keys` — same error shape as before |
| `post_gen_project.py` | `validate_removed_answer_keys` remaps in-memory answers | leftover keys → `SystemExit(1)` |

`pre_gen` `main()` applies + rejects **before** `_write_copier_context`, so Copier env sees canonical keys. `_validate_generation_answers` leftover path is leftovers-only (apply already ran). `post_gen` does not rewrite `.copier-answers.yml` (file write stays `riso migrate`).

## Verify

```text
uv run pytest tests/unit/hooks/test_pre_gen_project.py -q -n 0
============================== 91 passed in 0.64s ==============================
```

Companion: `tests/unit/hooks/test_post_gen_project.py` also green (161 passed with both files).

`uv run ruff check` + `ruff format --check` on the four Python files: all checks passed.

## Not this slice

W1-C01–C05 Copier extras, W1-C08 no-legacy policy, W1-OUT coord-outbox, W2 CLI/WEB call-site wiring, answers-file rewrite via `riso migrate`.
