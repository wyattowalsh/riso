# CLI Contract

## JSON envelope

```json
{
  "ok": true,
  "command": "riso validate",
  "data": {},
  "errors": [],
  "warnings": []
}
```

## Exit codes

- `0` success
- `1` operational failure
- `2` usage/validation error
- `130` SIGINT

## Global flags

- `--json` — machine-readable output (works after subcommand)
- `--template-path` / `RISO_TEMPLATE_PATH`
- `--samples-path` / `RISO_SAMPLES_PATH`
- `--timeout SECONDS` — Copier operation timeout
- `--quiet` / `--verbose`
