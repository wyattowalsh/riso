# Contract delta: `coord-mcp-languages-typescript`

| Field              | Value                                                               |
| ------------------ | ------------------------------------------------------------------- |
| **change_id**      | `coord-mcp-languages-typescript`                                    |
| **applied_at**     | 2026-07-29T01:54:53Z                                                |
| **status**         | `applied`                                                           |
| **source_handoff** | `goals/riso-lane-platform/outbox/coord-mcp-languages-typescript.md` |

## Answer keys changed

| key                     | before           | after                            |
| ----------------------- | ---------------- | -------------------------------- |
| `mcp_languages` choices | python, rust, go | python, **typescript**, rust, go |

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

**Do not re-touch COORD paths.**

| lane     | exclusive paths to implement     | acceptance note                                    | done? |
| -------- | -------------------------------- | -------------------------------------------------- | ----- |
| node     | `template/files/node/mcp/**`     | TS MCP payload after choice restored (NODE-T03)    | ☐     |
| platform | answers only if migration needed | `samples/mcp-typescript` already uses `typescript` | ☐     |

## Verification evidence

| stage  | command                                                                                | result                                                 |
| ------ | -------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| V2     | `uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json` | ok:true                                                |
| commit | `e34927a`                                                                              | fix(template): add typescript to mcp_languages choices |

## Residual risks

- NODE payload quality for TS MCP still owned by NODE lane after W1.
