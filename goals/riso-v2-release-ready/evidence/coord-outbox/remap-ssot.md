# Contract delta: `remap-ssot`

Published by **W1-OUT**. W2 CLI / WEB / PLATFORM consume this; do not re-edit the remap SSOT files.

| Field | Value |
| --- | --- |
| **change_id** | `remap-ssot` |
| **applied_at** | 2026-08-13 |
| **status** | `applied` |
| **source_handoff** | `goals/riso-v2-release-ready/evidence/W1-M01-remap.md`, `W1-M02-twin.md` |
| **wave** | W1-OUT |
| **repo** | `/Users/ww/dev/projects/riso` (maintainer; branch `main`) |
| **samples/\*/render/\*\* writes** | **0** |

---

## Contract

Machine remap SSOT lives in `src/riso/core/removed_answer_keys.py`. Hook/CI twin is `scripts/lib/removed_answer_keys.py` (prefer packaged import; local fallback on `ImportError`).

```text
apply_removed_key_remaps(answers) -> RemapResult(answers, ops)
# ops: [{old, new_keys, action, before, after}]
reject_removed_answer_keys(answers)  # leftovers only; same error shape
```

**Order is apply then reject.** Do not invert. No dual-path aliases after remap. Do not overwrite a dest key that is already set (`_write_dests` keeps dest, still drops old after a successful apply). Unmapped values stay on the old key so reject stays fail-closed. Second apply is a no-op (idempotent).

Exported from `riso.core`: `ANSWER_KEY_REMAPS`, `REMOVED_ANSWER_KEYS`, `RemapOp`, `RemapResult`, `apply_removed_key_remaps`. `reject_removed_answer_keys` remains in `riso.core.answers` (leftovers only).

`scripts/lib` binds the same public names. TS (`web/src/lib/removedAnswerKeys.ts`) still has the **8-key reject set only** — no operators yet (WEB-T01).

Do **not** add a ninth remappable key without updating core + scripts.lib + TS together.

---

## Answer keys changed (8 operators)

