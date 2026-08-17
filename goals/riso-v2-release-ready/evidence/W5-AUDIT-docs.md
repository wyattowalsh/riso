# W5-AUDIT-docs — read-only docs lockstep

- Task: `W5-AUDIT-docs`
- Wave: W5
- Lane: **docs**
- Mode: inspect-only (this file is the only write)
- Repo: `/Users/ww/dev/projects/riso` (`git rev-parse --show-toplevel` / `.git/HEAD` denied by hook; workspace + prior GOAL/W4 evidence)
- Branch / HEAD (from `ASSURANCE.md` / `W4-PL-T08-sphinx.txt`, not re-checked via git): `main` · `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Date: 2026-08-14
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**
- Status: **no open P0/P1** after live inspection

## Contract

Audit live files (not stale ASSURANCE claims):

1. `docs/guides/v2-migration.md` + guides toctree
2. Root `CHANGELOG.md` `## [Unreleased] 2.0.0` names all eight remaps
3. `template/files/docs/upgrade-guide.md.jinja` lockstep (keys, mise, OpenSpec extra)
4. `template/files/AGENTS.md.jinja` pointers: mise, OpenSpec extra, ty / just / pnpm
5. No dual-path aliases after remap
6. `riso-mcp` only as prohibition

Remap SSOT (read-only): `src/riso/core/removed_answer_keys.py`.
Apply then reject. No dest overwrite. Idempotent. `_SAAS_AUTH_PROVIDERS = {clerk, authjs}` — `lucia` is **not** remapped.

P0 = correctness / remap-contract break. P1 = lockstep / DX still open in product docs.
`stale` = residual/evidence text already fixed in the live tree.
`closed` = verified-good surface recorded as a strength.

## Live SSOT (8/8)

| Old key | Operator | Dest | Live value rule vs docs |
| --- | --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` | match |
| `api_language` | wrap-list | `api_languages` | match |
| `docs_site` | derive | `docs_module`, `docs_framework` | match |
| `mcp_language` | wrap-list + `_MCP_ALIASES` `node`/`js`→`typescript` | `mcp_languages` | match (value alias, not a dual-path key) |
| `saas_starter_module` | rename | `saas_infra_module` | match |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` | `lucia` fail-closes; docs match SSOT (not `plan.md` / W1 outbox lucia row) |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` | match |
| `include_admin` | rename-bool | `saas_admin_dashboard` | match |

`graphql_api_module` / `websocket_module` called out as derived Jinja flags, not remapped user keys, in v2-migration, CHANGELOG, and generated upgrade-guide.

Copier dest (`template/copier.yml` L1337–1347): `saas_auth_provider` choices are `clerk` / `authjs` only. Lockstep with lucia fail-close.

## 1. v2-migration + toctree

`docs/guides/v2-migration.md` exists. Contents:

- Apply then reject; no dest overwrite; idempotent; no dual-path after remap
- Full 8-row remap table + value rules
- `uv run riso migrate DEST|--answers-file PATH [--dry-run] [--json]`
- Fail-closed leftover example (`saas_auth: firebase` → exit 2 replacement string)
- `riso update` remaps `.copier-answers.yml` first
- Related 2.0 defaults: mise always-on (Python 3.11, Node **20**, not maintainer 22), `openspec_extra` default off, **ty**, **just**, hypothesis+respx
- `riso-mcp` mentioned only as a separate 1.x removal → `{doc}`mcp-to-cli-migration``

`docs/guides/index.md` L7–20 toctree:

```text
Riso 2.0 Answers Migration <v2-migration>
```

Parent `docs/index.md` hidden toctree includes `Guides <guides/index>`. Prior PL-T08 built `docs/_build/html/guides/v2-migration.html` under `sphinx-build -W` (not re-run this audit).

Sibling pointers (lockstep, not the D02 verify target): `docs/changelog.md`, `docs/tools/riso-cli.md`, `docs/guides/troubleshooting.md`.

## 2. CHANGELOG Unreleased 2.0.0

`CHANGELOG.md` L9–77: `## [Unreleased] 2.0.0`.

- Draft; **no `v2.0.0` git tag** sentence present
- `### ⚠ BREAKING CHANGES` names all eight old keys, operators, dests, apply-then-reject, no dest overwrite, idempotent, no dual-path, fail-closed leftover shape
- lucia fail-closes (matches live SSOT)
- `uv run riso migrate DEST|--answers-file PATH [--dry-run] [--json]`
- `riso update` remaps before Copier
- Links `docs/guides/v2-migration.md`

Historical `## [Unreleased]` at L420 is pre-1.0 notes (W4-D03). Not the 2.0 section. Not elevated.

`docs/changelog.md` is a pointer (8 keys + migrate argv + `{doc}`guides/v2-migration``). Not a second story.

## 3. Generated upgrade-guide lockstep

`template/files/docs/upgrade-guide.md.jinja`:

| Required | Present |
| --- | --- |
| `apply_removed_key_remaps` then reject leftovers | L8–13 |
| 8 remaps + operators + dests + lucia fail-close | L40–49 |
| No dest overwrite; idempotent; no dual-path | L10–13, L33 |
| `riso migrate` / `riso update` preview-then-apply | L21–31 |
| mise always-on; Node **20**; pins match `mise.toml.jinja` (`3.11` / `20` / `9.15.0` / `0.4.30`) | L60–76 |
| `openspec_extra` default **disabled**; does not gate mise | L79–90 |
| **ty** / **just** / **pnpm** | L3–4, L112, L136–140 |
| `riso-mcp` prohibition only | L187–188 |

