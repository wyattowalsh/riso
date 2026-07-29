# DESKTOP → COORD: non-enum desktop feature tokens

| Field                             | Value                                                                                                    |
| --------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **change_id**                     | `COORD-non-enum-desktop-features`                                                                        |
| **requesting_lane**               | `desktop`                                                                                                |
| **summary**                       | Decide keep-vs-add-vs-strip for Tauri gates that reference tokens outside Copier `desktop_features` enum |
| **status**                        | `proposed`                                                                                               |
| **needs_shared_generation_gates** | `no`                                                                                                     |

## Topic

non-enum-features

## Evidence

Copier `desktop_features` choices (enum SSOT):

- `auto_updater`
- `tray_icon`
- `custom_titlebar`
- plus combinations / `none`

Tokens used in `template/files/tauri/**` that are **not** in the enum:

| Token                | Surfaces                                                                 | Behavior today                           |
| -------------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| `system_info`        | `App.tsx`, `commands.rs`, `Cargo.toml`, README (neutralized)             | Dead branch — never selected via answers |
| `menu`               | `menu.rs`, `lib.rs`, `main.rs`, ARCHITECTURE                             | Dead branch                              |
| `transparent_window` | `tauri.conf.json`                                                        | Dead branch → `transparent: false`       |
| `deep_linking`       | `tauri.conf.json`, `Cargo.toml`                                          | Dead branch                              |
| `notifications`      | `package.json`, `capabilities`, `Cargo.toml`, `main.rs`, QUICK_REFERENCE | Dead branch                              |
| `file_system`        | `package.json`, `capabilities`, `Cargo.toml`, `main.rs`, QUICK_REFERENCE | Dead branch                              |

Enum features **are** wired correctly for electron-vite + tauri (W2 DESKTOP deep-feature pass).

## Current behavior

Non-enum tokens are safely gated: with real sample answers they never activate. Dead code remains for potential future enum expansion. Docs no longer advertise `system_info` as a contracted feature.

## Requested contract change

COORD pick one policy per token (or blanket policy):

1. **Strip** — DESKTOP removes dead gates/code in a follow-up (clean current-state).
1. **Promote** — expand `desktop_features` choices (and catalog/docs) then DESKTOP keeps/finishes wiring.
1. **Keep dead** — leave inactive gates as optional future hooks; document as non-contractual.

Recommended default: **strip** `transparent_window` / `deep_linking` / `notifications` / `file_system` / `menu` / `system_info` unless product wants them in the enum this cycle.

## DESKTOP blocked work

None for enum deep features. Follow-up strip/promote only after outbox.

## Suggested acceptance tests

```bash
uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
# After promote: sample with new feature tokens validates and renders
# After strip: no non-enum token references remain under template/files/tauri/**
```

## Prompt keys

Only if **promote** chosen — example shape:

| key                | type                    | default        | when            | help           | choices (if any)                   |
| ------------------ | ----------------------- | -------------- | --------------- | -------------- | ---------------------------------- |
| `desktop_features` | str (multiselect-style) | `auto_updater` | desktop enabled | extend choices | add promoted tokens + combinations |

## Hook validation rules

None unless promote introduces illegal combos (e.g. feature requires framework).

## Payload follow-ups

| lane     | exclusive paths                                         | acceptance note                                     |
| -------- | ------------------------------------------------------- | --------------------------------------------------- |
| DESKTOP  | `template/files/tauri/**`, `template/files/electron/**` | Strip or finish promoted features                   |
| PLATFORM | samples                                                 | Update answers only if new enum tokens are promoted |

## Samples to re-validate

| path                                      |
| ----------------------------------------- |
| `samples/electron-app/copier-answers.yml` |
| `samples/tauri-app/copier-answers.yml`    |

## Non-goals

- DESKTOP will not invent Copier keys.
- DESKTOP will not edit sample answers (PLATFORM lock).
