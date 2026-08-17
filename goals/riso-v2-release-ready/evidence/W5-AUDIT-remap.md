# W5-AUDIT — remap (apply-then-reject SSOT)

- Task: `AUDIT-remap`
- Wave: W5
- Lane: **remap** (inspect-only)
- Write root: this file only
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset; `.git/HEAD` hook-denied, same as W4-R03)
- Date: 2026-08-14
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**
- Status: **no open P0/P1** after live-file inspection

## Contract checked

`apply_removed_key_remaps` **then** `reject_removed_answer_keys`. No dest overwrite if dest is set. Idempotent. No dual-path aliases after remap.

Eight keys: `api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`, `saas_auth`, `saas_billing`, `include_admin`.

Three-way parity: `src/riso/core/removed_answer_keys.py`, `scripts/lib/removed_answer_keys.py` (`_FALLBACK_*`), `web/src/lib/removedAnswerKeys.ts`.

## Method

Read-only. SSOT: `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/*.md`. Live sources via `read_file` / `grep`. This session has no shell (cannot `git rev-parse` / `uv run pytest` / `check_removed_key_ssot.py`). `.git/HEAD` is hook-denied.

Prior recorded ladder: `evidence/W3-PL-T10-ssot.txt` (`check_removed_key_ssot.py` exit 0) and `evidence/W4-A01-pytest-agents.txt` (remap/migrate/update **unit** tests passed; two JOIN integration tests failed on then-`api_tracks=python`). Those JOIN failures are **stale vs live test source** (see below).

Do not treat ASSURANCE, W2-CLI-JOIN, or residual narrative as live truth.

## 1. Eight-key machine table (three-way)

Live `REMOVED_ANSWER_KEYS` / `ANSWER_KEY_REMAPS` match on all three surfaces and `plan.taskgraph.json` `remap_keys`.

| Old key | action | dest |
| --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` |
| `api_language` | wrap-list | `api_languages` |
| `docs_site` | derive | `docs_module`, `docs_framework` |
| `mcp_language` | wrap-list | `mcp_languages` |
| `saas_starter_module` | rename | `saas_infra_module` |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` |
| `include_admin` | rename-bool | `saas_admin_dashboard` |

Replacement prose is identical (backticks included), e.g. `saas_auth` → `` `saas_auth_module` plus `saas_auth_provider` ``.

`scripts/lib` prefers packaged `riso.core.removed_answer_keys` and binds `_FALLBACK_*` only on `ImportError`. Fallback tables + `_fallback_apply_removed_key_remaps` mirror core operators, dest-write, leftover-leave, and drop-old-after-apply.

`check_removed_key_ssot.py` compares key sets, op tuples, and `CANONICAL_OPS`; also scans sample `copier-answers.yml` for leftover YAML keys. Wired as `just quality` → `ssot`.

Sample leftover scan this session: `rg '^(api_tracks|api_language|docs_site|mcp_language|saas_starter_module|saas_auth|saas_billing|include_admin):' samples --glob '**/copier-answers.yml'` → **empty**.

`lucia` is **not** in `_SAAS_AUTH_PROVIDERS` / `SAAS_AUTH_PROVIDERS` (`clerk`, `authjs` only). Copier `saas_auth_provider` choices are `clerk` / `authjs`. Fail-closed lucia is intentional (no new vendor; documented in `docs/guides/v2-migration.md` and the no-legacy policy). Plan v3 table still lists lucia as remappable — **stale plan text**, not a live SSOT gap.

## 2. Apply API / dest / leftover

`apply_removed_key_remaps` (`src/riso/core/removed_answer_keys.py`):

- Does not mutate the input mapping.
- Unmapped values (`dests is None`) **leave the old key** and record **no** op.
- `_write_dests` writes a dest only when `key not in out`; still records the kept dest in `after`.
- Successful apply **deletes** the old key.
- Second apply on remapped answers is a no-op (`ops == ()`).

`reject_removed_answer_keys` / `apply_then_reject_removed_keys` live in `src/riso/core/answers.py`. Choke point used by CLI load paths:

