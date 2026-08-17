# W0-T01j — Joined dirty-tree inventory

- Task: `W0-T01j`
- Wave: W0 / group W0B
- Deps: W0-T01a … W0-T01f
- Exclusive write: `goals/riso-v2-release-ready/evidence/W0-inventory.md`
- Verify: every dirty path owned; planned `samples/*/render/` writes = **0**
- Status: **green**

Companion: [`W0-keep-drop.md`](./W0-keep-drop.md) (W0-T03). Checksum: `plan.taskgraph.json` (W0-T04; valid, no refresh).

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (`.git` present; `.git/refs/heads/main` readable) |
| Branch | `main` (porcelain: `main...origin/main [ahead 34, behind 1]`) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| `origin/main` | `6134759f78bdb2c8b160462d55e8b87b09d81291` (v1.2.11) |
| This worker | no shell; no git mutation; branch not changed |

## Sources (read, not invented)

| Kind | Path |
| --- | --- |
| Lane maps | `evidence/W0-dirty-{py,node,saas,sys,desktop,cross}.md` |
| Key hits | `evidence/W0-ssot-diff.md`, `W0-rg-samples.txt`, `W0-rg-web.txt`, `W0-rg-gates.txt` |
| Full porcelain | `019ffa08` `terminal/call-26af77c5-…-232.log` (`git status --short` + `git diff --name-only` + `git ls-files --others`) |
| Later deltas | `019ff9d6` `call-2da8d941-…-63.log` (`M pyproject.toml`); `call-2b37110c-…-83.log` (`M scripts/lib/paths.py`, `M src/riso/template/__init__.py`, `M electron.vite.config.ts.jinja`); `call-6935198d-…-126.log` (dirty count 364; SaaS `runtime/{nextjs,remix}` present) |
| Live worktree | `list_dir` / `read_file` / `grep` on this HEAD |

## Ownership rules

Plan exclusive locks (`plan.md` + `plan.taskgraph.json` `lane_locks`). First match wins.

| Lane | Roots |
| --- | --- |
| COORD | `template/copier.yml`, `template/hooks/**`, `template/macros/**`, `template/prompts/**`, `template/files/module_catalog.json.jinja`, `.github/context/**`, `template/files/.github/context/**` |
| CLI | `src/riso/**`, `tests/unit/test_cli/**` |
| PY | `template/files/python/**` |
| NODE | `template/files/node/**` except `node/saas/**` |
| SAAS | `template/files/node/saas/**`, `template/files/saas-starter/**` |
| SYS | `template/files/go/**`, `template/files/rust/**` |
| DESKTOP | `template/files/electron/**`, `template/files/tauri/**` |
| WEB | `web/**` (write lock is `web/src/**`, `web/tests/**`) |
| PLATFORM | `scripts/ci/**`, `scripts/lib/**`, `scripts/render-samples.sh`, `template/files/quality/**`, `samples/**/copier-answers.yml`, `samples/metadata/**`, `tests/unit/ci/**`, `tests/unit/hooks/**`, `tests/unit/setup_scripts/**`, `tests/unit/test_go_templates.py`, `tests/unit/test_task_runner_templates.py` |
| DOCS | `docs/**`, `CHANGELOG.md`, `template/files/docs/**`, `template/files/AGENTS.md.jinja`, `template/files/CLAUDE.md.jinja`, `template/files/DESIGN.md.jinja` |
| MISE | `template/files/mise.toml.jinja`, `.mise.toml` |
| SKILL | `.agents/skills/riso-release-readiness/**` |
| GOAL | `goals/riso-v2-release-ready/**` |
| PRIOR-GOAL | `goals/riso-lane-*/**`, `goals/riso-lanes-assurance/**` — owned so they are not unowned; **do not edit this wave** |
| UNLOCKED | maintainer `pyproject.toml` — no exclusive lock; **do not edit this wave** |
| OUT-OF-SCOPE | `.claude/**`, `.grok/**` — harness; **do not edit** |

Hard forbid: `samples/*/render/**`, lockfile hand-edits, secrets, reintroduce `riso-mcp`.

## Reconciliation (T01a–f vs porcelain vs worktree)

