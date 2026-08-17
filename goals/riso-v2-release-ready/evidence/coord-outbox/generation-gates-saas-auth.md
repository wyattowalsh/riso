# Contract delta: `generation-gates-saas-auth`

Published by **W1-OUT**. Shared generation gates no longer read leftover `saas_auth`.

| Field | Value |
| --- | --- |
| **change_id** | `generation-gates-saas-auth` |
| **applied_at** | 2026-08-13 |
| **status** | `applied` (old-key read dropped); apply-before-reject in gates still **CLI-T15** |
| **source_handoff** | `goals/riso-v2-release-ready/evidence/W1-M01-remap.md` (W1-C06) |
| **wave** | W1-OUT |
| **repo** | `/Users/ww/dev/projects/riso` (maintainer; branch `main`) |
| **samples/\*/render/\*\* writes** | **0** |

---

## Contract

`src/riso/core/generation_gates.py` `_collect_saas_selected` **must not** read leftover `saas_auth`.

Current collect keys:

- `saas_runtime`, `saas_hosting`, `saas_database`, `saas_orm`
- `saas_auth_module`, `saas_auth_provider`
- `saas_storage`, `saas_cicd`
- `saas_billing_provider`

`rg '"saas_auth"' src/riso/core/generation_gates.py` is empty. Remaining hits are `saas_auth_module` / `saas_auth_provider` only.

SaaS combo rules still key off `saas_infra_module` (canonical), not `saas_starter_module`.

`validate_answers_for_generation` still runs `_removed_key_errors` **without** calling `apply_removed_key_remaps`. That leftover scan is correct **after** apply. CLI-T15 must apply remaps on the answers dict **before** leftover errors so mapped `saas_auth` / `saas_billing` / `include_admin` do not fail closed.

Do **not** reintroduce old-key reads in gates, hooks, wizard, or Jinja defaults.

---

## Answer keys changed

| key | before (gates) | after (gates) |
| --- | --- | --- |
| `saas_auth` | read in `_collect_saas_selected` (W0 leftover) | **not read**; remap dests only |
| `saas_auth_module` | — | collected when set |
| `saas_auth_provider` | — | collected when set |

Remap of `saas_auth` values (SSOT, not gates):

| historical value | dest |
| --- | --- |
| `none` / `disabled` / `false` / `off` | `saas_auth_module=disabled` |
| `clerk` / `authjs` / `lucia` | `saas_auth_module=enabled` + that `saas_auth_provider` |
| anything else | leftover → reject |

---

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| --- | --- | --- |
| leftover `saas_auth` after apply | `_removed_key_errors` | `saas_auth: removed answer key; use \`saas_auth_module\` plus \`saas_auth_provider\`` |
| Neon + Supabase Storage | `_saas_errors` | unchanged combo (uses collected canonical tokens) |
| Supabase Realtime without `saas_database=supabase` | `_saas_errors` | unchanged |

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
| **required** | `yes` |
| **summary** | CLI-T15: apply remaps before `validate_answers_for_generation` leftover errors. Keep `_collect_saas_selected` free of `saas_auth`. |
| **closed** | old-key **read** already removed from `_collect_saas_selected` |

W2 must **not** add `saas_auth` back as a dual-path collector “just in case”.

---

## Payload checklist

**Do not re-introduce leftover `saas_auth` reads.**

| lane | exclusive paths to implement | acceptance note | done? |
| --- | --- | --- | --- |
| cli | `generation_gates` call path + `test_generation_gates.py` | CLI-T15 apply-before-leftover; existing combo tests stay green | ☐ |
| saas | `template/files/node/saas/**` | SAAS-T01/T02: `runtime/{nextjs,remix}` present; no flatten | ☐ |
| web | presets / store | WEB-T04: no old `saas_auth` in presets | ☐ |
| platform | sample answers | no `saas_auth:` / `saas_billing:` / `include_admin` in `copier-answers.yml` | ☐ |

---

## Verification evidence

| stage | command | result |
| --- | --- | --- |
| W1-C06 + remap tests | `uv run pytest tests/unit/test_cli/test_remap.py tests/unit/test_cli/test_generation_gates.py -q -n 0` | **85 passed** |
| leftover read | grep `"saas_auth"` in `generation_gates.py` | **empty**; only `_module` / `_provider` |

W0 `evidence/W0-rg-gates.txt` leftover citation is **historical** (pre-C06). Current tree matches this outbox.

---

## Residual risks

- If CLI-T15 is skipped, mapped 1.x `saas_auth` still errors in `validate_answers_for_generation`.
- Wizard/presets that still emit `saas_auth` will fail closed after remap wiring (WEB-T04).

## Notes

- Never hand-edit `samples/*/render/`.
- Do not reintroduce `riso-mcp`.
