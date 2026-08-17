# W5-CLOSE-WEB — wizard dest lockstep

- Wave: CLOSE-WEB
- Lane: WEB
- Exclusive writes: `web/src/**`, `web/e2e/**`, `web/tests/**`, this file
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main`
- HEAD: `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Date: 2026-08-14
- Status: **green** (no remaining P0/P1 in the WEB lock)
- Residual: none (`residuals/WEB.md` not created)
- `samples/*/render/**` writes: **0**
- Lockfile / secrets / `riso-mcp`: **0**
- Foreign-tree writes: **0** (`samples/metadata/matrix-data.json` was not created)

## Method

Read `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/*.md` first. Re-read live wizard + Copier dest files (not W2-WEB-join / W5-AUDIT-wizard claims). Confirmed cwd via `git rev-parse --show-toplevel`. Stayed on `main`. Did not commit, tag, push, or start/kill `render_matrix.py`.

## Lock P0/P1

### WIZ-P1-lucia-dest — **closed**

Live Copier dest (`template/copier.yml` `saas_auth_provider`) is `clerk` | `authjs` only (help has no Lucia). Python + TS remap tables omit lucia from `SAAS_AUTH_PROVIDERS` / `_SAAS_AUTH_PROVIDERS`. Wizard still published dest `lucia` via stale `web/src/data/matrix-data.json` (`generated_at` 2026-07-11) plus hardcoded fallback/union/copy.

| Surface | After |
| --- | --- |
| `RisoConfig.saas_auth_provider` | `'clerk' \| 'authjs'` (`web/src/lib/store.ts`) |
| SaaSConfig fallback/labels | `['clerk', 'authjs']` — no lucia |
| validation cost row | lucia branch removed |
| ContextualCard | clerk / Auth.js only |
| Demo marketing | `Clerk or Auth.js` |
| `matrix-data.json` | regenerated from live `copier.yml`; dest choices `clerk`, `authjs`; help has no Lucia; `openspec_extra` default `disabled`; `task_runner` default `just` |
| leftover `saas_auth: lucia` | still unmapped → fail-closed (not remapped to dest) |

Regen wrote **only** `web/src/data/matrix-data.json` (reused `scripts/ci/generate_matrix_data.py` helpers; did **not** call `main()`, did **not** write `samples/metadata/matrix-data.json`).

## Seeded contracts (re-verified live)

| Contract | Verdict | Live |
| --- | --- | --- |
| TS remap twin == Python 8-key SSOT | **green** | Same 8 keys/ops; `SAAS_AUTH_PROVIDERS = {clerk, authjs}`; apply then reject; no dest overwrite |
| Import remaps then fail-closed | **green** | `api.importConfig`, `importPresetYAML`, `parseShareableURL` / share parse, `updateConfig` all `applyThenRejectRemovedKeys` |
| Export never emits old keys | **green** | `configToCopierArgs` / `generateYamlConfig` / `api.exportConfig` / `exportPresetYAML` remap then drop `REMOVED_ANSWER_KEYS` |
| Presets canonical | **green** | `PRESETS` dest keys only; no `"lucia"` dest |
| OpenSpec off / `task_runner=just` | **green** | `defaultRisoConfig` + live matrix defaults |

`saas_auth: lucia` remains an intentional leftover fail-close. It is **not** a dest alias.

## Tests

```text
pnpm --dir web run test:run
 Test Files  14 passed (14)
      Tests  308 passed (308)
```

New/adjusted:

- `web/src/__tests__/matrixData.test.ts` — dest choices clerk\|authjs; no lucia help; defaults clerk / just / OpenSpec off
- `store.test.ts` — dest default clerk; serialized defaults have no lucia
- `exportConfig.test.ts` — leftover `saas_auth: lucia` throws; dest export of clerk has no lucia
- `presets.canonical.test.ts` — no dest lucia
- `removedAnswerKeys.test.ts` — leftover lucia stays on old key (no dest write)

Prettier + eslint on touched TS/TSX: exit 0.

## Path lock (this session)

| Class | Count |
| --- | --- |
| WEB product + tests | 11 |
| GOAL evidence | 1 (`W5-CLOSE-WEB.md`) |
| `samples/*/render/**` | 0 |
| `samples/metadata/**` | 0 |
| lockfiles | 0 |

This-session product files: `store.ts`, `validation.ts`, `SaaSConfig.tsx`, `ContextualCard.tsx`, `Demo.tsx`, `matrix-data.json`, plus the five test files listed above.

## Not WEB

Foreign P0/P1s in the seed JSON (`PAY-*`, `NODE-*`, `GATES-*`, `MS-*`, `RES-*`, default dest, refine-stop) stay with their owners. Not edited here.
