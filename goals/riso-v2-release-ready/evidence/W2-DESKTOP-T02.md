# W2 DESK-T02 — ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` + plugins

- Task: `DESK-T02`
- Wave: W2 / lane DESKTOP
- Deps: `DESK-T01`
- Exclusive write: `template/files/electron/**`, `template/files/tauri/**`
- Verify: jinja `package.json` / `.eslintrc.cjs`
- Status: **green**
- `samples/*/render/**` writes: **0**

## Contract

Generated desktop apps stay on ESLint **9** with the **eslintrc** (non-flat) config. Scripts set `ESLINT_USE_FLAT_CONFIG=false`.

Dirty-tree KEEP vs HEAD already present; not rewritten this wave.

| Surface | Evidence |
| --- | --- |
| Electron `package.json.jinja` | `eslint: ^9.18.0`; lint/lint:fix prefix `ESLINT_USE_FLAT_CONFIG=false`; plugins `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `@typescript-eslint/{parser,eslint-plugin}` |
| Tauri `package.json.jinja` | same ESLint 9 + env flag; `eslint-plugin-react-hooks` + `@typescript-eslint/*` |
| Electron `.eslintrc.cjs.jinja` | extends `plugin:react-hooks/recommended`; plugin `react-refresh` (byte-identical to HEAD; not dirty) |
| Tauri `.eslintrc.cjs.jinja` | extends `plugin:react-hooks/recommended` (byte-identical to HEAD; not dirty) |

No new vendors. No flat-config rewrite.
