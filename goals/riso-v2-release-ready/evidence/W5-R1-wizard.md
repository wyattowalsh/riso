# W5-R1 — Review pass 1, surface=wizard

- Task: `W5-R1`
- Wave: W5
- Lane: GOAL (inspect-only; this file only)
- Surface: wizard (`web/src/**` + live e2e at `web/tests/e2e/**`; `web/e2e/**` does not exist)
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (`.git/refs/heads/main`; `.git/HEAD` hook-denied; no shell for `git rev-parse --show-toplevel`; tool cwd is the same repo root)
- Date: 2026-08-14
- Prior review blob: empty / untrusted. `ASSURANCE.md`, `W5-AUDIT-wizard.md`, `W5-CLOSE-WEB.md`, and `W2-WEB-join.md` were read then re-checked against the live tree.
- Product-code writes: **0**
- `samples/*/render/**` writes: **0**
- Lockfiles / secrets / `riso-mcp`: **0**
- `render_matrix.py`: not started or killed
- Status: **no P0 / no P1** after live inspection

## Contract

P0 = correctness / contract break. P1 = lockstep / DX. Empty lists only after inspection.

Remap is apply-then-reject. `applyRemovedKeyRemaps` then leftover reject. No dest overwrite if dest is set. Idempotent. No dual-path aliases after remap. Generated Node floor stays 20. OpenSpec extra stays off by default. SaaS Next/Remix flatten stays reverted. `saas_auth: lucia` stays an unmapped leftover fail-close (not a dest alias).

## Method

Read `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/*.md` first. Then read live wizard + Copier SSOT:

- Twin: `web/src/lib/removedAnswerKeys.ts` vs `src/riso/core/removed_answer_keys.py`
- Import/export: `api.ts`, `configSchemas.ts`, `presets.ts`, `exportConfig.ts`, `store.ts`
- UI dest: `SaaSConfig.tsx`, `ProjectBasics.tsx`, `ReviewOutput.tsx`, `FileTreePreview.tsx`, `Hero.tsx`, `App.tsx`, presets
- Matrix: `web/src/data/matrix-data.json` (`generated_at` 2026-08-14T05:34:27Z) vs `template/copier.yml`
- E2E: `web/tests/e2e/{import-remap,wizard,smoke}.spec.ts` + fixtures
- Grep: eight removed keys as live `config.*` reads; `lucia`; `flatten_monorepo`; `node_version` / 22; `riso-mcp`; `include_openspec`

No `pnpm` / `uv run` this session (no shell). Verdicts are live-tree, not test reruns.

## Mission checklist (live)

