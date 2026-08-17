# W5-R1 — surface=CLI

- Task: `W5-R1`
- Wave: W5 review pass 1
- Surface: **CLI**
- Mode: read-only inspection
- Write root: this file only
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-14
- Product-code edits: **0**
- `samples/*/render/**` writes: **0**
- Lockfile / secret / `riso-mcp` / `render_matrix.py`: **0**
- Status: **1 P1** (export `--data` list dests); **P0 empty**

## Method

Live-tree only. Did **not** treat `ASSURANCE.md`, `W2-CLI-JOIN.md`, or `W5-CLOSE-CLI.md` as truth.

Read: `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md`, `facts.meta.json`, `residuals/{CLI,GOAL}.md`.

Inspected:

- `src/riso/cli/**` (`app.py`, `helpers.py`, `output.py`, `config.py`, all `commands/*`)
- `src/riso/core/**` (`removed_answer_keys.py`, `answers.py`, `generation_gates.py`, `diff.py`, `errors.py`, `names.py`, `paths.py`)
- `src/riso/template/**` (`__init__.py` gates/worker, `hooks_runner.py`, `_copier_worker.py`)
- `tests/unit/test_cli/**` (remap/migrate/update/recopy/validate/helpers/export/gates/JOIN-adjacent)
- `tests/integration/test_riso_cli.py`
- `tests/integration/test_control_plane_gates.py`
- Lockstep probes: `template/copier.yml` dest prompts/defaults, `docs/guides/v2-migration.md`, `web/src/lib/removedAnswerKeys.ts` (`SAAS_AUTH_PROVIDERS`)

Git confirm: `read_file` on `.git/HEAD` was **hook-denied**. This harness has no `run_terminal_command`, so `git rev-parse --show-toplevel` / `git tag -l` / pytest were **not** re-run. Workspace path is `/Users/ww/dev/projects/riso`. Do not treat W5-CLOSE HEAD `f7951fe` as re-verified.

## Contract checked

`apply_removed_key_remaps` **then** `reject_removed_answer_keys`. No dest overwrite if dest is set. Idempotent. No dual-path aliases after remap.

Eight keys: `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`.

Generated Node floor stays 20 (CLI does not raise it). OpenSpec extra stays off by default (CLI reads Copier defaults). SaaS Next/Remix flatten is not a CLI write. Maintainer `riso-mcp` must stay gone under `src/riso`.

## Live remap SSOT

`src/riso/core/removed_answer_keys.py`:

- `REMOVED_ANSWER_KEYS` / `ANSWER_KEY_REMAPS` are the same 8 keys.
- Operators match the live migration guide (`docs/guides/v2-migration.md` L39–67), not the stale plan v3 lucia row.
- `_SAAS_AUTH_PROVIDERS = {clerk, authjs}`. `lucia` / `firebase` leave the old key (`dests is None`) for reject.
- `_write_dests` writes only when `key not in out`. Successful apply deletes the old key.
- Input mapping is not mutated.

Choke point: `src/riso/core/answers.py` `apply_then_reject_removed_keys` (L79–83) and `remap_answers_file` (apply-then-reject, write only if `write and result.ops`).

`rg answers.get("…old key…")` on `src/riso` is **empty**. Old-key tokens in `src/riso` exist only inside the remap table / leftover error strings.

`rg riso-mcp src/riso` is **empty**. `rg` Node 22 / `openspec` under `src/riso` is **empty** (defaults come from `template/copier.yml`: `openspec_extra: "disabled"` at `_defaults` L95 and prompt L534–551).

## Call-site wiring (apply then reject)

| Site | Live |
| --- | --- |
| `helpers.resolve_answers` | apply-then-reject on provided, then merge defaults |
| `helpers.validate_and_raise` | apply-then-reject, mutate caller, then schema validate |
| `validate` / `copy` / `export` | via `resolve_answers` |
| `migrate` / `update` | `remap_answers_file` (dry-run no write; leftover no write) |
| `recopy` | provided + dest file + merge all apply-then-reject; dest write only when live |
| `diff` copy | `resolve_answers` |
| `diff` update/recopy | apply-then-reject on `{**existing, **provided}` |
| `compute_diff` | apply-then-reject on preview answers; update/recopy re-merge dest then apply-then-reject (dest already set wins) |
| `generation_gates.validate_answers_for_generation` | apply first, leftover errors on remapped dict, then SaaS/language gates |
| `_collect_saas_selected` | `saas_auth_module` / `saas_auth_provider` only — no leftover `saas_auth` |
| `template._enforce_generation_gates` | apply (mutate if ops), then gates; used by `run_generator` / `run_update` / `run_recopy` |

