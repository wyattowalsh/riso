# W4 A-T03 — Path-lock audit

**When:** 2026-07-29\
**Command:** `git rev-parse --show-toplevel` → `/Users/ww/dev/projects/riso`\
**Command:** `git status --short` → **93** dirty leaf paths\
**Branch:** `main`

## Classification rules

Same as `inventory-dirty.md` lane roots (COORD/PY/NODE/SAAS/SYS/DESKTOP/CLI/PLATFORM/ASSURANCE/OUT-OF-SCOPE).

## Results

| Metric                                    | Count |
| ----------------------------------------- | ----: |
| Dirty paths                               |    93 |
| Mapped to a lane                          |    91 |
| OUT-OF-SCOPE (harness)                    |     2 |
| Unowned                                   | **0** |
| Foreign-tree violations                   | **0** |
| Forbidden render hand-edits in dirty list | **0** |

### By lane (current dirty)

| Lane         | Paths |
| ------------ | ----: |
| ASSURANCE    |    50 |
| COORD        |    16 |
| DESKTOP      |     9 |
| NODE         |     8 |
| PLATFORM     |     4 |
| OUT-OF-SCOPE |     2 |
| CLI          |     1 |
| PY           |     1 |
| SAAS         |     1 |
| SYS          |     1 |

### OUT-OF-SCOPE (not violations)

- `.claude/skills/mcp-installer/`
- `.grok/`

### PLATFORM dirty (expected)

- `tests/unit/ci/test_generate_matrix_data.py`
- `tests/unit/ci/test_run_quality_suite.py`
- `tests/unit/ci/test_verify_version_sync.py`
- (plus goals package paths under PLATFORM lane packages if present)

### path_lock_violations

```text
(none)
```

## Notes

- Product commits for W1–W3 largely cleaned tracked diffs; remaining dirty is mostly untracked `goals/**` packages + local harness.
- Render directories may be rewritten by live `render_matrix.py` (pid observed during W4) via official scripts — not hand-edits.
