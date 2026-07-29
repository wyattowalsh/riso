# Contract delta: `api-features-normalize`

| Field              | Value                                                   |
| ------------------ | ------------------------------------------------------- |
| **change_id**      | `api-features-normalize`                                |
| **applied_at**     | 2026-07-29T01:54:53Z                                    |
| **status**         | `applied`                                               |
| **source_handoff** | `goals/riso-lane-py/handoffs/api-features-normalize.md` |

## Answer keys changed

| key                                       | before                     | after                         |
| ----------------------------------------- | -------------------------- | ----------------------------- |
| `api_features` (render context)           | raw string/list            | sorted token list via pre_gen |
| `graphql_api_module` / `websocket_module` | derived via substring `in` | derived via token membership  |

## Illegal combos now enforced

| rule / condition              | location  | error message (summary)    |
| ----------------------------- | --------- | -------------------------- |
| token-safe feature membership | `pre_gen` | n/a (normalize, not error) |

## Module catalog rows

| name     | change |
| -------- | ------ |
| _(none)_ |        |

## Context files

| file     | action | parity_verified |
| -------- | ------ | --------------- |
| _(none)_ |        | n/a             |

## CLI handoff required

| Field        | Value                                                            |
| ------------ | ---------------------------------------------------------------- |
| **required** | `no`                                                             |
| **summary**  | CLI `normalize_api_features` already token-safe; hooks now match |

## Payload checklist

| lane | exclusive paths to implement | acceptance note                                 | done? |
| ---- | ---------------------------- | ----------------------------------------------- | ----- |
| py   | dual-gated WS/GQL jinja      | may rely on list membership; recheck PY-T03/T04 | ☐     |

## Verification evidence

| stage  | command                          | result                                                    |
| ------ | -------------------------------- | --------------------------------------------------------- |
| pytest | TestNormalizeApiFeatureModules   | passed                                                    |
| V2     | api-python + full-stack validate | ok:true                                                   |
| commit | `d8ca744`                        | fix(hooks): normalize api_features as token list like CLI |

## Residual risks

- Jinja templates that assumed comma-string api_features still work (list membership).
- Substring false positives eliminated for module derivation.
