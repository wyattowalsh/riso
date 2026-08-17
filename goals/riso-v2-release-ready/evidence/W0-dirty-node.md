# W0-T01b — Dirty-tree map, lane NODE

- Task: `W0-T01b`
- Wave: W0 / group W0A
- Lane: NODE
- Exclusive write roots: `template/files/node/**` except `template/files/node/saas/**`
- Verify: every dirty non-SaaS `node` path owned; keep-or-drop vs `plan.md`; `samples/*/render/` write count = 0
- Status: **green**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (tool cwd; `.git` present) |
| Branch | `main` (`.git/HEAD` → `ref: refs/heads/main`) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| `origin/main` | `6134759f78bdb2c8b160462d55e8b87b09d81291` — local `main` **ahead 34, behind 1** |
| Filter | `template/files/node/**` minus `template/files/node/saas/**` |

Commands required by the mission: `git status --short` and `git diff --name-only`.

This worker has no shell (`run_terminal_command` not in the subagent tool list; `.git/HEAD` `read_file` hook-denied). Porcelain was taken from live parent-session `git status --short` captures on this same HEAD, then confirmed against the current worktree:

- `.git/HEAD`, `.git/refs/heads/main`, `.git/refs/remotes/origin/main`, `.git/logs/HEAD` (via `grep`)
- Parent session `019ff9d6` terminal:
  - `call-2da8d941-…-63.log` — `git status --short` (428-line snapshot; NODE M/D block complete)
  - `call-6935198d-…-126.log` — later resume: dirty count **364**, `main`, mermaid `theme.ts.jinja` present, SaaS `runtime/{nextjs,remix}` present
  - `call-2b37110c-…-83.log` — launch-time `git status --short --branch`: still `main...origin/main [ahead 34, behind 1]`
- Live `list_dir` / `grep` on `template/files/node/**` (no `tailwind.config`; mermaid files present; saas runtimes present)

No git mutation. Branch not changed.

## NODE commits already on HEAD (not dirty)

These landed **before** current HEAD and are therefore not `git status` / `git diff` paths:

| SHA (short) | Subject |
| --- | --- |
| `de65da91` | `fix(template): align non-SaaS Node MCP and api-node correctness` |

July 29 W2 NODE payload work is committed. The rows below are **uncommitted Aug-13 dirty-tree polish** on top of that HEAD.

## Matching dirty paths (NODE filter)

`git status --short` ∩ `template/files/node/**` \ `template/files/node/saas/**`:

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `template/files/node/apps/api-node/src/main.ts.jinja` | **KEEP** — matching dirty-tree polish; does not fight 2.0 remap/lockstep |
| `M` | `template/files/node/docs/docusaurus/.github/workflows/deploy-docs.yml.jinja` | **KEEP** — docs deploy lockstep with mermaid/docs track (NODE-T01) |
| `M` | `template/files/node/docs/docusaurus/docs/guides/getting-started.md.jinja` | **KEEP** — mermaid/docs docusaurus (NODE-T01) |
| `M` | `template/files/node/docs/docusaurus/docs/reference/configuration.md.jinja` | **KEEP** — mermaid/docs docusaurus (NODE-T01) |
| `M` | `template/files/node/docs/docusaurus/docusaurus.config.ts.jinja` | **KEEP** — plan keep list “DESIGN + mermaid”; W2 NODE-T01 mermaid theme blocks |
| `M` | `template/files/node/docs/docusaurus/src/css/custom.css.jinja` | **KEEP** — mermaid/token lockstep (NODE-T01) |
| `M` | `template/files/node/docs/docusaurus/src/css/tailwind.css.jinja` | **KEEP** — Tailwind CSS (not `tailwind.config.ts`); NODE-T01 |
| `M` | `template/files/node/docs/docusaurus/src/pages/index.module.css.jinja` | **KEEP** — mermaid/docs docusaurus (NODE-T01) |
| `M` | `template/files/node/docs/docusaurus/static/img/logo.svg.jinja` | **KEEP** — matching polish |
| `M` | `template/files/node/docs/docusaurus/static/manifest.json.jinja` | **KEEP** — matching polish |
| `D` | `template/files/node/docs/docusaurus/tailwind.config.ts.jinja` | **KEEP deleted** — W2 NODE-T03: leftover `tailwind.config.ts` absence is intentional; do not restore |
| `M` | `template/files/node/docs/fumadocs/.env.example.jinja` | **KEEP** — mermaid/docs fumadocs (NODE-T02) |
| `M` | `template/files/node/docs/fumadocs/.github/workflows/deploy.yml.jinja` | **KEEP** — docs deploy lockstep (NODE-T02) |
| `M` | `template/files/node/docs/fumadocs/app/api/search/route.ts.jinja` | **KEEP** — mermaid/docs fumadocs (NODE-T02) |
| `M` | `template/files/node/docs/fumadocs/app/global.css.jinja` | **KEEP** — mermaid/token lockstep (NODE-T02) |
| `M` | `template/files/node/docs/fumadocs/app/shadcn-theme.css.jinja` | **KEEP** — mermaid/docs fumadocs (NODE-T02) |
| `M` | `template/files/node/docs/fumadocs/components/mermaid/index.tsx.jinja` | **KEEP** — plan keep list mermaid; NODE-T02 |
| `??` | `template/files/node/docs/fumadocs/components/mermaid/theme.ts.jinja` | **KEEP** — new mermaid theme file (worktree 3.9k, 2026-08-13); not in origin mermaid dir; not in tracked M/D block next to `index.tsx.jinja` |
| `M` | `template/files/node/docs/fumadocs/next.config.ts.jinja` | **KEEP** — mermaid/docs fumadocs (NODE-T02) |
| `M` | `template/files/node/docs/fumadocs/static/img/logo.svg.jinja` | **KEEP** — matching polish |

