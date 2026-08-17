# W1-M01 — Machine remap SSOT + W1-C06 gates

- Tasks: `W1-M01`, `W1-M01b`, `W1-M01c`, `W1-M01d`, `W1-M01e`, `W1-C06`
- Wave: W1
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset)
- Exclusive writes: `src/riso/core/removed_answer_keys.py`, `src/riso/core/__init__.py`, `src/riso/core/generation_gates.py`, `tests/unit/test_cli/test_remap.py`, `tests/unit/test_cli/fixtures/remap/`, `tests/unit/test_cli/test_generation_gates.py`, this file
- `samples/*/render/**` writes: **0**
- Status: **green**

## Contract

`apply_removed_key_remaps(answers) -> RemapResult(answers, ops)` then `reject_removed_answer_keys` on leftovers. No dest overwrite when the dest key is already set. Drop the old key after a successful apply. Second apply is a no-op. Unmapped values stay on the old key so reject stays fail-closed.

## `ANSWER_KEY_REMAPS` (8 operators)

| Old key | action | new_keys |
| --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` |
| `api_language` | wrap-list | `api_languages` |
| `docs_site` | derive | `docs_module`, `docs_framework` |
| `mcp_language` | wrap-list (`node`/`js` → `typescript`) | `mcp_languages` |
| `saas_starter_module` | rename | `saas_infra_module` |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` |
| `include_admin` | rename-bool | `saas_admin_dashboard` |

Exported from `riso.core`: `ANSWER_KEY_REMAPS`, `RemapOp`, `RemapResult`, `apply_removed_key_remaps`.

`reject_removed_answer_keys` is unchanged (leftovers only; same error shape). Call sites still reject-before-remap until W2 CLI-T10–T15.

## W1-C06

`generation_gates._collect_saas_selected` no longer reads leftover `saas_auth`. It collects `saas_auth_module` and `saas_auth_provider`. `rg '"saas_auth"' src/riso/core/generation_gates.py` is empty; remaining hits are `saas_auth_module` / `saas_auth_provider`.

## Fixtures

`tests/unit/test_cli/fixtures/remap/`: one YAML per old key, plus `mixed.yml`, `already_canonical.yml`, `leftover.yml`.

## Verify

```text
uv run pytest tests/unit/test_cli/test_remap.py tests/unit/test_cli/test_generation_gates.py -q -n 0
============================== 85 passed in 0.10s ==============================
```

Also: `test_answers.py` + `test_removed_keys_packaging.py` still green (90 passed with the files above).

## Not this slice

W1-M02 (`scripts/lib` twin), W1-M03 (three-way parity), and W2 call-site wiring (`riso migrate`, apply-then-reject in helpers/update/gates) stay for their owners.