| Lane | T01 map | Porcelain ∩ filter | Live worktree | Join |
| --- | --- | --- | --- | --- |
| PY T01a | 63 owned | matches + later `test_cli.py.jinja` / `custom.js.jinja` | same | **63** (T01a) |
| NODE T01b | 20 owned | matches | mermaid `theme.ts.jinja` present; `tailwind.config.ts.jinja` absent | **20** (T01b) |
| SAAS T01c | **0** (treated as committed/restored) | 38 `M` + 25 runtime `D` + flatten `??` + 1 `saas-starter` `M` | **flatten gone**; `runtime/{nextjs,remix}` **present**; remaining `M` files still on disk | **39 KEEP polish** (missed `M`); flatten **DROP / gone**; runtime `D` **not current** |
| SYS T01d | **0** (treated as in HEAD) | 12 go `M` + 20 rust `M` + 1 rust `??` | those paths exist | **33** SYS KEEP |
| DESKTOP T01e | 9 (post-HEAD boot/lint) | extra electron/tauri `M`/`??` vs HEAD | ESM exclude, `env.d.ts`, `vite-env.d.ts`, no clang/lld | **9** (T01e) **+ 36** porcelain extras = **45** KEEP |
| CROSS T01f | 56 | matches + later `paths.py` / `__init__.py` | same | **56** (T01f) |
| Gaps | adjacent only | COORD/DOCS/PLATFORM/CLI tests/`pyproject.toml`/`goals/**` | present | owned below |

T01c/T01d undercount is closed here: those paths have owners. Flatten copies are **not** current dirty (deleted from the worktree after the 26af77c5 snapshot) and stay **dropped**.

## Counts (current dirty, owned)

| Owner | Paths | Notes |
| --- | ---: | --- |
| PY | 63 | T01a |
| NODE | 20 | T01b |
| SAAS | 39 | porcelain `M` still on disk; flatten not counted |
| SYS | 33 | porcelain `M`/`??` T01d omitted |
| DESKTOP | 45 | T01e 9 + porcelain extras |
| CLI | 6 | 2 CROSS + 4 `tests/unit/test_cli/**` |
| WEB | 29 | inside CROSS 56 |
| PLATFORM | 20 | 4 CROSS scripts + quality + ci/hooks/setup tests |
| DOCS | 24 | 21 CROSS docs + AGENTS/CLAUDE/DESIGN |
| COORD | 1 | `module_catalog.json.jinja` |
| UNLOCKED | 1 | `pyproject.toml` |
| PRIOR-GOAL | porcelain `M` 3 + `??` leaves | do not edit |
| GOAL | this-wave `evidence/W0-*` | this package |
| OUT-OF-SCOPE | 2 dir rows | `.claude/`, `.grok/` |
| **Current product dirty owned** | **281** | PY+NODE+SAAS+SYS+DESKTOP+CLI+WEB+PLATFORM+DOCS+COORD+UNLOCKED |
| Unowned | **0** | |
| Planned `samples/*/render/` writes | **0** | |

CROSS 56 = CLI 2 + WEB 29 + PLATFORM scripts 4 + DOCS maintainer/payload 21. Not double-counted in the 279.

## `samples/*/render/` write count

**0**

- No `samples/**/render/**` row in porcelain status, diff, or untracked dump.
- Live `samples/*/` listings: `copier-answers.yml` (+ some metadata). **No** `render/` directories.
- `.gitignore` L468: `samples/*/render/`.
- `plan.md` / `plan.taskgraph.json` `hard_forbid` includes `samples/*/render/**`.
- No W1–W4 task writes under `samples/*/render/` (PLATFORM owns answers + `samples/metadata/**` only).
- This join writes only this file.

## Path → owner

Status: `M` modified · `D` deleted · `R` rename · `??` untracked. Keep/drop vs `plan.md` (detail in `W0-keep-drop.md`).

### PY — `template/files/python/**` (63) — source T01a

All **KEEP** matching polish / PY-T05–T08. Hypothesis+respx **not yet** in dirty `test` extra.

