# W1-M02 / W1-M03 — Hook-safe twin + core ↔ scripts.lib parity

- Tasks: `W1-M02`, `W1-M03`
- Wave: W1
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset / commit)
- Exclusive writes: `scripts/lib/removed_answer_keys.py`, `tests/unit/test_cli/test_removed_keys_packaging.py`, this file
- `samples/*/render/**` writes: **0**
- Status: **green**

## W1-M02 — hook-safe twin

`scripts/lib/removed_answer_keys.py` prefers the packaged SSOT when `riso` is importable:

- `REMOVED_ANSWER_KEYS`
- `ANSWER_KEY_REMAPS`
- `RemapOp` / `RemapResult`
- `apply_removed_key_remaps`

On `ImportError` (hooks that only put `scripts/` on `sys.path`) it binds the local twin:

- `_FALLBACK_REMOVED_ANSWER_KEYS` (same 8 keys + replacement strings)
- `_FALLBACK_ANSWER_KEY_REMAPS` (same 8 operators)
- `_fallback_apply_removed_key_remaps`

Apply contract matches core: remap known keys, leave unmapped leftovers for reject, do not overwrite a dest key that is already set, drop the old key after a successful apply, second apply is a no-op.

## W1-M03 — parity (core ↔ scripts.lib)

TS three-way key+op parity stays WEB-T01 / PL-T10.

| Check | Result |
| --- | --- |
| Packaged import preferred when `riso` is importable | pass (`is` identity) |
| Fallback keys == core keys (8, same strings) | pass |
| Fallback remap table `(old, new_keys, action)` == core | pass |
| Fallback apply answers+ops == core (26 cases + mixed + dest-set + leftover + idempotent) | pass |
| `ImportError` path binds local remaps + apply | pass |

## Verify

```text
uv run pytest tests/unit/test_cli/test_removed_keys_packaging.py -q -n 0
============================== 33 passed in 0.12s ==============================
```

Also: `uv run ruff check` + `ruff format --check` + `uv run ty check` on the two write roots — all passed.

## Not this slice

W1-C07 (hooks apply-then-reject), WEB-T01 (TS remap), PL-T10 (three-way CI checker).
