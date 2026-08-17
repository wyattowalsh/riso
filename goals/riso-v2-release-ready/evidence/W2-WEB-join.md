# W2-WEB join

- Wave: W2 / lane WEB
- Tasks: `WEB-T01` `WEB-T02` `WEB-T03` `WEB-T04` `WEB-T05` `WEB-T06` `WEB-JOIN`
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive writes: `web/src/**`, `web/tests/**`, this evidence tree
- `samples/*/render/**` writes: **0**
- Residual file: none (`residuals/WEB.md` not created)
- Date: 2026-08-13

## Remap contract (TS twin)

`web/src/lib/removedAnswerKeys.ts` now matches core `apply_removed_key_remaps`:

- 8 keys + operators: wrap-list / derive / rename / split / rename-bool
- apply then reject leftovers
- do not overwrite a dest key that is already set
- drop old key after successful apply
- second apply is a no-op
- preview strings via `formatRemapPreview`

Import (`api.importConfig`, `importPresetYAML`, share parse) applies remaps then fail-closes leftovers. Export (`configToCopierArgs`, `generateYamlConfig`, `api.exportConfig`, `exportPresetYAML`) remaps first and never emits old keys.

## Task results

| ID | Decision | Verify | Status |
| --- | --- | --- | --- |
| WEB-T01 | `remapRemovedAnswerKeys` / `applyRemovedKeyRemaps` + preview; 8-key set + operator names | `removedAnswerKeys.test.ts` (77) | green |
| WEB-T02 | YAML import/paste remap then fail-closed leftovers | `api.import.test.ts`, `presets.test.ts` import cases | green |
| WEB-T03 | `exportConfig` / export-yaml never emit old keys | `exportConfig.test.ts` + `api.import.test.ts` export case | green |
| WEB-T04 | built-in presets canonical only | `presets.canonical.test.ts`; `rg` old tokens in `presets.tsx`/`presets.ts` empty (`W2-WEB-rg-presets.txt`) | green |
| WEB-T05 | store defaults `task_runner=just`, OpenSpec `disabled`, no mypy | `store.test.ts` defaults | green |
| WEB-T06 | Playwright remapped 1.x YAML happy + leftover error | `tests/e2e/import-remap.spec.ts` | green |
| WEB-JOIN | vitest + smoke/wizard/remap e2e | below | green |

## Verify

```text
pnpm --dir web run test:run
 Test Files  13 passed (13)
      Tests  301 passed (301)

pnpm --dir web exec playwright test --retries=0
  19 passed (1.1m)
  (import-remap 2 + smoke 2 + wizard 15)
```

## Not WEB

- `samples/*/copier-answers.yml` → PLATFORM
- `copier.yml` / hooks / Python SSOT → COORD/CLI
- three-way CI checker `check_removed_key_ssot.py` → PL-T10