| Status | Path |
| --- | --- |
| `M` | `template/files/python/coverage.cfg.jinja` |
| `M` | `template/files/python/docs/_static/css/components.css` |
| `M` | `template/files/python/docs/_static/css/custom.css` |
| `M` | `template/files/python/docs/_static/css/design-tokens.css` |
| `M` | `template/files/python/docs/_static/css/lucide-icons.css` |
| `M` | `template/files/python/docs/conf.py.jinja` |
| `M` | `template/files/python/pyproject.toml.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/example_async.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/init.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/list.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/plugin.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/quickstart.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/commands/version.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/exceptions.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/formatter.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/core/prompts.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/plugins/README.md.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/cli/plugins/example_plugin.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/codegen/EXAMPLES.md.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/codegen/README.md.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/config.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/mutations/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/queries/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/subscriptions/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/graphql_api/types/__init__.py.jinja` |
| `M` | `template/files/python/src/{{ package_name }}/quickstart.py.jinja` |
| `M` | `template/files/python/tests/codegen/fixtures/sample_templates/python-microservice/template.yml` |
| `M` | `template/files/python/tests/conftest.py.jinja` |
| `M` | `template/files/python/tests/graphql/__init__.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_auth.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_complexity.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_dataloaders.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_errors.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_mutations.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_playground.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_queries.py.jinja` |
| `M` | `template/files/python/tests/graphql/test_subscriptions.py.jinja` |
| `M` | `template/files/python/tests/test_cli_commands.py.jinja` |
| `M` | `template/files/python/tests/test_cli_config.py.jinja` |
| `M` | `template/files/python/tests/test_cli_formatters.py.jinja` |
| `M` | `template/files/python/tests/test_cli_plugins.py.jinja` |
| `M` | `template/files/python/tests/test_quickstart.py.jinja` |
| `M` | `template/files/python/tests/test_cli.py.jinja` |
| `D` | `template/files/python/docs/guides/quickstart.md` |
| `D` | `template/files/python/docs/guides/testing-strategy.md` |
| `D` | `template/files/python/docs/index.md` |
| `D` | `template/files/python/docs/tools/index.md` |
| `??` | `template/files/python/docs/_static/js/riso-plotly-template.json` |
| `??` | `template/files/python/docs/_static/mpl/riso.mplstyle` |
| `??` | `template/files/python/docs/_static/js/custom.js.jinja` |
| `??` | `template/files/python/docs/guides/quickstart.md.jinja` |
| `??` | `template/files/python/docs/guides/testing-strategy.md.jinja` |
| `??` | `template/files/python/docs/index.md.jinja` |
| `??` | `template/files/python/docs/tools/index.md.jinja` |

### NODE — `template/files/node/**` \ `saas/**` (20) — source T01b

All **KEEP**. `tailwind.config.ts.jinja` **KEEP deleted** (NODE-T03).

| Status | Path |
| --- | --- |
| `M` | `template/files/node/apps/api-node/src/main.ts.jinja` |
| `M` | `template/files/node/docs/docusaurus/.github/workflows/deploy-docs.yml.jinja` |
| `M` | `template/files/node/docs/docusaurus/docs/guides/getting-started.md.jinja` |
| `M` | `template/files/node/docs/docusaurus/docs/reference/configuration.md.jinja` |
| `M` | `template/files/node/docs/docusaurus/docusaurus.config.ts.jinja` |
| `M` | `template/files/node/docs/docusaurus/src/css/custom.css.jinja` |
| `M` | `template/files/node/docs/docusaurus/src/css/tailwind.css.jinja` |
| `M` | `template/files/node/docs/docusaurus/src/pages/index.module.css.jinja` |
| `M` | `template/files/node/docs/docusaurus/static/img/logo.svg.jinja` |
| `M` | `template/files/node/docs/docusaurus/static/manifest.json.jinja` |
| `D` | `template/files/node/docs/docusaurus/tailwind.config.ts.jinja` |
| `M` | `template/files/node/docs/fumadocs/.env.example.jinja` |
| `M` | `template/files/node/docs/fumadocs/.github/workflows/deploy.yml.jinja` |
| `M` | `template/files/node/docs/fumadocs/app/api/search/route.ts.jinja` |
| `M` | `template/files/node/docs/fumadocs/app/global.css.jinja` |
| `M` | `template/files/node/docs/fumadocs/app/shadcn-theme.css.jinja` |
| `M` | `template/files/node/docs/fumadocs/components/mermaid/index.tsx.jinja` |
| `??` | `template/files/node/docs/fumadocs/components/mermaid/theme.ts.jinja` |
| `M` | `template/files/node/docs/fumadocs/next.config.ts.jinja` |
| `M` | `template/files/node/docs/fumadocs/static/img/logo.svg.jinja` |

### SAAS — current dirty (39) — T01c gap closed

T01c reported 0. Parent porcelain still listed these as `M`; they exist on disk. **KEEP** matching polish (not flatten). W2 SAAS-T04 token/a11y only; no new vendors.

