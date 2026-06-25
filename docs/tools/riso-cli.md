# Riso CLI

Agent-native command-line interface for scaffolding from the Riso Copier template.

## Install

From a repository checkout:

```bash
uv sync
uv run riso doctor --json
```

From PyPI (`pip install riso` or `uv tool install riso`), pass `--template-path` when not in a checkout.

## JSON envelope

All commands support `--json` for stable machine-readable output:

```json
{
  "ok": true,
  "command": "riso validate",
  "data": {},
  "errors": [],
  "warnings": []
}
```

On failure: non-zero exit, `"ok": false`, populated `errors`, no stack traces in `--json` mode.

## Exit codes

| Code | Meaning                |
| ---- | ---------------------- |
| 0    | Success                |
| 1    | Operational failure    |
| 2    | Usage/validation error |
| 130  | Interrupted (SIGINT)   |

## Discovery

```bash
uv run riso doctor --json
uv run riso template path --json
uv run riso prompts --json
uv run riso prompts show project_name --json
uv run riso variants list --json
uv run riso variants show default --json
uv run riso catalog modules --json
```

## Validation

```bash
uv run riso validate --answers-file path.yml --json
uv run riso validate --data project_name=MyApp --json
```

## Mutations

```bash
uv run riso copy ./my-app --answers-file samples/default/copier-answers.yml --json
uv run riso copy ./my-app --answers-file answers.yml --dry-run --json
uv run riso update ./my-app --json
uv run riso recopy ./my-app --json
uv run riso diff ./my-app --operation update --json
```

## Export

```bash
uv run riso export cli --answers-file answers.yml
uv run riso export yaml --data project_name=MyApp
# Top-level aliases (same behavior):
uv run riso export-cli --answers-file answers.yml
uv run riso export-yaml --data project_name=MyApp
```

## Path overrides

- `--template-path` or `RISO_TEMPLATE_PATH`
- `--samples-path` or `RISO_SAMPLES_PATH`

Without a checkout, pass `--template-path` explicitly.
