# W0-T03 — Keep / drop per lane

- Task: `W0-T03`
- Wave: W0 / group W0B
- Deps: `W0-T01j`
- Exclusive write: `goals/riso-v2-release-ready/evidence/W0-keep-drop.md`
- Verify: SaaS Next/Remix flatten **stays dropped**
- Status: **green**

Source of paths: [`W0-inventory.md`](./W0-inventory.md). Plan keep/drop: `plan.md` L24–26 + W2 task ids.

## Required keep (must not rewrite)

Live worktree checked this session.

| Item | Evidence | Decision |
| --- | --- | --- |
| Desktop Electron ESM (`electron-store`) | `template/files/electron/electron.vite.config.ts.jinja` uses `externalizeDepsPlugin({ exclude: ['electron-store'] })` on main + preload | **KEEP** (DESK-T01) |
| `go.work` `.` + `./mcp` | `template/files/go/go.work.jinja` `use` lists `.` and `./mcp`; comment forbids `./cli` / `./api` | **KEEP** (SYS-T01) |
| `BaseCommand.execute()` | `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja` validates then `run()` | **KEEP** (PY-T07) |
| `--skip-post-gen` | `src/riso/cli/app.py` option + `_GLOBAL_FLAGS` contains `"--skip-post-gen"` | **KEEP** (CLI-T17) |
| DESIGN + mermaid | `template/files/DESIGN.md.jinja`; PY DESIGN tokens / mpl / plotly / `custom.js.jinja`; NODE docusaurus mermaid blocks + fumadocs `components/mermaid/{index,theme}.ts.jinja` | **KEEP** (PY-T06, NODE-T01/T02) |

## Required drop

| Item | Evidence | Decision |
| --- | --- | --- |
| SaaS Next/Remix flatten at `node/saas` app root | Root `next.config.js.jinja`, `remix.config.js.jinja`, `middleware.ts.jinja`, `app/page.tsx.jinja`, `app/layout.tsx.jinja`, `app/root.tsx.jinja` **do not exist**. `app/` is only `api/examples/**`. `runtime/nextjs` and `runtime/remix` **are present**. | **DROP** (stay dropped; SAAS-T03) |
| Idle-gate pytest `.jinja` collection hack | Generated `pyproject.toml.jinja` has no `python_files` widening | **DROP** (PY-T08) |
| Maintainer `riso-mcp` | Not in dirty tree; hard forbid | **DROP** |
| Dual-path aliases after remap | Remap contract: apply then reject leftovers | **DROP** (W1/W2 implement) |
| Hand-edit `samples/*/render/**` | `.gitignore` + `hard_forbid`; join write count **0** | **DROP / forbid** |

## Per-lane

### COORD

| Item | Decision |
| --- | --- |
| `template/files/module_catalog.json.jinja` dirty polish | **KEEP** until W1-C04 (ty / mise / OpenSpec extra) |
| `copier.yml`, hooks | not dirty; W1 serial; `openspec_extra` default off; always-on generated `mise.toml` |
| Dual-path / leftover old keys in hooks | **DROP** after W1-C07 apply-then-reject |

### CLI

| Item | Decision |
| --- | --- |
| `--skip-post-gen` in `_GLOBAL_FLAGS` | **KEEP** |
| `list_sample_variants` `os.scandir` CM | **KEEP** |
| Dirty `tests/unit/test_cli/test_{argv_normalize,output,recopy,validate}.py` | **KEEP** |
| `generation_gates` leftover `saas_auth` (committed, not dirty) | **DROP in W1-C06** (use module/provider) |
| Reject-before-remap at call sites | **REWRITE** W2 CLI-T10–T16 (`apply` then reject) |

### PY

| Item | Decision |
| --- | --- |
| DESIGN tokens / mpl / plotly / `custom.js.jinja` | **KEEP** |
| `BaseCommand.execute()` validate+run + `test_cli.py.jinja` | **KEEP** |
| pytest `python_files` = `test_*.py` only (no `.jinja` collection) | **KEEP** |
| ty/ruff/uv; mypy not default | **KEEP** |
| `.md` → `.md.jinja` docs renames | **KEEP the rename** |
| `hypothesis` + `respx` in `test` extra | **not in dirty tree** (`test = ["pytest>=8.4.2"]` only) — W2 PY-T01–T04 add |