| Status | Path |
| --- | --- |
| `M` | `template/files/node/saas/Dockerfile.jinja` |
| `M` | `template/files/node/saas/README.md.jinja` |
| `M` | `template/files/node/saas/components.json.jinja` |
| `M` | `template/files/node/saas/components/LanguageSwitcher.tsx.jinja` |
| `M` | `template/files/node/saas/components/layouts/dashboard.tsx.jinja` |
| `M` | `template/files/node/saas/components/search/SearchDialog.tsx.jinja` |
| `M` | `template/files/node/saas/components/settings/index.tsx.jinja` |
| `M` | `template/files/node/saas/docs/ARCHITECTURE.md.jinja` |
| `M` | `template/files/node/saas/hosting/cloudflare/wrangler.toml.jinja` |
| `M` | `template/files/node/saas/integrations/ai/anthropic/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/ai/openai/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/analytics/amplitude/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/analytics/posthog/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/auth/helpers.ts.jinja` |
| `M` | `template/files/node/saas/integrations/email/postmark/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/email/resend/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/email/templates/index.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/email/templates/invoice.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/email/templates/password-reset.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/email/templates/subscription-change.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/email/templates/team-invite.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/email/templates/welcome.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/jobs/inngest/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/jobs/trigger/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/marketing/landing/components.tsx.jinja` |
| `M` | `template/files/node/saas/integrations/scheduler/cron.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/algolia/README.md.jinja` |
| `M` | `template/files/node/saas/integrations/search/algolia/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/algolia/hooks.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/algolia/index.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/algolia/types.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/meilisearch/README.md.jinja` |
| `M` | `template/files/node/saas/integrations/search/meilisearch/client.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/meilisearch/hooks.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/meilisearch/index.ts.jinja` |
| `M` | `template/files/node/saas/integrations/search/meilisearch/types.ts.jinja` |
| `M` | `template/files/node/saas/lib/multi-tenant/README.md.jinja` |
| `M` | `template/files/node/saas/package.json.jinja` |
| `M` | `template/files/saas-starter/README.md.jinja` |

**Not current dirty (stay dropped / restored):**

| Was | Path | Now |
| --- | --- | --- |
| `??` flatten at `node/saas` root | `next.config.js.jinja`, `remix.config.js.jinja`, `middleware.ts.jinja`, `open-next.config.ts.jinja`, `postcss.config.mjs.jinja`, `app/page.tsx.jinja`, `app/layout.tsx.jinja`, `app/root.tsx.jinja`, `app/globals.css.jinja`, `app/(marketing)/**`, `app/admin/**`, `app/api/blog/**`, `app/api/cron/**`, `app/api/health/**`, `app/dashboard/**`, `app/routes/**`, `app/styles/**`, plus flatten `lib/*`, `db/`, `hooks/`, `prisma/`, `public/`, `tests/api/` | **absent** (read_file 404 on root Next/Remix configs). `app/` is only `api/examples/**`. |
| `D` runtime | `template/files/node/saas/runtime/nextjs/**`, `runtime/remix/**` | **present** (SAAS-T01/T02). Do not re-delete. |

### SYS — T01d gap closed (33)

T01d reported 0. Porcelain `M`/`??` still on disk. **KEEP**. `go.work` `.`+`./mcp` is in-tree (SYS-T01). Do not restore `go/cli/internal/**`.