| Item | Verdict | Live evidence |
| --- | --- | --- |
| TS remap twin == Python 8-key SSOT | **green** | Same 8 keys and ops (`derive` / `wrap-list` / `rename` / `split` / `rename-bool`). Same mapper sets. `SAAS_AUTH_PROVIDERS = {clerk, authjs}` (no lucia). `writeDests` skips dest if already in `out`. Apply leaves unmapped leftovers. `applyThenRejectRemovedKeys` throws `RemovedAnswerKeyError`. |
| Import YAML / share / paste fail-closed | **green** | `api.importConfig`, `importPresetYAML`, `parseShareConfigPayload` / `parseShareableURL`, `updateConfig` all `applyThenRejectRemovedKeys`. `App.tsx` renders `Share URL rejected:`. `CustomPresetsSection` shows leftover error, no apply card. E2E leftover fixture `saas_auth: firebase`. |
| Export never emits old keys | **green** | Official Review download is `generateYamlConfig` → `configToCopierArgs`: apply-then-reject, assign dest keys, `delete` `REMOVED_ANSWER_KEYS`. CLI snippet is `uv run riso copy <dest> --answers-file copier-answers.yml` (no `--data`). `api.exportConfig` / `exportPresetYAML` also remap first. |
| Presets canonical | **green** | `PRESETS` dest keys only (`saas_infra_module`, `saas_auth_provider: clerk`, `mcp_languages: ['typescript']`). No `flatten_monorepo`. No dest `"lucia"`. `presets.canonical.test.ts`. |
| Store defaults | **green** | `task_runner` from matrix/`just`. `openspec_extra` from matrix/`disabled`. No `mypy`. `saas_auth_provider` clerk. Matrix `defaults` (not only `_defaults`) is what `matrixData.ts` reads. |
| Node floor 20 / not 22 | **green** | Wizard has no `node_version` field and does not emit 22. Matrix `python_versions` 3.11–3.13. Generated Node pin is mise (preview always adds `mise.toml`). |
| OpenSpec extra default off | **green** | Store + matrix + `ProjectBasics` default `disabled`. Export assigns `openspec_extra`. |
| Flatten stays reverted | **green** | No `flatten_monorepo` in `web/src`. SaaS dest values stay `nextjs-16` / `remix-2`. Template still has separate `runtime/{nextjs,remix}`. |
| Dest lucia closed | **green** | Copier choices clerk\|authjs (`template/copier.yml` L1337–1347). Matrix prompt same. `SaaSConfig` fallback `['clerk','authjs']`. Store union `'clerk' \| 'authjs'`. Cost rows clerk/authjs only. Product `web/src` has **no** `lucia` outside tests. Leftover `saas_auth: lucia` still unmapped. |
| E2E WEB-T06 | **green (present)** | `web/tests/e2e/import-remap.spec.ts`: mixed 1.x YAML remaps to dest keys; leftover shows error and does not apply. Playwright `testDir` is `./tests/e2e`. |
| No dual-path after remap | **green** | `rg` `config.(api_tracks\|api_language\|docs_site\|mcp_language\|saas_starter_module\|saas_auth\|saas_billing\|include_admin)` in `web/src` is empty. Old names live only in the remapper / tests / matrix help prose. |
| No `riso-mcp` package | **green** | No `riso-mcp` / `riso_mcp` in `web/src`. |

## Inspected, not elevated (below P1)

Do not reset the dry-review counter on these:

- **Persist / custom-preset hydrate** uses `dropLeftoverRemovedKeys` (`store.ts` `canonicalizeConfig`, `configSchemas.ts` `parseCustomPresetsStorage`). Comment: hydration, never throw. YAML import, share URL, and `updateConfig` still fail-closed.
- **Stale localStorage dest `saas_auth_provider=lucia`** would still export if a pre-CLOSE-WEB persist existed. No live writer remains. Not a current-source dest offer.
- **`api.exportConfig`** stringifies remapped answers as-is. Official Review path is `generateYamlConfig`. WEB-T03 (no old keys) holds on both.
- **Hero.tsx** still demos `--data key=value`. Live CLI still accepts `--data` (`src/riso/cli/app.py`, `helpers.py`). Review export command is `--answers-file`.
- **FileTreePreview / preset trees** still sketch SaaS as `apps/web` (or `web`). Generated payload uses `runtime/{nextjs,remix}` (`template/files/node/saas/package.json.jinja`). Schematic preview only; answers do not reintroduce flatten.
- **FileTreePreview** always adds `mise.toml` (correct). It does not preview `openspec/` when `openspec_extra=enabled` (preview DX, not answers).
- **Wizard does not expose** every Copier prompt (`desktop_module`, `saas_storage`, `saas_cicd`, `saas_enterprise_bridge`, …). Missing keys keep Copier defaults. Not a 2.0 remap break.
- **`web/e2e/**` is absent.** Live Playwright root is `web/tests/e2e/**` (`playwright.config.ts` L4). Inspected that tree.

## P0

None after inspection.

## P1

None after inspection. Prior AUDIT `WIZ-P1-lucia-dest` is **closed** in the live tree (CLOSE-WEB dest lockstep still holds).

## Writes

This evidence file only. No commit / tag / push. No `render_matrix` start/kill. No `residuals/WEB.md` (no owned wizard residual).
