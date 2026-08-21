# No Legacy Answer Policy

Riso 2.0 remaps the eight known removed Copier keys, then fail-closes leftovers.
After a successful remap, only canonical component-first keys remain. Dual-path
aliases are forbidden after remap.

## Contract

Apply then reject. Do not invert the order.

1. `apply_removed_key_remaps(answers)` — remap every known key that has a mapped
   value.
1. `reject_removed_answer_keys(answers)` — fail closed on leftovers (unknown
   removed keys, or known keys whose values could not be remapped).

Operator rules (SSOT: `src/riso/core/removed_answer_keys.py`):

- Do **not** overwrite a destination key that is already set. Keep the dest
  value; still drop the old key after a successful apply.
- Drop the old key only after a successful apply.
- Second apply is a no-op (idempotent).
- Unmapped values stay on the old key so reject stays fail-closed.
- Reject error shape is unchanged:
  `{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}`.
- After remap, do **not** keep dual-path aliases, hidden fallbacks, or
  old-key reads in hooks, CLI, wizard, gates, or generated defaults.

`riso migrate` and `riso update` use this same apply-then-reject choke point
(including `--dry-run` preview). Every other answers call site
(`resolve_answers`, `validate_and_raise`, `recopy`, `diff`, `copy`,
`generation_gates`, hooks `pre_gen`/`post_gen`, wizard import) must apply then
reject — never reject-only, never alias both old and new.

## The eight known keys

These are the only remappable removed keys. The set is `REMOVED_ANSWER_KEYS`
and `ANSWER_KEY_REMAPS` (8/8; same names in `scripts/lib` and
`web/src/lib/removedAnswerKeys.ts`).

| Old key               | Operator    | Canonical dest                                     | Value rules                                                                                                                                                                                          |
| --------------------- | ----------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_tracks`          | derive      | `api_module` plus `api_languages`                  | empty/`none`/`disabled` → `api_module=disabled`; else `api_module=enabled` and languages = intersection of tokens with `{python,node,rust,go}` (also `fastapi`→python, `fastify`→node, `actix`→rust) |
| `api_language`        | wrap-list   | `api_languages`                                    | scalar `python`/`node`/`rust`/`go` → `[that]`; already-list → keep                                                                                                                                   |
| `docs_site`           | derive      | `docs_module` plus `docs_framework`                | `none`/`false`/`disabled`/`off` → `docs_module=disabled`; `sphinx`/`sphinx-shibuya` → enabled + `sphinx-shibuya`; `docusaurus` / `fumadocs` → enabled + that framework                               |
| `mcp_language`        | wrap-list   | `mcp_languages`                                    | scalar `python`/`typescript`/`rust`/`go` → `[that]`; map `node`/`js` → `typescript`; already-list → keep the list shape, drop empty items, and still apply `node`/`js` → `typescript`                |
| `saas_starter_module` | rename      | `saas_infra_module`                                | copy `enabled`/`disabled`                                                                                                                                                                            |
| `saas_auth`           | split       | `saas_auth_module` plus `saas_auth_provider`       | `none`/`disabled`/`false`/`off` → `saas_auth_module=disabled`; `clerk`/`authjs` → module enabled + that provider; `lucia` is unmapped and fail-closes                                                |
| `saas_billing`        | split       | `saas_billing_module` plus `saas_billing_provider` | `none`/`disabled`/`false`/`off` → `saas_billing_module=disabled`; `stripe`/`paddle`/`lemonsqueezy` → module enabled + that provider                                                                  |
| `include_admin`       | rename-bool | `saas_admin_dashboard`                             | truthy/falsey → bool                                                                                                                                                                                 |

Do not add a ninth remappable key without updating the three-way SSOT and this
table together.

`graphql_api_module` / `websocket_module` are derived Jinja flags, not removed
user keys. Do not list them here.

## Required behavior

- Remap the eight known keys, then fail-closed leftovers.
- Do not add hidden aliases, fallbacks, or dual-path behavior after remap.
- Keep active docs, examples, samples, web presets, and generated default
  answers on canonical keys only.
- No sample `copier-answers.yml` and no generated default answers may contain a
  removed Copier key after migrate.
- Allow removed-key strings only in: this policy, remap fixtures, negative
  tests, `riso migrate`/`update` preview, and release notes / the v2 migration
  guide that explain remap-then-reject.

## Forbidden

- Dual-path aliases after remap (reading or writing both old and new keys).
- Accepting leftover removed keys or guessing unmapped historical values.
- Overwriting a dest key that is already set.
- Reintroducing reject-only handling at a call site that already has remaps.
- Reintroducing `riso-mcp`.