### NODE

| Item | Decision |
| --- | --- |
| Docusaurus + fumadocs mermaid / token CSS | **KEEP** |
| New `theme.ts.jinja` | **KEEP** |
| Leftover `docs/docusaurus/tailwind.config.ts.jinja` | **KEEP deleted** (NODE-T03) |
| Restore `tailwind.config.ts` | **DROP** |

### SAAS

| Item | Decision |
| --- | --- |
| `runtime/nextjs/**` | **KEEP** (present) |
| `runtime/remix/**` | **KEEP** (present) |
| `template/files/saas-starter/**` | **KEEP** |
| Next/Remix flatten copies at `node/saas` root | **DROP** (absent; stay dropped) |
| Porcelain `M` integrations/README/package polish (39 paths) | **KEEP** matching polish; no new runtime/host/vendor (SAAS-T04) |

### SYS

| Item | Decision |
| --- | --- |
| `go.work` `use` `.` + `./mcp` | **KEEP** |
| Porcelain go/rust MCP polish (33 paths) | **KEEP** |
| Restore `template/files/go/cli/internal/**` | **DROP** |
| Rust `_exclude`s | **KEEP** unchanged unless COORD outbox (SYS-T02) |

### DESKTOP

| Item | Decision |
| --- | --- |
| electron-store `externalizeDepsPlugin({exclude})` | **KEEP** |
| ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` + plugins | **KEEP** |
| `env.d.ts.jinja` + Tauri `vite-env.d.ts.jinja` | **KEEP** |
| No clang/lld in Tauri cargo config | **KEEP** (local file is incremental + Windows `/DEBUG:NONE` only) |
| just recipes + remaining porcelain electron/tauri polish | **KEEP** |
| Drop any DESKTOP dirty path | **none** |

### WEB

| Item | Decision |
| --- | --- |
| Wizard a11y/focus/theme/store polish (all dirty `web/**`) | **KEEP** |
| Canonical keys in `store.ts` / `exportConfig.ts` | **KEEP** |
| Reject-only SSOT (`removedAnswerKeys.ts` not dirty) | **REWRITE** WEB-T01 to apply-then-reject (keep 8-key set) |

### PLATFORM

| Item | Decision |
| --- | --- |
| `render_matrix.py` + pruned `iter_sample_answer_files` | **KEEP** (PL-T06 blocking; not residualable) |
| Quality jinja + ci/hooks/setup test moves | **KEEP** |
| Sample answers | already clean of 8 old keys (W0-T02b) |

### DOCS / SKILL / MISE / GOAL

| Item | Decision |
| --- | --- |
| Maintainer + generated docs polish; `DESIGN.md.jinja`; AGENTS/CLAUDE pointers | **KEEP** |
| `docs/guides/v2-migration.md` | **add later** (W4-D01; not dirty) |
| CHANGELOG Unreleased 2.0.0 | **add later** (W4-D03; no tag) |
| Skill “do not convert” + 5-key list | **REWRITE** W1-C08 (8 keys; remap then fail-closed) |
| Generated `mise.toml.jinja` | **add later** (MISE-T01); Node pin **20**, not maintainer 22 |
| This-wave `evidence/W0-*` | **KEEP** |
| Prior `goals/riso-lane-*` and `goals/riso-lanes-assurance/**` | **KEEP as-is / do not edit** |
| Unlocked `pyproject.toml` | **do not edit in W0** |

## Flatten stay-dropped (explicit)

Do **not** restore these at `template/files/node/saas/` root (or mixed Next+Remix app tree):

- `next.config.js.jinja`, `remix.config.js.jinja`, `middleware.ts.jinja`
- `open-next.config.ts.jinja`, `postcss.config.mjs.jinja`
- `app/page.tsx.jinja`, `app/layout.tsx.jinja`, `app/root.tsx.jinja`, `app/globals.css.jinja`
- `app/(marketing)/**`, `app/admin/**`, `app/dashboard/**`, `app/routes/**`
- flatten copies of health/blog/cron routes, prisma/db, dual `lib/auth.ts` at root

Copier continues to emit runtime files from `runtime/nextjs/**` and `runtime/remix/**` only.

W0-T03 verify met: flatten stays dropped.
