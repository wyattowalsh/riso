# Riso CLI

Agent-native command-line interface for scaffolding from the Riso Copier template.

## Install

From a repository checkout:

```bash
uv sync --group cli
uv run riso doctor --json
```

Installed wheels include the Copier template, so `pip install riso` or
`uv tool install riso` can resolve it without a checkout. Use `--template-path`
to select another trusted template explicitly. Sample variant discovery still
uses a repository checkout or an explicit `--samples-path`.

The **PyPI / `pyproject.toml` package** is `1.2.11`. Template
`copier.yml` `_metadata.version` is `2.0.0` (Unreleased hard major; no
`v2.0.0` git tag). `riso doctor` reports `checks.riso_version` from the
installed package, not the template metadata.

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

## Global flags

These flags may appear before or after the subcommand (`uv run riso update DEST --force-unsafe` is valid).

| Flag / env                                 | Purpose                                                                                                               |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `--json`                                   | Machine-readable envelope                                                                                             |
| `--quiet` / `-q`, `--verbose` / `-v`       | Log volume                                                                                                            |
| `--template-path` / `RISO_TEMPLATE_PATH`   | Template root                                                                                                         |
| `--samples-path` / `RISO_SAMPLES_PATH`     | Samples root                                                                                                          |
| `--timeout SECONDS`                        | Copier operation timeout (default 300)                                                                                |
| `--force-unsafe`                           | Explicitly authorize Copier's unsafe checks for extensions or task-bearing sources; Riso still disables Copier tasks. |
| `--skip-post-gen` / `RISO_SKIP_POST_GEN=1` | Skip Riso's managed bundled post-generation hook. Copier tasks remain disabled.                                       |

Example:

```bash
uv run riso --force-unsafe update ./my-app --json
uv run riso --skip-post-gen copy ./my-app --answers-file answers.yml --json
```

## Discovery

```bash
uv run riso doctor --json
uv run riso check-update ./my-app --json
uv run riso template path --json
uv run riso prompts --json
uv run riso prompts show project_name --json
uv run riso variants list --json
uv run riso variants show default --json
uv run riso catalog modules --json
uv run riso catalog dependencies --json
```

### `riso catalog dependencies`

Summarizes lock files and tooling pins for the checkout: `uv.lock`, root `pnpm-lock.yaml`, `web/pnpm-lock.yaml`, and `pyproject.toml` when present. Use this instead of parsing lock files by hand.

### Nested sample variants

`riso variants list` recursively discovers `copier-answers.yml` files, including
nested names such as `saas-starter/enterprise-ready`. It prunes rendered output,
metadata, dependencies, virtual environments, Git data, and Python caches from
the walk.

Maintainer automation uses `scripts.lib.paths.iter_sample_answer_files` with the
same pruning contract. See {doc}`../api/scripts` and the unit tests under
`tests/unit/lib/test_paths.py`.

## Validation

```bash
uv run riso validate --answers-file path.yml --json
uv run riso validate --data project_name=MyApp --json
uv run riso validate --answers-file path.yml --schema-only --json
```

`--answers-file` is a Copier answers YAML (`copier-answers.yml` / `.copier-answers.yml`). `--data KEY=VALUE` is a repeatable inline override.

Default `riso validate` remaps removed 1.x keys then runs **generation combination gates** (SaaS incompatibilities, empty language lists). Pass `--schema-only` to check Copier prompt schema and choice sets only and skip those combo gates. Copy, update, and recopy always run generation gates.

```bash
# Generation gates (default)
uv run riso validate --answers-file path.yml --json
# Prompt schema only
uv run riso validate --answers-file path.yml --schema-only --json
```

## Mutations

```bash
uv run riso copy ./my-app --answers-file samples/default/copier-answers.yml --json
uv run riso copy ./my-app --answers-file answers.yml --dry-run --json
uv run riso update ./my-app --json
uv run riso recopy ./my-app --json
uv run riso diff ./my-app --operation update --json
```

`riso migrate` takes **exactly one** target. Do not write `DEST|--answers-file` as a single token:

```bash
uv run riso migrate ./my-app --dry-run --json
uv run riso migrate --answers-file path.yml --dry-run --json
```

Write remaps by dropping `--dry-run`. See {doc}`../guides/v2-migration`.

### Overwrite and unsafe permission

Riso workers pass `skip_tasks=True` for copy, update, and recopy. Copier can still
require unsafe authorization for a task-bearing update source even when tasks
are disabled. Supply `--force-unsafe` explicitly after reviewing that source;
Riso never infers unsafe permission from a bundled template selection.

| Operation | `overwrite`    | `unsafe`              |
| --------- | -------------- | --------------------- |
| `copy`    | `--force` only | `--force-unsafe` only |
| `update`  | always `True`  | `--force-unsafe` only |
| `recopy`  | always `True`  | `--force-unsafe` only |

`riso export cli` includes Copier `--overwrite` on the emitted `copier copy`
string.

## Export

```bash
uv run riso export cli --answers-file answers.yml
uv run riso export yaml --answers-file answers.yml
uv run riso export yaml --data project_name=MyApp
# Top-level aliases (same behavior):
uv run riso export-cli --answers-file answers.yml
uv run riso export-yaml --answers-file answers.yml
```

| Flag                    | Owner  | Meaning                                                                                                                                                                                                      |
| ----------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--answers-file` / `-f` | Riso   | Path to a Copier **answers** YAML. Canonical input for validate / copy / export / migrate.                                                                                                                   |
| `--data KEY=VALUE`      | Riso   | Repeatable inline answer override.                                                                                                                                                                           |
| `--data-file`           | Copier | Copier's native extra-data file (`copier copy --data-file`). **Not** a Riso export flag today. Do not pass it to `riso export`. Generated Copier commands use this flag; Riso commands use `--answers-file`. |

`riso export` emits Copier/Riso command strings and YAML. It does not run Copier.

## Path overrides

- `--template-path` or `RISO_TEMPLATE_PATH`
- `--samples-path` or `RISO_SAMPLES_PATH`

Resolution uses the explicit path, the environment override, then the checkout
or packaged template. Riso-managed post-generation hooks run only for the bundled
template, in a child process bounded by the operation timeout. External templates
cannot select a Riso-managed hook. Riso disables Copier tasks; the unsafe flag
only authorizes Copier checks for extensions and task-bearing templates.

The wheel and source distribution contain the CLI, template payload, and required
hook helpers. Maintainer dependency trees, sample renders, and the web build are
excluded from the package inputs.

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

## Doctor

`uv run riso doctor --json` sets `ready` (and `checks.ready`) only when all of
the following hold:

- Template path resolves and exists, and `copier.yml` loads
- Copier is importable (PATH `copier` is optional)
- `uv` is on `PATH`
- `git` is on `PATH`
- Installed Copier package version meets template `_min_copier_version`
  (`9.1.0`)

`checks.git`, `checks.min_copier_version`, and `checks.copier.meets_min`
surface those gates. Unsafe permission is never inferred from the selected template.

When `ready` is false, `riso doctor` still prints the checks payload (including
`--json`) and exits `1`.

### `riso check-update`

Wraps `copier check-update --output-format json` in an existing destination:

```bash
uv run riso check-update ./my-app --json
```

`data.update_available` is informational; Riso exits `0` when Copier JSON
parses even if a newer template version exists.
