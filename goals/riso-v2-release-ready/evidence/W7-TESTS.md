# W7-TESTS — payload P0/P1 contract locks

- **Wave:** W7 / PAYLOAD tests
- **Task:** lock dest-root Node script aliases, GHA/GitLab typecheck filters, SaaS client barrels, nested SaaS CI pins
- **Lane:** tests only (exclusive write `tests/unit/test_node_templates.py`, create `tests/unit/test_saas_template_clients.py`, this file)
- **Date (UTC):** 2026-08-18T10:05:45Z
- **Repo:** `/Users/ww/dev/projects/riso`
- **Branch:** `main`
- **HEAD:** `e4029ca8d8213a896bd9ca841525ce4d73bbca19` (worktree dirty; this session did not commit)
- **Product / template writes:** 0
- **`samples/*/render/**` writes:** 0
- **Lockfile / secrets / tag / push:** 0
- **Status:** **green** — 36 passed

## Sibling wait

Polled product files three times (read, not sleep-loop). All four sibling surfaces were present before the assertions were written:

| Surface                                 | Live at write time                                                                     |
| --------------------------------------- | -------------------------------------------------------------------------------------- |
| Dest-root `package.json.jinja`          | Node-API-gated `"typecheck"` / `"type-check"` → `pnpm --filter api-node run typecheck` |
| `riso-quality.yml.jinja` `node-quality` | `pnpm --filter api-node` lint / typecheck / test                                       |
| `.gitlab/.gitlab-ci.yml.jinja`          | per-surface `--filter` / `--dir`; no dest-root `pnpm run typecheck`                    |
| SaaS `lib/database/client.ts.jinja`     | untracked; exports `prisma` and `db`                                                   |
| SaaS `lib/auth/helpers.ts.jinja`        | untracked; `export * from '@/integrations/auth/helpers'`                               |
| Nested SaaS `ci.yml.jinja`              | `PNPM_VERSION: '9'`; `pnpm run typecheck`                                              |

Sibling evidence already on disk: `W7-NODE-CI-GHA.md`, `W7-SAAS-GHA.md`.

## Added

Extended `tests/unit/test_node_templates.py` (kept pylint disable header; added helper docstrings). Created `tests/unit/test_saas_template_clients.py` so SaaS client/CI locks stay out of the Node docs/api-node file.

| Contract                                 | Assertion                                                                                                                                                               |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dest-root type-check / typecheck aliases | Rendered Node-API `package.json` scripts both equal `pnpm --filter api-node run typecheck`                                                                              |
| Dest-root docs-only                      | fumadocs dest-root scripts omit `type-check` / `typecheck`                                                                                                              |
| GHA `node-quality`                       | source job + rendered workflow use `--filter api-node` for lint / typecheck / test; dest-root `pnpm run type-check` / `pnpm run lint` / `pnpm test` absent from the job |
| GitLab dest-root typecheck               | source has no `pnpm run typecheck`; fumadocs-only / saas-only / Node-API renders stay filtered (`docs-fumadocs`, `--dir node/saas`, `api-node`)                         |
| SaaS `lib/database/client.ts.jinja`      | file exists; source exports `prisma` and `db`; prisma render exports `{ prisma }`; drizzle render exports `const db` + live schema path                                 |
| SaaS `lib/auth/helpers.ts.jinja`         | file exists; source + render re-export `@/integrations/auth/helpers`                                                                                                    |
| Nested SaaS `ci.yml.jinja`               | `PNPM_VERSION: '9'`; `pnpm run typecheck` present; `pnpm run type-check` absent (source + render)                                                                       |

## Verify

```text
uv run pytest tests/unit/test_node_templates.py tests/unit/test_saas_template_clients.py -q -n 0
# 36 passed in 0.31s

uv run ruff check tests/unit/test_node_templates.py tests/unit/test_saas_template_clients.py
# All checks passed!

uv run ruff format --check tests/unit/test_node_templates.py tests/unit/test_saas_template_clients.py
# 2 files already formatted

uv run pylint --rcfile=pyproject.toml tests/unit/test_node_templates.py tests/unit/test_saas_template_clients.py
# Your code has been rated at 10.00/10
```

**Pass count: 36 passed / 0 failed / 0 skipped.** (18 prior Node docs/api-node tests + 8 dest-root/GHA/GitLab + 9 SaaS)

## Path lock

| Class                     | Count                                                                           |
| ------------------------- | ------------------------------------------------------------------------------- |
| Product / template writes | 0                                                                               |
| Test writes               | `tests/unit/test_node_templates.py`, `tests/unit/test_saas_template_clients.py` |
| Evidence                  | this file                                                                       |
| `residuals/**`            | 0                                                                               |
| `samples/*/render/**`     | 0                                                                               |

## Not this lane

- Editing dest-root `package.json.jinja`, GHA, GitLab, or SaaS product templates
- Official dest re-render
- Commit / tag / push
