# Answers drift audit

## Method

- Enumerated all `samples/*/copier-answers.yml` (23 files).
- Ran `uv run riso validate --answers-file … --json` (8-way parallel).
- Classified failures against published Copier contract (no invented keys).

## Initial failures (before PLATFORM fixes)

| Variant | Error | Class |
|---------|-------|-------|
| api-monorepo, api-python, changelog-*, circleci-node, docs-docusaurus, docs-fumadocs-full, docs-sphinx, full-stack, gitlab-ci-python, go-api | `api_features: expected list for multiselect` | PLATFORM_FIX |
| mcp-typescript | `mcp_languages: invalid choice 'typescript'` | COORD_HANDOFF |

## PLATFORM fixes applied

Converted legacy string `api_features` values to multiselect lists:

| Old | New |
|-----|-----|
| `none` | `[]` |
| `websocket` | `[websocket]` YAML list |
| `graphql,websocket` | list of both |

Variants updated (12): api-monorepo, api-python, changelog-full-stack, changelog-monorepo, changelog-python, circleci-node, docs-docusaurus, docs-fumadocs-full, docs-sphinx, full-stack, gitlab-ci-python, go-api.

## Post-fix validate

- OK: 22 / 23
- FAIL: mcp-typescript only → see outbox `coord-mcp-languages-typescript.md`

## Matrix decision

`MATRIX_REQUIRED=true` (answers files changed).
