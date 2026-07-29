# W2-DESKTOP evidence summary

**Wave:** W2-DESKTOP\
**Status:** green\
**Date (UTC context):** 2026-07-28 / 2026-07-29 session

## Commands

```bash
# Jinja (63 templates)
find template/files/electron template/files/tauri -name '*.jinja' -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# → Validated 63 Jinja template(s): all OK

uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
# → ok:true valid:true

uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
# → ok:true valid:true
```

## Artifact paths

- `goals/riso-lanes-assurance/evidence/W2-DESKTOP-jinja.txt`
- `goals/riso-lanes-assurance/evidence/W2-DESKTOP-validate-electron-app.json`
- `goals/riso-lanes-assurance/evidence/W2-DESKTOP-validate-tauri-app.json`
- `goals/riso-lane-desktop/audit/AUDIT-20260728.md`
- `goals/riso-lane-desktop/handoffs/COORD-electron-forge-exclusions.md`
- `goals/riso-lane-desktop/handoffs/COORD-non-enum-desktop-features.md`

## Payload changes (exclusive roots only)

### Electron

- `template/files/electron/package.json.jinja` — gate `electron-updater` + publish script on `auto_updater`; gate platform build scripts on `desktop_platforms`

### Tauri

- `src-tauri/src/main.rs.jinja` — unified setup; register updater + process plugins when `auto_updater`
- `src-tauri/Cargo.toml.jinja` — gate updater/process deps on `auto_updater`
- `src-tauri/capabilities/default.json.jinja` — updater + process permissions
- `src-tauri/tauri.conf.json.jinja` — platform-scoped bundle targets; updater plugin conf placeholders
- `src-tauri/src/commands.rs.jinja` — `UpdaterExt` import fix
- `src-tauri/src/menu.rs.jinja` — set menu + event handler when non-enum menu ever selected
- `package.json.jinja` — frontend updater/process packages when `auto_updater`
- `src/components/UpdateChecker.tsx.jinja` — use `getVersion()` (removed missing `get_app_version` invoke)
- `README.md.jinja` — drop non-enum `system_info` feature bullet

## Non-goals observed

- No writes to `samples/*/copier-answers.yml` (PLATFORM lock)
- No hand-edits to `samples/*/render/`
- No `copier.yml` / hooks edits (COORD)
- Forge scaffold not implemented (COORD handoff)
