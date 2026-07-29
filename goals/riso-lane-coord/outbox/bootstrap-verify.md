# Bootstrap verification evidence

First `/goal` run for COORD: process artifacts only — no unsolicited contract edits by this run.

| Field         | Value                           |
| ------------- | ------------------------------- |
| **change_id** | `bootstrap-verify`              |
| **status**    | `applied` (bootstrap complete)  |
| **scope**     | `goals/riso-lane-coord/**` only |

## Artifacts created

- [x] `inbox/`, `outbox/`, `inbox/done/` (+ `.gitkeep`)
- [x] `handoff-template.md`
- [x] `outbox-template.md`
- [x] `LANE.md`
- [x] `APPLY-CHECKLIST.md`
- [x] `README.md`
- [x] `examples/minimal-handoff.md`, `examples/minimal-outbox.md` (**non-executable**)

## Verification evidence

| stage       | command                                                                         | result                                      | log under `{SCRATCH}`                             |
| ----------- | ------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------- |
| structural  | package + section gates                                                         | ARTIFACTS_AND_SECTIONS_OK                   | `structural_check.txt`                            |
| V1 ×2       | `uv run python scripts/ci/verify_context_sync.py`                               | exit 0; in sync                             | `verify_context_sync.log`                         |
| V2 ×2       | `uv run riso validate --answers-file samples/default/copier-answers.yml --json` | `ok: true`, `valid: true`                   | `riso_validate_default.json`, `_run2`             |
| V3p         | `uv run riso --json prompts`                                                    | `ok: true`                                  | `riso_prompts.json`                               |
| V3c         | `uv run riso --json catalog modules`                                            | `ok: true`, 11 modules                      | `riso_catalog.json`                               |
| V5 optional | `uv run pytest tests/unit/ci/test_verify_context_sync.py -q -n 0`               | 21 passed                                   | `pytest_verify_context_sync.txt`                  |
| V6          | package inventory + path audit                                                  | all 19 files under `goals/riso-lane-coord/` | `goal_package_files.txt`, `path_audit_report.txt` |

Notes:

- Catalog smoke is **`uv run riso --json catalog modules`** (subcommand group).
- Pre-existing dirty paths elsewhere in the worktree are not from this bootstrap.
