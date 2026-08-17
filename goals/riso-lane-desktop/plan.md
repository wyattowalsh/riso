# Plan: Riso Lane DESKTOP (parallel-optimized)

## 0. Critique of the thin plan (what we improve)

| Weakness | Fix in this plan |
|----------|------------------|
| Coarse “deep features” blob | **Hyperfine** task IDs `D0…D5` / leaves `D*.*.*` with deps |
| No internal parallel model | **DESKTOP sub-lanes** with exclusive write roots + wave DAG |
| Forge/non-enum buried | Explicit **COORD handoff schemas** + token inventory |
| Merge conflicts unstated | **Hard collision table** (index.ts, tauri.conf, Cargo, App.tsx) |
| Verify afterthought | Baseline → per-wave → closeout commands with exit criteria |
| Render smoke vague | Official `render-samples.sh` only; never hand-edit renders |
| Subagent prompts missing | **Dispatch template** per sub-lane |

## 1. Solution approach

DESKTOP is the exclusive owner of Electron + Tauri Copier payload scaffolds:

| Write root | Live framework(s) |
|------------|-------------------|
| `template/files/electron/**` | **electron-vite only** today (flat tree) |
| `template/files/tauri/**` | **tauri** |

**Interview priority:** deep correctness of contracted enum features:

- `auto_updater`
- `tray_icon`
- `custom_titlebar`

…plus `desktop_platforms` packaging (`mac` / `windows` / `linux`).

**Framework matrix:**

| `desktop_framework` | Scaffold | Sample |
|---------------------|----------|--------|
| `electron-vite` | Present under `electron/` | `samples/electron-app` (`desktop_features: auto_updater,custom_titlebar`) |
| `tauri` | Present under `tauri/` | `samples/tauri-app` (all three features) |
| `electron-forge` | **Missing** | none |

**Contract stance:** no new Copier keys. Non-enum tokens found in Tauri trees → align/neutralize + COORD handoff. Forge → COORD first; scaffold only after COORD approves exclusion shape.

### 1.1 DESKTOP sub-lanes (parallel write roots)

| Sub-lane | Exclusive write roots | Parallel with |
|----------|----------------------|---------------|
| **E-MAIN** | `electron/src/main/**`, `electron/src/preload/**`, `electron/src/shared/**` | All T-*; not concurrent multi-writers on same main file |
| **E-UI** | `electron/src/renderer/**` | All T-*; parallel E-MAIN if IPC contract frozen |
| **E-PKG** | `electron/electron-builder.yml.jinja`, `electron/package.json.jinja`, `electron/resources/**`, electron root configs (vite/ts/eslint/prettier/postcss/tailwind/gitignore) | All T-* |
| **E-DOCS** | `electron/README.md.jinja`, `electron/.env.example.jinja` | Prefer after E-feature waves |
| **T-FE** | `tauri/src/**` | All E-* |
| **T-RS** | `tauri/src-tauri/src/**` | All E-*; serialize with T-CFG on shared feature names |
| **T-CFG** | `tauri/src-tauri/tauri.conf.json.jinja`, `capabilities/**`, `Cargo.toml.jinja`, `build.rs.jinja`, `rustfmt.toml.jinja`, `icons/**` | All E-* |
| **T-DOCS** | `tauri/README.md.jinja`, `ARCHITECTURE.md.jinja`, `QUICKSTART.md.jinja`, `QUICK_REFERENCE.md.jinja`, `.env.example.jinja`, root `package.json.jinja` / vite/ts/postcss/tailwind under tauri | Prefer after T-feature waves; **package.json** is a collision file → lead-only if multi-agent |
| **OPS** | `goals/riso-lane-desktop/**` (handoffs, audit notes) | Always |
| **VERIFY** | none (commands only) | After writer waves |

### 1.2 Hard collision table (single-writer)

