# W2 SAAS join — summary

- Wave: W2 / lane SAAS
- Barrier: W1-OUT (read; COORD outbox `generation-gates-saas-auth` honored — no leftover `saas_auth` collector)
- Status: **green**
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso` · branch `main` · HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (no checkout / stash / reset / commit / tag / push)
- Exclusive writes only: `template/files/node/saas/**`, `template/files/saas-starter/**`, `goals/riso-v2-release-ready/evidence/W2-SAAS-*`
- `samples/*/render/**` writes: **0**
- Residual: none (`residuals/SAAS.md` not required)

## Tasks

| ID | Verify | Status |
| --- | --- | --- |
| SAAS-T01 | `runtime/nextjs` exists | green |
| SAAS-T02 | `runtime/remix` exists | green |
| SAAS-T03 | no mixed Next+Remix at `node/saas` root | green (W2 join key) |
| SAAS-T04 | token/a11y polish; no new vendor/runtime/host | green |

## Commands

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git branch --show-current       # main
test -d template/files/node/saas/runtime/nextjs
test -d template/files/node/saas/runtime/remix
# flatten probes at node/saas root: all ABSENT
find template/files/node/saas template/files/saas-starter -type f -name '*.jinja' -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 197 Jinja template(s): all OK
git status --short -- 'samples/*/render/**'   # empty
```

## Foreign trees

Not written: `copier.yml`, hooks, `samples/**/copier-answers.yml`, `src/riso/**`, `web/**`, `uv.lock`, `pnpm-lock.yaml`.

## Remap contract

Lane does not implement remaps. Templates use canonical keys (`saas_infra_module`, `saas_auth_module` / `saas_auth_provider`, `saas_search_provider`). No leftover `saas_auth` / `saas_billing` / `include_admin` / `saas_starter_module` reads in owned trees.
