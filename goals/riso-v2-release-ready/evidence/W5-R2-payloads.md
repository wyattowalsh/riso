# W5-R2 — Review pass 2, surface=payloads

- Date: 2026-08-18
- Mode: independent re-read of live jinja/hooks (pass 1 untrusted)
- Status: **no new P0 / no new P1** on the required contract. Pass-1 items are fixed in source.

## Pass 1 disposition

| id                                 | Verdict   | Live evidence                                                                                     |
| ---------------------------------- | --------- | ------------------------------------------------------------------------------------------------- |
| PAY-P0-fumadocs-static-metadata    | **fixed** | `robots.ts.jinja` / `sitemap.ts.jinja` export `dynamic = 'force-static'` and `revalidate = false` |
| PAY-P0-gha-matrix-ungated-python   | **fixed** | `riso-matrix.yml.jinja` gates `matrix-test`; else `scaffold-ok`                                   |
| PAY-P0-gha-deps-ungated-python     | **fixed** | `riso-deps-update.yml.jinja` gates `update-python-deps` + `scaffold-ok`                           |
| PAY-P0-gitlab-pages-docs-path      | **fixed** | `mv node/docs/fumadocs/out public/`                                                               |
| PAY-P0-circle-pages-docs-path      | **fixed** | same dest path                                                                                    |
| PAY-P1-uv-root-gitlab / circle     | **fixed** | `uv --directory python sync` and ruff/ty/pylint                                                   |
| PAY-P1-quality-just-python-ungated | **fixed** | `justfile.quality.jinja` `_python` gate                                                           |
| PAY-P0-06 MCP pytest path          | **fixed** | `working-directory: python` + `tests/test_mcp.py`                                                 |

## P0

None new after inspection.

## P1

None new that reset refine-stop. SaaS `@/db/schema` imports remain only on drizzle-gated admin pages / docs examples (not official default-smoke). Nested fumadocs deploy workflow is unused by GHA (repo-root workflows only).

## Strengths

Hooks apply-then-reject. Generated Node 20. OpenSpec extra off + `EMPTY_SCAFFOLD_DIRS` includes `openspec`. SaaS `runtime/{nextjs,remix}` unflattened. hypothesis + respx extras and shipped tests.
