# W5-AUDIT-wizard — read-only review

- Task: `AUDIT-wizard`
- Wave: W5
- Lane: **wizard** (inspect-only; this file only)
- Surface: `web/src` remap twin, YAML import, export, presets, store defaults
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `.git/HEAD` read hook-denied; `.git/refs/heads/main` = `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (matches `ASSURANCE.md` / `W3-PL-T10-ssot.txt`)
- Date: 2026-08-14
- Product-code writes: **0**
- `samples/*/render/**` writes: **0**
- Lockfiles / secrets / `riso-mcp`: **0**
- Status: **one live P1** (lucia dest lockstep). Mission remap/import/export/preset/default contracts are green in the live tree.

## Method

Read `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/*.md` first. Then read live files (not W2-WEB-join or memory). No shell (`git rev-parse` / `pnpm` / `uv run` not available in this session). Compared TS twin line-by-line to `src/riso/core/removed_answer_keys.py` and `src/riso/core/answers.py`.

## Remap contract (live)

Apply then reject. No dest overwrite. Idempotent. No dual-path aliases after remap.

| Surface | Live |
| --- | --- |
| Python SSOT | `src/riso/core/removed_answer_keys.py` `apply_removed_key_remaps` + `answers.py` `reject_removed_answer_keys` |
| TS twin | `web/src/lib/removedAnswerKeys.ts` `applyRemovedKeyRemaps` then `applyThenRejectRemovedKeys` |
| 8 keys | `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin` |
| Ops | derive / wrap-list / derive / wrap-list / rename / split / split / rename-bool |
| Dest write | `writeDests` / `_write_dests`: skip if dest key already in `out`; still record `after[key] = out[key]`; delete old key only after a successful map |
| lucia as **old** `saas_auth` | fail-closed (not in `SAAS_AUTH_PROVIDERS` / `_SAAS_AUTH_PROVIDERS`) |
| lucia as **dest** `saas_auth_provider` | Copier dropped it; wizard still offers it — **P1** below |

`scripts/ci/check_removed_key_ssot.py` parses the TS tables statically. Historical `evidence/W3-PL-T10-ssot.txt` exit 0. Twin tables still match that expected 8-key set.

## Mission checklist

| Item | Verdict | Live evidence |
| --- | --- | --- |
| Remap twin == Python SSOT | **closed** | Same 8 keys, same ops, same mapper sets, same no-overwrite `writeDests`, same apply-then-leave-unmapped |
| Import YAML then fail-closed | **closed** | `api.importConfig`, `importPresetYAML`, `parseShareConfigPayload` all `applyThenRejectRemovedKeys`. UI: `CustomPresetsSection` + `App.tsx` share URL. Tests + `web/tests/e2e/import-remap.spec.ts` leftover error |
| Export never emits old keys | **closed** | `configToCopierArgs` / `generateYamlConfig` / `api.exportConfig` / `exportPresetYAML` remap then delete `REMOVED_ANSWER_KEYS`. Review tab uses `generateYamlConfig`. CLI snippet is `uv run riso copy <dest> --answers-file copier-answers.yml` (no `--data`, no `{{outputDir}}`) |
| Presets canonical | **closed** | `PRESETS` configs use dest keys only (`saas_infra_module`, `saas_auth_provider: clerk`, `mcp_languages: ['typescript']`). `presets.canonical.test.ts` + no old-key literals in `presets.tsx` / `presets.ts` |
| Store defaults `task_runner=just`, OpenSpec off | **closed** | `defaultRisoConfig` `fromMatrix(..., 'just')` / `fromMatrix(..., 'disabled')`. Matrix `defaults.task_runner` is `just`. `openspec_extra` is missing from stale matrix → fallback `'disabled'`. `store.test.ts` asserts both + no `mypy` |

## Inspected (not elevated)

- **Persist / custom-preset JSON hydrate** uses `dropLeftoverRemovedKeys` (`store.ts` `canonicalizeConfig`, `configSchemas.ts` `parseCustomPresetsStorage`). Comment: hydration, never throw. YAML import and `updateConfig` still fail-closed. Not an import-path hole.
- **`api.exportConfig`** stringifies remapped answers as-is. Official Review download is `generateYamlConfig` → `configToCopierArgs`, which also rewrites `api_features` comma tokens to a Copier list. WEB-T03 (no old keys) holds on both paths.
- **Hero.tsx** still demos `--data` key=value. Live CLI still accepts `--data`. Review export command is `--answers-file`.
- **`riso copy` has no `--defaults` flag** (`src/riso/cli/app.py` / `commands/copy.py`). Pass-1 “missing `--defaults`” is stale.
- **Pass-1 include_docker / include_github_actions / shared/types.ts / toCopierAnswers** — gone from `web/src`.
- **Share-URL leftovers** — `parseShareableURL` throws; `App.tsx` renders `Share URL rejected:`.
- **`saas_admin_dashboard` / `openspec_extra` UI** — present (`SaaSConfig.tsx`, `ProjectBasics.tsx`). FileTreePreview always adds `mise.toml`; it does not preview `openspec/` (preview DX, not answers).
- **CLI languages** python/rust/go only. TypeScript is MCP-only. Docs frameworks fumadocs / docusaurus / sphinx-shibuya (no MkDocs, no `none`).
- No `config.api_tracks` (etc.) dual-path reads in `web/src`.
- W2-WEB-join (2026-08-13) claimed WEB green; this pass re-read the tree. Remap/import/export/preset/default claims still hold. Lucia dest was not in that join.

## Open P1

### WIZ-P1-lucia-dest

Wizard still publishes `saas_auth_provider=lucia`. Live Copier does not.

| Field | Value |
| --- | --- |
| owner | WEB (`web/src/**`); matrix regen via `uv run python scripts/ci/generate_matrix_data.py` (PLATFORM if that script is locked) |
| files | `web/src/data/matrix-data.json` L1449–1458 and L2041; `web/src/components/steps/SaaSConfig.tsx` L231–242; `web/src/lib/store.ts` L127; `web/src/lib/validation.ts` L600–608; `web/src/components/sidebar/ContextualCard.tsx` L153–154; `web/src/pages/Demo.tsx` L285 |
| Copier SSOT | `template/copier.yml` `saas_auth_provider` choices = `clerk`, `authjs` only (L1337–1347). Remap tables (Py + TS) also omit lucia |
| why P1 | User can pick lucia; `generateYamlConfig` emits `saas_auth_provider: lucia`; `riso validate` / `riso copy` fail. Default remains `clerk`, so the happy path is fine. Not a removed-**key** emit |
| root | `matrix-data.json` `generated_at` = `2026-07-11`; no `openspec_extra` prompt/default in that blob. `buildChoiceOptions` prefers matrix choices, then hardcoded `fallbackChoices` that still list lucia |
| fix | Drop lucia from store union, SaaSConfig fallback/labels, validation, ContextualCard, Demo copy. Regen matrix from current `copier.yml`. Keep lucia as an **unmapped leftover** for old key `saas_auth: lucia` (already fail-closed) |

## Closed (mission strengths)

Recorded as `closed` findings in the JSON block so the five contracts stay visible.

## Writes

This evidence file only. No commit / tag / push. No `render_matrix` start/kill. No residuals file (`residuals/WEB.md` not created).
