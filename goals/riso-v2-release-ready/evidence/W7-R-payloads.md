# W7 — Payloads review of dest-root Node CI + SaaS clients

- Date: 2026-08-18
- Surface: payloads (source only)
- Status: **no remaining P0** on the W6-R2 payloads findings

## W6-R2 disposition

| id                               | Verdict                                                                                                                                                                    |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PAY-P0-dest-root-node-ci-scripts | **fixed** — dest-root `typecheck`/`type-check` aliases (Node API only); GHA uses `--filter api-node`; GitLab/Circle per-surface filters; no dest-root `pnpm run typecheck` |
| PAY-P0-saas-next-missing-modules | **fixed** — `lib/database/client.ts.jinja` (prisma+drizzle) and `lib/auth/helpers.ts.jinja` re-export                                                                      |
| PAY-P1-saas-nested-gha           | **fixed in place** — `PNPM_VERSION` 9; `typecheck`; e2e.yml also 9. Nested file still not dest-root loadable (known; COORD)                                                |

## P0

None after live re-read of the files listed above.

## P1

None new. Nested SaaS GHA still ships under `node/saas/.github/` (GHA dest-root will not load it). Not a contract break of the 2.0 remap/ladder.

## Tests

`uv run pytest tests/unit/test_node_templates.py tests/unit/test_saas_template_clients.py tests/unit/test_gitlab_ci_templates.py tests/unit/test_circleci_templates.py -q -n 0` — **62 passed**.