```text
result = apply_removed_key_remaps(answers)
reject_removed_answer_keys(result.answers)
```

Error shape: `{key}: removed answer key; use {REMOVED_ANSWER_KEYS[key]}`.

TS twin: `applyRemovedKeyRemaps` + `applyThenRejectRemovedKeys` (same order). Persist hydration uses `dropLeftoverRemovedKeys` (remap then **drop** leftovers, never throw) in `web/src/lib/store.ts` `canonicalizeConfig` / `web/src/lib/configSchemas.ts` `parseCustomPresetsStorage`. Share/export/presets/`updateConfig` still **reject**. That is a persist-hydration exception, not a dual-path alias (old keys are not kept live). Below P1 for this lane.

## 3. CLI update / migrate (dry-run + live)

`riso migrate` (`src/riso/cli/commands/migrate.py` + `app.py`): `DEST` **or** `--answers-file` (exactly one), `--dry-run`, global `--json`. Calls `remap_answers_file(path, write=not dry_run)`.

`remap_answers_file`: apply-then-reject first; write only if `write and result.ops`. Leftover raises **before** any write.

`riso update` remaps `.copier-answers.yml` the same way. Dry-run: no write, then `validate_answers_for_generation`, then `compute_diff` with remapped answers, payload includes `remap`. Live: write remapped YAML when ops exist, then Copier `run_update`.

Preview: `src/riso/cli/output.py` `_emit_remap_preview` (ops / already-canonical / `dry_run` / `wrote`).

Other CLI sites also apply-then-reject (not reject-only):

| Site | Path |
| --- | --- |
| `resolve_answers` | `src/riso/cli/helpers.py` |
| `validate_and_raise` | same |
| `validate` / `copy` | via `resolve_answers` |
| `recopy` | dest file via `remap_answers_file`; merge via `apply_then_reject_removed_keys` |
| `diff` | apply-then-reject on merged answers |
| `export` | apply-then-reject on `--data` overrides |

## 4. Hooks apply then reject

`template/hooks/pre_gen_project.py`:

- `main()` calls `_validate_removed_answer_keys` **before** `_validate_generation_answers`.
- `_validate_removed_answer_keys` = `_apply_removed_key_remaps` then `_reject_leftover_removed_keys`.
- Apply mutates context in place; leftovers stay for reject.

`template/hooks/post_gen_project.py` `validate_removed_answer_keys`: apply in place, then `SystemExit(1)` on leftover.

`rg` of leftover old-key **reads** in hooks (`saas_auth` / `api_tracks` / `docs_site` / … as live aliases) is empty. Remaining `saas_auth_*` reads are canonical dests.

W1 outbox `generation-gates-saas-auth.md` still says gates leftover-scan runs **without** apply (CLI-T15 pending). Live `validate_answers_for_generation` **does** apply first. Outbox is stale.

## 5. `generation_gates` must not read leftover `saas_auth`

`_collect_saas_selected` collects `saas_auth_module` and `saas_auth_provider` only. No leftover `saas_auth` token.

`validate_answers_for_generation` remaps, then leftover-errors on the remapped dict, then SaaS / language gates on remapped answers. Mapped `saas_auth=clerk` does not fail closed; `saas_auth=firebase` does.

Control plane: `_enforce_generation_gates` applies remaps (mutates when ops exist) then `validate_answers_for_generation`. Called from `run_generator`, `run_update`, recopy merge.

## 6. Tests (operators, dest, leftover, CLI, hooks)

Fixtures: `tests/unit/test_cli/fixtures/remap/` — one YAML per old key + `mixed.yml` + `already_canonical.yml` + `leftover.yml` (`saas_auth: firebase`).

