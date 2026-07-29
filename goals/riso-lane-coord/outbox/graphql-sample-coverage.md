# Contract delta: `graphql-sample-coverage`

| Field              | Value                                                      |
| ------------------ | ---------------------------------------------------------- |
| **change_id**      | `graphql-sample-coverage`                                  |
| **applied_at**     | 2026-07-29T01:54:53Z                                       |
| **status**         | `rejected` (no COORD contract change; residual → PLATFORM) |
| **source_handoff** | `goals/riso-lane-py/handoffs/graphql-sample-coverage.md`   |

## Answer keys changed

| key                                       | before | after |
| ----------------------------------------- | ------ | ----- |
| _(none — answers are PLATFORM exclusive)_ |        |       |

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| ---------------- | -------- | ----------------------- |
| _(none)_         |          |                         |

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

| lane     | exclusive paths to implement              | acceptance note                              | done? |
| -------- | ----------------------------------------- | -------------------------------------------- | ----- |
| platform | `samples/*/copier-answers.yml`            | add/extend GraphQL-enabled sample (PL-T02\*) | ☐     |
| py       | `template/files/python/**/graphql_api/**` | PY-T03 dual-gate after sample exists         | ☐     |

## Verification evidence

| stage    | command                                         | result         |
| -------- | ----------------------------------------------- | -------------- |
| policy   | contract already accepts graphql                | no COORD edit  |
| residual | `goals/riso-lanes-assurance/residuals/COORD.md` | PLATFORM owner |

## Residual risks

- Matrix may under-exercise GraphQL until PLATFORM answers land.
