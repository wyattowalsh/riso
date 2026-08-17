# COORD lane — operating manual

Standing protocol for the **serial Wave-0** template-contract owner in the Riso maintainer repo. This is not a product feature backlog.

## One-line law

Many agents may **read** contracts. Only **one** agent may **write** COORD paths. Payload lanes implement only after outbox publish — never by re-editing COORD files.

## Exclusive write ownership

| Path | Notes |
|------|--------|
| `template/copier.yml` | Prompt SSOT |
| `template/hooks/**` | pre_gen, post_gen, validators |
| `template/macros/**` | Shared Jinja predicates |
| `template/files/module_catalog.json.jinja` | Module rows + `selected_state` |
| `template/prompts/**` | Prompt fragments |
| `.github/context/**` | Context snippets (source) |
| `template/files/.github/context/**` | Must stay **byte-parity** with `.github/context/` |
| `goals/riso-lane-coord/**` | Process artifacts, inbox/outbox |

## Forbidden writes (never)

- `template/files/python/**`, `node/**`, `go/**`, `rust/**`, `frontend/**`, `electron/**`, `tauri/**`, `quality/**`, `testing/**`
- `src/riso/**` (including `generation_gates` / `removed_answer_keys`) — **CLI lane**
- `web/**`
- `samples/*/render/**` (regenerate only via scripts)
- `uv.lock`, `pnpm-lock.yaml` (hand-edit)
- Secrets (commit, print, or persist)

## Hard rules

1. No branches, worktrees, commits, or pushes unless the human explicitly asks.
2. All Python via `uv run` (never bare `python` / `pytest`).
3. Prefer clean current-state contracts; no legacy/migration/dual-path unless human asks or concrete persisted consumers require it.
4. If payload work is needed under language trees: **stop after contract**; list work in outbox — do not implement PY/NODE/SAAS/SYS/DESKTOP bodies.
5. Shared answer gates live under CLI (`src/riso/core/generation_gates.py`). COORD never edits them; publish CLI handoff in outbox when needed.

## Inbound / outbound

| Direction | Location | Template |
|-----------|----------|----------|
| In | `goals/riso-lane-coord/inbox/<change-id>.md` or `goals/<lane>/handoffs/` | [handoff-template.md](./handoff-template.md) |
| Out | `goals/riso-lane-coord/outbox/<change-id>.md` | [outbox-template.md](./outbox-template.md) |

Applied handoffs may move to `inbox/done/`.

## Wave model (parallel where legal)

```text
R  READ-ONLY RECON     — many agents
B  BOOTSTRAP docs      — first empty-inbox run; goals/* only
C  COORD APPLY         — single writer, one change-id
O  OUTBOX FAN-OUT      — messengers / SSOT sections
P  PAYLOAD             — other lanes (COORD stops)
V  VERIFY              — staged commands
```

**Never** two writers on `copier.yml` / hooks / catalog / context.

## Apply loop (summary)

1. Recon: list inbox; empty → idle SOP (or bootstrap if artifacts missing).
2. Claim one `change-id`; reject incomplete handoffs.
3. Smallest coherent edits across owned surfaces only.
4. Context: edit both trees in one step when context is touched.
5. If gates need shared logic → CLI outbox section; do not edit `src/riso/**`.
6. Publish `outbox/<change-id>.md`.
7. Run default verification bar; record evidence in outbox.

See [APPLY-CHECKLIST.md](./APPLY-CHECKLIST.md) for micro-steps.

## Idle SOP

When `inbox/` and sibling handoffs are empty:

- Do **not** invent prompt keys or touch contracts.
- Report idle; restate ownership if helpful.
- Bootstrap (templates + dry-run) only when process artifacts are missing.

## Default verification bar

| Stage | When | Command |
|-------|------|---------|
| V1 | Context touched or bootstrap health | `uv run python scripts/ci/verify_context_sync.py` |
| V2 | Apply / bootstrap | `uv run riso validate --answers-file samples/<v>/copier-answers.yml --json` |
| V3 | Prompts/catalog touched or bootstrap | `uv run riso --json prompts` · `uv run riso --json catalog modules` |
| V4 | Hooks changed | `uv run pytest tests/unit/hooks/... -q -n 0` (narrow `-k` when possible) |
| V6 | After writes | `git status` allowlist (COORD-owned + goals only) |

Full sample matrix is **not** default.

## Related

- [facts.md](./facts.md) — accepted outcomes
- [plan.md](./plan.md) — hyperfine task graph
- [goal.md](./goal.md) — launch entry
