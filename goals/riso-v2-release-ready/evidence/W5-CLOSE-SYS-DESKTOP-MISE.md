# W5-CLOSE-SYS-DESKTOP-MISE

- **Mission:** `CLOSE-SYS-DESKTOP-MISE`
- **Date:** 2026-08-14
- **Repo:** `/Users/ww/dev/projects/riso`
- **Branch:** `main` (unchanged; no checkout / stash / reset / rebase)
- **HEAD:** `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- **Exclusive write roots:** `template/files/go/**`, `template/files/rust/**`, `template/files/electron/**`, `template/files/tauri/**`, `template/files/mise.toml.jinja`
- **Also allowed:** this file; `residuals/SYS-DESKTOP-MISE.md` (not written)
- **Product-code edits this session:** **0**
- **`samples/*/render/**` writes:** **0**
- **Maintainer `.mise.toml` writes:** **0** (no pin bug)
- **Status:** **green** — lock has no remaining P0/P1

SSOT read first: `goal.md`, `facts.md`, `plan.md`, `ASSURANCE.md`, `residuals/{GOAL,PLATFORM,CLI,OPENSPEC,SKILL}.md`. Seeded/audit JSON treated as untrusted; every keep item re-read from live files.

## Assigned P0/P1 vs lock

None of the verified-gap or audit P0/P1 `file` values sit in this lock. Foreign owners (NODE/PY/SAAS/COORD/PLATFORM/GOAL/WEB) left untouched.

Seeded keep-work (re-verified live, already implemented; not rewritten):

| Keep | Live file | Live proof |
| --- | --- | --- |
| electron-store ESM exclude | `template/files/electron/electron.vite.config.ts.jinja` L8 + L24 | `externalizeDepsPlugin({ exclude: ['electron-store'] })` on main + preload |
| `go.work` `.` + `./mcp` | `template/files/go/go.work.jinja` | no `project_layout` gate; `_has_root` includes CLI/API/MCP Go; never `./cli`/`./api` |
| Generated floors | `template/files/mise.toml.jinja` L6–7 | `python = "3.11"`, `node = "20"`; **no** `22` in that file |
| Maintainer Node 22 | `.mise.toml` L7 | `node = "22.23.1"`; `git status --short -- .mise.toml` empty |

## Checklist (live)

| Item | Verdict | Evidence |
| --- | --- | --- |
| `go.work` `.` + `./mcp` | **closed** | jinja emits `use (` + `.` + optional `./mcp`; tests `test_go_work_*` pass |
| `go.mod` MCP-only parent | **closed** | `{% if _has_cli_or_api or _has_mcp %}`; `test_go_mod_mcp_only_emits_workspace_parent` |
| `go/cli/internal/**` | **closed** (absent) | `test ! -d template/files/go/cli/internal` |
| Rust `_exclude`s (7) | **closed** | same 7 COORD lines as `W2-SYS-rust-excludes.txt` (not this lock) |
| Rust MCP-only workspace | **closed** | virtual `[workspace] members = ["mcp"]`; dest `samples/rust-mcp/render/rust/Cargo.toml` matches |
| electron-store exclude | **closed** | live jinja ×2; dest `samples/electron-app/render/electron/electron.vite.config.ts` matches |
| ESLint 9 + `ESLINT_USE_FLAT_CONFIG=false` | **closed** | both `package.json.jinja`; `.eslintrc.cjs.jinja` present |
| `env.d.ts` / Tauri `vite-env.d.ts` | **closed** | files exist |
| no clang/lld | **closed** | `rg` empty under `template/files/tauri/src-tauri/.cargo`; dest cargo config is incremental + Windows `/DEBUG:NONE` only |
| Generated mise floors | **closed** | python 3.11 / node 20 / pnpm 9.15.0 / uv 0.4.30 |
| Maintainer `.mise.toml` | **closed** | Node 22.23.1 unchanged |
| Generated engines.node | **closed** | electron + tauri `>=20.0.0` |
| Assigned lock P0/P1 | **none** | no gap/audit item targets this lock |

## Dest staleness (not residualed; not a lock P0/P1)

Official W3 dests predate some source fixes. **Do not hand-edit `samples/*/render/**`.** Official `render-samples.sh` / `render_matrix.py` only.

| Dest | Live source would emit | Dest today |
| --- | --- | --- |
| `samples/go-{api,cli,mcp}/render/go/go.work` | non-empty `use (` + `.` (+ `./mcp` for MCP) | empty |
| `samples/go-mcp/render/go/go.mod` | `module riso-go-mcp` + `go 1.24` | empty |
| `samples/rust-mcp/render/mise.toml` | also `rust = "1.81"` (`mcp_languages: [rust]`) | python/node/pnpm/uv only |
| `samples/{electron,tauri}-app/render/.mise.toml` | excluded by COORD `copier.yml` L2101 | leftover dual file from PL-T06 |

Go/rust matrix `render_status=failed` is **fumadocs** `output: string` (NODE), not SYS compile. Electron/tauri matrix rows are `ok`.

## Verify (this session)

```text
git rev-parse --show-toplevel
# /Users/ww/dev/projects/riso
git rev-parse --abbrev-ref HEAD
# main
git rev-parse HEAD
# f7951fe62e7c635f3a90d17811d3711c2a2d7c1b

uv run pytest tests/unit/test_go_templates.py \
  tests/unit/test_electron_templates.py \
  tests/unit/test_new_templates.py -q -n 0
# 108 passed

find template/files/go template/files/rust template/files/electron template/files/tauri \
  -name '*.jinja' -print0 \
  | xargs -0 uv run python scripts/ci/validate_jinja_templates.py
# Validated 148 Jinja template(s): all OK
uv run python scripts/ci/validate_jinja_templates.py template/files/mise.toml.jinja
# Validated 1 Jinja template(s): all OK

# 8/8 ok:true
uv run riso validate --answers-file samples/{go-api,go-cli,go-mcp,rust-api,rust-cli,rust-mcp,electron-app,tauri-app}/copier-answers.yml --json
```

## Path lock

| Class | Count |
| --- | --- |
| This-session product writes | **0** |
| This-session evidence writes | this file |
| `samples/*/render/**` hand-edits | **0** |
| Lockfile hand-edits | **0** |
| Maintainer `.mise.toml` | **0** |
| Secrets printed | **0** |
| Residual file | **none** (nothing blocking this lock) |

No commit / tag / push / PyPI. No `riso-mcp`. Generated Node floor not raised to 22. OpenSpec extra not touched. SaaS flatten not touched.