`git diff --name-only` ∩ same filter = the 18 `M` + 1 `D` rows (untracked `theme.ts.jinja` excluded).

**Count: 20** matching dirty paths (18 modified, 1 deleted, 1 untracked).

**Foreign (SAAS; listed only to exclude):** parent `git status --short` also showed many `M`/`D`/`??` under `template/files/node/saas/**`. Those belong to W0-T01c / SAAS. Not owned here. Later resume restored `runtime/{nextjs,remix}` (see SAAS confirm). Flatten copies stay **dropped** per `plan.md`.

## plan.md keep / drop (NODE)

| Item | Decision | Why |
| --- | --- | --- |
| DESIGN + mermaid (docusaurus theme blocks + fumadocs `components/mermaid/**`) | **KEEP** | `plan.md` “what stays from the dirty tree”; W2 NODE-T01 / NODE-T02 |
| Token/CSS lockstep (`custom.css`, `tailwind.css`, `global.css`, `shadcn-theme.css`) | **KEEP** | matching polish; no new vendor |
| Leftover `tailwind.config.ts` (docusaurus `.jinja`) | **KEEP deleted** | NODE-T03; worktree `rg tailwind.config` under `template/files/node` is empty |
| Restore `tailwind.config.ts` | **DROP** | fights NODE-T03 |
| SaaS Next/Remix flatten copies at saas app root | **DROP / SAAS** | plan “stays dropped”; not a NODE write |
| Hand-edit `samples/*/render/**` | **DROP / forbid** | hard forbid |
| Reintroduce `riso-mcp` | **DROP / forbid** | hard forbid |

## `samples/*/render/` write count

**0**

- Filter is `template/files/node/**` except `node/saas/**` — no `samples/**` path matches.
- No planned NODE write under `samples/*/render/`.
- Hard forbid: never hand-edit `samples/*/render/**`.

## SAAS runtime confirm (mission extra)

Not NODE write roots. Confirmed present for W0-T01c / W2 SAAS-T01/T02 (restore already landed; flatten stays dropped):

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** (`app/`, `lib/`, `docs/`, `tests/`, `middleware.ts.jinja`, `next.config.js.jinja`, `postcss.config.mjs.jinja`) |
| `template/files/node/saas/runtime/remix` | **yes** (`app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `remix.config.js.jinja`) |

## W2 NODE follow-through (no W0 rewrite)

- `NODE-T01` — mermaid/docs docusaurus (keep dirty jinja above).
- `NODE-T02` — mermaid/docs fumadocs (keep dirty jinja + new `theme.ts.jinja`).
- `NODE-T03` — `tailwind.config.ts` stays deleted.

No NODE residual. No files outside `goals/riso-v2-release-ready/evidence/W0-dirty-node.md` written.
