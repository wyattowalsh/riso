# W0-T06 evidence — plan.taskgraph.json

- Captured (UTC): `2026-07-29T02:00:00Z`
- Repo: `/Users/ww/dev/projects/riso`
- Task: W0-T06 Emit/refresh `plan.taskgraph.json` checksum of locks; JSON valid
- Artifact: `goals/riso-lanes-assurance/plan.taskgraph.json`

## Validation

| Check              | Result                                                                |
| ------------------ | --------------------------------------------------------------------- |
| JSON parses        | **yes** (object with required top-level keys)                         |
| Waves present      | W0, W1, W2, W3, W4 only — **no new waves invented**                   |
| W0 join            | W0-T01…W0-T06                                                         |
| W1 serial handoffs | W1-H01…H08 + W1-OUT                                                   |
| W2 lanes           | PY, NODE, SAAS, SYS, DESKTOP, CLI                                     |
| W3 PLATFORM        | PL-T01…PL-T10                                                         |
| W4 ASSURANCE       | A-T01…A-T04                                                           |
| `verify_full`      | present (quality, 23 validates, render_matrix, jinja, pytest targets) |

## Lock checksum refresh (W0-T06)

Added fields (no wave/task ID invent):

- `lock_checksum` — canonical newline-sorted exclusive locks + `json_valid: true` + `no_new_waves: true`
- `lane_locks` — per-lane exclusive roots mirrored from plan.md
- `grok_context_packs` — 9 pack paths (W0-T05 outputs)

Canonical lock set (sorted):

```
.github/context/
samples/*/copier-answers.yml
samples/metadata/
scripts/ci/
scripts/render-samples.sh
src/riso/
template/copier.yml
template/files/.github/context/
template/files/electron/
template/files/go/
template/files/module_catalog.json.jinja
template/files/node/
template/files/node/saas/
template/files/python/
template/files/quality/
template/files/rust/
template/files/saas-starter/
template/files/tauri/
template/files/testing/
template/hooks/
template/macros/
template/prompts/
tests/unit/test_cli/
```

## Status

**green** — JSON valid; locks checksum refreshed; waves unchanged.
