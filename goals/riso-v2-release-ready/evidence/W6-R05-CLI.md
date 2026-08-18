# W6-R05 — surface=CLI

- Task: `W6-R05`
- Wave: W6 review (second dry pass)
- Surface: **CLI**
- Mode: read-only inspection
- Write root: this file only
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-18
- Compared: `goals/riso-v2-release-ready/evidence/W6-R04-CLI.md` (P0 empty; P1 empty). Also noted `W6-R03-CLI.md` / `W5-R1-CLI.md`.
- Product-code edits: **0**
- `samples/*/render/**` writes: **0**
- Lockfile / secret / `riso-mcp` / `render_matrix.py`: **0**
- Status: **P0 empty**; **P1 empty**

## Method

Live-tree only. Did **not** treat `ASSURANCE.md`, `W2-CLI-JOIN.md`, `W5-CLOSE-CLI.md`, or residuals as truth. `W6-R04-CLI.md` used as the comparison checklist, not as current status.

Inspected:

- `src/riso/cli/**` (`app.py`, `helpers.py`, `output.py`, `config.py`, all `commands/*`)
- `src/riso/core/**` (`removed_answer_keys.py`, `answers.py`, `generation_gates.py`, `diff.py`, `errors.py`, `names.py`, `paths.py`)
- `src/riso/template/**` (`__init__.py` `_enforce_generation_gates`)
- `tests/unit/test_cli/**` (remap / migrate / export / helpers / update / recopy / validate / generation_gates)

No pytest / `just quality` / git rev re-run this session (read-only review; no shell).

## Contract checked

`apply_removed_key_remaps` **then** `reject_removed_answer_keys`. No dest overwrite if dest is set. Idempotent. No dual-path aliases after remap.

Eight keys: `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`.

Generated Node floor stays 20 (CLI does not raise it). OpenSpec extra stays off by default (CLI does not mention `openspec`). Maintainer `riso-mcp` must stay gone under `src/riso`.

## vs W6-R04

| W6-R04 item                                      | W6-R05 live                                      |
| ------------------------------------------------ | ------------------------------------------------ |
| P0 empty (apply-then-reject + migrate wired)     | **still true**                                   |
| P1 empty                                         | **still true**                                   |
| `CLI-P1-export-list-data` already not still real | **still not real** — YAML wrap-list + round-trip |
| No `export list` subcommand                      | **still true** (`cli` + `yaml` only)             |

No new P0/P1 versus W6-R04.

## Live remap SSOT

`src/riso/core/removed_answer_keys.py`:

- `REMOVED_ANSWER_KEYS` / `ANSWER_KEY_REMAPS` are the same 8 keys.
- `_SAAS_AUTH_PROVIDERS = {clerk, authjs}`. `lucia` / `firebase` leave the old key (`dests is None`) for reject.
- `_write_dests` writes only when `key not in out`. Successful apply deletes the old key.
- Input mapping is not mutated.

Choke point: `src/riso/core/answers.py` `apply_then_reject_removed_keys` (L79–83) and `remap_answers_file` (apply-then-reject, write only if `write and result.ops`).

Old-key tokens under `src/riso` exist only inside the remap table / leftover error strings (`removed_answer_keys.py`). No `answers.get("<old key>")` dual-path reads.

`rg riso-mcp src/riso` is **empty**. `rg` Node 22 / `openspec` under `src/riso` is **empty**.

## Call-site wiring (apply then reject)

| Site                                               | Live                                                                                     |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `helpers.resolve_answers`                          | apply-then-reject on provided, then merge defaults, then apply-then-reject again         |
| `helpers.validate_and_raise`                       | apply-then-reject, mutate caller, then schema validate                                   |
| `validate` / `copy` / `export`                     | via `resolve_answers`                                                                    |
| `migrate` / `update`                               | `remap_answers_file` (dry-run no write; leftover no write)                               |
| `recopy`                                           | provided + dest file + merge all apply-then-reject; dest write only when live            |
| `diff` copy                                        | `resolve_answers`                                                                        |
| `diff` update/recopy                               | apply-then-reject on `{**existing, **provided}`                                          |
| `compute_diff`                                     | apply-then-reject on preview answers; update/recopy re-merge dest then apply-then-reject |
| `generation_gates.validate_answers_for_generation` | apply first, leftover errors on remapped dict, then SaaS/language gates                  |
| `_collect_saas_selected`                           | `saas_auth_module` / `saas_auth_provider` only — no leftover `saas_auth`                 |
| `template._enforce_generation_gates`               | apply (mutate if ops), then gates; used by `run_generator` / `run_update` / `run_recopy` |

