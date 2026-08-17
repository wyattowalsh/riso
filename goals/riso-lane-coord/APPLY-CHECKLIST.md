# COORD apply checklist (one change-id)

Use after a filled handoff exists in `inbox/` (or sibling `handoffs/`). **Serial single writer.** Do not start a second change-id until this list completes for the current CID.

## Pre-flight

- [ ] R0: No branch/commit/push unless human asked
- [ ] R1–R2: Confirmed handoff path and `change_id`
- [ ] R3: Surface matrix filled (copier / hooks / macros / catalog / context / gates)
- [ ] R4: `needs_shared_generation_gates` decided (CLI handoff only if yes)
- [ ] R6: Affected `samples/*/copier-answers.yml` listed
- [ ] R7: Baseline `uv run python scripts/ci/verify_context_sync.py` (if context may change)

## Claim

- [ ] C0: Set status `in_progress` on handoff; sole claimer
- [ ] C1: Schema-complete vs [handoff-template.md](./handoff-template.md); else reject outbox and stop

## Apply (only surfaces named by handoff)

- [ ] C2: `template/copier.yml` (+ `template/prompts/**` if needed) — keys, defaults, when, help
- [ ] C3: `template/macros/**` if required
- [ ] C4: Hook validation (`pre_gen` / `post_gen` / `validators/**`) with clear errors
- [ ] C5: Draft CLI ticket text if shared gates needed — **do not edit `src/riso/**`**
- [ ] C6: `template/files/module_catalog.json.jinja` rows / `selected_state`
- [ ] C7: Context both sides (`.github/context/` and `template/files/.github/context/`)
- [ ] C8: Path audit — no forbidden trees dirtied

## Outbox

- [ ] C9: Write `outbox/<change-id>.md` from [outbox-template.md](./outbox-template.md)
- [ ] Explicit “do not re-touch COORD paths” present for payload lanes
- [ ] CLI section filled when gates handoff required
- [ ] C10: Mark handoff `applied` or move to `inbox/done/`

## Verification (default bar)

- [ ] V1 if context touched: `uv run python scripts/ci/verify_context_sync.py`
- [ ] V2: `uv run riso validate --answers-file <affected> --json` for each listed sample
- [ ] V3 if prompts/catalog touched: `uv run riso --json prompts` and/or `uv run riso --json catalog modules`
- [ ] V4 if hooks changed: narrow `uv run pytest tests/unit/hooks/... -q -n 0`
- [ ] V6: `git status --short` allowlist only
- [ ] Evidence table filled in outbox

## Stop conditions

- [ ] No PY/NODE/SAAS/SYS/DESKTOP/FE payload implementation in this run
- [ ] No full matrix unless human asked or contract unprovable cheaper
- [ ] No secrets committed/printed/persisted
