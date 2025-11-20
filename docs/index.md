# Riso Developer Documentation

Welcome to the Riso maintainer hub. This site captures the authoritative
source of truth for the template, automation, and module catalog. It uses the
[Shibuya theme](https://github.com/asual/sphinx-shibuya) with a rich Sphinx
stack for authored guides, API reference, and repo metadata.

:::{admonition} How to build locally
:class: tip

```bash
uv sync --group docs
uv run sphinx-build docs docs/_build
```
:::

:::{toctree}
:maxdepth: 2
:hidden:

Guides <guides/index>
Tools <tools/index>
API Reference <api/index>
Changelog <changelog>
:::

## Maintainer shortcuts

:::{cards}
:class-columns: three
:class-card: sd-shadow-sm sd-rounded-1 sd-border-secondary sd-bg-light

- :octicons-rocket-24: **Quality gate** — run `make quality` inside
  `samples/default/render` for the canonical lane (ruff, mypy, pylint, pytest
  with coverage). See {doc}`guides/testing-strategy` for the coverage policy
  (90%+ unit, explicit integration/e2e evidence).
- :material-book-open-variant: **Authoring** — new guides belong in
  `docs/guides/`; mirror changes into `template/files/python/docs/` so rendered
  projects inherit the same navigation.
- :octicons-cpu-24: **Automation** — use `scripts/render-samples.sh` to refresh
  renders and `scripts/ci/run_quality_suite.py` to align Taskipy/Makefile
  quality lanes before merging.
:::

## What's inside the repo

- **Template renderer:** `scripts/render-samples.sh` orchestrates copier runs
  and keeps smoke results in `samples/*/smoke-results.json` aligned with
  `samples/metadata/module_success.json`.
- **Quality tooling:** The Python quality lane lives in
  `template/files/shared/quality/` (Makefile + uv tasks) with orchestration
  scripts in `scripts/ci/run_quality_suite.py` and
  `scripts/ci/check_quality_parity.py`.
- **Context sync:** Canonical GitHub context files are stored under
  `.github/context/` and validated by `scripts/ci/verify_context_sync.py`
  against the template payload.
- **Docs payload:** The Sphinx site here is mirrored to the template under
  `template/files/python/docs/` so new projects inherit the same authoring
  experience.

## Quality and coverage at a glance

- **Coverage floor:** Aim for **≥90% unit test coverage** across rendered
  Python packages; integration and e2e suites must exercise the critical paths
  (auth, CLI, API, background tasks) even if excluded from the unit threshold.
  Enforce `--cov-fail-under=90` locally and in CI to prevent regressions.
- **Artifacts:** CI uploads JUnit XML, Cobertura coverage, and log bundles for
  every job; use them to justify exceptions or to spot regressions. Combine
  coverage from unit, integration, and e2e runs with `coverage combine` before
  publishing `coverage.xml`.
- **Matrix:** Python 3.11–3.13 are required; keep deps and lockfiles updated so
  coverage is stable across versions.

The navigation above mirrors the global template roadmap and the Sphinx
configuration used by the `sphinx-shibuya` docs_site option. When you adjust
the configuration here, keep the template copy in sync so new renders inherit
the latest improvements.
