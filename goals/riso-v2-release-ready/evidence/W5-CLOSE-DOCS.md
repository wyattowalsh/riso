# W5-CLOSE-DOCS — lockstep remaps + sphinx-W

- Task: `CLOSE-DOCS`
- Wave: W5
- Lane: **DOCS**
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main`
- HEAD: `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (no checkout / stash / reset / commit / tag / push)
- Date: 2026-08-14
- Exclusive writes this session: listed below
- `samples/*/render/**` writes: **0**
- Git tags `v2.0.0` / `2.0.0`: **absent**
- Status: **green** (no remaining P0/P1 in the DOCS lock)

## Contract

Seeded keep + lockstep (re-verified live against
`src/riso/core/removed_answer_keys.py`):

1. `docs/guides/v2-migration.md` + `docs/guides/index.md` toctree
2. `CHANGELOG.md` `## [Unreleased] 2.0.0` names all eight remaps
3. Generated `template/files/docs/upgrade-guide.md.jinja` remaps / mise / OpenSpec
4. `template/files/AGENTS.md.jinja` pointers: mise, OpenSpec extra, ty / just / pnpm
5. `template/files/DESIGN.md.jinja` same pointers (now in the CLOSE-DOCS lock)
6. No dual-path aliases after remap; `lucia` fail-closes; `riso-mcp` prohibition only
7. Official `sphinx-build -W` exit 0
8. **No version tag**

Apply then reject. No dest overwrite. Idempotent. Generated Node floor stays
**20**. `openspec_extra` default **disabled**. SaaS flatten stays dropped (not
this lock).

Confirmed JSON P0/P1 files (`justfile`, `samples/default/render`, NODE/PAY/WIZ
payloads, residuals GOAL/PLATFORM/OPENSPEC) sit **outside** this lock. Not
edited. Not residualed here.

## Live SSOT (8/8, unchanged)

| Old key | Operator | Dest | Docs |
| --- | --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` | match |
| `api_language` | wrap-list | `api_languages` | match |
| `docs_site` | derive | `docs_module`, `docs_framework` | match |
| `mcp_language` | wrap-list + `node`/`js`→`typescript` | `mcp_languages` | match |
| `saas_starter_module` | rename | `saas_infra_module` | match |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` | `clerk`/`authjs` only; `lucia` fail-closes |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` | match |
| `include_admin` | rename-bool | `saas_admin_dashboard` | match |

`_SAAS_AUTH_PROVIDERS = {clerk, authjs}`. Copier dest has no `lucia`.

## This-session edits (lock only)

| File | Why |
| --- | --- |
| `README.md` | First-touch maintainer lockstep: eight remaps, migrate argv, no-tag, mise Node 20, `openspec_extra` off, Documentation link |
| `docs/index.md` | Quick Start includes `riso migrate --dry-run` |
| `docs/guides/quickstart.md` | migrate pointer + official `sphinx-build -W -b html` |
| `docs/upgrade-guide.md.jinja` | Maintainer CI/container page now points at the 2.0 remap contract (excluded from Sphinx via `**/*.jinja`) |
| `template/files/DESIGN.md.jinja` | mise / OpenSpec / upgrade-guide pointers; mermaid bag stays **file-local** (do not named-export) |
| `template/files/docs/modules/prompt-reference.md.jinja` | `lucia` fail-closes, not a dest provider |

Kept as-is (already lockstep; not rewritten this session):

- `docs/guides/v2-migration.md` (untracked from W4-D01; 8 remaps + dry-run + fail-closed leftover)
- `docs/guides/index.md` toctree `Riso 2.0 Answers Migration <v2-migration>`
- `CHANGELOG.md` `## [Unreleased] 2.0.0` (pre-existing dirty)
- `template/files/docs/upgrade-guide.md.jinja` (8 remaps, mise 3.11/20/9.15.0/0.4.30, OpenSpec off)
- `template/files/AGENTS.md.jinja` (mise / OpenSpec extra / ty / just / pnpm / migrate)

## Verify

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git rev-parse --abbrev-ref HEAD # main
git tag -l 'v2.0.0' '2.0.0'     # empty

uv run --group docs sphinx-build -E -W -b html docs docs/_build/html
# build succeeded. 25 sources including guides/v2-migration.md

uv run python scripts/ci/validate_jinja_templates.py \
  template/files/docs/upgrade-guide.md.jinja \
  template/files/AGENTS.md.jinja \
  template/files/DESIGN.md.jinja \
  template/files/docs/modules/prompt-reference.md.jinja
# Validated 4 Jinja template(s): all OK

uv run pytest tests/unit/template/test_agents_md_render.py -q -n 0
# 10 passed
```

| Check | Result |
| --- | --- |
| page `docs/guides/v2-migration.md` | present |
| toctree lists `v2-migration` | `docs/guides/index.md` L18 |
| CHANGELOG `## [Unreleased] 2.0.0` names 8 remaps + lucia fail-close | present |
| generated upgrade-guide remaps + mise Node 20 + OpenSpec off | present |
| AGENTS pointers mise / OpenSpec / ty / just / pnpm | present |
| DESIGN pointers mise / OpenSpec / ty / just / pnpm | present this session |
| `v2.0.0` / `2.0.0` tags | **empty** |
| `sphinx-build -E -W` | exit 0; `docs/_build/html/guides/v2-migration.html` present |
| jinja validate (4 files) | all OK |
| `test_agents_md_render.py` | 10 passed |
| StrictUndefined render AGENTS / DESIGN / upgrade-guide / prompt-reference | OK (AGENTS/DESIGN also without `openspec_extra` key) |
| `samples/*/render/**` hand-edits | **0** |

## Not this lock

- Restore `samples/default/render` (PLATFORM / official `render-samples.sh`)
- Docusaurus named-export payload (`template/files/node/docs/**`)
- Sphinx `linkcheck` recipe / `python/Makefile.jinja`
- Wizard lucia dest (`web/**`)
- Refine-stop review pair (GOAL)
- `justfile` / `validate-agents` dest requirement

Those remain foreign residuals. They do not flip `fact-migration-docs`.

## Path lock

| Class | Count |
| --- | --- |
| This-session product writes | 6 paths under `docs/**`, `README.md`, `template/files/{DESIGN.md.jinja,docs/modules/prompt-reference.md.jinja}` |
| This-session evidence | this file |
| `samples/*/render/**` hand-edits | **0** |
| Lockfile edits | **0** |
| Commit / tag / push / PyPI | **0** |
| Secrets printed | **0** |
| Foreign-tree edits | **0** |
