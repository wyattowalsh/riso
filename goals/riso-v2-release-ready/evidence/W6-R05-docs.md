# W6-R05 — Review pass 2 (dry), surface=docs

- Task: `W6-R05`
- Wave: W6
- Lane: GOAL evidence only (this file is the exclusive write)
- Mode: inspect-only against the **live tree** (second dry pass after `W6-R04-docs.md`)
- Date: 2026-08-18
- Workspace: `/Users/ww/dev/projects/riso`
- Git: no checkout / stash / reset / rebase / commit / tag / push
- `samples/*/render/**` writes: **0**
- Product / template / docs source edits: **0**
- Prior blobs (`W6-R04-docs.md`, `W6-R03-docs.md`, `W6-DOCS-changelog.md`, `W5-R1-docs.md`, `W5-R2-docs.md`) used as pointers only; every keep/drop re-read live
- Status: **P0 empty; P1 empty.** Prior `DOCS-P1-01` remains closed on live `CHANGELOG.md`. No new findings vs W6-R04.

## Rubric (this pass)

Required surfaces:

1. `docs/guides/v2-migration.md` (+ guides toctree)
1. Root `CHANGELOG.md` `## [Unreleased] 2.0.0`
1. `template/files/docs/upgrade-guide.md.jinja`
1. `template/files/AGENTS.md.jinja`

**P0** = migration guide missing **or** CHANGELOG Unreleased 2.0.0 section missing.

**P1** = `api_features` dest-prompt vocabulary not lockstep across those surfaces (GraphQL/WebSocket still taught only as derived flags, or omitted where sibling operator copy names the Copier prompt).

Remap SSOT (read-only): `src/riso/core/removed_answer_keys.py`.
Apply then reject. No dest overwrite. Idempotent. `_SAAS_AUTH_PROVIDERS = {clerk, authjs}` — `lucia` is **not** remapped.

Copier dest (`template/copier.yml` L63–67, L354–365): `api_features` is the live multiselect (`graphql`, `websocket`) when `api_module=enabled`. `graphql_api_module` / `websocket_module` are legacy **no-prompt** defaults.

## W6-R04 disposition (re-read, not inherited)

| id           | W6-R04                              | W6-R05 live                                                                                        |
| ------------ | ----------------------------------- | -------------------------------------------------------------------------------------------------- |
| (P0)         | empty                               | **still empty** — both required pages exist                                                        |
| `DOCS-P1-01` | closed on Unreleased 2.0.0 dest-key | **still closed** — Unreleased 2.0.0 L57–60 names `api_features` as Copier dest key + enable recipe |

W6-R03 recorded `rg api_features CHANGELOG.md` empty. W6-DOCS-changelog inserted the dest-key sentence. This pass re-read `CHANGELOG.md` L9–85 independently: two `api_features` hits, both in the Unreleased 2.0.0 section. Flags are **not** added to the 8-row remap table. No new P0/P1 versus W6-R04.

## Live SSOT vs remap tables (8/8)

| Old key               | Operator                                            | Dest                                           | v2-migration                          | CHANGELOG 2.0.0 | upgrade-guide.jinja                      |
| --------------------- | --------------------------------------------------- | ---------------------------------------------- | ------------------------------------- | --------------- | ---------------------------------------- |
| `api_tracks`          | derive                                              | `api_module`, `api_languages`                  | match                                 | match           | match                                    |
| `api_language`        | wrap-list                                           | `api_languages`                                | match                                 | match           | match                                    |
| `docs_site`           | derive                                              | `docs_module`, `docs_framework`                | match                                 | match           | match                                    |
| `mcp_language`        | wrap-list + `_MCP_ALIASES` `node`/`js`→`typescript` | `mcp_languages`                                | match                                 | match           | match (value alias, not a dual-path key) |
| `saas_starter_module` | rename                                              | `saas_infra_module`                            | match                                 | match           | match                                    |
| `saas_auth`           | split                                               | `saas_auth_module`, `saas_auth_provider`       | `clerk`/`authjs`; `lucia` fail-closes | same            | same                                     |
| `saas_billing`        | split                                               | `saas_billing_module`, `saas_billing_provider` | match                                 | match           | match                                    |
| `include_admin`       | rename-bool                                         | `saas_admin_dashboard`                         | match                                 | match           | match                                    |

AGENTS.md.jinja has no second remap table (correct). Never Touch lists all eight old keys (L262).

## Inspected roots (live)

