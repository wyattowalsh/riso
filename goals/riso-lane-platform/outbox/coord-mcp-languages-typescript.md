# PLATFORM outbox → COORD: mcp-languages-typescript

## Failing command

```bash
uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json
```

## Exit code / summary

- exit 2
- `mcp_languages: invalid choice 'typescript'`

## Redacted log excerpt

```text
{"ok": false, "command": "riso validate", "errors": ["mcp_languages: invalid choice 'typescript'"]}
```

## Suspected paths

- `template/copier.yml` — `mcp_languages.choices` is currently `python`, `rust`, `go` only
- Help text and path exclusion jinja still mention `typescript` in `mcp_languages` (e.g. node/mcp paths)
- `samples/mcp-typescript/copier-answers.yml` intentionally uses `mcp_languages: [typescript]`

## Why not PLATFORM-owned

PLATFORM must not invent Copier choices or edit `template/copier.yml`. Restoring `typescript` (or renaming the sample contract) is a COORD contract decision.

## Requested fix

1. Add `typescript` back to `mcp_languages` multiselect choices (aligned with help text + path exclusions), **or**
2. Publish a COORD outbox rename of the sample language key/choice and the intended answers migration.

## Blocked PLATFORM work (if any)

- `samples/mcp-typescript` remains non-validating until COORD resolves.
- Full matrix may fail or skip smoke for this variant depending on render path.

## Repro steps

1. `uv run riso validate --answers-file samples/mcp-typescript/copier-answers.yml --json`
2. Observe invalid choice error.