| Status | Path |
| --- | --- |
| `M` | `template/files/go/api/internal/handlers/health.go.jinja` |
| `M` | `template/files/go/api/internal/server/server.go.jinja` |
| `M` | `template/files/go/mcp/README.md.jinja` |
| `M` | `template/files/go/mcp/cmd/server/main.go.jinja` |
| `M` | `template/files/go/mcp/go.mod.jinja` |
| `M` | `template/files/go/mcp/internal/mcp/resources.go.jinja` |
| `M` | `template/files/go/mcp/internal/mcp/server.go.jinja` |
| `M` | `template/files/go/mcp/internal/mcp/tools.go.jinja` |
| `M` | `template/files/go/mcp/internal/resources/system.go.jinja` |
| `M` | `template/files/go/mcp/internal/tools/echo.go.jinja` |
| `M` | `template/files/go/mcp/internal/tools/http_fetch.go.jinja` |
| `M` | `template/files/go/mcp/internal/tools/timestamp.go.jinja` |
| `M` | `template/files/rust/Cargo.toml.jinja` |
| `M` | `template/files/rust/Makefile.jinja` |
| `M` | `template/files/rust/justfile.jinja` |
| `M` | `template/files/rust/mcp/Cargo.toml.jinja` |
| `M` | `template/files/rust/mcp/README.md.jinja` |
| `M` | `template/files/rust/mcp/justfile.jinja` |
| `M` | `template/files/rust/mcp/src/lib.rs.jinja` |
| `M` | `template/files/rust/mcp/src/main.rs.jinja` |
| `M` | `template/files/rust/mcp/src/prompts/mod.rs.jinja` |
| `M` | `template/files/rust/mcp/src/prompts/review.rs.jinja` |
| `M` | `template/files/rust/mcp/src/resources/mod.rs.jinja` |
| `M` | `template/files/rust/mcp/src/resources/system.rs.jinja` |
| `M` | `template/files/rust/mcp/src/tools/echo.rs.jinja` |
| `M` | `template/files/rust/mcp/src/tools/http_fetch.rs.jinja` |
| `M` | `template/files/rust/mcp/src/tools/mod.rs.jinja` |
| `M` | `template/files/rust/mcp/src/tools/timestamp.rs.jinja` |
| `M` | `template/files/rust/mcp/src/transport/http.rs.jinja` |
| `M` | `template/files/rust/mcp/src/transport/mod.rs.jinja` |
| `M` | `template/files/rust/mcp/src/transport/sse.rs.jinja` |
| `M` | `template/files/rust/src/main.rs.jinja` |
| `??` | `template/files/rust/mcp/src/server.rs.jinja` |

### DESKTOP (45)

T01e 9 **plus** porcelain extras vs HEAD. All **KEEP** (desktop ESM / ESLint 9 / d.ts / no clang-lld / just polish).

| Status | Path | In T01e? |
| --- | --- | --- |
| `M` | `template/files/electron/electron.vite.config.ts.jinja` | yes |
| `M` | `template/files/electron/package.json.jinja` | yes |
| `M` | `template/files/electron/tsconfig.web.json.jinja` | yes |
| `??` | `template/files/electron/src/renderer/env.d.ts.jinja` | yes |
| `??` | `template/files/electron/justfile.jinja` | yes |
| `M` | `template/files/tauri/package.json.jinja` | yes |
| `??` | `template/files/tauri/src/vite-env.d.ts.jinja` | yes |
| `??` | `template/files/tauri/justfile.jinja` | yes |
| `M` | `template/files/tauri/src-tauri/.cargo/config.toml.jinja` | yes |
| `M` | `template/files/electron/README.md.jinja` | gap |
| `M` | `template/files/electron/src/main/index.ts.jinja` | gap |
| `M` | `template/files/electron/src/main/ipc.ts.jinja` | gap |
| `M` | `template/files/electron/src/main/menu.ts.jinja` | gap |
| `M` | `template/files/electron/src/main/tray.ts.jinja` | gap |
| `M` | `template/files/electron/src/main/updater.ts.jinja` | gap |
| `M` | `template/files/electron/src/main/window.ts.jinja` | gap |
| `M` | `template/files/electron/src/renderer/App.tsx.jinja` | gap |
| `M` | `template/files/electron/src/renderer/components/TitleBar.tsx.jinja` | gap |
| `M` | `template/files/electron/src/renderer/index.html.jinja` | gap |
| `M` | `template/files/electron/src/renderer/store.ts.jinja` | gap |
| `M` | `template/files/electron/src/renderer/styles/index.css.jinja` | gap |
| `M` | `template/files/electron/src/shared/types.ts.jinja` | gap |
| `M` | `template/files/electron/tailwind.config.js.jinja` | gap |
| `??` | `template/files/electron/resources/icon.icns` | gap |
| `??` | `template/files/electron/resources/icon.ico` | gap |
| `??` | `template/files/electron/resources/icon.png` | gap |
| `M` | `template/files/tauri/QUICK_REFERENCE.md.jinja` | gap |
| `M` | `template/files/tauri/README.md.jinja` | gap |
| `M` | `template/files/tauri/src-tauri/capabilities/default.json.jinja` | gap |
| `M` | `template/files/tauri/src-tauri/icons/README.md.jinja` | gap |
| `M` | `template/files/tauri/src-tauri/src/commands.rs.jinja` | gap |
| `M` | `template/files/tauri/src-tauri/src/tray.rs.jinja` | gap |
| `M` | `template/files/tauri/src-tauri/tauri.conf.json.jinja` | gap |
| `M` | `template/files/tauri/src/App.tsx.jinja` | gap |
| `M` | `template/files/tauri/src/components/TitleBar.tsx.jinja` | gap |
| `M` | `template/files/tauri/src/components/UpdateChecker.tsx.jinja` | gap |
| `M` | `template/files/tauri/src/styles.css.jinja` | gap |
| `M` | `template/files/tauri/tailwind.config.js.jinja` | gap |
| `??` | `template/files/tauri/.prettierrc.jinja` | gap |
| `??` | `template/files/tauri/src-tauri/icons/128x128.png` | gap |
| `??` | `template/files/tauri/src-tauri/icons/128x128@2x.png` | gap |
| `??` | `template/files/tauri/src-tauri/icons/32x32.png` | gap |
| `??` | `template/files/tauri/src-tauri/icons/icon.icns` | gap |
| `??` | `template/files/tauri/src-tauri/icons/icon.ico` | gap |
| `??` | `template/files/tauri/src-tauri/icons/icon.png` | gap |

