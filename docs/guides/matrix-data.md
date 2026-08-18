# Matrix Data Snapshot

Riso publishes a consolidated matrix of template prompts, defaults, and sample
variants for the web configurator. Generation writes two different paths; only
one is committed.

## What is gitignored vs committed

| Path | Git | Role |
| ---- | --- | ---- |
| `samples/metadata/` (including `matrix-data.json` and `render_matrix.json`) | **Gitignored** (`samples/metadata/` in `.gitignore`) | Local / CI scratch. Do not commit. Do not treat as the published consumer. |
| `web/src/data/matrix-data.json` | **Committed** | The configurator consumer. This is the snapshot the web app loads. |

Avoid hand-editing either JSON file. Regenerate, then commit only
`web/src/data/matrix-data.json` when the wizard must pick up prompt or sample
changes.

## Sources

- `template/copier.yml` for prompt definitions and defaults
- `samples/metadata/render_matrix.json` when a local render matrix exists
  (gitignored; optional input)
- Nested `samples/**/copier-answers.yml` via
  `scripts.lib.paths.iter_sample_answer_files` when the render matrix is missing
  (includes `samples/saas-starter/*/copier-answers.yml`)

## Regenerate locally

```bash
uv run python scripts/ci/render_matrix.py
uv run python scripts/ci/generate_matrix_data.py
```

`generate_matrix_data.py` writes `samples/metadata/matrix-data.json` (scratch)
and `web/src/data/matrix-data.json` (committed consumer).

## Where it shows up

- The web configurator loads `web/src/data/matrix-data.json` for option lists
  and defaults.
- Maintainer docs link here when describing prompt defaults.
- The `Matrix Data` workflow (`.github/workflows/matrix-data.yml`) can open a
  refresh PR for the committed web snapshot.

## Updating options

1. Update `template/copier.yml`.
1. Regenerate the matrix snapshot (or run the workflow).
1. Commit `web/src/data/matrix-data.json` if the wizard should change.
1. Leave `samples/metadata/` untracked.
