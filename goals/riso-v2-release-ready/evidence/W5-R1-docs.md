# W5-R1-docs — Review pass 1 (docs surface)

- Task: `W5-R1` surface=`docs`
- Wave: W5 Review pass 1
- Lane: GOAL evidence only (this file is the exclusive write)
- Mode: inspect-only against the **live tree**
- Date: 2026-08-14
- Workspace: `/Users/ww/dev/projects/riso`
- Git: `read_file` of `.git/HEAD` was hook-denied; no `run_terminal_command` in this harness. Workspace path matches `git rev-parse --show-toplevel` from sibling GOAL evidence (`W5-LADDER-sphinx.txt` L18: `/Users/ww/dev/projects/riso`, branch `main`, HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`). This session did not checkout / stash / reset / rebase / commit / tag / push.
- `samples/*/render/**` writes: **0**
- Product / template / docs source edits: **0**
- Prior review blob: empty (untrusted). `ASSURANCE.md` / `W5-AUDIT-docs.md` / `W5-CLOSE-DOCS.md` used only as pointers, not as verdicts.

## Contract (this surface)

Inspect live roots: `docs/**`, `CHANGELOG.md`, `README.md`, `template/files/docs/**`, `template/files/AGENTS.md.jinja`.

P0 = correctness / remap-contract break (wrong apply order, dest overwrite, dual-path **after remap** of the eight keys, lucia as a mapped dest, generated Node 22, OpenSpec extra on by default, `riso-mcp` as a live product, missing `v2-migration` / Unreleased 2.0.0).

P1 = lockstep / DX still open in product docs (keys, defaults, 2.0 behavior out of step across those roots).

Remap SSOT (read-only): `src/riso/core/removed_answer_keys.py`.
Apply then reject. No dest overwrite if dest is set (`_write_dests` L312–318). Idempotent. `_SAAS_AUTH_PROVIDERS = {clerk, authjs}` — `lucia` is **not** remapped.

## Live SSOT vs docs (8/8)

| Old key | Operator | Dest | Live docs |
| --- | --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` | match (`v2-migration`, CHANGELOG, generated upgrade-guide) |
| `api_language` | wrap-list | `api_languages` | match |
| `docs_site` | derive | `docs_module`, `docs_framework` | match |
| `mcp_language` | wrap-list + `_MCP_ALIASES` `node`/`js`→`typescript` | `mcp_languages` | match (value alias, not a dual-path **key**) |
| `saas_starter_module` | rename | `saas_infra_module` | match |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` | `clerk`/`authjs` only; `lucia` fail-closes |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` | match |
| `include_admin` | rename-bool | `saas_admin_dashboard` | match |

Copier dest (`template/copier.yml` L1337–1347): `saas_auth_provider` choices `clerk` / `authjs` only. Lockstep with lucia fail-close.

`graphql_api_module` / `websocket_module` are **not** in `REMOVED_ANSWER_KEYS`. `copier.yml` L65–67: “Legacy answer keys (no Copier prompts): prefer `api_features` multiselect.” Prompt `api_features` is at `template/copier.yml` L354–365 (`graphql`, `websocket`).

## Inspected roots (live)

| Path | Result |
| --- | --- |
| `docs/guides/v2-migration.md` | Present. Apply-then-reject; 8-row table + value rules; migrate argv; leftover `saas_auth: firebase` exit-2 string matches `REMOVED_ANSWER_KEYS`; lucia fail-closes; mise Node **20**; `openspec_extra` off; ty/just; hypothesis+respx. |
| `docs/guides/index.md` L18 | Toctree `Riso 2.0 Answers Migration <v2-migration>`. |
| `docs/index.md` L67–68 | Quick Start `uv run riso migrate --answers-file … --dry-run`. Hidden toctree includes `guides/index`. |
| `CHANGELOG.md` L9–77 | `## [Unreleased] 2.0.0`. No-tag sentence. All 8 remaps + operators + dests + contract. Links `docs/guides/v2-migration.md`. |
| `docs/changelog.md` L3–8 | Pointer to Unreleased 2.0.0 + `{doc}`guides/v2-migration``. |
| `README.md` L48–62 | Eight remaps, migrate argv, no-tag, mise Node 20, `openspec_extra` off. **P1-01** Module Reference (L72–73). |
| `docs/guides/quickstart.md` | migrate + Node 20 + OpenSpec off + official `sphinx-build -W`. |
| `docs/guides/troubleshooting.md` L186–189, L326–336 | Leftover 8 keys → `riso migrate --dry-run`; apply-then-reject pointer. |
| `docs/tools/riso-cli.md` L68–72 | migrate argv + pointer to v2-migration. |
| `docs/tools/riso-mcp-server.md` | Title `riso-mcp (removed)`. No catalog frontmatter. Hidden tools toctree only. |
| `docs/guides/mcp-to-cli-migration.md` | Tombstone. |
| `docs/api/index.md` L43–46 | Removed in v1.2.0. |
| `docs/upgrade-guide.md.jinja` | Maintainer CI/container page; remap pointer at top. Sphinx `exclude_patterns` includes `**/*.jinja`. Not W4-D04. |
| `template/files/docs/upgrade-guide.md.jinja` | Apply-then-reject; 8 remaps; lucia fail-close; mise pins `3.11`/`20`/`9.15.0`/`0.4.30` match `template/files/mise.toml.jinja`; OpenSpec default off; ty/just/pnpm; `riso-mcp` prohibition only. Canonical prompt table omits `api_features` (**P1-03**). |
| `template/files/docs/modules/prompt-reference.md.jinja` | Dest keys + lucia fail-close. **Omits `api_features`.** |
| `template/files/docs/modules/graphql.md.jinja` | **P1-02** teaches `graphql_api_module=enabled`. |
| `template/files/docs/modules/websockets.md.jinja` L32 | Correct `--data api_features=websocket`. |
| `template/files/docs/modules/api-python.md.jinja` L7–14 | Correct `api_features=[graphql]` / `[websocket]`. |
| `template/files/AGENTS.md.jinja` | mise Node **20**, OpenSpec default disabled, ty/just/pnpm, apply-then-fail-closed + 8 Never Touch keys. No `api_features`. |
| `docs/conf.py` L138–149 | Excludes `**/*.jinja`, `modules/**`. Published matrix-data is `docs/guides/matrix-data.md` (no stale `api_languages` choices). |

Sibling CLI (not edited): `src/riso/cli/commands/migrate.py` envelope fields match `v2-migration.md` (`answers_file`, `changed`, `written`, `dry_run`, `ops`, `answers`, `template_path`, `message`). Human preview in `src/riso/cli/output.py` L134–150 matches the documented `remap: N key(s)` / `already canonical` / `dry_run: true` shape. Leftover error string matches `reject_removed_answer_keys`.

Official sphinx dest from sibling GOAL evidence (`W5-LADDER-sphinx.txt`): `uv run --group docs sphinx-build -W -b html docs docs/_build/html` exit 0; `docs/_build/html/guides/v2-migration.html` present. **Not re-run here.**

## P0

None after inspection.

Eight remapped keys are not documented as post-remap aliases. Apply-then-reject, no dest overwrite, idempotent, lucia fail-close, generated Node 20, OpenSpec extra off, `riso-mcp` prohibition/tombstone only, `v2-migration` + Unreleased 2.0.0 all live.

## P1

### DOCS-P1-01 — README Module Reference still lists legacy GraphQL/WebSocket keys as prompts

| Field | Value |
| --- | --- |
| **id** | `DOCS-P1-01` |
| **file** | `README.md` |
| **issue** | Module Reference treats `graphql_api_module` and `websocket_module` as current Prompt Keys. Live Copier SSOT says those are legacy **no-prompt** defaults; the user prompt is `api_features`. README never names `api_features`. |
| **evidence** | `README.md` L72–73 vs `template/copier.yml` L65–67 and L354–365. `rg api_features README.md` empty. `docs/**` also has **zero** `api_features` hits (including `docs/guides/v2-migration.md` L50–51, which only says the flags are derived / not remapped). |
| **fix** | Replace those two rows with `api_features` (`graphql`, `websocket` multiselect when `api_module=enabled`). Note `graphql_api_module` / `websocket_module` as derived Jinja flags, not prompts. Add the same one-liner to `docs/guides/v2-migration.md` next to the derived-flag sentence. |

### DOCS-P1-02 — generated GraphQL module doc teaches the legacy enable key

| Field | Value |
| --- | --- |
| **id** | `DOCS-P1-02` |
| **file** | `template/files/docs/modules/graphql.md.jinja` |
| **issue** | Generated GraphQL page tells operators to render with `graphql_api_module=enabled`. Sibling generated docs already teach `api_features`. That is a dual-path enable recipe in the generated payload docs. |
| **evidence** | `graphql.md.jinja` L8 and L729. Contrast `template/files/docs/modules/api-python.md.jinja` L7–14 and `websockets.md.jinja` L30–32 (`--data api_features=websocket`). Excludes still honor **either** `api_features` **or** the legacy flag (`copier.yml` L2019–2026) — docs should not keep the legacy path as the documented enable. |
| **fix** | Same wording as `api-python.md.jinja` / `websockets.md.jinja`: `api_module=enabled` + `api_languages=[python]` + `api_features=[graphql]`. Keep the derived-flag mention only as “not a Copier prompt.” |

### DOCS-P1-03 — generated prompt-reference / upgrade-guide omit `api_features`

| Field | Value |
| --- | --- |
| **id** | `DOCS-P1-03` |
| **file** | `template/files/docs/modules/prompt-reference.md.jinja` |
| **issue** | The generated prompt matrix is the 2.0 key list for agents. It documents dest SaaS keys and “was `saas_auth`” notes but never lists `api_features`, the live Copier prompt that turns GraphQL/WebSocket on. Upgrade-guide canonical table and `AGENTS.md.jinja` also omit it. |
| **evidence** | `prompt-reference.md.jinja` L9–31 (no `api_features` row). `template/files/docs/upgrade-guide.md.jinja` L114–130 canonical table. `template/files/AGENTS.md.jinja` (no `api_features`). `rg api_features template/files/docs template/files/AGENTS.md.jinja` hits only `websockets.md.jinja` + `api-python.md.jinja`. |
| **fix** | Add an `api_features` row (`graphql`, `websocket`; default `[]`; when `api_module=enabled`) to prompt-reference and the upgrade-guide canonical table. One pointer in AGENTS Module Guides is enough (no second remap table). |

## Closed / strengths (not findings)

| id | file | note |
| --- | --- | --- |
| DOCS-C01 | `docs/guides/v2-migration.md` | Page + toctree. Contract + 8 remaps + migrate dry-run + fail-closed leftover. |
| DOCS-C02 | `CHANGELOG.md` | `## [Unreleased] 2.0.0` names all 8 remaps, operators, dests, no-tag sentence. |
| DOCS-C03 | `template/files/docs/upgrade-guide.md.jinja` | Remap contract, mise Node 20 pins, OpenSpec extra off, ty/just/pnpm. |
| DOCS-C04 | `template/files/AGENTS.md.jinja` | Pointers for mise / OpenSpec extra / ty / just / pnpm; 8 Never Touch keys. |
| DOCS-C05 | `docs/guides/v2-migration.md` + tombstones | No dual-path **key** aliases for the eight remaps. `riso-mcp` prohibition / 1.x pointer only. |

## Below P1 (not elevated)

- `CHANGELOG.md` L420 leftover `## [Unreleased]` pre-1.0 block (not the 2.0 section).
- `docs/conf.py` default `RISO_VERSION` `0.1.0` (env override; not a remap/default contract).
- `docs/index.md` Quality Gate card still lists pylint inside `just quality` (pylint is pre-commit; not v2 key lockstep).
- `README.md` Tests badge `398` vs current maintainer pytest count (badge drift).
- `docs/modules/matrix-data.md.jinja` example `api_languages` choices `none/python/node/both` — Sphinx-excluded (`**/*.jinja` + `modules/**`).
- `docs/research/saas-starter-synthesis-report.md` historical `include_admin` in a research schema dump — not operator answers.
- Generated upgrade-guide / AGENTS do not mention hypothesis+respx (maintainer `v2-migration.md` does). Absence, not contradiction. W4-D04 verify did not require it.
- `plan.md` / `evidence/coord-outbox/remap-ssot.md` still list `lucia` as a mapped provider. **Live SSOT + live product docs fail-close lucia.** Goal/outbox drift, not a product-docs gap.
- `docs/guides/agent-scaffolding.md` does not mention `riso migrate` (validate still apply-then-rejects in memory).
- `docs/_build/guides/` (non-html dest) missing `v2-migration.html` is a stale sibling tree. Official dest `docs/_build/html/guides/v2-migration.html` exists per GOAL sphinx evidence.

## Path lock

Exclusive write this session: `goals/riso-v2-release-ready/evidence/W5-R1-docs.md`.

| Class | Count |
| --- | --- |
| Product / template / docs source edits | **0** |
| `samples/*/render/**` hand-edits | **0** |
| Lockfile edits | **0** |
| Commit / tag / push / PyPI | **0** |
| Secrets printed | **0** |
| `render_matrix.py` started or killed | **0** |

## SSOT files read

`goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md`, `facts.meta.json`, `residuals/GOAL.md`, `residuals/GOAL-EVIDENCE.md`, `src/riso/core/removed_answer_keys.py`, `src/riso/core/answers.py`, `src/riso/cli/commands/migrate.py`, `src/riso/cli/output.py`, `template/copier.yml` (defaults + `api_features` + `openspec_extra` + `saas_auth_provider`), `template/files/mise.toml.jinja`.
