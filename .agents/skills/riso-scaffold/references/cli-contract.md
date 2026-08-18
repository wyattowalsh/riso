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
- `--force-unsafe` — Copier `unsafe=True`; on **update**, run Copier tasks even when the worker would pass `skip_tasks=True`
- `--skip-post-gen` / `RISO_SKIP_POST_GEN=1` — skip Riso post-generation hooks after copy/update/recopy

`riso validate` runs generation combo gates by default. Pass `--schema-only` for Copier prompt-schema checks only.
