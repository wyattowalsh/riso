# NODE handoffs (W2)

## Open / forwarded

### PLATFORM — `api_features` multiselect answers

- **Problem:** Several Node-related samples fail `riso validate` with `api_features: expected list for multiselect` because answers still use scalar `api_features: none`.
- **Evidence:** `goals/riso-lanes-assurance/evidence/W2-NODE-docs-docusaurus.json` (same for docs-fumadocs-full, circleci-node).
- **Owner:** PLATFORM (exclusive answers root).
- **Suggested fix:** `api_features: []` or explicit feature list; re-run validate then matrix.

## Closed / not needed

- COORD `coord-mcp-languages-typescript` already applied (W1-H01); NODE TS MCP payload updated in-lane.
- No new Copier keys required for NODE correctness fixes.
