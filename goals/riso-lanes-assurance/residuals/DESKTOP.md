# Residual — DESKTOP (foreign failure observed during W2)

## Not a DESKTOP product residual

DESKTOP W2 payload + electron unit tests are green. The following failure was observed while scanning modified tests and is **owned by PLATFORM** (exclusive roots: `scripts/hooks/**`, `tests/unit/ci/**`). DESKTOP does not cross-lane edit those paths.

| Field               | Value                                                                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **owner**           | PLATFORM                                                                                                                                                                                                    |
| **task**            | Foreign: `tests/unit/ci/test_quality_tool_check.py`                                                                                                                                                         |
| **command**         | `uv run pytest tests/unit/ci/test_quality_tool_check.py -q --tb=line -n0`                                                                                                                                   |
| **status**          | failing (ImportError)                                                                                                                                                                                       |
| **blocking reason** | Test imports `_subprocess_env` from `hooks.quality_tool_check`, but `scripts/hooks/quality_tool_check.py` has no such symbol. Incomplete PLATFORM/CLI affinity work on mise-trusted env for uv tool probes. |

### Redacted log

```
FAILED tests/unit/ci/test_quality_tool_check.py::test_subprocess_env_trusts_cwd_for_mise
ImportError: cannot import name '_subprocess_env' from 'hooks.quality_tool_check'
```

### Suggested PLATFORM fix

Either implement `_subprocess_env()` in `scripts/hooks/quality_tool_check.py` (set `MISE_TRUSTED_CONFIG_PATHS` to include cwd + parent) and use it from `_run()`, or delete/adjust the untracked test until the helper lands.

### DESKTOP green evidence

- `uv run pytest tests/unit/test_electron_templates.py -q` → 42 passed
- Evidence: `goals/riso-lanes-assurance/evidence/W2-DESKTOP-pytest-electron.txt`
