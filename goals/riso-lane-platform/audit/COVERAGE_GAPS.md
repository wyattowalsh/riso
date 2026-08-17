# CI coverage gaps (PLATFORM)

## First-run pack (required progress)

| Module | Status |
|--------|--------|
| `run_quality_suite.py` | **done** — `tests/unit/ci/test_run_quality_suite.py` |
| `generate_matrix_data.py` | **done** — `tests/unit/ci/test_generate_matrix_data.py` |
| `verify_version_sync.py` | **done** — `tests/unit/ci/test_verify_version_sync.py` |

## Deferred (intentional for this run)

| Module | Reason |
|--------|--------|
| `validate_jinja_templates.py` | lower risk / pre-commit path; defer |
| `validate_saas_combinations.py` | often fails for SAAS payload; outbox SAAS if needed |
| `run_baseline_quickstart.py` | timing evidence; defer |
| `bump_template_npm_deps.py` | npm pin audits; defer |
| `sync_template_shadcn_components.py` | SAAS probe; defer / handoff SAAS |

## Existing coverage (baseline)

See `tests/unit/ci/test_*.py` for modules already covered.
