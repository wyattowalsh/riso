# Handoff: `<change-id>`

Copy this file to `goals/riso-lane-coord/inbox/<change-id>.md` (or `goals/<requesting-lane>/handoffs/<change-id>.md`) and fill every required section before COORD applies.

| Field | Value |
|-------|-------|
| **change_id** | `<change-id>` |
| **requesting_lane** | `py` \| `node` \| `saas` \| `sys` \| `desktop` \| `cli` \| `platform` \| `fe` \| `qual` \| other |
| **summary** | One-line intent |
| **status** | `proposed` \| `in_progress` \| `applied` \| `rejected` |
| **needs_shared_generation_gates** | `yes` \| `no` — if **yes**, CLI lane must change `src/riso/core/generation_gates.py` (and related); **COORD never edits `src/riso/**`** |

---

## Prompt keys

Required for any new/updated Copier answers. Include defaults and when-conditions.

| key | type | default | when | help | choices (if any) |
|-----|------|---------|------|------|------------------|
| | | | | | |

Notes:

- Prefer clean current-state contracts; no legacy/dual-path keys unless human requires them.
- List only keys this handoff needs; do not restate the entire `copier.yml`.

---

## Hook validation rules

Illegal combinations and expected errors (pre_gen UX). Prefer shared gates when `riso validate` must enforce the same rule.

| condition (illegal combo) | error message | preferred surface (`hooks_local` \| `gates_shared`) |
|---------------------------|---------------|-----------------------------------------------------|
| | | |

If `preferred_surface` is `gates_shared`, set `needs_shared_generation_gates: yes` and describe the CLI follow-up under **CLI / generation_gates handoff** below. COORD may add hook-local messages only for UX/tooling; it does **not** edit `src/riso/**`.

---

## Module catalog rows

Updates to `template/files/module_catalog.json.jinja` (`selected_state` expressions, new modules, deps, validation commands).

| name | prompt_key | default_state | selected_state | dependencies | docs_path | ci_jobs | validation_commands |
|------|------------|---------------|----------------|--------------|-----------|---------|---------------------|
| | | | | | | | |

---

## Macros

Impact on `template/macros/**` (e.g. `module_flags.jinja`).

| file | change |
|------|--------|
| | |

---

## Context snippets

Files under `.github/context/` that must be added/updated (COORD mirrors to `template/files/.github/context/` for byte parity).

| filename | intent |
|----------|--------|
| | |

---

## CLI / generation_gates handoff

**COORD never edits `src/riso/**`.** If shared validation must change:

| Item | Detail |
|------|--------|
| Needed? | `yes` \| `no` |
| Files (CLI-owned) | e.g. `src/riso/core/generation_gates.py`, `src/riso/core/removed_answer_keys.py` |
| Summary for CLI lane | What to enforce in `validate_answers_for_generation` |

---

## Payload follow-ups

What other lanes implement **after** COORD publishes the outbox. Paths only — no payload implementation in this handoff.

| lane | exclusive paths | acceptance note |
|------|-----------------|-----------------|
| | | |

COORD stops at the contract boundary. Payload lanes must **not** re-touch COORD paths (`template/copier.yml`, `template/hooks/**`, `template/macros/**`, `template/files/module_catalog.json.jinja`, `template/prompts/**`, `.github/context/**`, `template/files/.github/context/**`).

---

## Samples to re-validate

| path |
|------|
| `samples/<variant>/copier-answers.yml` |

---

## Non-goals

- …

---

## Author notes (optional)

- …
