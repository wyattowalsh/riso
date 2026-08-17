# W2-DESKTOP join

- Wave: W2 / lane DESKTOP
- Tasks: `DESK-T01`, `DESK-T02`, `DESK-T03`, `DESK-T04`, `DESK-JOIN`
- Status: **green**
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive writes: `template/files/electron/**`, `template/files/tauri/**`, this evidence set
- `samples/*/render/**` writes: **0**
- Residual file: none (`residuals/DESKTOP.md` not created)

## Task results

| ID | Decision | Verify | Status |
| --- | --- | --- | --- |
| DESK-T01 | keep `externalizeDepsPlugin({ exclude: ['electron-store'] })` on main + preload | `test_electron_templates.py` + render (exclude ×2) | green |
| DESK-T02 | keep ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` + hooks/ts plugins | both `package.json.jinja` + `.eslintrc.cjs.jinja` | green |
| DESK-T03 | keep `env.d.ts.jinja` + Tauri `vite-env.d.ts.jinja`; align `window.api`; include `*.d.ts` | files exist; tsconfigs include `*.d.ts` | green |
| DESK-T04 | keep no clang/lld in Tauri cargo config | `rg` on `.cargo` empty; render has no clang/lld | green |
| DESK-JOIN | electron + new-template tests | **58 passed** (`test_electron_templates.py` 42 + `test_new_templates.py` 16) | green |

## This-wave payload writes

| Path | Why |
| --- | --- |
| `template/files/electron/src/renderer/env.d.ts.jinja` | typecheck: `window.api` matches preload (not `store.get` stub) |
| `template/files/tauri/tsconfig.json.jinja` | include `src/**/*.d.ts` so `vite-env.d.ts` is in the program |
| `template/files/tauri/src-tauri/.cargo/config.toml.jinja` | comment only: default linker (clang/lld already gone) |

Dirty KEEP already in tree (not rewritten): `electron.vite.config.ts.jinja`, both `package.json.jinja`, `electron/tsconfig.web.json.jinja`, `tauri/src/vite-env.d.ts.jinja`. Remaining porcelain electron/tauri polish left untouched (W0 KEEP).

## Commands

```bash
uv run pytest tests/unit/test_electron_templates.py tests/unit/test_new_templates.py -q -n 0
# 58 passed

find template/files/electron template/files/tauri -name '*.jinja' -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 68 Jinja template(s): all OK

uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
# ok:true valid:true

uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
# ok:true valid:true

rg -n -i 'clang|lld|fuse-ld' template/files/tauri/src-tauri/.cargo
# (no matches)
```

## Artifact paths

- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-T01.md`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-T02.md`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-T03.md`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-T04.md`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-pytest.txt`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-jinja.txt`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-validate-electron-app.json`
- `goals/riso-v2-release-ready/evidence/W2-DESKTOP-validate-tauri-app.json`

## Not this lane

- `tests/unit/test_electron_templates.py` assertions for exclude / ESLint env / cargo lld — foreign tree (no `tests/**` lock). JOIN ran the existing file; it stays green.
- `samples/*/copier-answers.yml` — PLATFORM
- `copier.yml` / hooks — COORD
- `test_go_templates.py` — SYS (already green in `W2-SYS-T01.md`)

## Non-goals honored

- No `samples/*/render/**` writes
- No lockfile hand-edits
- No `riso-mcp`
- No new languages / runtimes / vendors
- No commit / tag / push
