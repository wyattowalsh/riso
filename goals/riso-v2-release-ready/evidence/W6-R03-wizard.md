# W6-R03 — Review, surface=wizard

- Task: `W6-R03`
- Wave: W6
- Lane: GOAL (inspect-only; this file only)
- Surface: wizard (`web/src/**`)
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-18
- Prior review blobs: untrusted. Re-read live `web/src/**` plus Python remap SSOT. `W5-R1-wizard.md` / `W5-R2-wizard.md` / `W5-CLOSE-WEB.md` / `W5-AUDIT-wizard.md` were not used as verdicts.
- Product-code writes: **0** (`web/src/**` not edited)
- `samples/*/render/**` writes: **0**
- Lockfiles / secrets / `riso-mcp`: **0**
- `render_matrix.py`: not started or killed
- Tests this session: **not re-run** (live-tree review)
- Status: **no P0 / no P1** after live inspection

## Summary

Wizard remap twin is still lockstep with the Python 8-key SSOT. Public import / share / `updateConfig` / export paths apply then fail-closed. Built-in presets emit dest keys only. Store + matrix default `task_runner` is `just`. No new wizard P0 or P1.

| Contract                  | Verdict   |
| ------------------------- | --------- |
| 8-key remap + fail-closed | **green** |
| No old keys in presets    | **green** |
| `task_runner=just`        | **green** |

## Contract

P0 = correctness / contract break. P1 = lockstep / DX. Empty lists only after inspection.

Remap is apply-then-reject. `applyRemovedKeyRemaps` then leftover reject. No dest overwrite if dest is set. Idempotent. No dual-path aliases after remap. `saas_auth: lucia` stays an unmapped leftover fail-close (not a dest alias). Generated Node floor stays 20. OpenSpec extra stays off by default.

Plan rows in scope (`plan.md` WEB-T01…T05):

| ID      | Ask                                                   | Live                                                                                  |
| ------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| WEB-T01 | `remapRemovedAnswerKeys` + 8-key set                  | `web/src/lib/removedAnswerKeys.ts`                                                    |
| WEB-T02 | Import YAML / paste: remap then fail-closed leftovers | `api.importConfig`, `importPresetYAML`, share parse, `updateConfig`                   |
| WEB-T03 | Export never emits old keys                           | `configToCopierArgs` / `generateYamlConfig` / `api.exportConfig` / `exportPresetYAML` |
| WEB-T04 | Presets use canonical keys only                       | `PRESETS` in `web/src/components/presets/presets.tsx`                                 |
| WEB-T05 | Store defaults: `task_runner=just`                    | `defaultRisoConfig` + matrix `defaults`                                               |

## Method

Read live wizard + Copier remapper (not prior review prose):

- Twin: `web/src/lib/removedAnswerKeys.ts` vs `src/riso/core/removed_answer_keys.py` + `src/riso/core/answers.py` `apply_then_reject_removed_keys`
- Import/export: `api.ts`, `configSchemas.ts`, `presets.ts`, `exportConfig.ts`, `store.ts`, `App.tsx`, `CustomPresetsSection.tsx`
- Presets: `web/src/components/presets/presets.tsx` + `presets.canonical.test.ts`
- Defaults: `store.ts`, `matrixData.ts`, `web/src/data/matrix-data.json`, `ProjectBasics.tsx`
- Grep: eight removed keys as live `config.*` reads; `lucia` / `mypy` / `flatten_monorepo` / `riso-mcp` in product `web/src`

## Mission checklist (live)

