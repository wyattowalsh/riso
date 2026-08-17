# W2-CLI-JOIN

- Task: `CLI-JOIN`
- Wave: W2
- Status: **residualed** (unit green; 2 foreign integration tests stale)
- `samples/*/render/**` writes: **0**

## Command

```text
uv run pytest tests/unit/test_cli/ tests/integration/test_riso_cli.py tests/integration/test_control_plane_gates.py -q -n 0
```

## Result

```text
FAILED tests/integration/test_riso_cli.py::test_validate_rejects_removed_key
FAILED tests/integration/test_control_plane_gates.py::test_run_generator_rejects_removed_keys_before_worker
================== 2 failed, 238 passed, 2 skipped in 22.27s ===================
```

Skipped: `test_update_dry_run_json`, `test_recopy_dry_run_json` (default render not present).

## Failures (expected after apply-then-reject)

Both tests send remappable `api_tracks=python`. After CLI-T10/T15 that value remaps to `api_module=enabled` + `api_languages=['python']` and **must not** fail closed.

| Test | Assertion | Actual |
| --- | --- | --- |
| `test_validate_rejects_removed_key` | exit 2 + `api_tracks` error | exit 0, `valid: true` |
| `test_run_generator_rejects_removed_keys_before_worker` | `ValidationFailedError` | worker path allowed (remapped) |

Leftover fail-closed is covered in exclusive unit tests with `saas_auth: firebase` (`leftover.yml`).

## Residual

`goals/riso-v2-release-ready/residuals/CLI.md` — owner GOAL; flip those two tests to an unmapped leftover (do not reintroduce reject-before-remap).
