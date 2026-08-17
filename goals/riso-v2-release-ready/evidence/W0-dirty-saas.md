# W0-T01c — Dirty-tree map, lane SAAS

- Task: `W0-T01c`
- Wave: W0 / group W0A
- Lane: SAAS
- Exclusive write roots: `template/files/node/saas/**`, `template/files/saas-starter/**`
- Filter: `template/files/node/saas/**` and any `saas-starter` path
- Verify: `runtime/{nextjs,remix}` noted present; keep-or-drop vs `plan.md`; `samples/*/render/` write count = 0
- Status: **green**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (tool cwd; `.git` present) |
| Branch | `main` (`.git/HEAD` → `ref: refs/heads/main`) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| `origin/main` | `6134759f78bdb2c8b160462d55e8b87b09d81291` — **behind** local `main` |
| Filter | keep only `template/files/node/saas/**` and `saas-starter` |

Commands required by the mission: `git status --short` and `git diff --name-only`.

This worker has no shell (`run_terminal_command` not available). Porcelain was reconstructed from:

- `.git/HEAD`, `.git/refs/heads/main`, `.git/refs/remotes/origin/main`, `.git/logs/HEAD`, `.git/COMMIT_EDITMSG`
- worktree inventory of `template/files/node/saas/**` and `template/files/saas-starter/**`
- flatten-copy probes at the `node/saas` package root
- `origin/main` GitHub contents/tree for `template/files/node/saas` (including recursive `runtime/`) and `template/files/saas-starter`
- committed SAAS history (reflog + `goals/riso-lanes-assurance/evidence/W2-SAAS-sweep.md`)
- `samples/*/render/` absence / `.gitignore`

No git mutation. Branch not changed.

## SAAS commits already on HEAD (not dirty)

These landed **before** current HEAD and are therefore not `git status` / `git diff` paths:

| SHA (short) | Subject |
| --- | --- |
| `bfd6f00` | `fix(template): runtime-aware SAAS auth/billing and starter alignment` |
| `08a93e7` | `docs: record W2 SAAS verification evidence and empty residual` |

HEAD is a later docs/assurance commit. SAAS payload trees are in that history.

## Matching dirty paths (SAAS filter)

`git status --short` ∩ `{template/files/node/saas/**, **saas-starter**}`:

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| — | *(none)* | — |

`git diff --name-only` ∩ same filter: **empty**.

**Count: 0** matching dirty paths.

Worktree layout is the committed / restored SAAS shape, not a new uncommitted flatten:

| Check | Result |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **present** (plan KEEP; W2 `SAAS-T01`) |
| `template/files/node/saas/runtime/remix` | **present** (plan KEEP; W2 `SAAS-T02`) |
| Flatten copies at `node/saas` root (`next.config.js.jinja`, `remix.config.js.jinja`, `middleware.ts.jinja`, `app/page.tsx.jinja`, `app/layout.tsx.jinja`, `app/root.tsx.jinja`) | **absent** (plan DROP; W2 `SAAS-T03`) |
| `template/files/node/saas/app/` | only `api/examples/**` (shared API examples; not a mixed Next+Remix app root) |
| `template/files/saas-starter/README.md.jinja` | present |
| `template/files/saas-starter/saas-starter.config.ts.jinja` | present |
| Repo-root `saas-starter/` | **absent** (not a write root) |
| `samples/saas-starter/**` | answers/metadata only (PLATFORM lock); no `render/` dir |
| Untracked extras under SAAS write roots | **none** observed |

## plan.md keep / drop (SAAS)

`plan.md` “what stays from the dirty tree” / W2 SAAS tasks — applied even though those files are **already committed or already restored** (not currently dirty):

| Item | Decision | Why |
| --- | --- | --- |
| `template/files/node/saas/runtime/nextjs/**` | **KEEP** | `plan.md` keep list; W2 `SAAS-T01`; Copier still targets runtime paths |
| `template/files/node/saas/runtime/remix/**` | **KEEP** | `plan.md` keep list; W2 `SAAS-T02` |
| `template/files/saas-starter/**` | **KEEP** | exclusive SAAS write root; starter README + config |
| SaaS Next/Remix flatten copies at `node/saas` app root | **DROP** | plan “stays dropped”; incomplete flatten broke generation; W2 `SAAS-T03` |
| Token/a11y polish only (no new vendors/runtimes/hosts) | **KEEP** (later W2 `SAAS-T04`) | no new runtime/host; not a W0 rewrite |
| Hand-edit `samples/*/render/**` | **DROP / forbid** | hard forbid |
| Maintainer `riso-mcp` | **DROP** | hard forbid |

## `samples/*/render/` write count

**0**

- SAAS filter is `template/files/node/saas/**` and `saas-starter`. No path under those roots is `samples/*/render/**`.
- `samples/saas-starter/all-in-one/render` is not present in the worktree.
- `.gitignore` has `samples/*/render/` (ignored; not a planned SAAS write).
- No SAAS-lane write under `samples/*/render/` is planned (`plan.md` hard forbid).

## SAAS runtime confirm (mission required)

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** (`app/`, `lib/`, `docs/`, `tests/`, `middleware.ts.jinja`, `next.config.js.jinja`, `postcss.config.mjs.jinja`) |
| `template/files/node/saas/runtime/remix` | **yes** (`app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `remix.config.js.jinja`) |

## W2 SAAS follow-through (no W0 rewrite)

- `SAAS-T01` — `runtime/nextjs` present (already in tree).
- `SAAS-T02` — `runtime/remix` present (already in tree).
- `SAAS-T03` — no flatten copies at saas app root (already absent).
- `SAAS-T04` — token/a11y polish only after T03; no new vendors.

No SAAS residual. No files outside `goals/riso-v2-release-ready/evidence/W0-dirty-saas.md` written.
