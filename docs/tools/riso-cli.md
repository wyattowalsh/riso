# Riso CLI

Agent-native command-line interface for scaffolding from the Riso Copier template.

## Install

From a repository checkout:

```bash
uv sync
uv run riso doctor --json
```

Installed wheels include the Copier template, so `pip install riso` or
`uv tool install riso` can resolve it without a checkout. Use `--template-path`
to select another trusted template explicitly. Sample variant discovery still
uses a repository checkout or an explicit `--samples-path`.

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
uv run riso migrate DEST|--answers-file PATH [--dry-run] [--json]
```

`riso migrate` applies the eight 1.x remaps then fail-closes leftovers. See
{doc}`../guides/v2-migration`.

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

Resolution uses the explicit path, the environment override, then the checkout
or packaged template. Riso-managed post-generation hooks run only for the bundled
template, in a child process bounded by the operation timeout. External templates
cannot select a Riso-managed hook; their Copier tasks require the explicit unsafe
opt-in.

Update and recopy validate canonical answers before generation and persist Riso's
answer remaps only after success. This preserves existing answers when validation
or worker startup fails; it does not roll back arbitrary files that Copier itself
has already modified during a failing operation. Dry-run previews do not write
destination answers.

Update and recopy follow `_src_path` in the destination's saved Copier answers.
An explicit `--template-path` or `RISO_TEMPLATE_PATH` must match that source;
passing `_src_path` as ordinary answer data cannot switch it. A conflicting source
selection is rejected before generation. Copier's versioned update still requires
a Git-backed source, and any required unsafe opt-in remains explicit.
