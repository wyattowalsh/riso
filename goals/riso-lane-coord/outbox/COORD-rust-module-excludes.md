# Contract delta: `COORD-rust-module-excludes`

| Field              | Value                                                        |
| ------------------ | ------------------------------------------------------------ |
| **change_id**      | `COORD-rust-module-excludes`                                 |
| **applied_at**     | 2026-07-29T01:54:53Z                                         |
| **status**         | `applied`                                                    |
| **source_handoff** | `goals/riso-lane-sys/handoffs/COORD-rust-module-excludes.md` |

## Answer keys changed

| key      | before | after |
| -------- | ------ | ----- |
| _(none)_ |        |       |

## Illegal combos now enforced

| rule / condition                  | location                | error message (summary) |
| --------------------------------- | ----------------------- | ----------------------- |
| rust/cli excluded unless CLI+rust | `copier.yml` `_exclude` | path omit               |
| rust/api excluded unless API+rust | `copier.yml` `_exclude` | path omit               |

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

| lane     | exclusive paths to implement      | acceptance note                                | done? |
| -------- | --------------------------------- | ---------------------------------------------- | ----- |
| sys      | `template/files/rust/**`          | ensure Cargo workspace members match excludes  | ☐     |
| platform | `samples/rust-*` answers (PL-T03) | single-module layouts stay lean after excludes | ☐     |

## Verification evidence

| stage  | command                                                                              | result                                                    |
| ------ | ------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| grep   | rust/cli + rust/api `_exclude` present                                               | yes                                                       |
| V2     | `uv run riso validate --answers-file samples/api-monorepo/copier-answers.yml --json` | ok:true                                                   |
| commit | `ed664c4`                                                                            | fix(template): exclude unused rust/cli and rust/api trees |

## Residual risks

- SYS Cargo.toml member lists must stay consistent when only MCP rust is enabled.