### CLI (6)

| Status | Path | keep |
| --- | --- | --- |
| `M` | `src/riso/cli/app.py` | **KEEP** `--skip-post-gen` in `_GLOBAL_FLAGS` (CLI-T17) |
| `M` | `src/riso/template/__init__.py` | **KEEP** `os.scandir` CM |
| `M` | `tests/unit/test_cli/test_argv_normalize.py` | **KEEP** CLI tests |
| `M` | `tests/unit/test_cli/test_output.py` | **KEEP** |
| `M` | `tests/unit/test_cli/test_recopy.py` | **KEEP** |
| `M` | `tests/unit/test_cli/test_validate.py` | **KEEP** |

`generation_gates.py` is **not** dirty (committed leftover `saas_auth` at L60 — W0-T02d / W1-C06).

### WEB (29) — source T01f

All **KEEP** wizard polish. Remap ops still W1/WEB-T01.

`web/index.html`, `web/src/index.css`, 3 `__tests__` `M`, `?? ProjectBasics.test.tsx`, 21 component `M`, `?? Switch.tsx`, `exportConfig.ts`, `store.ts`, `useFocusTrap.ts` — full list in `W0-dirty-cross.md`.

### PLATFORM (20)

| Status | Path | keep |
| --- | --- | --- |
| `M` | `scripts/ci/check_quality_parity.py` | **KEEP** ladder |
| `M` | `scripts/ci/generate_matrix_data.py` | **KEEP** |
| `M` | `scripts/ci/render_matrix.py` | **KEEP** PL-T06; do not residual |
| `M` | `scripts/lib/paths.py` | **KEEP** pruned `iter_sample_answer_files` |
| `M` | `template/files/quality/coverage.cfg.jinja` | **KEEP** |
| `M` | `template/files/quality/justfile.quality.jinja` | **KEEP** |
| `M` | `template/files/quality/makefile.quality.jinja` | **KEEP** |
| `M` | `template/files/quality/uv_tasks/quality.py.jinja` | **KEEP** |
| `??` | `template/files/quality/.pylintrc.jinja` | **KEEP** |
| `M` | `tests/unit/ci/test_check_quality_parity.py` | **KEEP** |
| `M` | `tests/unit/ci/test_render_matrix.py` | **KEEP** |
| `??` | `tests/unit/ci/test_generate_matrix_data.py` | **KEEP** |
| `??` | `tests/unit/ci/test_run_quality_suite.py` | **KEEP** |
| `??` | `tests/unit/ci/test_verify_version_sync.py` | **KEEP** |
| `R` | `tests/unit/hooks/test_quality_tool_check.py` → `tests/unit/hooks/test_hooks_quality_tool_check.py` | **KEEP** |
| `R` | `tests/unit/scripts/__init__.py` → `tests/unit/setup_scripts/__init__.py` | **KEEP** |
| `R` | `tests/unit/scripts/test_bump_npm_deps.py` → `tests/unit/setup_scripts/test_bump_npm_deps.py` | **KEEP** |
| `R` | `tests/unit/scripts/test_setup_detection.py` → `tests/unit/setup_scripts/test_setup_detection.py` | **KEEP** |
| `M` | `tests/unit/test_go_templates.py` | **KEEP** SYS-T01 gate |
| `M` | `tests/unit/test_task_runner_templates.py` | **KEEP** |

