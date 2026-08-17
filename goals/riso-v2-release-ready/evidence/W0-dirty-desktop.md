# W0-T01e — Dirty-tree map DESKTOP

- Task: W0-T01e
- Wave: W0 / group W0A
- Lane lock: `template/files/electron/**`, `template/files/tauri/**`
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (`.git/refs/heads/main`)
- HEAD: `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — last reflog commit `docs(docs): W4 ASSURANCE report and handoffs closeout` (2026-07-29)
- When: 2026-08-13
- Verify: every dirty `template/files/electron/**` and `template/files/tauri/**` path listed; keep-or-drop vs `plan.md`; `samples/*/render/**` write count **0**

## Commands

This subagent has no shell (`git status` / `git diff` / `git rev-parse` not executable). `.git/HEAD` is hook-denied; loose refs and content compare were used instead.

```text
# Intended (blocked here — no porcelain runner)
git rev-parse --show-toplevel   # expected: /Users/ww/dev/projects/riso
git status --short
git diff --name-only

# Recovered
.git/refs/heads/main     → f7951fe62e7c635f3a90d17811d3711c2a2d7c1b
.git/logs/HEAD           → last commit f7951fe (W4 ASSURANCE, 2026-07-29)
.git/refs/remotes/origin/main → 6134759f78bdb2c8b160462d55e8b87b09d81291 (stale fetch; GitHub main is the same 1.2.11)
```

Filter: keep only `template/files/electron/**` and `template/files/tauri/**`.

**Dirty = worktree vs local HEAD (`f7951fe`).** That HEAD is not on GitHub (422). Origin/main `6134759` (2026-06-26) is far behind local commits. Files that differ from origin **only** because of the 2026-07-29 DESKTOP commit `75eca3e` (`fix(template): gate electron and tauri desktop deep features`) are **in HEAD, not dirty**. Listed below are paths that are new or further-edited after that HEAD (Aug 13 boot/lint/typecheck keep-fixes + just recipes).

Status codes (inferred, not porcelain): `M` tracked content change vs HEAD/origin baseline after subtracting the July 29 gate commit · `??` absent from origin/main tree and absent from the July 29 DESKTOP payload list.

## Matching dirty paths

| Status | Path | keep / drop vs `plan.md` | Why |
| --- | --- | --- | --- |
| `M` | `template/files/electron/electron.vite.config.ts.jinja` | **KEEP** | `plan.md` L24 + DESK-T01: `externalizeDepsPlugin({ exclude: ['electron-store'] })`. Origin still has bare `externalizeDepsPlugin()`. |
| `M` | `template/files/electron/package.json.jinja` | **KEEP** | DESK-T02: `ESLINT_USE_FLAT_CONFIG=false`, ESLint 9 plugins (`eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `@typescript-eslint/*`). Also carries July 29 updater/platform gates (already in HEAD; extra lint/pnpm edits are the post-HEAD dirty). |
| `M` | `template/files/electron/tsconfig.web.json.jinja` | **KEEP** | DESK-T03 companion: `include` adds `src/renderer/**/*.d.ts` so `env.d.ts` is typechecked. Origin include has no `*.d.ts`. |
| `??` | `template/files/electron/src/renderer/env.d.ts.jinja` | **KEEP** | DESK-T03 + L24: Vite/`window.api` types. 404 on origin/main. |
| `??` | `template/files/electron/justfile.jinja` | **KEEP** | Matching polish. Generated just is canon (`facts.md` task_runner / just+uv). Not a flatten-style fight. |
| `M` | `template/files/tauri/package.json.jinja` | **KEEP** | DESK-T02: `ESLINT_USE_FLAT_CONFIG=false` + `@typescript-eslint/*` / prettier-plugin. July 29 `auto_updater` plugin gates stay (HEAD). |
| `??` | `template/files/tauri/src/vite-env.d.ts.jinja` | **KEEP** | DESK-T03 + L24. 404 on origin/main. |
| `??` | `template/files/tauri/justfile.jinja` | **KEEP** | Same just-canon polish as Electron. |
| `M` | `template/files/tauri/src-tauri/.cargo/config.toml.jinja` | **KEEP** | DESK-T04 + L24: no clang/lld. Origin still has `linker = "clang"` and `link-arg=-fuse-ld=lld`. Local is incremental + Windows `/DEBUG:NONE` only. |

**Dirty count:** 9 (5 Electron, 4 Tauri). **Drop:** none in this lane.

## Not dirty (do not treat as W0 inventory)

These differ from origin/main because they are **already in local HEAD** (July 29 feature-gate commit / earlier), or they **match** origin:

| Path | Reason excluded |
| --- | --- |
| `template/files/electron/.eslintrc.cjs.jinja` | Byte-identical to origin/main. ESLint 9 version already on origin `package.json` (`eslint: ^9.18.0`). |
| `template/files/tauri/.eslintrc.cjs.jinja` | Byte-identical to origin/main. |
| `template/files/tauri/tsconfig.json.jinja` | Byte-identical to origin/main. |
| `template/files/electron/src/main/{window,ipc,tray,updater,menu}.ts.jinja` and Tauri `src-tauri/**` feature-gate files (`main.rs`, `Cargo.toml`, `capabilities`, `tauri.conf.json`, `commands.rs`, `menu.rs`, `UpdateChecker.tsx`, `README.md`) | July 29 `75eca3e` payload (`goals/riso-lanes-assurance/evidence/W2-DESKTOP-summary.md`). In HEAD. W2 DESK-T* keeps those; they are not post-HEAD dirty. |

## `samples/*/render/` write count

**0**

No dirty path under this lane is `samples/*/render/**`. Filter roots are only `template/files/electron/**` and `template/files/tauri/**`. Hard-forbid honored.

## SAAS runtime presence (requested confirm)

Not a DESKTOP write. Existence only:

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** (app/, docs/, lib/, middleware, next.config, postcss, tests) |
| `template/files/node/saas/runtime/remix` | **yes** (`app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `remix.config.js.jinja`) |

Matches `plan.md` “SaaS `runtime/{nextjs,remix}` restored” / SAAS-T01–T02. Flatten stays dropped.

## Plan keep-list coverage (DESKTOP)

| `plan.md` keep / W2 task | Dirty path(s) | Verdict |
| --- | --- | --- |
| electron-store `externalizeDepsPlugin({exclude})` / DESK-T01 | `electron.vite.config.ts.jinja` | KEEP |
| ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` + plugins / DESK-T02 | both `package.json.jinja` | KEEP |
| `env.d.ts.jinja` + Tauri `vite-env.d.ts.jinja` / DESK-T03 | new d.ts + `tsconfig.web.json.jinja` include | KEEP |
| no clang/lld in Tauri cargo config / DESK-T04 | `.cargo/config.toml.jinja` | KEEP (lld already gone locally) |
| just recipes (matching polish) | both `justfile.jinja` | KEEP |

## Join notes for W0-T01j / W0-T03

- Re-run `git status --short` + `git diff --name-only` when a porcelain runner is available; replace inferred `M`/`??` with real codes if they differ.
- No DESKTOP dirty path should be dropped. None fights the goal.
- Exclusive write for this task: this file only.