| Coverage | Where |
| --- | --- |
| 8 operators + table completeness | `test_remap.py` |
| idempotent second apply | `test_idempotent_second_apply_is_noop` |
| do-not-overwrite wrap/split/derive | `test_do_not_overwrite_dest_*` |
| leftover reject (`firebase`) | `test_unmapped_value_left_for_reject`, `test_unknown_leftover_raises_after_apply` |
| lucia fail-closed | `test_lucia_saas_auth_fail_closes` |
| migrate dry-run (8 keys, no write) | `test_migrate.py` `test_migrate_dry_run_loads_fixture` |
| migrate live + idempotent second | `test_migrate_mixed_fixture_then_idempotent_second_pass` |
| migrate leftover no-write | `test_migrate_leftover_fails_closed` |
| update dry-run / live write / leftover | `test_update.py` |
| core ↔ scripts.lib fallback parity | `test_removed_keys_packaging.py` (includes firebase leftover + dest-already-set) |
| gates leftover + no `saas_auth` collect | `test_generation_gates.py` |
| helpers / answers choke point | `test_helpers.py`, `test_answers.py` |
| hooks apply-then-reject + dest + leftover | `tests/unit/hooks/test_pre_gen_project.py`, `test_post_gen_project.py` |
| TS twin (operators, dest, lucia, leftover.yml) | `web/src/__tests__/removedAnswerKeys.test.ts` |

W4-A01 recorded **98** remap/migrate/update unit tests passed. This session did not re-run pytest.

## 7. Integration leftover is `saas_auth=firebase`

Live source (not remappable `api_tracks`):

- `tests/integration/test_riso_cli.py::test_validate_rejects_removed_key` — `--data saas_auth=firebase`, expects exit 2 and `saas_auth` in errors.
- `tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker` — `data={"saas_auth": "firebase", ...}`, expects `ValidationFailedError`, worker not called.

W3-PL-T03 traceback still shows the **old** argv `api_tracks=python` (exit 0 / DID NOT RAISE). W4-A01 summary lists the same two names as failed. Residual `CLI.md` / `W2-CLI-JOIN.md` / ASSURANCE still narrate that failure. **Live files are already flipped.** Treat those docs as stale; do not restore reject-before-remap.

`residuals/CLI.md` status field is already `closed (parent closeout 2026-08-14)`; the body still describes the api_tracks failure.

## Findings

| id | severity | file | issue |
| --- | --- | --- | --- |
| REMAP-STALE-01 | stale | `goals/riso-v2-release-ready/ASSURANCE.md` | Closeout still claims JOIN tests fail on remappable `api_tracks`. Live tests use `saas_auth=firebase`. |
| REMAP-STALE-02 | stale | `goals/riso-v2-release-ready/residuals/CLI.md` | Narrative + `W2-CLI-JOIN.md` still show api_tracks reject-before-remap. Status already closed; source already flipped. |
| REMAP-STALE-03 | stale | `goals/riso-v2-release-ready/plan.md` | Plan/outbox still remap `lucia` and say gates reject-only. Live: lucia fail-closes; gates apply then reject. |
| REMAP-CLOSED-01 | closed | `src/riso/core/removed_answer_keys.py` | 8-key three-way SSOT + fallback twin + TS operators. |
| REMAP-CLOSED-02 | closed | `src/riso/core/answers.py` | Apply-then-reject choke point wired on update/migrate (dry-run+live), resolve/validate/copy/recopy/diff/export. |
| REMAP-CLOSED-03 | closed | `src/riso/core/generation_gates.py` | `_collect_saas_selected` does not read leftover `saas_auth`. |
| REMAP-CLOSED-04 | closed | `tests/unit/test_cli/test_remap.py` | Operators, idempotence, do-not-overwrite, leftover reject (`firebase`), lucia fail-closed. |
| REMAP-CLOSED-05 | closed | `tests/integration/test_riso_cli.py` | JOIN leftover is unmapped `saas_auth=firebase`, not remappable `api_tracks`. |

No still-open implementation P0/P1.

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 1 (`evidence/W5-AUDIT-remap.md`) |
| Product / hook / sample / lockfile edits | 0 |
| `samples/*/render/**` hand-edits | 0 |
| Secrets printed | 0 |
| `render_matrix.py` started or killed | 0 |