| Item                                    | Verdict   | Live evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TS remap twin == Python 8-key SSOT      | **green** | Same 8 keys: `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`. Same ops (`derive` / `wrap-list` / `rename` / `split` / `rename-bool`). Same mapper sets. `SAAS_AUTH_PROVIDERS = {clerk, authjs}` (no lucia). `writeDests` skips dest if already in `out`. Apply leaves unmapped leftovers. `applyThenRejectRemovedKeys` throws `RemovedAnswerKeyError`. Plan alias `remapRemovedAnswerKeys` delegates to `applyRemovedKeyRemaps`. |
| Import YAML / share / paste fail-closed | **green** | `api.importConfig`, `importPresetYAML`, `parseShareConfigPayload` / `parseShareableURL`, `updateConfig` all `applyThenRejectRemovedKeys`. `App.tsx` renders `Share URL rejected:`. `CustomPresetsSection` sets `importError` and does not apply the card. Leftover fixture `saas_auth: firebase`. Unmapped `saas_auth: lucia` also throws.                                                                                                                                                                      |
| Export never emits old keys             | **green** | Official Review download is `generateYamlConfig` → `configToCopierArgs`: apply-then-reject, assign dest keys only. CLI snippet is `uv run riso copy <dest> --answers-file copier-answers.yml`. `api.exportConfig` / `exportPresetYAML` remap first.                                                                                                                                                                                                                                                             |
| Presets canonical                       | **green** | All 13 `PRESETS` configs use dest keys (`saas_infra_module`, `saas_auth_module` + `saas_auth_provider: clerk`, `mcp_languages: ['typescript']`, `api_languages`, `docs_framework`). `rg` of the eight old keys in `web/src/components/presets/` is empty. `presets.canonical.test.ts` asserts `findRemovedAnswerKeys` empty and no dest `"lucia"`.                                                                                                                                                              |
| Store defaults `task_runner=just`       | **green** | `defaultRisoConfig.task_runner = fromMatrix("task_runner", "just")`. Matrix `template.defaults.task_runner` and `template._defaults.task_runner` are `"just"`. Prompt default `"just"`. `ProjectBasics` fallback `'just'`. `FileTreePreview` / `ReviewOutput` display fallback `'just'`. `store.test.ts` WEB-T05 asserts `just`. OpenSpec `disabled`. No `mypy`.                                                                                                                                                |

## Confirmations requested this pass

### 1. `removedAnswerKeys` 8-key remap + fail-closed

`REMOVED_ANSWER_KEYS` and `ANSWER_KEY_REMAPS` are exactly the eight Python keys. Dest mappers match `_DEST_MAPPERS`. Apply-then-reject:

```ts
applyRemovedKeyRemaps → formatRemovedAnswerKeyErrors → throw RemovedAnswerKeyError
```

matches

```py
apply_removed_key_remaps → reject_removed_answer_keys → ValidationFailedError
```

Fail-closed call sites (public answers): `api.importConfig`, `api.exportConfig`, `importPresetYAML`, `exportPresetYAML`, `generateShareableURL` + `parseShareConfigPayload`, `updateConfig`, `configToCopierArgs`.

### 2. No old keys in presets

`web/src/components/presets/presets.tsx` `PRESETS[].config` has no `api_tracks` / `api_language` / `docs_site` / `mcp_language` / `saas_starter_module` / `saas_auth` / `saas_billing` / `include_admin`. SaaS presets use `saas_auth_provider: 'clerk'` only.

### 3. `task_runner=just`

Default is `just` from live matrix + hardcoded fallback. UI still offers makefile / both / none as **choices**, not defaults.

## Inspected, not elevated (below P1)

Do not reset the dry-review counter on these:

- **Persist / custom-preset hydrate** uses `dropLeftoverRemovedKeys` (`store.ts` `canonicalizeConfig`, `configSchemas.ts` `parseCustomPresetsStorage`). Comment: hydration, never throw. YAML import, share URL, and `updateConfig` still fail-closed.
- **Stale localStorage dest `saas_auth_provider=lucia`** would still export if a pre-CLOSE-WEB persist existed. No live writer remains. Dest union and `SaaSConfig` fallback are `clerk` | `authjs`.
- **`api.generateProject`** posts the config object without remapping. File comment: scaffolded / unused; live Review path is `generateYamlConfig`.
- **Hero.tsx** still demos `--data key=value`. Review export command is `--answers-file`.
- **FileTreePreview / preset trees** still sketch SaaS as `apps/web`. Answers do not reintroduce flatten (`nextjs-16` / `remix-2`).
- **FileTreePreview** always adds `mise.toml`. It does not preview `openspec/` when `openspec_extra=enabled` (preview DX, not answers).
- Product `web/src` has **no** `lucia` / `mypy` / `flatten_monorepo` / `riso-mcp` outside tests. `rg` `config.(api_tracks|api_language|docs_site|mcp_language|saas_starter_module|saas_auth|saas_billing|include_admin)` in `web/src` is empty.

## P0

None after inspection.

## P1

None after inspection. Prior AUDIT `WIZ-P1-lucia-dest` remains **closed** in the live tree.

## Writes

This evidence file only. No commit / tag / push. No `web/src/**` edits. No `residuals/WEB.md` (no owned wizard residual).
