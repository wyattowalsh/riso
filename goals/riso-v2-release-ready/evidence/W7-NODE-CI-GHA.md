# W7-NODE-CI-GHA — dest-root Node CI scripts (GHA)

- Wave: W7 / PAYLOAD Node CI
- Task: close `PAY-P0-dest-root-node-ci-scripts` (GHA + dest-root package.json only)
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `e4029ca8d8213a896bd9ca841525ce4d73bbca19`
- Exclusive writes: `template/files/package.json.jinja`, `template/files/.github/workflows/riso-quality.yml.jinja`, `template/files/.github/workflows/riso-deps-update.yml.jinja`, this file
- `samples/*/render/**` writes: **0**
- Commits / tags / pushes: **0**
- Status: **source-closed**

## Finding

GHA `node-quality` / `update-node-deps` called dest-root `pnpm run lint`, `pnpm run type-check`, `pnpm test`. Dest-root `package.json` had no `type-check` / `typecheck`. Dest-root `lint` is `eslint --fix "**/*.{js,ts}"` with **no dest-root eslint config**, so it is not a valid Node API quality step. Workspace `api-node` already defines `lint` and `typecheck` as `tsc --noEmit -p tsconfig.json`.

## Change

1. Dest-root `package.json.jinja`: when `api_module == 'enabled'` and `'node' in api_languages`, add both aliases:
   - `"typecheck": "pnpm --filter api-node run typecheck"`
   - `"type-check": "pnpm --filter api-node run typecheck"`
     Existing dest-root `lint` kept. Node engine stays `>=20.0.0` (not 22).
1. `riso-quality.yml.jinja` `node-quality` (already Node-API gated): run
   `pnpm --filter api-node run lint`, `pnpm --filter api-node run typecheck`, `pnpm --filter api-node test`.
1. `riso-deps-update.yml.jinja` `update-node-deps`: same three filter commands. PR body matches.

GitLab / Circle not edited (sibling lock).

## Live (source)

| Path                         | After                                                                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Dest-root scripts, Node API  | L38–42 `dev`/`build`/`test` plus `typecheck`/`type-check` → `pnpm --filter api-node run typecheck`; L54 `lint` unchanged |
| Dest-root scripts, docs-only | no `typecheck` / `type-check`                                                                                            |
| Dest-root engines            | L88–89 `node: >=20.0.0`, `pnpm: >=9.0.0`                                                                                 |
| GHA `node-quality`           | L173–180 filter lint / typecheck / test; `node-version: '20'`                                                            |
| GHA `update-node-deps`       | L96–99 same three commands; `node-version: '20'`                                                                         |

`api-node` (`template/files/node/apps/api-node/package.json.jinja`, not this lock): `"lint"` / `"typecheck"` = `tsc --noEmit -p tsconfig.json`.

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # e4029ca8d8213a896bd9ca841525ce4d73bbca19
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/package.json.jinja \
  template/files/.github/workflows/riso-quality.yml.jinja \
  template/files/.github/workflows/riso-deps-update.yml.jinja
# Validated 3 Jinja template(s): all OK
# throwaway jinja render (not dest): Node API dest-root JSON has both aliases
#   → pnpm --filter api-node run typecheck; lint stays eslint --fix; engines.node >=20
#   docs-fumadocs dest-root has no typecheck/type-check
#   node-quality + update-node-deps use filter lint/typecheck/test; dest-root
#   pnpm run lint / type-check / pnpm test absent; node-version 20; node 22 absent
git status --short -- 'samples/*/render/**'   # empty
```

## Residuals (not this lock)

| Residual                                                                  | Disposition                                                 |
| ------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Official Node dest workflows still dest-root `pnpm run type-check`        | PLATFORM re-render only; do not hand-edit dest              |
| GitLab / Circle dest-root Node jobs                                       | sibling agent; out of this exclusive write                  |
| Dest-root `lint` remains `eslint --fix` with no dest-root eslint config   | kept on purpose; GHA no longer uses it for Node API quality |
| Dest-root `typecheck` alias unused by GHA (GHA calls `--filter` directly) | kept for GitLab `typecheck` / local `pnpm run type-check`   |

## Path lock

| Class                                   | Count                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| Product write                           | 3 — dest-root `package.json.jinja`, `riso-quality.yml.jinja`, `riso-deps-update.yml.jinja` |
| Evidence                                | this file                                                                                  |
| `samples/*/render/**`                   | 0                                                                                          |
| GitLab / Circle                         | 0                                                                                          |
| Lockfile / secret / commit / tag / push | 0                                                                                          |

## Verdict

```yaml
id: PAY-P0-dest-root-node-ci-scripts
status: source-closed
files:
  - template/files/package.json.jinja
  - template/files/.github/workflows/riso-quality.yml.jinja
  - template/files/.github/workflows/riso-deps-update.yml.jinja
summary: >
  Dest-root package.json now exposes typecheck and type-check aliases
  that delegate to api-node. GHA node-quality and update-node-deps run
  pnpm --filter api-node lint/typecheck/test instead of dest-root eslint
  --fix and a missing type-check script. Node stays 20.
```
