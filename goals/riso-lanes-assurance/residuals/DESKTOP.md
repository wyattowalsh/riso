# Residual — DESKTOP (foreign failure observed during W2)

## Not a DESKTOP product residual

DESKTOP W2 payload + electron unit tests are green. The foreign `quality_tool_check` ImportError observed while scanning modified tests is **historical / closed**. PLATFORM restored `_subprocess_env` and closed maintainer `just quality` (quality_green). DESKTOP did not cross-lane edit those paths.

**Active bar residual (not DESKTOP-owned):** PLATFORM R1 full `render_matrix` — [`PLATFORM.md`](./PLATFORM.md). See [`ASSURANCE.md`](../ASSURANCE.md). PLATFORM R2 `just quality` is closed green.

### Foreign: `tests/unit/ci/test_quality_tool_check.py` — **CLOSED (W3)**

| Field               | Value                                                                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **status**          | historical / closed                                                                                                                                                                                         |
| **owner**           | PLATFORM                                                                                                                                                                                                    |
| **task**            | PL-T07 helper + PL-T09 `just quality`                                                                                                                                                                       |
| **command**         | `uv run pytest tests/unit/ci/test_quality_tool_check.py -q --tb=line -n0`                                                                                                                                   |
| **applied**         | `scripts/hooks/quality_tool_check.py` defines `_subprocess_env` and `_run()` uses it. `test_subprocess_env_trusts_cwd_for_mise` passed.                                                                     |
| **evidence**        | [`ASSURANCE.md`](../ASSURANCE.md) fact #11 quality_green · `evidence/W3-PL-T07-quality-tool-fix.txt` · `evidence/W3-PL-T09-just-quality-rerun.log` · [`PLATFORM.md`](./PLATFORM.md) R2 closed |

### Historical W2 log (superseded)

```
FAILED tests/unit/ci/test_quality_tool_check.py::test_subprocess_env_trusts_cwd_for_mise
ImportError: cannot import name '_subprocess_env' from 'hooks.quality_tool_check'
```

W3 evidence shows the same test **PASSED** after the helper landed.

### DESKTOP green evidence

- `uv run pytest tests/unit/test_electron_templates.py -q` → 42 passed
- Evidence: `goals/riso-lanes-assurance/evidence/W2-DESKTOP-pytest-electron.txt`
