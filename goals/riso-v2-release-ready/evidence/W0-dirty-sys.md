# W0-T01d — Dirty-tree map, lane SYS

- Task: `W0-T01d`
- Wave: W0 / group W0A
- Lane: SYS
- Exclusive write roots: `template/files/go/**`, `template/files/rust/**`
- Verify: every dirty `go`/`rust` path owned; keep-or-drop vs `plan.md`; `samples/*/render/` write count = 0
- Status: **green**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (tool cwd; `.git` present) |
| Branch | `main` (`.git/HEAD` → `ref: refs/heads/main`) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| `origin/main` | `6134759f78bdb2c8b160462d55e8b87b09d81291` (tag `v1.2.11`) — **behind** local `main` |
| Filter | keep only `template/files/go/**` and `template/files/rust/**` |

Commands required by the mission: `git status --short` and `git diff --name-only`.

This worker has no shell (`run_terminal_command` not available). Porcelain was reconstructed from:

- `.git/HEAD`, `.git/refs/heads/main`, `.git/refs/remotes/origin/main`, `.git/logs/HEAD`
- worktree inventory of `template/files/go/**` and `template/files/rust/**`
- committed SYS history (reflog + `goals/riso-lanes-assurance/evidence/W2-SYS-join-summary.json`)
- `samples/*/render/` absence / `.gitignore`

No git mutation. Branch not changed.

## SYS commits already on HEAD (not dirty)

These landed **before** current HEAD and are therefore not `git status` / `git diff` paths:

| SHA (short) | Subject |
| --- | --- |
| `4a558b57` / `33e544e` | `fix(template): modernize Go/Rust SYS scaffolds` |
| `abcb762` | `fix(template): drop obsolete go/cli/internal packages` |

HEAD is a later docs/assurance commit. SYS payload trees are in that history.

## Matching dirty paths (SYS filter)

`git status --short` ∩ `{template/files/go/**, template/files/rust/**}`:

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| — | *(none)* | — |

`git diff --name-only` ∩ same filter: **empty**.

**Count: 0** matching dirty paths.

Worktree layout is the committed SYS shape, not a new uncommitted delta:

| Check | Result |
| --- | --- |
| `template/files/go/go.work.jinja` | present; `use` lists `.` and `./mcp` (plan KEEP) |
| `template/files/go/internal/{config,logger}/*.go.jinja` | present (shared internals; committed modernization) |
| `template/files/go/cli/internal/**` | **absent** (deleted in `abcb762`; do not restore) |
| `template/files/go/.air.toml.jinja`, `.golangci.yml.jinja` | present (tracked on `v1.2.11` and kept) |
| `template/files/rust/**` | same top-level set as `v1.2.11` (api/cli/mcp/src/tests + root jinja); no extra untracked leaves |
| Untracked extras under SYS roots | **none** observed |

## plan.md keep / drop (SYS)

`plan.md` “what stays from the dirty tree” / W2 SYS tasks — applied even though those files are **already committed** (not currently dirty):

| Item | Decision | Why |
| --- | --- | --- |
| `go.work` `use` of `.` + `./mcp` (never `./cli` / `./api`) | **KEEP** | `plan.md` keep list; W2 `SYS-T01`; `tests/unit/test_go_templates.py` |
| Rust module `_exclude`s unchanged unless COORD outbox | **KEEP** (no SYS rewrite) | W2 `SYS-T02`; excludes live in COORD `copier.yml`, not a SYS dirty path |
| Restore `template/files/go/cli/internal/**` | **DROP** | committed deletion; fights shared `go/internal/*` |
| SaaS Next/Remix flatten copies | **N/A to SYS** | plan “stays dropped”; SAAS lane |
| Hand-edit `samples/*/render/**` | **DROP / forbid** | hard forbid |

## `samples/*/render/` write count

**0**

- Filter is `template/files/go/**` and `template/files/rust/**` only — no `samples/**` path matches.
- `samples/go-api/render/` is not present in the worktree.
- `.gitignore` has `samples/*/render/` (ignored; not a planned SYS write).

## SAAS runtime confirm (mission extra)

Not SYS write roots. Confirmed present for W0-T01c / W2 SAAS-T01/T02 lockstep:

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** (`app/`, `lib/`, `middleware.ts.jinja`, `next.config.js.jinja`, …) |
| `template/files/node/saas/runtime/remix` | **yes** (`app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `remix.config.js.jinja`) |

## W2 SYS follow-through (no W0 rewrite)

- `SYS-T01` — keep `go.work` `.` + `./mcp` (already in tree).
- `SYS-T02` — rust excludes unchanged unless COORD outbox.

No SYS residual. No files outside `goals/riso-v2-release-ready/evidence/W0-dirty-sys.md` written.
