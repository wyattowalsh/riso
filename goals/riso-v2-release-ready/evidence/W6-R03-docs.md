# W6-R03 — Review pass, surface=docs

- Task: `W6-R03`
- Wave: W6
- Lane: GOAL evidence only (this file is the exclusive write)
- Mode: inspect-only against the **live tree**
- Date: 2026-08-18
- Workspace: `/Users/ww/dev/projects/riso`
- Git: `read_file` of `.git/HEAD` was hook-denied; no checkout / stash / reset / rebase / commit / tag / push
- `samples/*/render/**` writes: **0**
- Product / template / docs source edits: **0**
- Prior blobs (`W5-AUDIT-docs.md`, `W5-R1-docs.md`, `W5-R2-docs.md`, `W5-CLOSE-DOCS.md`) used as pointers only; every keep/drop re-read live
- Status: **no P0; 1 P1** (`api_features` lockstep)

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

| Path                                         | Result                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `docs/guides/v2-migration.md`                | **Present.** Apply-then-reject; 8-row table + value rules; lucia fail-close; leftover `saas_auth: firebase` exit-2 string matches `REMOVED_ANSWER_KEYS["saas_auth"]`; migrate argv `DEST` xor `--answers-file` + `--dry-run` + `--json`; JSON envelope fields match `src/riso/cli/commands/migrate.py` (`answers_file`, `changed`, `written`, `dry_run`, `ops`, `answers`, `template_path`, `message`); `riso update` remaps first; mise Node **20**; `openspec_extra` off; ty/just; hypothesis+respx. Derived flags **plus** `api_features` enable recipe (L50–53). `riso-mcp` is a 1.x pointer only. |
| `docs/guides/index.md` L18                   | Toctree `Riso 2.0 Answers Migration <v2-migration>`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `CHANGELOG.md` L9–83                         | `## [Unreleased] 2.0.0` **present.** No-tag sentence. All 8 remaps + operators + dests + apply-then-reject + no dest overwrite + idempotent + fail-closed leftover shape. Links `docs/guides/v2-migration.md`. Derived-flag sentence (L57–58) does **not** name `api_features`. Zero `api_features` hits in the file.                                                                                                                                                                                                                                                                                  |
| `docs/changelog.md` L3–8                     | Pointer to Unreleased 2.0.0 + `{doc}`guides/v2-migration\`\`. Not a second story.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `template/files/docs/upgrade-guide.md.jinja` | Apply-then-reject; 8 remaps; lucia fail-close; mise pins `3.11`/`20`/`9.15.0`/`0.4.30` match `template/files/mise.toml.jinja`; OpenSpec default off + `default('disabled')`; ty/just/pnpm; `riso-mcp` prohibition only. Canonical table L122 names `api_features`. Remap-section derived-flag sentence (L51–52) still omits the dest prompt (same page has the row).                                                                                                                                                                                                                                   |
| `template/files/AGENTS.md.jinja`             | mise Node **20** (not 22); OpenSpec extra default disabled; ty/just/pnpm; apply-then-fail-closed + migrate dry-run; eight Never Touch keys. Module Guides L208: `api_features` enables GraphQL/WebSocket; flags are derived. No `riso-mcp` product mention.                                                                                                                                                                                                                                                                                                                                            |

## P0

None. Both required pages exist:

- `docs/guides/v2-migration.md` (toctree listed)
- `CHANGELOG.md` `## [Unreleased] 2.0.0`

## P1

### DOCS-P1-01 — CHANGELOG Unreleased 2.0.0 omits `api_features` dest prompt

| Field        | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **id**       | `DOCS-P1-01`                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **file**     | `CHANGELOG.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **issue**    | Unreleased 2.0.0 tells operators that `graphql_api_module` / `websocket_module` are derived Jinja flags and not remapped, but never names the live Copier dest prompt `api_features`. Sibling operator copy in `docs/guides/v2-migration.md` L50–53, generated `upgrade-guide.md.jinja` L122, and `AGENTS.md.jinja` L208 already teach `api_features` (`graphql`, `websocket`) when `api_module=enabled`. That is dest-key lockstep drift on a required surface. |
| **evidence** | `rg api_features CHANGELOG.md` empty. Contrast `CHANGELOG.md` L57–58 vs `docs/guides/v2-migration.md` L50–53 vs `template/copier.yml` L65–67 and L354–365.                                                                                                                                                                                                                                                                                                       |
| **fix**      | Add the same one-liner next to the derived-flag sentence: enable GraphQL/WebSocket with `api_features` (`graphql`, `websocket`) when `api_module=enabled`. Do not add the flags as remapped keys.                                                                                                                                                                                                                                                                |

## Closed / strengths (not findings)

| id       | file                                         | note                                                                                                         |
| -------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| DOCS-C01 | `docs/guides/v2-migration.md`                | Page + toctree. Contract + 8 remaps + migrate dry-run + fail-closed leftover + `api_features` enable recipe. |
| DOCS-C02 | `CHANGELOG.md`                               | Section exists; 8 remaps, operators, dests, contract, no-tag sentence. (P1 is dest-prompt wording only.)     |
| DOCS-C03 | `template/files/docs/upgrade-guide.md.jinja` | Remap contract, mise Node 20 pins, OpenSpec extra off, ty/just/pnpm, `api_features` in canonical table.      |
| DOCS-C04 | `template/files/AGENTS.md.jinja`             | Pointers for mise / OpenSpec extra / ty / just / pnpm; 8 Never Touch keys; `api_features` pointer.           |
| DOCS-C05 | v2-migration + upgrade-guide + AGENTS        | No dual-path **key** aliases for the eight remaps. `riso-mcp` prohibition / 1.x pointer only.                |

## Below P1 (not elevated)

- `CHANGELOG.md` L432 leftover `## [Unreleased]` pre-1.0 block (not the 2.0 section).
- Generated upgrade-guide remap paragraph (L51–52) repeats the short derived-flag sentence without `api_features`; the same page’s canonical table already names the dest prompt.
- `plan.md` / `evidence/coord-outbox/remap-ssot.md` still list `lucia` as a mapped provider. **Live SSOT + live product docs fail-close lucia.** Goal/outbox drift, not a product-docs gap.
- `docs/changelog.md` pointer does not name `api_features` (it is not one of the four required surfaces).
- Generated upgrade-guide / AGENTS do not mention hypothesis+respx (maintainer `v2-migration.md` does). Absence, not contradiction.
- Official `sphinx-build -W` not re-run this pass.

## Path lock

Exclusive write this session: `goals/riso-v2-release-ready/evidence/W6-R03-docs.md`.

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
