# Residual — NODE (W2)

## Status

NODE exclusive payload correctness work completed under `template/files/node/**` except `node/saas/**`.

W2 join-validate residual for scalar `api_features: none` is **historical / closed**. PLATFORM list-normalized sample answers in W3. Rechecked 2026-08-18: `docs-docusaurus`, `docs-fumadocs-full`, and `circleci-node` use `api_features: []`. NODE must not edit `samples/*/copier-answers.yml`.

**Active bar residual (not NODE-owned):** PLATFORM R1 full `render_matrix` — [`PLATFORM.md`](./PLATFORM.md). See [`ASSURANCE.md`](../ASSURANCE.md).

## Residuals

### R1 — PLATFORM answers shape (`api_features`) — **CLOSED (W3)**

| Field                | Value                                                                                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **status**           | historical / closed                                                                                                                                                           |
| **owner**            | PLATFORM                                                                                                                                                                      |
| **task_ids**         | NODE-T06 (join validate) · PL-T02 / PL-T05                                                                                                                                    |
| **blocking**         | No — W3 answers list-normalize landed; 37/37 validate green                                                                                                                   |
| **applied**          | PLATFORM commit `0327b1b`. Recheck: `samples/docs-docusaurus`, `docs-fumadocs-full`, `circleci-node` are `api_features: []` (not scalar `none`).                               |
| **green peers**      | `samples/docs-fumadocs/copier-answers.yml` · `samples/mcp-typescript/copier-answers.yml`                                                                                      |
| **evidence**         | [`ASSURANCE.md`](../ASSURANCE.md) fact #12 · `evidence/W5-validate-37.json` (37/37) · `evidence/W3-PL-T05-validate-summary.json` · `evidence/W3-PL-T01-answers-diff.md` · historical W2: `W2-NODE-docs-docusaurus.json`, `W2-NODE-docs-fumadocs-full.json`, `W2-NODE-circleci-node.json`, `W2-NODE-summary.md` |

## NODE-owned work (not residual)

| Task                             | Result                                                                                |
| -------------------------------- | ------------------------------------------------------------------------------------- |
| NODE-T01 Fumadocs                | Green — docs env/status aligned with api-node; jinja OK                               |
| NODE-T02 Docusaurus              | Green payload; sample validate residualed then closed by W3 answers                   |
| NODE-T03 TS MCP                  | Green — httpStream host/port, tsup config, fastmcp/zod pins, zod record schemas       |
| NODE-T04 api-node                | Green — health test expects `healthy`; shared_logic imports used                      |
| NODE-T05 shared-config/workspace | Green — saas list entry retained; no saas content edits                               |
| NODE-T06 join validate           | Closed by PLATFORM answers (37/37); core docs-fumadocs + mcp-typescript already green |
| NODE-T07 refine                  | Done as correctness-only (no new product modules)                                     |

## Forbidden-path audit

- No NODE edits under `template/files/node/saas/**` (SAAS lane dirty files present from other lanes — not NODE)
- No edits to copier/hooks/macros/catalog/answers/lockfiles by NODE