| File | Why | Owner |
|------|-----|-------|
| `electron/src/main/index.ts.jinja` | Merges updater/tray/window init | **E-MAIN lead** |
| `electron/electron-builder.yml.jinja` | Platforms + updater publish | **E-PKG lead** |
| `electron/package.json.jinja` | deps/scripts | **E-PKG lead** |
| `electron/src/preload/index.ts.jinja` | IPC surface | **E-MAIN lead** |
| `electron/src/shared/types.ts.jinja` | Shared contracts | **E-MAIN lead** (freeze before E-UI) |
| `tauri/src-tauri/tauri.conf.json.jinja` | window/tray/bundle/updater | **T-CFG lead** |
| `tauri/src-tauri/Cargo.toml.jinja` | features/plugins | **T-CFG lead** |
| `tauri/src-tauri/src/main.rs.jinja` / `lib.rs.jinja` | plugin wiring | **T-RS lead** |
| `tauri/src/App.tsx.jinja` | titlebar + updater + system_info UI | **T-FE lead** |
| `tauri/package.json.jinja` | optional feature deps | **T-DOCS/T-CFG lead** |

Subagents needing collision-file changes file `goals/riso-lane-desktop/handoffs/root-dep-<id>.md` for the lead to apply.

### 1.3 Global hard rules (all subagents)

- Write **only** `template/files/electron/**` and `template/files/tauri/**` (+ goal handoffs under `goals/riso-lane-desktop/**`).
- **Never** edit: `copier.yml`, hooks, macros, catalog, language trees, `frontend/**`, `node/saas/**`, `src/riso/**`, `web/**`, sample answers, `samples/*/render/**`.
- No branches / worktrees / commits / pushes unless human asks.
- No lockfile hand-edits; no secrets; `uv run` for maintainer Python.
- Do not invent Copier answer keys.
- Prefer local desktop renderer; do not take frontend/saas ownership.

### 1.4 Ownership router (foreign failures)

| Symptom | Owner | DESKTOP action |
|---------|-------|----------------|
| electron/tauri jinja or feature gates | **DESKTOP** | Fix |
| copier desktop_* enums / exclusions / catalog | **COORD** | Handoff |
| sample answers / render matrix / CI scripts | **PLATFORM** | Handoff |
| `riso validate` CLI bugs | **CLI** | Handoff |
| shared root `template/files/package.json.jinja` outside electron/tauri | foreign | Handoff |

## 2. Artifact contracts

### 2.1 COORD handoff (`goals/riso-lane-desktop/handoffs/<id>.md`)

```markdown
# DESKTOP → COORD: <id>
## Topic
forge | exclusions | non-enum-features | other
## Evidence (paths, tokens, sample answers)
## Current behavior
## Requested contract change
## DESKTOP blocked work
## Suggested acceptance tests
```

### 2.2 Audit note (`goals/riso-lane-desktop/audit/AUDIT-<date>.md`)

Sections: enum gate matrix, non-enum token table, exclusion mismatch, IPC/plugin contracts, sample validate results, jinja results, open handoffs.

### 2.3 Non-enum token inventory (codebase fact)

Observed outside Copier `desktop_features` choices (`auto_updater`, `tray_icon`, `custom_titlebar`):

| Token | Surfaces (examples) |
|-------|---------------------|
| `system_info` | tauri App.tsx, commands.rs, Cargo, README |
| `menu` | menu.rs, lib/main, ARCHITECTURE/README |
| `transparent_window` | tauri.conf.json |
| `deep_linking` | tauri.conf, Cargo |
| `notifications` | package.json, capabilities, Cargo, main |
| `file_system` | package.json, capabilities, Cargo, main |

**Policy:** align/neutralize under enum where safe; never add Copier keys; file COORD handoff for keep-vs-add-vs-strip.

## 3. Hyperfine task graph (DAG)

```
Wave D0 ── audit + baseline (parallel R)
   │
Wave D1 ── electron deep features (parallel E-* with collision leads)
   │
Wave D2 ── tauri deep features (parallel T-*; ∥ Wave D1 fully)
   │
Wave D3 ── non-enum alignment (T-heavy)  ∥  COORD handoffs (OPS)
   │
Wave D4 ── docs sync (E-DOCS ∥ T-DOCS)
   │
Wave D5 ── VERIFY (serial) + optional render smoke
   │
Wave D6 ── (CONDITIONAL) electron-forge after COORD
```

### Legend

- **R** read-only · **W** write · **S** serial gate · **P** parallel set

