# W0-T02a — three-way `REMOVED_ANSWER_KEYS` SSOT diff

- Task: W0-T02a
- Wave: W0 / group W0A
- Repo: `/Users/ww/dev/projects/riso` (workspace root; `read_file` / `grep` only — no `git` mutation)
- Verify: exactly 8 keys; cite any value drift
- Status: **green** — 8 keys, identical key set, **no value drift**

## Sources (read, not edited)

| Surface | Path | Role |
| --- | --- | --- |
| CLI / package | `src/riso/core/removed_answer_keys.py` | Packaged SSOT (`dict[str, str]`) |
| hooks / scripts fallback | `scripts/lib/removed_answer_keys.py` | Prefer `riso.core` import; local twin on `ImportError` |
| web wizard | `web/src/lib/removedAnswerKeys.ts` | TS `Record<string, string>`; comment says keep parity with core |

`src/riso/core/answers.py` re-exports the core dict (not a fourth copy). Not a write target for this task.

## Key set (exactly 8)

Declaration order is the same in all three dicts and matches `plan.taskgraph.json` `remap_keys`:

| # | Old key | In core | In scripts.lib fallback | In TS |
| --- | --- | --- | --- | --- |
| 1 | `api_tracks` | yes | yes | yes |
| 2 | `api_language` | yes | yes | yes |
| 3 | `docs_site` | yes | yes | yes |
| 4 | `mcp_language` | yes | yes | yes |
| 5 | `saas_starter_module` | yes | yes | yes |
| 6 | `saas_auth` | yes | yes | yes |
| 7 | `saas_billing` | yes | yes | yes |
| 8 | `include_admin` | yes | yes | yes |

- Extra keys in any dict: **none**
- Missing keys vs plan `remap_keys`: **none**
- Key-set symmetric difference (core Δ scripts.lib Δ TS): **empty**

Tests already encode the count/set (not re-run here):

- `tests/unit/test_cli/test_answers.py` — `len(REMOVED_ANSWER_KEYS) == 8`
- `tests/unit/test_cli/test_removed_keys_packaging.py` — `len(core_keys) == 8` and `dict(mod.REMOVED_ANSWER_KEYS) == dict(core_keys)` when `riso` is importable
- `web/src/__tests__/removedAnswerKeys.test.ts` — `Object.keys(...).toHaveLength(8)` and sorted key list equals the eight names above

## Value table (replacement prose)

Values are **human replacement strings** today (plan critique: not yet a machine `ANSWER_KEY_REMAPS` table). Compared after stripping language string delimiters only.

| Old key | core (`src/riso/core/removed_answer_keys.py` L6–13) | scripts.lib fallback (`scripts/lib/removed_answer_keys.py` L15–22) | TS (`web/src/lib/removedAnswerKeys.ts` L5–12) | Drift |
| --- | --- | --- | --- | --- |
| `api_tracks` | `` `api_module` plus `api_languages` `` | identical | identical | none |
| `api_language` | `` `api_languages` `` | identical | identical | none |
| `docs_site` | `` `docs_module` plus `docs_framework` `` | identical | identical | none |
| `mcp_language` | `` `mcp_languages` `` | identical | identical | none |
| `saas_starter_module` | `` `saas_infra_module` `` | identical | identical | none |
| `saas_auth` | `` `saas_auth_module` plus `saas_auth_provider` `` | identical | identical | none |
| `saas_billing` | `` `saas_billing_module` plus `saas_billing_provider` `` | identical | identical | none |
| `include_admin` | `` `saas_admin_dashboard` `` | identical | identical | none |

Byte-level notes on the eight values:

- Same destination names, same `` `backticks` `` around those names, same ` plus ` conjunction, no extra spaces or punctuation.
- Python uses `"..."` literals; TS uses `'...'` literals. That is syntax, not payload drift.
- TS keys are unquoted identifiers (`api_tracks:` vs `"api_tracks":`). Same names.

**Value drift: none.**

## Structural / packaging differences (not dict-value drift)

These do **not** change the eight key→string mappings:

1. **core** (`src/riso/core/removed_answer_keys.py` L14–17) carries a comment that `graphql_api_module` / `websocket_module` stay *derived* Jinja flags and must **not** be listed as removed user keys. Those names are absent from all three dicts.
2. **scripts.lib** wraps the dict in `try: from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS` / `except ImportError:` fallback. When the package import succeeds, the fallback dict is unused and the bound object is the core dict. The fallback body is still a full twin (8 keys, same strings) for hooks that only put `scripts/` on `sys.path`.
3. **TS** also exports `findRemovedAnswerKeys` / `formatRemovedAnswerKeyErrors` (error shape: `{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}`), matching `reject_removed_answer_keys` in `src/riso/core/answers.py`. Helpers are not extra keys.

## Remap-contract gap (inventory only; W1 owns the fix)

All three dicts store replacement **prose**, not operators. Plan W1-M01 / W1-M02 / WEB-T01 still need `ANSWER_KEY_REMAPS` + `apply_removed_key_remaps` (apply then reject leftovers). W0-T02a does not implement that.

## Verdict

| Check | Result |
| --- | --- |
| Exactly 8 keys in each of the three dicts | pass |
| Same key set and declaration order | pass |
| Replacement-string value drift | **none** |
| Extra / missing keys vs `plan.taskgraph.json` `remap_keys` | none |

W0-T02a verify (`8 keys identical`) is met.
