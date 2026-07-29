# PL-T01 — COORD outbox keys vs sample answers

**Wave:** W3 PLATFORM\
**Generated:** 2026-07-28

## COORD outbox change-ids reviewed

| change_id                        | status              | answer-key impact for PLATFORM                                                  |
| -------------------------------- | ------------------- | ------------------------------------------------------------------------------- |
| `coord-mcp-languages-typescript` | applied             | `mcp_languages` may include `typescript` — `samples/mcp-typescript` already set |
| `COORD-go-version-mcp`           | applied             | `go_version` when go in mcp — `samples/go-mcp` already has `go_version: "1.24"` |
| `COORD-rust-module-excludes`     | applied             | no new keys; enables lean rust samples (PL-T03)                                 |
| `exclude-empty-dirs`             | applied             | no answer keys                                                                  |
| `api-features-normalize`         | applied             | **`api_features` must be list** (not scalar `none` / comma-string)              |
| `graphql-sample-coverage`        | residualed→PLATFORM | enable GraphQL on primary matrix sample(s)                                      |
| `bootstrap-verify`               | applied             | n/a                                                                             |

## Pre-patch inventory (top-level `samples/*/copier-answers.yml`)

| sample               | `api_features` before        | action                                      |
| -------------------- | ---------------------------- | ------------------------------------------- |
| api-monorepo         | `none` (string)              | → `[]`                                      |
| api-python           | `none` (string)              | → `[]`                                      |
| changelog-full-stack | `graphql,websocket` (string) | → `[graphql, websocket]`                    |
| changelog-monorepo   | `none` (string)              | → `[]`                                      |
| changelog-python     | `none` (string)              | → `[]`                                      |
| circleci-node        | `none` (string)              | → `[]`                                      |
| docs-docusaurus      | `none` (string)              | → `[]`                                      |
| docs-fumadocs-full   | `none` (string)              | → `[]`                                      |
| docs-sphinx          | `none` (string)              | → `[]`                                      |
| full-stack           | `websocket` (string)         | → `[graphql, websocket]` (GraphQL coverage) |
| gitlab-ci-python     | `none` (string)              | → `[]`                                      |
| go-api               | `none` (string)              | → `[]`                                      |
| *(11 others)*        | key absent or N/A            | no change                                   |

## Missing sample variants (handoff)

| handoff                            | gap                                   | PL task                        |
| ---------------------------------- | ------------------------------------- | ------------------------------ |
| `PLATFORM-rust-samples`            | no `samples/rust-{api,cli,mcp}`       | PL-T03 create answers          |
| `graphql-sample-coverage`          | only changelog-full-stack had graphql | PL-T02 full-stack gets graphql |
| `PLATFORM-go-api-features-answers` | go-api scalar                         | PL-T02 list normalize          |
| `QUAL-go-template-tests`           | optional test asserts                 | PL-T04                         |

## Invented keys

**None.** Only shapes/values for existing COORD keys (`api_features` list tokens `graphql`/`websocket`; rust module language choices already in copier.yml).