Canonical-prompt table names dest keys and says “Not `api_language` / `api_tracks` / …” (prohibition, not dual-path).

Minor (not P1): `mcp_language` row omits the already-list keep sentence that v2-migration/CHANGELOG spell out. Operator + `node`/`js`→`typescript` still match SSOT.

`docs/upgrade-guide.md.jinja` (maintainer CI/container page) is a **different** file. Sphinx `exclude_patterns` includes `**/*.jinja`, so it is not a published 2.0 operator page. W4-D04 lock is the generated jinja. Not elevated.

## 4. AGENTS.md.jinja pointers

`template/files/AGENTS.md.jinja` (pointers; no second remap table):

| Pointer | Where |
| --- | --- |
| mise always-on, `mise install`, Node **20** (not 22) | Overview L26, QR L39, Setup L86, Security L230, Active L279, Recent L296 |
| `openspec_extra` default disabled; does not gate mise | Overview L27, Module Guides L202, Active L281, Recent L297 |
| **ty** / **just** / **pnpm** | Overview L28, QR, Code Quality, Never Touch L263, Active L275–280, Recent L300 |
| Remap apply-then-fail-closed + `riso migrate --dry-run` | Setup L97–98, Never Touch 8 keys L262, Recent L295 → `docs/upgrade-guide.md` |

`openspec_extra | default('disabled')` keeps StrictUndefined render. No `riso-mcp` product mention (absence is compliant).

## 5. Dual-path / riso-mcp

Published operator docs do **not** keep old keys as aliases after remap. `_MCP_ALIASES` / fastapi-fastify-actix are **value** maps documented as such.

`riso-mcp` hits in docs/template are tombstones or prohibitions:

- `docs/guides/v2-migration.md` L10–11 — 1.x removal pointer
- `docs/guides/mcp-to-cli-migration.md` — “has been removed”
- `docs/tools/riso-mcp-server.md` — title `riso-mcp (removed)` (hidden tools toctree only; no live-catalog frontmatter)
- `docs/api/index.md` L44–46 — removed in v1.2.0
- `docs/guides/agent-scaffolding.md` — use CLI, not removed server
- `template/files/docs/upgrade-guide.md.jinja` L188 — “Do not restore `riso-mcp`”
- `template/files/DESIGN.md.jinja` L257–258 — do not document as a default

`src/riso` has no `riso-mcp` package (W3-PL-T09 + this grep). CHANGELOG 1.2.0 historical removal is not a 2.0 reintroduction.

## Not elevated (below P1)

- `docs/modules/matrix-data.md.jinja` still shows example `api_languages` choices `none/python/node/both`. File is excluded (`**/*.jinja` + `modules/**`). Published `docs/guides/matrix-data.md` does not repeat those choices.
- Maintainer `docs/upgrade-guide.md.jinja` still teaches GHA/container `copier update` and has no remap table. Not Sphinx-published; not W4-D04.
- `plan.md` remap table and `evidence/coord-outbox/remap-ssot.md` still list `lucia` as a mapped `saas_auth` provider. **Live SSOT + live docs fail-close lucia.** Goal/outbox drift, not a product-docs gap (see stale finding).
- CHANGELOG L420 leftover `## [Unreleased]` pre-1.0 block.

## Findings

| id | severity | file | issue |
| --- | --- | --- | --- |
| DOCS-C01 | closed | `docs/guides/v2-migration.md` | Page + `docs/guides/index.md` toctree list `v2-migration`. Apply-then-reject, 8 remaps, migrate dry-run, fail-closed leftovers. |
| DOCS-C02 | closed | `CHANGELOG.md` | `## [Unreleased] 2.0.0` names all 8 remaps, operators, dests, contract, no-tag sentence. |
| DOCS-C03 | closed | `template/files/docs/upgrade-guide.md.jinja` | Lockstep with SSOT + v2-migration: remaps, mise Node 20, OpenSpec extra off, ty/just/pnpm. |
| DOCS-C04 | closed | `template/files/AGENTS.md.jinja` | Pointers for mise, OpenSpec extra, ty/just/pnpm; 8 removed keys in Never Touch. |
| DOCS-C05 | closed | `docs/guides/v2-migration.md` | No dual-path key aliases. `riso-mcp` only as prohibition / 1.x pointer. |
| DOCS-S01 | stale | `goals/riso-v2-release-ready/evidence/W0-inventory.md` | W0/W0-dirty-cross/W0-keep-drop said `docs/guides/v2-migration.md` was absent. Live file + toctree exist. |
| DOCS-S02 | stale | `goals/riso-v2-release-ready/evidence/coord-outbox/remap-ssot.md` | Outbox/plan lucia-as-mapped-provider. Live `_SAAS_AUTH_PROVIDERS` + v2-migration/CHANGELOG/upgrade-guide fail-close lucia. |

No P0/P1.

## Path lock

Exclusive write this session: `goals/riso-v2-release-ready/evidence/W5-AUDIT-docs.md`.

| Class | Count |
| --- | --- |
| Product / template / docs source edits | **0** |
| `samples/*/render/**` hand-edits | **0** |
| Lockfile edits | **0** |
| Commit / tag / push / PyPI | **0** |
| Secrets printed | **0** |

## SSOT files read

`goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md`, `residuals/GOAL.md`, `evidence/W4-D01.md`, `W4-D03.md`, `W4-D04.md`, `W4-R03-gates.md`, `W4-PL-T08-sphinx.txt`.
