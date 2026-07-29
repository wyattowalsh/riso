# Contract delta: `COORD-go-version-mcp`

| Field              | Value                                                  |
| ------------------ | ------------------------------------------------------ |
| **change_id**      | `COORD-go-version-mcp`                                 |
| **applied_at**     | 2026-07-29T01:54:53Z                                   |
| **status**         | `applied`                                              |
| **source_handoff** | `goals/riso-lane-sys/handoffs/COORD-go-version-mcp.md` |

## Answer keys changed

| key               | before                                       | after                      |
| ----------------- | -------------------------------------------- | -------------------------- |
| `go_version` when | `go in cli_languages or go in api_languages` | + `or go in mcp_languages` |

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| ---------------- | -------- | ----------------------- |
| _(none new)_     |          |                         |

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

| lane | exclusive paths to implement | acceptance note                        | done? |
| ---- | ---------------------------- | -------------------------------------- | ----- |
| sys  | `template/files/go/mcp/**`   | templates already default `go_version` | ☐     |

## Verification evidence

| stage  | command                                                                        | result                                               |
| ------ | ------------------------------------------------------------------------------ | ---------------------------------------------------- |
| V2     | `uv run riso validate --answers-file samples/go-mcp/copier-answers.yml --json` | ok:true                                              |
| commit | `b70352e`                                                                      | fix(template): prompt go_version when MCP selects go |

## Residual risks

- None for COORD; SYS may bump MCP default docs to 1.24 separately.