### Wave D0 — Research / baseline (max parallel R)

| ID | Kind | Task | Deps | Done when |
|----|------|------|------|-----------|
| D0.1 | R | Inventory electron gates → matrix | — | every electron jinja listed with gate expr |
| D0.2 | R | Inventory tauri gates + non-enum tokens | — | token→files map complete |
| D0.3 | R | Diff vs `template/copier.yml` desktop_* (read-only) | D0.1, D0.2 | enum/actual table |
| D0.4 | R | Electron IPC contract map (main/preload/shared/renderer) | — | channel list for updater/tray/titlebar |
| D0.5 | R | Tauri plugin/capability/Cargo map for enum features | — | conf/Cargo/cap matrix |
| D0.6 | R | Sample answers expected feature sets | — | electron-app / tauri-app recorded |
| D0.7 | R | Copier `_exclude` desktop paths vs real tree | — | mismatch note |
| D0.8 | S | Baseline validate + jinja | — | logs saved under `audit/` |

```bash
uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
uv run python scripts/ci/validate_jinja_templates.py template/files/electron template/files/tauri
```

### Wave D1 — Electron deep features (P with collision leads)

#### D1.U Updater (auto_updater)

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D1.U1 | E-MAIN | `src/main/updater.ts.jinja` | D0.4, D0.8 |
| D1.U2 | E-MAIN | preload update channels | D1.U1 |
| D1.U3 | E-MAIN | shared types update events | D1.U1 |
| D1.U4 | E-PKG | electron-builder publish/updater | D0.1 |
| D1.U5 | E-PKG | entitlements when mac+updater | D1.U4 |
| D1.U6 | E-PKG | package.json electron-updater/log | D1.U4 |
| D1.U7 | E-MAIN lead | wire init in `index.ts.jinja` | D1.U1–U3 |

#### D1.T Tray (tray_icon)

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D1.T1 | E-MAIN | `tray.ts.jinja` | D0.4 |
| D1.T2 | E-MAIN lead | index wiring | D1.T1 (serialize with D1.U7) |

#### D1.C Titlebar (custom_titlebar)

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D1.C1 | E-MAIN | `window.ts.jinja` frame/titleBarStyle | D0.4 |
| D1.C2 | E-UI | `TitleBar.tsx.jinja` | D0.4 |
| D1.C3 | E-UI | App.tsx + styles | D1.C2 |

#### D1.P Platforms

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D1.P1 | E-PKG | builder mac/win/linux vs `desktop_platforms` | D0.1 (serialize D1.U4) |
| D1.P2 | E-PKG | electron-vite/ts/eslint configs still correctly gated | D0.1 |

**Wave D1 verify:**

```bash
uv run python scripts/ci/validate_jinja_templates.py template/files/electron
uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
```

### Wave D2 — Tauri deep features (P; fully ∥ D1)

#### D2.U Updater

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D2.U1 | T-FE | `UpdateChecker.tsx.jinja` | D0.5 |
| D2.U2 | T-FE lead | App.tsx mount | D2.U1 |
| D2.U3 | T-RS | commands/main updater hooks | D0.5 |
| D2.U4 | T-CFG lead | Cargo + tauri.conf updater | D0.5 |
| D2.U5 | T-CFG | capabilities if needed | D2.U4 |

#### D2.T Tray

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D2.T1 | T-RS | `tray.rs.jinja` + lib/main | D0.5 |
| D2.T2 | T-CFG lead | trayIcon conf + Cargo | D0.5 (serialize D2.U4) |

#### D2.C Titlebar

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D2.C1 | T-CFG lead | decorations/hiddenTitle | D0.5 |
| D2.C2 | T-FE | TitleBar + App + styles | D0.5 (serialize App with D2.U2) |

#### D2.P Platforms

| ID | Sub-lane | Files | Deps |
|----|----------|-------|------|
| D2.P1 | T-CFG lead | bundle targets vs platforms | D0.5 |
| D2.P2 | T-CFG | icons/build/rustfmt gates | D0.5 |

**Wave D2 verify:**

```bash
uv run python scripts/ci/validate_jinja_templates.py template/files/tauri
uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
```

### Wave D3 — Non-enum + handoffs (P)

