# Contract delta: `exclude-empty-dirs`

| Field              | Value                                               |
| ------------------ | --------------------------------------------------- |
| **change_id**      | `exclude-empty-dirs`                                |
| **applied_at**     | 2026-07-29T01:54:53Z                                |
| **status**         | `applied`                                           |
| **source_handoff** | `goals/riso-lane-py/handoffs/exclude-empty-dirs.md` |

## Answer keys changed

| key      | before | after |
| -------- | ------ | ----- |
| _(none)_ |        |       |

## Illegal combos now enforced

| rule / condition                                     | location                | error message (summary) |
| ---------------------------------------------------- | ----------------------- | ----------------------- |
| codegen package/tests excluded when codegen disabled | `copier.yml` `_exclude` | path omit               |
| empty optional shells removed post-gen               | `post_gen` cleanup      | rmdir empty shells      |

## Module catalog rows

| name     | change |
| -------- | ------ |
| _(none)_ |        |

## Context files

| file     | action | parity_verified |
| -------- | ------ | --------------- |
| _(none)_ |        | n/a             |

## CLI handoff required

| Field        | Value |
| ------------ | ----- |
| **required** | `no`  |
| **summary**  | n/a   |

## Payload checklist

| lane | exclusive paths to implement | acceptance note                    | done? |
| ---- | ---------------------------- | ---------------------------------- | ----- |
| py   | `template/files/python/**`   | PY-T09 recheck empty dirs after W1 | ☐     |

## Verification evidence

| stage   | command                            | result                                                        |
| ------- | ---------------------------------- | ------------------------------------------------------------- |
| V2      | validate cli-docs                  | ok:true                                                       |
| scratch | cli-docs render + post_gen cleanup | optional paths absent                                         |
| pytest  | TestCleanupEmptyScaffoldDirs       | passed                                                        |
| commit  | `0961211`                          | fix(template): omit empty optional python trees when disabled |

## Residual risks

- API dual-gate stubs still render when api_module disabled (intentional PY dual-gate, not empty).
- Full post_gen with quality tools may be slow; cleanup logic is unit-tested.
