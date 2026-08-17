# Contract delta: `<change-id>`

Published by COORD after applying an inbox handoff. Payload and CLI lanes consume this document and implement only their exclusive paths.

| Field | Value |
|-------|-------|
| **change_id** | `<change-id>` |
| **applied_at** | ISO-8601 timestamp |
| **status** | `applied` \| `rejected` \| `partial` |
| **source_handoff** | `goals/riso-lane-coord/inbox/<change-id>.md` (or sibling handoffs path) |

---

## Answer keys changed

| key | before | after |
|-----|--------|-------|
| | | |

---

## Illegal combos now enforced

| rule / condition | location (`pre_gen` \| `post_gen` \| `gates-handoff`) | error message (summary) |
|------------------|------------------------------------------------------|-------------------------|
| | | |

---

## Module catalog rows

| name | change |
|------|--------|
| | |

---

## Context files

| file | action (`add` \| `update` \| `remove`) | parity_verified (`yes` \| `no` \| `n/a`) |
|------|----------------------------------------|------------------------------------------|
| | | |

When context was touched, both `.github/context/` and `template/files/.github/context/` must be byte-identical (`uv run python scripts/ci/verify_context_sync.py`).

---

## CLI handoff required

| Field | Value |
|-------|-------|
| **required** | `yes` \| `no` |
| **summary** | What CLI must change under `src/riso/**` (e.g. `generation_gates`) |
| **CLI ticket path** | optional `goals/riso-lane-cli/inbox/...` when that package exists |

COORD never edits `src/riso/**`. If `required=yes`, CLI owns the shared gate change.

---

## Payload checklist

**Do not re-touch COORD paths.** Implement only the paths listed for your lane.

COORD exclusive (closed after this delta):

- `template/copier.yml`
- `template/hooks/**`
- `template/macros/**`
- `template/files/module_catalog.json.jinja`
- `template/prompts/**`
- `.github/context/**`
- `template/files/.github/context/**`

| lane | exclusive paths to implement | acceptance note | done? |
|------|------------------------------|-----------------|-------|
| py | `template/files/python/**` | | ☐ |
| node | `template/files/node/**` except `node/saas/` | | ☐ |
| saas | `template/files/node/saas/**` | | ☐ |
| sys | `template/files/go/**`, `template/files/rust/**` | | ☐ |
| desktop | `template/files/electron/**`, `template/files/tauri/**` | | ☐ |
| fe | `template/files/frontend/**` | | ☐ |
| qual | `template/files/quality/**`, `template/files/testing/**` | | ☐ |
| platform | sample **answers**/metadata (never `samples/*/render/` by hand) | | ☐ |
| cli | `src/riso/**` only if CLI handoff required | | ☐ |

---

## Verification evidence

| stage | command | result |
|-------|---------|--------|
| V1 context (if touched) | `uv run python scripts/ci/verify_context_sync.py` | |
| V2 samples | `uv run riso validate --answers-file samples/<v>/copier-answers.yml --json` | |
| V3 prompts | `uv run riso --json prompts` | |
| V3 catalog | `uv run riso --json catalog modules` | |
| V4 hooks (if hooks changed) | `uv run pytest tests/unit/hooks/... -q -n 0` | |
| V6 path audit | `git status --short` allowlist | |

Full sample matrix is **not** default.

---

## Residual risks

- …

---

## Notes

- Prefer clean current-state contracts; no legacy dual-path unless required.
- Never hand-edit `samples/*/render/`, `uv.lock`, or `pnpm-lock.yaml`.
- No branches/commits/pushes unless the human explicitly asks.