| ID | Kind | Task | Deps |
|----|------|------|------|
| D3.1 | W T-* | Align/neutralize `system_info` | D2 |
| D3.2 | W T-RS | Align/neutralize `menu` | D2 |
| D3.3 | W T-CFG | Align/neutralize `transparent_window`, `deep_linking` | D2 |
| D3.4 | W T-CFG | Align/neutralize `notifications`, `file_system` | D2 |
| D3.5 | OPS | Handoff non-enum tokens | D0.2, D0.3 |
| D3.6 | OPS | Handoff forge missing + exclusion mismatch | D0.7 |
| D3.7 | OPS | Handoff proposed forge layout post-exclusion rewrite | D3.6 |

### Wave D4 — Docs (E-DOCS ∥ T-DOCS)

| ID | Task | Deps |
|----|------|------|
| D4.1 | Electron README/.env match enum features/platforms | D1 |
| D4.2 | Tauri docs match enum reality (no false non-enum claims unless COORD keeps) | D2, D3 |

### Wave D5 — Closeout VERIFY (S)

| ID | Task | Automated |
|----|------|-----------|
| D5.1 | Jinja both trees | yes |
| D5.2 | validate electron-app | yes |
| D5.3 | validate tauri-app | yes |
| D5.4 | Optional render smoke electron-app | yes |
| D5.5 | Optional render smoke tauri-app | yes |
| D5.6 | Diff confined to electron/ + tauri/ (+ goals handoffs) | manual |

```bash
uv run python scripts/ci/validate_jinja_templates.py template/files/electron template/files/tauri
uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json
uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json
./scripts/render-samples.sh --variant electron-app --answers samples/electron-app/copier-answers.yml
./scripts/render-samples.sh --variant tauri-app --answers samples/tauri-app/copier-answers.yml
```

### Wave D6 — Conditional forge (blocked)

| ID | Task | Deps |
|----|------|------|
| D6.1 | COORD approval of exclusion shape + forge contract | D3.6, D3.7 |
| D6.2 | Scaffold under agreed path inside `electron/**` | D6.1 |
| D6.3 | Feature parity updater/tray/titlebar as applicable | D6.2 |
| D6.4 | Jinja + validate; PLATFORM owns any new sample answers | D6.3 |

## 4. Subagent dispatch template

```text
You are DESKTOP sub-lane <ID>.
WRITE ONLY: <paths>
FORBIDDEN: copier.yml, hooks, macros, catalog, other language trees, frontend/, node/saas/,
  src/riso/, web/, samples/**, lockfiles
RULES: no git branch/commit/push; no secrets; uv run for Python; no new Copier keys
TASKS: <task ids from plan>
COLLISION FILES: do not edit; file goals/riso-lane-desktop/handoffs/root-dep-<id>.md instead
VERIFY: <commands>
RETURN: summary, files touched, residual risks, handoffs filed
```

**Recommended fan-out after D0:**

| Agent | Tasks |
|-------|-------|
| E-MAIN | D1.U1–U3, D1.T1, D1.C1 + lead merges index/preload/types |
| E-UI | D1.C2–C3 |
| E-PKG | D1.U4–U6, D1.P* |
| T-FE | D2.U1–U2, D2.C2 |
| T-RS | D2.U3, D2.T1 |
| T-CFG | D2.U4–U5, D2.T2, D2.C1, D2.P* |
| OPS | D3.5–D3.7 anytime after D0 |

## 5. Risks

| Risk | Mitigation |
|------|------------|
| Collision-file thrash | Lead-only apply; root-dep handoffs |
| Over-stripping future features | COORD decide add vs strip; neutralize docs first |
| Exclusion mismatch | Never edit copier; D3.6 handoff |
| Render smoke cost | Optional after D5.1–D5.3 green |
| Cross-lane shared package.json at template root | Out of write roots → handoff |

## 6. Done when

- Enum deep features coherent on electron-vite + tauri
- COORD handoffs filed (forge, exclusions, non-enum)
- Validate both samples + jinja green
- Optional render smoke without hand-edited renders
- Diff only under `electron/**`, `tauri/**`, and `goals/riso-lane-desktop/**`