| Old key | Operator | Canonical dest | Value rules |
| --- | --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` | empty/`none`/`disabled`/`[]` → `api_module=disabled`; else enabled + intersection with `{python,node,rust,go}` (`fastapi`→python, `fastify`→node, `actix`→rust) |
| `api_language` | wrap-list | `api_languages` | scalar `python`/`node`/`rust`/`go` → `[that]`; already-list → keep |
| `docs_site` | derive | `docs_module`, `docs_framework` | `none`/`false`/`disabled`/`off` → `docs_module=disabled`; `sphinx`/`sphinx-shibuya` → enabled + `sphinx-shibuya`; `docusaurus` / `fumadocs` → enabled + that framework |
| `mcp_language` | wrap-list | `mcp_languages` | scalar `python`/`typescript`/`rust`/`go` → `[that]`; `node`/`js` → `typescript`; already-list → keep |
| `saas_starter_module` | rename | `saas_infra_module` | copy `enabled`/`disabled` |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` | off tokens → module disabled; `clerk`/`authjs`/`lucia` → enabled + provider |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` | off tokens → module disabled; `stripe`/`paddle`/`lemonsqueezy` → enabled + provider |
| `include_admin` | rename-bool | `saas_admin_dashboard` | truthy/falsey → bool |

`graphql_api_module` / `websocket_module` are derived Jinja flags, **not** removed user keys. Do not remap them.

---

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| --- | --- | --- |
| leftover removed key after remap (unknown key or unmapped value) | `reject_removed_answer_keys` / leftover reject | `{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}` |
| dest already set | apply | keep dest; drop old key if apply succeeded |

---

## Module catalog rows

| name | change |
| --- | --- |
| _(none for this CID)_ | remap is not a catalog extra |

---

## Context files

| file | action | parity_verified |
| --- | --- | --- |
| _(none)_ | | n/a |

---

## CLI / WEB handoff required

| Field | Value |
| --- | --- |
| **required** | `yes` |
| **summary** | Wire **apply then reject** at every answers call site. SSOT + hooks are done; CLI/WEB still reject-only. |
| **closed (do not re-edit)** | `src/riso/core/removed_answer_keys.py`, `scripts/lib/removed_answer_keys.py` |

Still reject-before-remap (W2 must flip):

| Site | Path | W2 task |
| --- | --- | --- |
| `resolve_answers` | `src/riso/cli/helpers.py` | CLI-T10 |
| `validate_and_raise` | `src/riso/cli/helpers.py` | CLI-T11 |
| `riso update` | `src/riso/cli/commands/update.py` | CLI-T12 |
| `riso recopy` | `src/riso/cli/commands/recopy.py` | CLI-T13 |
| `riso diff` | `src/riso/cli/commands/diff.py` | CLI-T14 |
| `validate_answers_for_generation` leftover scan | `src/riso/core/generation_gates.py` `_removed_key_errors` | CLI-T15 |
| `riso migrate` (new) | `src/riso/cli/` | CLI-T16 |
| wizard remap + preview | `web/src/lib/removedAnswerKeys.ts` | WEB-T01 |
| wizard import/paste | `web/src/**` | WEB-T02 |
| `exportConfig` / export-yaml | `web/src/**` | WEB-T03 |
| three-way key+op parity checker | `scripts/ci/check_removed_key_ssot.py` (new) | PL-T10 |

Fixtures already on disk (CLI-T18 may extend, not reinvent):

`tests/unit/test_cli/fixtures/remap/` — one YAML per old key + `mixed.yml` + `already_canonical.yml` + `leftover.yml`.

---

## Payload checklist

**Do not re-touch COORD / remap SSOT files.** Implement only exclusive paths.

COORD / CLI SSOT (closed after this delta):

- `src/riso/core/removed_answer_keys.py`
- `scripts/lib/removed_answer_keys.py`
- `tests/unit/test_cli/test_remap.py`
- `tests/unit/test_cli/test_removed_keys_packaging.py`
- `tests/unit/test_cli/fixtures/remap/**`

| lane | exclusive paths to implement | acceptance note | done? |
| --- | --- | --- | --- |
| cli | `src/riso/cli/**`, `src/riso/core/answers.py` / `helpers.py` / `generation_gates.py` (apply-before-reject only), `tests/unit/test_cli/**` | apply then reject at T10–T16; keep `--skip-post-gen`; no dest overwrite | ☐ |
| web | `web/src/lib/removedAnswerKeys.ts`, wizard import/export/presets | same 8 keys + operator names; remap then fail-closed leftovers; presets emit no old keys | ☐ |
| platform | `scripts/ci/check_removed_key_ssot.py`; `samples/**/copier-answers.yml` after CLI/WEB | 3-way key+op parity; no sample answers contain a removed key | ☐ |
| sys | rust excludes | **unchanged** unless a later COORD outbox says otherwise (SYS-T02) | ☐ |
| docs | `docs/guides/v2-migration.md` (W4) | document remap table + `riso migrate --dry-run` | ☐ |

---

## Verification evidence

| stage | command | result |
| --- | --- | --- |
| W1-M01 table + dest/idempotent/leftover | `uv run pytest tests/unit/test_cli/test_remap.py tests/unit/test_cli/test_generation_gates.py -q -n 0` | **85 passed** (`W1-M01-remap.md`) |
| W1-M02/M03 core ↔ scripts.lib | `uv run pytest tests/unit/test_cli/test_removed_keys_packaging.py -q -n 0` | **33 passed** (`W1-M02-twin.md`) |
| default validate | `uv run riso validate --answers-file samples/default/copier-answers.yml --json` | `ok: true` (`W1-C01-extras.md`) |

---

## Residual risks

- CLI/WEB still reject-only — 1.x answers fail before remap until T10–T16 / WEB-T01.
- TS operators can drift from Python; PL-T10 must lock the triple.
- Unmapped historical values must fail closed — do not guess.

## Notes

- Prefer clean current-state contracts; no legacy dual-path.
- Never hand-edit `samples/*/render/`, `uv.lock`, or `pnpm-lock.yaml`.
- Do not reintroduce `riso-mcp`.
- `render_matrix.py` is blocking later and may not be residualed.
