# W2 DESK-T03 — `env.d.ts.jinja` + Tauri `vite-env.d.ts.jinja`

- Task: `DESK-T03`
- Wave: W2 / lane DESKTOP
- Deps: `DESK-T01`
- Exclusive write: `template/files/electron/**`, `template/files/tauri/**`
- Verify: files exist; tsconfig includes `*.d.ts`
- Status: **green**
- `samples/*/render/**` writes: **0**

## Files

| Path | Role |
| --- | --- |
| `template/files/electron/src/renderer/env.d.ts.jinja` | Vite client + `window.api` matching preload (`storeGet` / window / theme / optional updater) |
| `template/files/electron/tsconfig.web.json.jinja` | `include` has `src/renderer/**/*.d.ts` (KEEP vs HEAD) |
| `template/files/tauri/src/vite-env.d.ts.jinja` | `/// <reference types="vite/client" />` |
| `template/files/tauri/tsconfig.json.jinja` | `include` now has `src/**/*.d.ts` (this wave) |

Renderer `App.tsx` / `TitleBar.tsx` call `window.api.getAppInfo`, `storeGet`-style IPC, etc. The prior stub typed `store.get` plus `[key: string]: unknown`, which fails `tsc --noEmit` under `tsconfig.web` strictness. This wave aligned `ElectronAPI` with preload and gated updater methods on `auto_updater`.

Disabled `desktop_module` still renders both d.ts templates empty.
