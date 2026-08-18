# W7-SAAS-GHA — nested SaaS GHA honesty (pnpm 9 / `typecheck`)

- Wave: W7 / PAY-P1-saas-nested-gha
- Task: in-place honesty fix for nested SaaS GitHub Actions templates
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `3213419a450e37a6c268382b3dc4de74350b07f0`
- Exclusive writes: `template/files/node/saas/.github/workflows/ci.yml.jinja`, `template/files/node/saas/.github/workflows/database.yml.jinja`, this file
- Dest-root `.github/workflows/**` writes: **0** (COORD/GATES lock)
- `samples/*/render/**` writes: **0**
- Commits / tags / pushes: **0**
- Status: **source-closed** (honesty only; nested files remain unloadable)

## Finding

GitHub Actions only loads workflows from dest-root `.github/workflows/`. Nested copies under `template/files/node/saas/.github/workflows/` never run after Copier ships them as `node/saas/.github/workflows/`. COORD/GATES lock dest-root workflow creation, so this ticket does not relocate the files.

The nested files still ship and must not advertise the wrong package manager or script names.

Canonical SaaS pins (`template/files/node/saas/package.json.jinja`):

| Surface          | Live                                                                       |
| ---------------- | -------------------------------------------------------------------------- |
| `engines.pnpm`   | `>=9.0.0`                                                                  |
| `packageManager` | `pnpm@9.15.0`                                                              |
| type script      | `"typecheck": "tsc --noEmit"` (`validate` also calls `pnpm run typecheck`) |
| Node             | `>=20.0.0`                                                                 |

Before this write:

| File                     | Bug                                           |
| ------------------------ | --------------------------------------------- |
| `ci.yml.jinja` L16       | `PNPM_VERSION: '8'`                           |
| `ci.yml.jinja` L49       | `pnpm run type-check` (script does not exist) |
| `database.yml.jinja` L28 | `PNPM_VERSION: '8'` (no `type-check` call)    |
| both                     | `NODE_VERSION: '20'` already correct          |

## Change

In-place only. No dest-root workflow added or moved.

1. `PNPM_VERSION: '8'` → `'9'` in `ci.yml.jinja` and `database.yml.jinja`.
1. `pnpm run type-check` → `pnpm run typecheck` in `ci.yml.jinja` (single call, lint job).
1. Keep `NODE_VERSION: '20'`.
1. Scan of both files after edit: no remaining `type-check` script invocations and no remaining `PNPM_VERSION: '8'`. Job titles "Lint & Type Check" / step name "Type check" are English labels, not script names.

`e2e.yml.jinja` still has `PNPM_VERSION: '8'` and is **out of this exclusive write** (no `type-check` bug).

## Live (source)

| Path                        | After                                      |
| --------------------------- | ------------------------------------------ |
| `ci.yml.jinja` L15–16       | `NODE_VERSION: '20'` / `PNPM_VERSION: '9'` |
| `ci.yml.jinja` L49          | `run: pnpm run typecheck`                  |
| `database.yml.jinja` L27–28 | `NODE_VERSION: '20'` / `PNPM_VERSION: '9'` |
| `database.yml.jinja`        | no typecheck / type-check script calls     |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # 3213419a450e37a6c268382b3dc4de74350b07f0
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/node/saas/.github/workflows/ci.yml.jinja \
  template/files/node/saas/.github/workflows/database.yml.jinja
# Validated 2 Jinja template(s): all OK
rg -n "PNPM_VERSION|type-check|typecheck|NODE_VERSION" \
  template/files/node/saas/.github/workflows/ci.yml.jinja \
  template/files/node/saas/.github/workflows/database.yml.jinja
# ci + database: PNPM_VERSION '9', NODE_VERSION '20', one `pnpm run typecheck`, no type-check
rg -n "PNPM_VERSION|type-check|typecheck" \
  template/files/node/saas/.github/workflows/e2e.yml.jinja
# residual: PNPM_VERSION: '8' (out of lock)
git status --short -- 'samples/*/render/**'   # empty
```

## Residuals (not this lock)

| Residual                                                                                                                                       | Disposition                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Nested SaaS GHA still unloadable from dest-root                                                                                                | Honesty-only; dest-root workflow add/move is COORD/GATES lock |
| `template/files/node/saas/.github/workflows/e2e.yml.jinja` still `PNPM_VERSION: '8'`                                                           | Same class; no `type-check`; out of exclusive write           |
| Docs still say `pnpm run type-check` (`README.md.jinja`, `CONTRIBUTING.md.jinja`, `docs/TROUBLESHOOTING.md.jinja`, `docs/DEPLOYMENT.md.jinja`) | Docs-only; out of exclusive write                             |
| Official `samples/*/render/` dests remain stale until PLATFORM re-render                                                                       | Do not hand-edit dest                                         |

## Path lock

| Class                                   | Count                                    |
| --------------------------------------- | ---------------------------------------- |
| Product write                           | 2 — `ci.yml.jinja`, `database.yml.jinja` |
| Evidence                                | this file                                |
| Dest-root `.github/workflows/**`        | 0                                        |
| `samples/*/render/**`                   | 0                                        |
| Lockfile / secret / commit / tag / push | 0                                        |

## Verdict

```yaml
id: PAY-P1-saas-nested-gha
status: source-closed
files:
  - template/files/node/saas/.github/workflows/ci.yml.jinja
  - template/files/node/saas/.github/workflows/database.yml.jinja
summary: >
  Nested SaaS CI/database workflows now pin PNPM_VERSION 9 and call
  pnpm run typecheck. NODE_VERSION stays 20. Files still do not load
  from dest-root. Sibling e2e.yml.jinja still pins pnpm 8 (out of lock).
```