`--skip-post-gen` remains in `_GLOBAL_FLAGS` (`app.py` L475–486).

`riso migrate` exists (`app.py` L270–293): exactly one of DEST or `--answers-file`; `--dry-run`; global `--json`. Implementation: `src/riso/cli/commands/migrate.py` → `remap_answers_file`. Tests: `tests/unit/test_cli/test_migrate.py` (8-key fixtures, dry-run, dest `.copier-answers.yml`, leftover fail-closed, idempotent second pass, `--help`).

`riso update` remaps `.copier-answers.yml` first, attaches `remap` preview, dry-run runs generation gates without write, live writes remaps then Copier.

Unit leftover / remappable coverage (not JOIN integration):

- `test_remap.py` — wrap/derive/rename/split/rename-bool, dest-not-overwrite, idempotence, leftover `firebase`, lucia fail-closed
- `test_helpers.py` — remappable `api_language` accepted; leftover `saas_auth=firebase` rejected
- `test_export.py` — remapped dests emitted; old keys omitted; wrap-list `--data` round-trips

## P0 — correctness / contract break

None after inspection.

Apply-then-reject is wired at every owned CLI/control-plane site. Dest overwrite is refused. Second apply is a no-op. Unmapped leftovers fail closed. Remappable `api_tracks=python` is not fail-closed. No dual-path old-key reads. No `riso-mcp`. `riso migrate` is registered and uses `remap_answers_file`. Generated Node floor is not raised in this tree. OpenSpec extra default is not flipped on by CLI.

## P1 — lockstep / DX

None.

### Disposition of closed `CLI-P1-export-list-data`

| Field             | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **id**            | `CLI-P1-export-list-data`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **W5-R1 issue**   | `riso export cli` serialized wrap-list dests as Python list repr (`api_languages=['python']`); `parse_data_pairs` / `_coerce_value` did not YAML-parse, so re-ingest was a string and Copier multiselect failed.                                                                                                                                                                                                                                                                                                     |
| **W6-R04 / R05**  | **fixed / not still real.** `format_data_assignment` (`src/riso/cli/commands/export.py` L20–29) YAML-dumps `list`/`dict` with `default_flow_style=True`. `_coerce_value` (`src/riso/cli/helpers.py` L49–68) `yaml.safe_load`s and returns lists/dicts. `test_export_cli_wrap_list_round_trips_through_parse_and_validate` (`tests/unit/test_cli/test_export.py` L101–128) splits the exported `riso_command`, parses `--data`, asserts `api_languages == ["python"]`, then `resolve_answers` + `validate_and_raise`. |
| **`export list`** | **does not exist.** `export` typer has `cli` and `yaml` only (`app.py` L395–472), plus aliases `export-cli` / `export-yaml`. `--data` on those commands is still `list[str]` key=value pairs, not a boolean flag and not an answers-file path. Do not re-file a missing `export list --data` boolean.                                                                                                                                                                                                                |

## Inspected, not findings

| Item                                                          | Why not P0/P1                                                                    |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Lucia fail-closed                                             | Live remap table + `test_lucia_saas_auth_fail_closes`; not a dest alias          |
| `riso recopy` omits `remap` preview payload                   | Still apply-then-rejects; dry-run does not write dest                            |
| `riso validate` is schema-only (no combo gates)               | Generation gates run on copy/update/recopy; pre-existing split                   |
| `--data api_languages=python` (bare string)                   | Pre-existing multiselect `--data` limit; exported wrap-list now YAML-round-trips |
| `diff` dest YAML via `yaml.safe_load` not `load_answers_file` | Preview path; leftover still apply-then-rejects                                  |
| pytest / `just quality` / tags                                | Not re-run this session                                                          |

## Path lock

| Class                                    | Count                        |
| ---------------------------------------- | ---------------------------- |
| This-session writes                      | 1 (`evidence/W6-R05-CLI.md`) |
| Product / hook / sample / lockfile edits | **0**                        |
| `samples/*/render/**` hand-edits         | **0**                        |
| Secrets printed                          | **0**                        |
| `render_matrix.py` started or killed     | **0**                        |

## summary

surface=cli. Compared to W6-R04-CLI (P0 empty, P1 empty): live apply-then-reject remains the single remap contract and is still wired through resolve/validate/copy/export/migrate/update/recopy/diff/generation_gates. `riso migrate` is still registered and writes only after apply-then-reject. Closed W5-R1 `CLI-P1-export-list-data` is still not real. No new findings. **P0 empty. P1 empty.**
