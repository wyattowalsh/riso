# Matrix Data Snapshot

Riso publishes a consolidated matrix of template prompts, defaults, and sample
variants for the web configurator. Generation writes two different paths; only
one is committed.

## What is gitignored vs committed

| Path                                                                        | Git                                                  | Role                                                                       |
| --------------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------- |
| `samples/metadata/` (including `matrix-data.json` and `render_matrix.json`) | **Gitignored** (`samples/metadata/` in `.gitignore`) | Local / CI scratch. Do not commit. Do not treat as the published consumer. |
| `web/src/data/matrix-data.json`                                             | **Committed**                                        | The configurator consumer. This is the snapshot the web app loads.         |

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

## Quality consolidation and render evidence

`render_matrix.py --skip-render` reuses an existing `render_matrix.json`. It fails
when that input is missing, malformed, empty, or contains failed variants. Each
record must have the complete render-result fields, a unique nonblank variant
name, and a recognized status with a matching integer return code. Invalid input
fails before either evidence output changes; no render fallback is started.

CI jobs that have only quality profile artifacts use the separate mode:

```bash
uv run python scripts/ci/render_matrix.py --quality-only \
  --quality-artifacts artifacts/quality-standard/quality-results.json \
  artifacts/quality-strict/quality-results.json
```

This writes `samples/metadata/quality_summary.json`, leaving render evidence
untouched. Each input must contain a completed `standard` or `strict` profile
with valid timing data; missing artifacts fail the job. The quality summary is
not a render result and is never substituted for the full release matrix.

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
