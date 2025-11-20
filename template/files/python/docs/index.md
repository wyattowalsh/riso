# {{ project_name }} Developer Documentation

Welcome to the Shibuya-powered Sphinx docs for **{{ project_name }}**. This site
is bundled with the `docs_site=sphinx-shibuya` option and ships with the same
configuration used by the Riso maintainers.

:::{admonition} Local build
:class: tip

```bash
uv sync --group docs
uv run sphinx-build docs docs/_build
```
:::

## Repo map

- **Automation:** `scripts/render-samples.sh` (from the template) shows how the
  project is rendered and exercised; use it as a baseline for your own smoke
  scripts.
- **Quality:** The bundled Makefile/Taskipy quality targets live in
  `quality/` (Makefile) and `.taskipy.toml` so `make quality` and
  `uv run task quality` stay in lockstep.
- **Docs:** The Sphinx site lives at `docs/` with static assets in `_static/`
  and optional tool metadata under `docs/tools/`.

## Quick navigation

:::{cards}
:class-columns: three
:class-card: sd-shadow-sm sd-rounded-1 sd-border-secondary sd-bg-light

- :octicons-rocket-24: **Quality gate** — run `make quality` for linting, typing,
  pytest, and coverage. See {doc}`guides/testing-strategy` for the ≥90% coverage
  policy and integration/e2e expectations.
- :material-book-open-variant: **Authoring** — add new guides under `docs/guides/`
  and update the toctree here to keep navigation consistent.
- :octicons-cpu-24: **Automation** — leverage the included GitHub Actions
  workflows for matrix testing and artifact uploads (coverage.xml, JUnit XML,
  quality logs).
:::

:::{toctree}
:maxdepth: 2
:hidden:

Guides <guides/index>
Tools <tools/index>
API Reference <api/index>
Changelog <changelog>
:::

## Quality and coverage at a glance

- **Coverage floor:** Aim for **≥90% unit test coverage** across your Python
  packages; integration and e2e suites must exercise critical paths (auth, CLI,
  API, background tasks) even if excluded from the unit threshold. Enforce
  `--cov-fail-under=90` locally and in CI to prevent regressions.
- **Artifacts:** CI uploads JUnit XML, Cobertura coverage, and log bundles for
  every job; use them to justify exceptions or to spot regressions. Combine
  coverage from unit, integration, and e2e runs with `coverage combine` before
  publishing `coverage.xml`.
- **Matrix:** Python 3.11–3.13 are required; keep deps and lockfiles updated so
  coverage is stable across versions.
