# DESKTOP → COORD: electron-forge + exclusion-path shape

| Field                             | Value                                                                                                                                  |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **change_id**                     | `COORD-electron-forge-exclusions`                                                                                                      |
| **requesting_lane**               | `desktop`                                                                                                                              |
| **summary**                       | Align copier `_exclude` desktop framework paths with flat electron-vite tree; decide forge scaffold contract before DESKTOP implements |
| **status**                        | `proposed`                                                                                                                             |
| **needs_shared_generation_gates** | `no`                                                                                                                                   |

## Topic

forge | exclusions

## Evidence (paths, tokens, sample answers)

| Item                        | Observation                                                         |
| --------------------------- | ------------------------------------------------------------------- |
| Live electron scaffold      | Flat tree under `template/files/electron/**` (electron-vite only)   |
| Live tauri scaffold         | Sibling `template/files/tauri/**` (not under `electron/`)           |
| Sample                      | `samples/electron-app` → `desktop_framework: electron-vite`         |
| Sample                      | `samples/tauri-app` → `desktop_framework: tauri`                    |
| `desktop_framework` choices | `electron-vite`, `electron-forge`, `tauri` in `template/copier.yml` |
| Missing tree                | No `template/files/electron/electron-forge/**`                      |
| Missing nested vite path    | No `template/files/electron/electron-vite/**` (files are flat)      |

Relevant `_exclude` lines in `template/copier.yml` (read-only evidence):

```yaml
- "{% if desktop_module != 'enabled' %}electron/{% endif %}"
- "{% if not (desktop_module == 'enabled' and desktop_framework == 'tauri') %}tauri/{% endif %}"
- "{% if not (desktop_module == 'enabled' and desktop_framework == 'electron-vite') %}electron/electron-vite/{% endif %}"
- "{% if not (desktop_module == 'enabled' and desktop_framework == 'electron-forge') %}electron/electron-forge/{% endif %}"
- "{% if not (desktop_module == 'enabled' and desktop_framework == 'tauri') %}electron/tauri/{% endif %}"
```

## Current behavior

1. Choosing `electron-vite` includes the flat `electron/` tree (because whole-tree exclude only fires when desktop disabled). The nested `electron/electron-vite/` exclude is a no-op (path does not exist).
1. Choosing `electron-forge` still includes the flat electron-vite files (no forge payload exists) and the forge exclude path is a no-op.
1. Choosing `tauri` correctly includes `tauri/` via the sibling exclude; `electron/tauri/` exclude is a no-op.
1. Users can select forge in the prompt and get an electron-vite scaffold silently.

## Requested contract change

Preferred clean current-state options (COORD chooses one):

**Option A (recommended):** Drop `electron-forge` from `desktop_framework` choices until a scaffold exists; rewrite excludes to match flat layout:

```yaml
# include electron/* only for electron-vite
- "{% if not (desktop_module == 'enabled' and desktop_framework == 'electron-vite') %}electron/{% endif %}"
# include tauri/* only for tauri
- "{% if not (desktop_module == 'enabled' and desktop_framework == 'tauri') %}tauri/{% endif %}"
# remove obsolete nested electron/electron-vite, electron/electron-forge, electron/tauri excludes
```

**Option B:** Keep forge in the enum; DESKTOP implements `template/files/electron/electron-forge/**` after COORD publishes exclusion shape + any catalog/docs updates. Nested layout preferred if forge coexists with vite under `electron/`.

**Option C:** Keep forge choice but illegal-combo / pre_gen error until scaffold ships (`desktop_framework == electron-forge` → hard fail with message).

## DESKTOP blocked work

- Wave D6 (electron-forge scaffold) blocked until COORD approves Option B (or equivalent).
- DESKTOP will not invent forge under exclusive roots without outbox approval.
- Enum deep features for electron-vite + tauri are **not** blocked.

## Suggested acceptance tests

```bash
uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
# After Option A exclude rewrite: render with desktop_framework=electron-vite includes electron/** and not tauri/**
# After Option A: render with desktop_framework=tauri includes tauri/** and not electron/**
# After Option C: validate answers with desktop_framework=electron-forge fails with clear error
```

## Prompt keys

No new keys. Possible choice-set change only:

| key                 | type | default         | when                        | help                                | choices (if any)                                    |
| ------------------- | ---- | --------------- | --------------------------- | ----------------------------------- | --------------------------------------------------- |
| `desktop_framework` | str  | `electron-vite` | `desktop_module == enabled` | unchanged or drop forge until ready | Option A: remove `electron-forge`; Option B/C: keep |

## Hook validation rules

| condition (illegal combo)                                                      | error message                                                               | preferred surface               |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------- | ------------------------------- |
| Option C only: `desktop_module=enabled` and `desktop_framework=electron-forge` | Electron Forge scaffold is not available yet; choose electron-vite or tauri | `hooks_local` or `gates_shared` |

## Module catalog / macros / context

Review catalog rows that mention forge; update selected_state if forge choice is removed or gated.

## CLI / generation_gates handoff

| Item                 | Detail                                    |
| -------------------- | ----------------------------------------- |
| Needed?              | `no` (unless Option C wants shared gates) |
| Files (CLI-owned)    | n/a                                       |
| Summary for CLI lane | n/a                                       |

## Payload follow-ups

| lane     | exclusive paths                | acceptance note                                     |
| -------- | ------------------------------ | --------------------------------------------------- |
| DESKTOP  | `template/files/electron/**`   | Implement forge scaffold only after Option B outbox |
| PLATFORM | `samples/*/copier-answers.yml` | No new sample until forge ships                     |

## Samples to re-validate

| path                                      |
| ----------------------------------------- |
| `samples/electron-app/copier-answers.yml` |
| `samples/tauri-app/copier-answers.yml`    |

## Non-goals

- DESKTOP will not edit `copier.yml` / hooks / catalog.
- DESKTOP will not hand-edit `samples/*/render/`.
