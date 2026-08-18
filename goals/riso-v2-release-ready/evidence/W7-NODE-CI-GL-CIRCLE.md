# W7-NODE-CI-GL-CIRCLE — dest-root Node CI (GitLab + Circle)

- Wave: W7 / PAY-P0 dest-root Node CI
- Task: close GitLab + Circle dest-root `typecheck` / `test` / `build` on Node jobs
- Date: 2026-08-18
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `e4029ca8d8213a896bd9ca841525ce4d73bbca19`
- Exclusive writes: `template/files/.gitlab/.gitlab-ci.yml.jinja`, `template/files/.circleci/config.yml.jinja`, this file
- `samples/*/render/**` writes: **0**
- Commits / tags / pushes: **0**
- Status: **source-closed**

## Finding

`lint:node` / `lint-node` / `test:node` / `test-node` / `build:node` / `build-node` emitted when fumadocs, docusaurus, saas, **or** Node API was on, then invoked dest-root `pnpm run typecheck` / `pnpm run test` / `pnpm run build`.

Dest-root `package.json.jinja` does not define those scripts unless Node API is on (`test` / `build` are `api-node` filters; dest-root `typecheck` is absent here — GHA sibling may add it later). Official `gitlab-ci-python` is Python API + fumadocs + `ci_platform: gitlab-ci` (`saas_infra_module` defaults `disabled`). That dest would emit `lint:node` and fail on dest-root `typecheck`, and must not run `api-node` typecheck.

## Change

Split Node job **commands** by enabled surface. Keep job names. Keep Node 20 (`node:20-alpine`, `cimg/node:20.18`). Do not retarget GHA or dest-root / SaaS `package.json`.

| Surface    | Lint                                                                          | Test                                          | Build                              |
| ---------- | ----------------------------------------------------------------------------- | --------------------------------------------- | ---------------------------------- |
| Node API   | `pnpm --filter api-node run lint` + `typecheck`                               | `pnpm --filter api-node test`                 | `pnpm --filter api-node run build` |
| Fumadocs   | `pnpm --filter docs-fumadocs run lint` + `typecheck`                          | (none — `pages` / `build-docs` already build) | (none)                             |
| Docusaurus | `pnpm --filter docs-docusaurus run lint` + `typecheck`                        | (none)                                        | (none)                             |
| SaaS       | `pnpm --dir node/saas run lint` + `typecheck` (`typecheck`, not `type-check`) | `pnpm --dir node/saas test`                   | `pnpm --dir node/saas run build`   |

`test:*` / `build:*` emit only when Node API or SaaS is on. Circle workflow matches (`test-node` / `build-node` require lint only when those jobs exist). W6 rust/go cwd (`cd rust` / `cd go` / `working_directory:`) left untouched.

## Live (throwaway Jinja render + `yaml.safe_load`)

| Case                                       | lint                                  | test / build                   | dest-root `pnpm run typecheck` |
| ------------------------------------------ | ------------------------------------- | ------------------------------ | ------------------------------ |
| `gitlab-ci-python` (python API + fumadocs) | `docs-fumadocs` lint + typecheck only | **absent**                     | **absent**; **no** `api-node`  |
| `circleci-node` (node API + fumadocs)      | api-node + docs-fumadocs              | api-node only                  | absent                         |
| node-API-only (GL/Circle)                  | api-node                              | api-node                       | absent                         |
| docusaurus-only (GL/Circle)                | docs-docusaurus                       | **absent**                     | absent                         |
| saas-only (GL/Circle)                      | `--dir node/saas` lint + typecheck    | `--dir node/saas` test / build | absent                         |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
git rev-parse HEAD              # e4029ca8d8213a896bd9ca841525ce4d73bbca19
uv run python scripts/ci/validate_jinja_templates.py \
  template/files/.gitlab/.gitlab-ci.yml.jinja \
  template/files/.circleci/config.yml.jinja
# Validated 2 Jinja template(s): all OK
uv run pytest tests/unit/test_gitlab_ci_templates.py tests/unit/test_circleci_templates.py -q -n 0
# 26 passed
# throwaway renders above all yaml.safe_load OK
# gitlab-ci-python lint:node.script = docs-fumadocs only; no test:node/build:node
git status --short -- 'samples/*/render/**'   # empty
```

## Residuals (not this lock)

| Residual                                                                | Disposition                                                     |
| ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| GHA `riso-quality` / `riso-deps-update` dest-root `pnpm run type-check` | sibling lock; not edited                                        |
| Dest-root `package.json.jinja` `typecheck` / `type-check` aliases       | sibling lock; not edited                                        |
| GitLab/Circle `pnpm run test:e2e` still dest-root                       | SaaS e2e; dest-root has no `test:e2e`; out of this lock         |
| GitLab/Circle fumadocs pages `pnpm run docs:build`                      | dest-root script exists when fumadocs is on; already path-fixed |
| Official dests not re-rendered                                          | regenerate-only via `scripts/render-samples.sh` / PLATFORM      |

## Path lock

| Class                                   | Count                                                            |
| --------------------------------------- | ---------------------------------------------------------------- |
| Product write                           | 2 — `.gitlab/.gitlab-ci.yml.jinja`, `.circleci/config.yml.jinja` |
| Evidence                                | this file                                                        |
| `samples/*/render/**`                   | 0                                                                |
| Lockfile / secret / commit / tag / push | 0                                                                |

## Verdict

```yaml
id: PAY-P0-dest-root-node-ci-gl-circle
status: source-closed
files:
  - template/files/.gitlab/.gitlab-ci.yml.jinja
  - template/files/.circleci/config.yml.jinja
summary: >
  GitLab/Circle Node jobs no longer call dest-root typecheck/test/build.
  Commands are per-surface (api-node filter, docs-* filter, --dir node/saas).
  gitlab-ci-python (fumadocs + Python API) runs only docs-fumadocs lint+typecheck.
```
