# W5-AUDIT — payloads-sys-desktop (read-only)

- **Mission:** `AUDIT-payloads-sys-desktop`
- **Lane:** `payloads-sys-desktop`
- **Date:** 2026-08-14
- **Repo:** `/Users/ww/dev/projects/riso` (workspace; `.git/HEAD` `read_file` hook-denied)
- **Branch:** `main` (`.git/refs/heads/main` → `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`; no checkout / stash / reset)
- **HEAD:** `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (`.git/logs/HEAD` last commit `docs(docs): W4 ASSURANCE report and handoffs closeout`)
- **Write root:** this file only
- **Product-code edits:** **0**
- **`samples/*/render/**` writes:** **0** (dests were read, never edited)
- **Python / `render_matrix.py`:** not invoked; no live matrix process observed or killed
- **Filter:** `template/files/go/**`, `template/files/rust/**`, `template/files/electron/**`, `template/files/tauri/**`, `template/files/mise.toml.jinja` (+ maintainer `.mise.toml` read-only)

SSOT read first: `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/{GOAL,PLATFORM,CLI,OPENSPEC,SKILL}.md`. Claims below are from live template / dest reads, not stale ASSURANCE or W2 join prose.

## Contract / method

Plan keep list + W2 SYS/DESK/MISE:

| Check | Required |
| --- | --- |
| `go.work` | KEEP `use ( . ; ./mcp )`; never `./cli` / `./api` |
| electron-store ESM | KEEP `externalizeDepsPlugin({ exclude: ['electron-store'] })` |
| Tauri linker | no `clang` / `lld` / `fuse-ld` in cargo config |
| Generated mise | `python = "3.11"`, `node = "20"` (do **not** raise to maintainer 22) |
| Maintainer `.mise.toml` | may stay Node 22 |
| Rust `_exclude`s | unchanged unless COORD outbox |
| OpenSpec extra | off by default (not this write root) |
| SaaS flatten | N/A to this lane (stays dropped) |

Method: `list_dir` + `read_file` + `grep` on live jinja. Official-matrix dests used as **smoke evidence only** (not SSOT when they disagree with current templates).

This session has no shell (`git rev-parse` / `uv run pytest` not executable).

## Checklist

| Item | Verdict | Live evidence |
| --- | --- | --- |
| `go.work.jinja` `.` + `./mcp` | **closed** | no `project_layout` gate; `_has_root` includes CLI/API/MCP Go; never `./cli`/`./api` |
| `go.mod.jinja` MCP-only parent | **closed** in source; dest stale | `{% if _has_cli_or_api or _has_mcp %}`; tests `test_go_mod_mcp_only_emits_workspace_parent` |
| `go/cli/internal/**` | **closed** (absent) | `template/files/go/cli/` is `cmd/` + `main.go.jinja` only |
| Rust `_exclude`s (7) | **closed** | same 7 lines as W2-SYS-T02 snapshot; COORD `copier.yml` |
| Rust MCP-only workspace | **closed** | virtual `[workspace] members = ["mcp"]`; dest `samples/rust-mcp/render/rust/Cargo.toml` matches |
| electron-store exclude | **closed** | main + preload L8/L24; dest `electron-app` render matches ×2 |
| ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` | **closed** | both `package.json.jinja`; `.eslintrc.cjs.jinja` present |
| `env.d.ts` / Tauri `vite-env.d.ts` | **closed** | files exist; tsconfigs include `*.d.ts`; dest confirms |
| no clang/lld | **closed** | `rg` empty under `template/files/{go,rust,electron}` and `tauri/src-tauri`; `.cargo` comment is “platform default linker” |
| Generated `mise.toml.jinja` floors | **closed** | `python = "3.11"`, `node = "20"`; no `22` in that file |
| Maintainer `.mise.toml` Node 22 | **closed** | `node = "22.23.1"` |
| Dual generated mise | **stale** | live `_exclude: ".mise.toml"`; dest still has both (PL-T06) |
| Empty dest `go.work` (go-api/cli/mcp) | **stale** | live jinja would emit; W3 dest predates the source fix |
| Empty dest `go.mod` (go-mcp only) | **stale** | live jinja emits MCP parent; dest `go/mcp/go.mod` is valid |

**No open P0/P1** on this lane’s live source after inspection.

## 1. Go — `go.work` / `go.mod` (SYS-T01)

Live `template/files/go/go.work.jinja`:

```1:17:template/files/go/go.work.jinja
{%- set _has_root = (cli_module == 'enabled' and 'go' in cli_languages)
                 or (api_module == 'enabled' and 'go' in api_languages)
                 or (mcp_module == 'enabled' and 'go' in mcp_languages) -%}
{%- set _has_mcp = mcp_module == 'enabled' and 'go' in mcp_languages -%}
{% if _has_root %}
go {{ go_version | default('1.24') }}
...
use (
	.
{%- if _has_mcp %}
	./mcp
{%- endif %}
)
{% endif %}
```

- No `project_layout == 'monorepo'` gate.
- Comment forbids `./cli` / `./api`.
- Unit tests in `tests/unit/test_go_templates.py` match the live file: `test_go_work_single_package_cli_lists_root`, `test_go_work_monorepo_mcp_only_lists_root_and_mcp` (W2-SYS-T01 names `test_go_work_single_package_cli_is_empty` / `…_lists_mcp` are **stale evidence**).

Live `go.mod.jinja` emits a root module when CLI/API **or** MCP Go is on (`test_go_mod_mcp_only_emits_workspace_parent`). `go/mcp/go.mod.jinja` stays `module {{ project_slug }}/mcp`.

**Stale dest (do not hand-edit):** official PL-T06 dests still show the **pre-fix** shape:

| Dest | `go.work` | root `go.mod` |
| --- | --- | --- |
| `samples/go-api/render/go/` | empty | `module riso-go-api` + gin/koanf |
| `samples/go-cli/render/go/` | empty | `module riso-go-cli` + cobra/koanf |
| `samples/go-mcp/render/go/` | empty | empty |
| `samples/go-mcp/render/go/mcp/go.mod` | — | valid `riso-go-mcp/mcp` + go-sdk |

W4-R02 memory / review notes that called empty single-package `go.work` and MCP-only empty `go.mod` **P0** are **stale vs live source**. Next official `render_matrix.py` / `render-samples.sh` will refresh dests. Do not residual `render_matrix`.

`template/files/go/cli/internal/**` remains **absent** (W0 DROP).

## 2. Rust — excludes + MCP-only workspace (SYS-T02)

Live COORD `_exclude` rust rows (7/7, unchanged vs `W2-SYS-rust-excludes.txt`):

- `rust/Makefile` / `rust/justfile` by `task_runner`
- `rust/` and `rust/Cargo.toml` unless any rust CLI/API/MCP
- `rust/mcp/`, `rust/cli/`, `rust/api/` per module

Live `template/files/rust/Cargo.toml.jinja`: MCP-only → virtual workspace `members = ["mcp"]` (no stub root crate). Dest `samples/rust-mcp/render/rust/Cargo.toml` matches. `rust/src/main.rs.jinja` is empty for MCP-only (gate requires rust-in-languages **and** no CLI/API/MCP modules). `rust/mcp/src/server.rs.jinja` is a real `rmcp` handler (not a placeholder). rust-version **1.81**.

go/rust matrix reds are **fumadocs** `next.config.ts` `output: string` TS2345 (NODE lane; sibling `W5-AUDIT-payloads-node.md` already closed that in source). Not a SYS compile/smoke.

## 3. Electron / Tauri (DESK-T01–T04)

### electron-store ESM exclude — closed

Live `template/files/electron/electron.vite.config.ts.jinja` L8 and L24:

```ts
plugins: [externalizeDepsPlugin({ exclude: ['electron-store'] })],
```

Main-process imports `Store from 'electron-store'` (`ipc.ts`, `tray.ts`, `window.ts`). `package.json.jinja` pins `electron-store: ^10.0.0` and `engines.node: ">=20.0.0"`. Dest `samples/electron-app/render/electron/electron.vite.config.ts` has the exclude **twice**. `render_status: ok`.

`tests/unit/test_electron_templates.py` asserts `externalizeDepsPlugin` is present but **does not** assert the `exclude: ['electron-store']` string. Implementation is correct; test tightness is below P1 (foreign `tests/**`).

### ESLint 9 + d.ts — closed

Both desktop `package.json.jinja` use `eslint: ^9.18.0` and `ESLINT_USE_FLAT_CONFIG=false`. Electron `.eslintrc.cjs.jinja` has react-hooks + react-refresh. `env.d.ts.jinja` types `window.api: ElectronAPI` (`storeGet` / theme / optional updater) to match preload. Tauri `vite-env.d.ts.jinja` is `/// <reference types="vite/client" />`. Tauri `tsconfig.json.jinja` include: `src/**/*.ts`, `src/**/*.tsx`, `src/**/*.d.ts`. Dest electron `env.d.ts` and tauri `vite-env.d.ts` match.

### no clang/lld — closed

Live `template/files/tauri/src-tauri/.cargo/config.toml.jinja`: incremental + Windows `/DEBUG:NONE` only. Comment: “Use the platform default linker.” `rg clang|lld|fuse-ld` on `template/files/tauri/src-tauri` is **empty**. Dest `samples/tauri-app/render/tauri/src-tauri/.cargo/config.toml` has neither. `tauri/.vscode/launch.json.jinja` still has `"type": "lldb"` (debugger, not linker) — left as-is. `render_status: ok`.

Tauri `Cargo.toml.jinja` `rust-version = "1.77.2"` is compatible with optional generated rust **1.81**; not a floor raise.

## 4. mise pins (MISE-T01–T03)

Live `template/files/mise.toml.jinja`:

```toml
[tools]
python = "3.11"
node = "20"
pnpm = "9.15.0"
uv = "0.4.30"
```

plus optional `rust = "1.81"` / `just = "1.34"` when those languages / `task_runner` match. **No `22`** in this file. Comment: generated Node floor is 20+; `mise install`.

Live maintainer `.mise.toml`: `python = "3.11"`, `node = "22.23.1"`, `pnpm = "11.11.0"`, `uv = "0.11.26"`. Floor not copied onto generated.

Live COORD `_exclude` (not this write root): `.mise.toml` — “mise.toml is the only generated mise config (Node pin 20).”

W1-C01 / `coord-outbox/mise-always.md` / W2-MISE-join “both always render” is **stale**. Live exclude is in `template/copier.yml` L2103–2104.

**Stale dest:** `samples/electron-app/render/` and `samples/tauri-app/render/` still contain **both** `mise.toml` (python 3.11 + node 20) **and** `.mise.toml` (node 20, **no python**, just 1.34). That is PL-T06 output from before the exclude (or before a re-render). Do not hand-delete dest files.

`samples/rust-mcp/render/mise.toml` lacks `rust = "1.81"`; live jinja would emit it for `mcp_languages: [rust]`. Dest stale vs current source.

## 5. Not elevated (below P1 / foreign)

- **Empty `electron/` tree on Tauri dest.** `copier.yml` excludes `electron/` only when `desktop_module != 'enabled'`. Tauri samples therefore copy `electron/**`; jinja gates empty the text files; static `resources/icon.*` still land. pnpm workspace does **not** include `electron/` or `tauri/`. `render_status: ok`. Owner **COORD** (`copier.yml` exclude should be `desktop_framework == 'electron-vite'`). Not a DESKTOP payload gate bug.
- **`electron-forge` choice** in `copier.yml` has no `electron/electron-forge/` payload. Official sample is `electron-vite`. No new vendor; not a 2.0 contract item.
- **Tauri mise does not pin rust** (desktop rust is not in `cli`/`api`/`mcp` language lists). MISE-T01 did not require a rust pin for desktop.
- **go/rust matrix fail** = fumadocs Next `output` typing (NODE). SYS/DESKTOP smoke is skipped (`quality_just` “not rendered”); electron/tauri matrix `ok`.
- **`openspec/` dirs** in dests → `residuals/OPENSPEC.md` (COORD). Default extra still `disabled`.
- **PAY-P0-06** (`riso-quality.yml.jinja` `tests/test_mcp.py`) is PLATFORM/payloads-py, not this lane.

## Findings (JSON companion)

| id | severity | file | issue |
| --- | --- | --- | --- |
| SYS-GO-WORK-KEEP | closed | `template/files/go/go.work.jinja` | Live `use ( . ; ./mcp )` for any Go track including single-package + MCP-only |
| SYS-GO-WORK-DEST-EMPTY | stale | `samples/go-*/render/go/go.work` | W3 dest empty; live jinja + tests already emit a non-empty `use (` |
| SYS-GOMOD-MCP-DEST | stale | `samples/go-mcp/render/go/go.mod` | W4-R02 P0; live `go.mod.jinja` emits MCP parent |
| SYS-RUST-MCP-WORKSPACE | closed | `template/files/rust/Cargo.toml.jinja` | Virtual workspace `members = ["mcp"]`; excludes unchanged |
| DESK-ELECTRON-STORE | closed | `template/files/electron/electron.vite.config.ts.jinja` | exclude on main + preload; dest confirms |
| DESK-NO-CLANG-LLD | closed | `template/files/tauri/src-tauri/.cargo/config.toml.jinja` | no clang/lld/fuse-ld |
| MISE-FLOORS | closed | `template/files/mise.toml.jinja` | python 3.11 / node 20; maintainer `.mise.toml` stays 22.23.1 |
| MISE-DUAL-DOTFILE | stale | `template/copier.yml` L2104 + dest `.mise.toml` | Dual always-on residual docs; live exclude + dest leftover from PL-T06 |

## Writes

This evidence file only. No commit / tag / push / PyPI. No `samples/*/render/**` edits. No lockfile edits. No `riso-mcp`. No residual file (`residuals/SYS.md` / `DESKTOP.md` / `MISE.md` not created — nothing blocking this lane).