| Path                                         | Result                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/guides/v2-migration.md`                | **Present.** Apply-then-reject; 8-row table + value rules; lucia fail-close; leftover `saas_auth: firebase` exit-2 string matches `REMOVED_ANSWER_KEYS["saas_auth"]`; migrate argv `DEST` xor `--answers-file` + `--dry-run` + `--json`; JSON envelope fields match `src/riso/cli/commands/migrate.py` (`answers_file`, `changed`, `written`, `dry_run`, `ops`, `answers`, `template_path`, `message`); `riso update` remaps first (L199–203); mise Node **20**; `openspec_extra` off; ty/just; hypothesis+respx. Derived flags **plus** `api_features` enable recipe (L50–53). `riso-mcp` is a 1.x pointer only. |
| `docs/guides/index.md` L18                   | Toctree `Riso 2.0 Answers Migration <v2-migration>`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `CHANGELOG.md` L9–85                         | `## [Unreleased] 2.0.0` **present.** No-tag sentence. All 8 remaps + operators + dests + apply-then-reject + no dest overwrite + idempotent + fail-closed leftover shape. Links `docs/guides/v2-migration.md`. L57–60: derived-flag sentence **and** dest-key sentence (`api_features` is the Copier dest key) **and** enable recipe (`graphql`, `websocket` when `api_module=enabled`). Two `api_features` hits, both in the Unreleased 2.0.0 section. Flags not in the remap table.                                                                                                                             |
| `docs/changelog.md` L3–8                     | Pointer to Unreleased 2.0.0 + `{doc}`guides/v2-migration\`\`. Not a second story.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `template/files/docs/upgrade-guide.md.jinja` | Apply-then-reject; 8 remaps; lucia fail-close; mise pins `3.11`/`20`/`9.15.0`/`0.4.30` match `template/files/mise.toml.jinja`; OpenSpec extra default off + `default('disabled')`; ty/just/pnpm; `riso-mcp` prohibition only. Canonical table L122 names `api_features`. Remap-section derived-flag sentence (L51–52) still omits the dest prompt (same page has the row).                                                                                                                                                                                                                                        |
| `template/files/AGENTS.md.jinja`             | mise Node **20** (not 22); OpenSpec extra default disabled; ty/just/pnpm; apply-then-fail-closed + migrate dry-run; eight Never Touch keys. Module Guides L208: `api_features` enables GraphQL/WebSocket; flags are derived. No `riso-mcp` product mention.                                                                                                                                                                                                                                                                                                                                                       |

## P0

None. Both required pages exist:

- `docs/guides/v2-migration.md` (toctree listed)
- `CHANGELOG.md` `## [Unreleased] 2.0.0`

## P1

None. All four required surfaces name `api_features` as the Copier dest / enable prompt for GraphQL/WebSocket. W6-R03 `DOCS-P1-01` is **not** still real. W6-R04 empty P1 list is unchanged. No new P0/P1.

## Closed / strengths (not findings)

| id       | file                                         | note                                                                                                            |
| -------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| DOCS-C01 | `docs/guides/v2-migration.md`                | Page + toctree. Contract + 8 remaps + migrate dry-run + fail-closed leftover + `api_features` enable recipe.    |
| DOCS-C02 | `CHANGELOG.md`                               | Section exists; 8 remaps, operators, dests, contract, no-tag sentence; dest-key + enable recipe still lockstep. |
| DOCS-C03 | `template/files/docs/upgrade-guide.md.jinja` | Remap contract, mise Node 20 pins, OpenSpec extra off, ty/just/pnpm, `api_features` in canonical table.         |
| DOCS-C04 | `template/files/AGENTS.md.jinja`             | Pointers for mise / OpenSpec extra / ty / just / pnpm; 8 Never Touch keys; `api_features` pointer.              |
| DOCS-C05 | v2-migration + CHANGELOG + upgrade + AGENTS  | Dest-prompt lockstep on `api_features`. No dual-path **key** aliases for the eight remaps.                      |

## Below P1 (not elevated)

- `CHANGELOG.md` L434 leftover `## [Unreleased]` pre-1.0 block (not the 2.0 section).
- Generated upgrade-guide remap paragraph (L51–52) repeats the short derived-flag sentence without `api_features`; the same page’s canonical table already names the dest prompt.
- `docs/changelog.md` pointer does not name `api_features` (it is not one of the four required surfaces).
- Generated upgrade-guide / AGENTS do not mention hypothesis+respx (maintainer `v2-migration.md` does). Absence, not contradiction.
- Official `sphinx-build -W` not re-run this pass.

## Path lock

Exclusive write this session: `goals/riso-v2-release-ready/evidence/W6-R05-docs.md`.

| Class                                  | Count |
| -------------------------------------- | ----- |
| Product / template / docs source edits | **0** |
| `samples/*/render/**` hand-edits       | **0** |
| Lockfile edits                         | **0** |
| Commit / tag / push / PyPI             | **0** |
| Secrets printed                        | **0** |
| `render_matrix.py` started or killed   | **0** |

## SSOT files read

`src/riso/core/removed_answer_keys.py`, `src/riso/cli/commands/migrate.py`, `template/copier.yml` (defaults + `api_features`), `template/files/mise.toml.jinja`, `docs/guides/v2-migration.md`, `docs/guides/index.md`, `CHANGELOG.md`, `docs/changelog.md`, `template/files/docs/upgrade-guide.md.jinja`, `template/files/AGENTS.md.jinja`.
