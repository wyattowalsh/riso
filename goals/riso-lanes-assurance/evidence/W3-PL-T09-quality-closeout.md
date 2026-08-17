# PL-T09 quality close-out

**Date:** 2026-07-29
**Command:** `just quality`
**Result:** green — lint ✓, ty ✓, **877 passed, 17 skipped, 0 failed, 0 errors**

## Root causes fixed

1. **Basename clash:** `tests/unit/hooks/test_quality_tool_check.py` vs `tests/unit/ci/test_quality_tool_check.py`
   - Renamed hooks file → `tests/unit/hooks/test_hooks_quality_tool_check.py`
2. **Package shadowing:** `tests/unit/scripts/` collided with repo `scripts/` package
   - Moved → `tests/unit/setup_scripts/`
3. **Timeout flake:** `test_copier_cmd_rejects_non_copier_executable` under concurrent matrix
   - Re-ran quality with matrix idle; passed

## Evidence

- Pass log: `W3-PL-T09-just-quality-rerun.log`
- Prior fail log: `W3-PL-T09-just-quality.log` (839 pass / 1 fail / 3 errors)
