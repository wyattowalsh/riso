# Contract delta: `hooks-apply`

Published by **W1-OUT**. Hooks already apply then reject leftovers. W2 must **not** re-edit `template/hooks/**`.

| Field | Value |
| --- | --- |
| **change_id** | `hooks-apply` |
| **applied_at** | 2026-08-13 |
| **status** | `applied` |
| **source_handoff** | `goals/riso-v2-release-ready/evidence/W1-C07-hooks.md` |
| **wave** | W1-OUT |
| **repo** | `/Users/ww/dev/projects/riso` (maintainer; branch `main`) |
| **samples/\*/render/\*\* writes** | **0** |

---

## Contract

`template/hooks/pre_gen_project.py` and `template/hooks/post_gen_project.py` import `REMOVED_ANSWER_KEYS` + `apply_removed_key_remaps` from `lib.removed_answer_keys` (W1-M02 twin).

Apply then reject leftovers. No dest overwrite when dest is already set. Drop the old key after a successful apply. Second apply is a no-op. Unmapped values stay on the old key so reject stays fail-closed. No dual-path aliases after remap.

| Hook | Apply | Then reject leftovers |
| --- | --- | --- |
| `pre_gen_project.py` | `_apply_removed_key_remaps` mutates Copier context in place | `_reject_leftover_removed_keys` — same error shape as before |
| `post_gen_project.py` | `validate_removed_answer_keys` remaps in-memory answers | leftover keys → `SystemExit(1)` |

`pre_gen` `main()` calls `_validate_removed_answer_keys` **before** `_write_copier_context`, so Copier env sees canonical keys. `_validate_generation_answers` leftover path is leftovers-only (apply already ran).

**`post_gen` does not rewrite `.copier-answers.yml`.** File rewrite stays `riso migrate` (CLI-T16).

---

## Answer keys changed

| key | before | after |
| --- | --- | --- |
| _(none new — same 8 remaps as `remap-ssot`)_ | reject-only in hooks | apply then leftover-reject |

---

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| --- | --- | --- |
| leftover removed key after hook remap | `pre_gen` `_reject_leftover_removed_keys` | `Removed Copier answer keys are no longer supported:` + `{key}: {replacement}` |
| leftover removed key after hook remap | `post_gen` `validate_removed_answer_keys` | same list; `SystemExit(1)` |

---

## Module catalog rows

| name | change |
| --- | --- |
| _(none)_ | |

---

## Context files

| file | action | parity_verified |
| --- | --- | --- |
| _(none)_ | | n/a |

---

## CLI handoff required

| Field | Value |
| --- | --- |
| **required** | `yes` (answers-file write only) |
| **summary** | Hooks remap in memory only. `riso migrate` / `riso update` own persisting remapped YAML. |
| **CLI ticket** | CLI-T12 / CLI-T16 |

COORD hooks (closed after this delta):

- `template/hooks/pre_gen_project.py`
- `template/hooks/post_gen_project.py`

---

## Payload checklist

**Do not re-touch COORD hook paths.**

| lane | exclusive paths to implement | acceptance note | done? |
| --- | --- | --- | --- |
| cli | `riso migrate` / `update` write remapped answers | persist apply result; hooks stay in-memory | ☐ |
| web | wizard import | same apply-then-reject; do not add hook aliases | ☐ |
| platform | sample answers | no leftover removed keys in `copier-answers.yml` | ☐ |

---

## Verification evidence

| stage | command | result |
| --- | --- | --- |
| V4 hooks | `uv run pytest tests/unit/hooks/test_pre_gen_project.py -q -n 0` | **91 passed** (`W1-C07-hooks.md`) |
| V4 companion | `tests/unit/hooks/test_post_gen_project.py` | green with pre_gen (161 passed both files) |
| lint | `uv run ruff check` + `ruff format --check` on the four Python files | all checks passed |

---

## Residual risks

- A missed CLI/WEB call site that still reject-only will fail 1.x YAML before remap (owned by `remap-ssot`, not hooks).
- Do not add a second hook-local remap table.

## Notes

- Never hand-edit `samples/*/render/`.
- Do not reintroduce `riso-mcp`.