Four `R` rows + 16 other = **20**.

### DOCS (24)

21 from T01f (`docs/**` + `template/files/docs/**`) **KEEP**. Plus:

| Status | Path | keep |
| --- | --- | --- |
| `M` | `template/files/AGENTS.md.jinja` | **KEEP** W4-D05 |
| `M` | `template/files/CLAUDE.md.jinja` | **KEEP** pointer lockstep |
| `??` | `template/files/DESIGN.md.jinja` | **KEEP** DESIGN tokens |

`docs/guides/v2-migration.md` is **absent** (W4-D01). Not dirty.

### COORD (1)

| Status | Path | keep |
| --- | --- | --- |
| `M` | `template/files/module_catalog.json.jinja` | **KEEP** for W1-C04 (ty/mise/OpenSpec). Serial COORD. |

`template/copier.yml` and `template/hooks/**`: **not dirty**. W1 owns them serially.

### UNLOCKED (1)

| Status | Path | Decision |
| --- | --- | --- |
| `M` | `pyproject.toml` | **OWNED / do not edit in W0**. No exclusive lock. Later COORD/PLATFORM only if a task needs it. |

### OUT-OF-SCOPE (2)

| Status | Path |
| --- | --- |
| `??` | `.claude/skills/mcp-installer/` |
| `??` | `.grok/` |

### PRIOR-GOAL (do not edit this wave)

Porcelain `M`:

| Status | Path |
| --- | --- |
| `M` | `goals/riso-lanes-assurance/ASSURANCE.md` |
| `M` | `goals/riso-lanes-assurance/handoffs-board.md` |
| `M` | `goals/riso-lanes-assurance/residuals/PLATFORM.md` |

Porcelain `??` (dir form + leaves in the 26af77c5 UNTRACKED dump): `goals/riso-lane-cli/`, `goals/riso-lane-coord/**`, `goals/riso-lane-desktop/**`, `goals/riso-lane-node/**`, `goals/riso-lane-platform/**`, `goals/riso-lane-py/**`, `goals/riso-lane-saas/**`, `goals/riso-lane-sys/**`, `goals/riso-lanes-assurance/{evidence,facts*,goal.md,grok-context,interview*,inventory-dirty.md,plan*,residuals/PY.md,residuals/SYS.md}`. Every leaf in that untracked list is owned **PRIOR-GOAL**.

### GOAL — this package

Tracked goal/plan/facts files were not in the 26af77c5 porcelain (already on the 34-ahead `main`). This wave’s untracked evidence:

| Status | Path |
| --- | --- |
| `??` | `goals/riso-v2-release-ready/evidence/W0-dirty-py.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-dirty-node.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-dirty-saas.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-dirty-sys.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-dirty-desktop.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-dirty-cross.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-ssot-diff.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-rg-samples.txt` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-rg-web.txt` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-rg-gates.txt` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-inventory.md` |
| `??` | `goals/riso-v2-release-ready/evidence/W0-keep-drop.md` |

## W0-T02 cite (not dirty-tree)

| ID | Result |
| --- | --- |
| T02a | 8 keys identical across core / scripts.lib / TS; no value drift |
| T02b | `samples/**/copier-answers.yml` old-key hits: **empty** (37 files) |
| T02c | wizard SSOT + tests cite all 8; presets/store/export emit canonical only |
| T02d | leftover `saas_auth` in `generation_gates.py:60`; skill lists 5/8 and still says “do not convert” |

## W0-T04 — taskgraph checksum (no refresh)

`plan.taskgraph.json` parsed. Waves: `W0`, `W1`, `W2`, `W3`, `W4` only (none invented).

Algo `canonical-newline-sorted-locks` = unique sorted exclusive write roots from `plan.md` locks **plus** planned `template/files/openspec/` (OS-T01).

Computed value equals `lock_checksum.value` already in the file (`source: W0-T04`, `json_valid: true`). **No rewrite.**

## Verdict

| Check | Result |
| --- | --- |
| Every current dirty path owned | **yes** (0 unowned) |
| SaaS flatten | **dropped** / absent at `node/saas` root |
| `runtime/{nextjs,remix}` | **present** |
| Planned `samples/*/render/` writes | **0** |
| T01c/T01d undercount | closed (SAAS 39 + SYS 33 owned) |
| JSON taskgraph | valid; checksum unchanged |

W0-T01j verify met.
