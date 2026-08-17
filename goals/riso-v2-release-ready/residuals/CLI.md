# Residual — Lane CLI

## Summary

CLI-T10–T18 are green: apply-then-reject is wired at every owned call site; `riso migrate` exists; fixtures load. Live unit remap tests pass. Integration JOIN tests assert fail-closed leftover `saas_auth=firebase`, **not** reject-before-remap on remappable `api_tracks`.

## Residuals

### R1 — JOIN integration tests — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | CLI-JOIN |
| **owner** | GOAL |
| **status** | closed |
| **command** | `uv run pytest tests/integration/test_riso_cli.py::test_validate_rejects_removed_key tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker -q -n 0` |
| **blocking reason** | — |
| **redacted log** | 2026-08-14 W5-CLOSE: both tests **PASSED** (`join_exit=0`). Remap/migrate/update suite **98 passed**. Tests use unmapped leftover `saas_auth=firebase`. Do **not** restore reject-before-remap on remappable `api_tracks`. |
| **fix** | none |
| **evidence** | `goals/riso-v2-release-ready/evidence/W5-CLOSE-pytest-remap.txt` |
