# W2 DESK-T01 — electron-store `externalizeDepsPlugin({exclude})`

- Task: `DESK-T01`
- Wave: W2 / lane DESKTOP
- Deps: `W1-OUT` (present under `evidence/coord-outbox/`)
- Exclusive write: `template/files/electron/**`
- Verify: `uv run pytest tests/unit/test_electron_templates.py -q -n 0`
- Status: **green**
- `samples/*/render/**` writes: **0**

## Repo

| Field | Value |
| --- | --- |
| CWD | `/Users/ww/dev/projects/riso` |
| Branch | `main` (unchanged) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` |

## Contract

`electron-store` v10 is ESM-only. Main-process files import `Store from 'electron-store'`. Bundling it (not externalizing as CJS `require`) is the boot keep-fix.

`template/files/electron/electron.vite.config.ts.jinja` already had the dirty-tree KEEP vs HEAD (`externalizeDepsPlugin()` → exclude). Not rewritten this wave.

```ts
plugins: [externalizeDepsPlugin({ exclude: ['electron-store'] })],
```

Present on **main** and **preload**.

## Verify

| Check | Result |
| --- | --- |
| `rg externalizeDepsPlugin template/files/electron/electron.vite.config.ts.jinja` | exclude on lines 8 and 24 |
| Jinja render | exclude string appears **twice** |
| `test_electron_templates.py` | **42 passed** (includes `test_electron_vite_config_renders_correctly`) |
