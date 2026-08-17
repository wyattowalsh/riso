# Contract delta: `policy-8keys`

Published by **W1-OUT**. Release-readiness policy is remap-then-fail-closed on **all 8** removed keys.

| Field | Value |
| --- | --- |
| **change_id** | `policy-8keys` |
| **applied_at** | 2026-08-13 |
| **status** | `applied` (skill body); `.claude` mirror **residualed** |
| **source_handoff** | `goals/riso-v2-release-ready/evidence/W1-C08-policy.md` |
| **wave** | W1-OUT |
| **repo** | `/Users/ww/dev/projects/riso` (maintainer; branch `main`) |
| **samples/\*/render/\*\* writes** | **0** |

---

## Contract

Old policy listed **5** keys and said **“Do not convert removed keys into canonical keys.”** That forbade `riso migrate` / `apply_removed_key_remaps`.

New policy (`.agents/skills/riso-release-readiness/references/no-legacy-answer-policy.md`):

1. `apply_removed_key_remaps` on the 8 known keys.
2. `reject_removed_answer_keys` leftovers (fail-closed).
3. No “do not convert” / “Do not convert” / “do-not-convert” anywhere under `.agents/skills/riso-release-readiness/**`.
4. No dual-path aliases, dest overwrite, or hidden fallbacks **after** remap.
5. `SKILL.md` stop rule: stop on leftover dual-path or non-fail-closed leftovers; pointer to the policy file.

Every answers call site (`resolve_answers`, `validate_and_raise`, `update`, `recopy`, `diff`, `copy`, `generation_gates`, hooks, wizard import) must apply then reject.

---

## Answer keys changed (policy table = SSOT names)

| Old key | Operator | Dest |
| --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` |
| `api_language` | wrap-list | `api_languages` |
| `docs_site` | derive | `docs_module`, `docs_framework` |
| `mcp_language` | wrap-list | `mcp_languages` |
| `saas_starter_module` | rename | `saas_infra_module` |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` |
| `include_admin` | rename-bool | `saas_admin_dashboard` |

8/8 match `REMOVED_ANSWER_KEYS` / `ANSWER_KEY_REMAPS` / `plan.taskgraph.json` `remap_keys`.

Removed-key strings are allowed only in: this policy, remap fixtures, negative tests, `riso migrate`/`update` preview, and v2 migration / CHANGELOG notes.

---

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| --- | --- | --- |
| leftover dual-path or non-fail-closed leftovers | skill stop rule | stop; see `no-legacy-answer-policy.md` |
| leftover removed key after remap | reject helpers | `{key}: removed answer key; use {replacement}` |

---

## Module catalog rows

| name | change |
| --- | --- |
| _(none)_ | policy is skill-only |

---

## Context files

| file | action | parity_verified |
| --- | --- | --- |
| _(none)_ | | n/a |

---

## CLI handoff required

| Field | Value |
| --- | --- |
| **required** | `yes` (behavior already specified by `remap-ssot`) |
| **summary** | Implement migrate/update apply-then-reject. Do **not** restore “do not convert”. |

SKILL (closed after this delta):

- `.agents/skills/riso-release-readiness/references/no-legacy-answer-policy.md`
- `.agents/skills/riso-release-readiness/SKILL.md`

---

## Payload checklist

**Do not re-touch `.agents/skills/riso-release-readiness/**`.**

| lane | exclusive paths to implement | acceptance note | done? |
| --- | --- | --- | --- |
| platform / skill-mirror | `.claude/skills/riso-release-readiness/**` | copy two files; then `validate_release_readiness_skill.py` (PL-T07). Foreign tree — see residual | ☐ |
| cli / web | call sites | follow this policy; no dual-path after remap | ☐ |
| docs | `docs/guides/v2-migration.md`, CHANGELOG Unreleased 2.0.0 | name the 8 remaps; **no version tag** | ☐ |

---

## Verification evidence

| stage | command | result |
| --- | --- | --- |
| phrase audit | `rg -n 'do not convert\|Do not convert\|do-not-convert' .agents/skills/riso-release-readiness` | empty |
| 8 keys | `rg` old keys in `no-legacy-answer-policy.md` | 8 table rows |
| skill validator | `uv run python scripts/ci/validate_release_readiness_skill.py` | **exit 1** — `.claude` mirror mismatch (residual, not this write) |

---

## Residual risks

- **R1** `.claude` skill mirror out of date. Owner: PLATFORM / PL-T07 (or SKILL if lock expands). Command and log: `goals/riso-v2-release-ready/residuals/SKILL.md`. Exclusive write root did not include `.claude/**`; silent copy forbidden.

## Notes

- Never hand-edit `samples/*/render/`.
- Do not reintroduce `riso-mcp`.
- No git tag / PyPI publish from this policy.
