# Residual — NODE (W2)

## Status

NODE exclusive payload correctness work completed under `template/files/node/**` except `node/saas/**`.

Three sample validates fail **only** because PLATFORM-owned answers use `api_features: none` (string) instead of a multiselect list. NODE must not edit `samples/*/copier-answers.yml`.

## Residuals

### R1 — PLATFORM answers shape (`api_features`)

| Field                | Value                                                                                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **owner**            | PLATFORM                                                                                                                                                                      |
| **task_ids**         | NODE-T06 (join validate) · PL-T02\*                                                                                                                                           |
| **blocking**         | No — does not block NODE payload tree; blocks full join sample matrix for some Node samples                                                                                   |
| **command**          | `uv run riso validate --answers-file samples/docs-docusaurus/copier-answers.yml --json`                                                                                       |
| **error (redacted)** | `api_features: expected list for multiselect`                                                                                                                                 |
| **also fails**       | `samples/docs-fumadocs-full/copier-answers.yml`, `samples/circleci-node/copier-answers.yml`                                                                                   |
| **green peers**      | `samples/docs-fumadocs/copier-answers.yml` ok:true · `samples/mcp-typescript/copier-answers.yml` ok:true                                                                      |
| **evidence**         | `goals/riso-lanes-assurance/evidence/W2-NODE-docs-docusaurus.json`, `W2-NODE-docs-fumadocs-full.json`, `W2-NODE-circleci-node.json`, `W2-NODE-summary.md`                     |
| **fix**              | PLATFORM: set `api_features: []` (or feature list) on affected answer files; never leave scalar `none` for multiselect keys. Align with W1 `api-features-normalize` contract. |

## NODE-owned work (not residual)

| Task                             | Result                                                                                |
| -------------------------------- | ------------------------------------------------------------------------------------- |
| NODE-T01 Fumadocs                | Green — docs env/status aligned with api-node; jinja OK                               |
| NODE-T02 Docusaurus              | Green payload; sample validate residualed to PLATFORM answers                         |
| NODE-T03 TS MCP                  | Green — httpStream host/port, tsup config, fastmcp/zod pins, zod record schemas       |
| NODE-T04 api-node                | Green — health test expects `healthy`; shared_logic imports used                      |
| NODE-T05 shared-config/workspace | Green — saas list entry retained; no saas content edits                               |
| NODE-T06 join validate           | Residualed (PLATFORM answers on 3 samples); core docs-fumadocs + mcp-typescript green |
| NODE-T07 refine                  | Done as correctness-only (no new product modules)                                     |

## Forbidden-path audit

- No NODE edits under `template/files/node/saas/**` (SAAS lane dirty files present from other lanes — not NODE)
- No edits to copier/hooks/macros/catalog/answers/lockfiles by NODE
