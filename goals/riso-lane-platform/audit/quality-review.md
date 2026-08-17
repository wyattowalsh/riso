# Quality payload review

## Command

```bash
uv run python scripts/ci/check_quality_parity.py
```

**Result:** exit 0 — `Quality parity checks passed.`

## Surfaces reviewed

| Path | Notes |
|------|--------|
| `template/files/quality/justfile.quality.jinja` | just runner quality targets |
| `template/files/quality/makefile.quality.jinja` | make runner quality targets |
| `template/files/quality/ruff.toml.jinja` | ruff config fragment |
| `template/files/quality/pylintrc.jinja` | pylint (strict) |
| `template/files/quality/coverage.cfg.jinja` | coverage |
| `template/files/quality/uv_tasks/quality.py.jinja` | uv task quality helper |

## Cross-lane note

`check_quality_parity.py` also reads `template/files/python/tasks/quality.py.jinja` (**PY** write root). Parity currently green; if that path drifts, file PY outbox — do not edit from PLATFORM.