`--skip-post-gen` remains in `_GLOBAL_FLAGS` (`app.py` L485) and is hoisted (`test_argv_normalize.py`).

`riso migrate` exists (`app.py` L270–293): exactly one of DEST or `--answers-file`; `--dry-run`; global `--json`. Human preview via `output._emit_remap_preview`.

`riso update` remaps `.copier-answers.yml` first, attaches `remap` preview, dry-run runs generation gates without write, live writes remaps then Copier.

JOIN leftover (live tests, not remappable `api_tracks`):

- `tests/integration/test_riso_cli.py::test_validate_rejects_removed_key` — `--data saas_auth=firebase`, exit 2
- `tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker` — `saas_auth=firebase`, worker not called

`test_remap.py` covers wrap/derive/rename/split/rename-bool, dest-not-overwrite, idempotence, leftover `firebase`, lucia fail-closed. Fixtures: 8 keys + mixed + leftover + already-canonical.

Lucia fail-closed is **lockstep** with Copier `saas_auth_provider` choices (`clerk`/`authjs` only, `template/copier.yml` L1337–1347), docs (`v2-migration.md` L65), and wizard `SAAS_AUTH_PROVIDERS`. Plan v3 lucia-remap row is stale, not a CLI bug.

`saas_admin_dashboard` is `type: bool` (`copier.yml` L1587–1597). `include_admin` rename-bool → bool is schema-correct.

## P0 — correctness / contract break

None after inspection.

Remap apply-then-reject is wired at every owned CLI/control-plane site. Dest overwrite is refused. Second apply is a no-op. Unmapped leftovers fail closed with the pointer string. Remappable `api_tracks=python` is not fail-closed. No dual-path old-key reads. No `riso-mcp`. Generated Node floor is not raised in this tree. OpenSpec extra default is not flipped on by CLI.

## P1 — lockstep / DX

### CLI-P1-export-list-data

| Field | Value |
| --- | --- |
| **id** | `CLI-P1-export-list-data` |
| **file** | `src/riso/cli/commands/export.py` |
| **issue** | `riso export cli` remaps wrap-list dests into `--data` via `f"{key}={value}"` (Python list repr). `parse_data_pairs` / `_coerce_value` only coerce bool/int/float, so `api_languages=['python']` re-enters as a **string**. `api_languages` / `mcp_languages` are Copier `multiselect: true` (`template/copier.yml` L309–311, L379–381); `validate_answers` then errors `expected list for multiselect`. A working `--data api_tracks=python` (in-process remap) is exported as a **non-ingestible** `riso copy` command. `export yaml` is fine (YAML lists). `copier --data` may YAML-parse the same token; the first-class `riso_command` does not. |
| **evidence** | `export.py` L36–59; `helpers.py` L30–59; `template/__init__.py` L419–421; `tests/unit/test_cli/test_export.py` L74–87 asserts remapped dests appear (`api_module=enabled`) but never re-parses them. |
| **fix** | Serialize list dests as YAML (`[python]`) **and** YAML-parse `--data` values in `parse_data_pairs` (or emit `--answers-file` only). Add a round-trip test: export remapped wrap-list `--data` → `parse_data_pairs` → list → `run_validate` ok. |

## Inspected, not findings

| Item | Why not P0/P1 |
| --- | --- |
| Plan v3 lucia remap | Live schema/docs/wizard/CLI all fail-close lucia |
| W2-CLI-JOIN / ASSURANCE JOIN narrative | Stale; live JOIN tests use `saas_auth=firebase` |
| `riso recopy` omits `remap` preview payload | Plan required preview on update/migrate; recopy still apply-then-rejects and dry-run does not write dest |
| `riso validate` is schema-only (no combo gates) | Generation gates run on copy/update/recopy; pre-existing split |
| `--data api_languages=python` (string) fails list type | Pre-existing multiselect `--data` limit; in-process remap of old keys still works |
| `riso.cli` `__all__ = ["main"]` without import | Entry point is `riso.cli.app:main`; `python -m riso.cli` uses `__main__.py` |
| `diff` dest YAML via `yaml.safe_load` not `load_answers_file` | Preview path; leftover still apply-then-rejects |
| pytest / `just quality` / tags | Not re-run this session (no shell; `.git/HEAD` hook-denied) |

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 1 (`evidence/W5-R1-CLI.md`) |
| Product / hook / sample / lockfile edits | **0** |
| `samples/*/render/**` hand-edits | **0** |
| Secrets printed | **0** |
| `render_matrix.py` started or killed | **0** |
