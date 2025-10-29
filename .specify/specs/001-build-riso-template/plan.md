# Implementation Plan: Riso Template Foundation

**Branch**: `001-build-riso-template` | **Date**: 2025-10-29 | **Spec**: [specs/001-build-riso-template/spec.md](specs/001-build-riso-template/spec.md)  
**Input**: Feature specification from `/specs/001-build-riso-template/spec.md`

## Summary

Deliver a copier-driven GitHub template that defaults to a lightweight Python 3.11 project (uv, pytest, jupyter, ruff, mypy, pylint) and offers opt-in modules for Typer CLI, FastAPI/Fastify APIs (with dedicated runbooks), fastmcp integrations, shared logic, and dual documentation stacks (Sphinx/Shibuya, Fumadocs/Next.js). The template must regenerate deterministic samples, wire governance automation (timing, success-rate, and documentation SLA telemetry), and keep module combinations composable without bloating the baseline render.

## Technical Context

**Language/Version**: Python 3.11 via uv; Node.js 20 LTS with TypeScript 5.x  
**Primary Dependencies**: uv, pytest, jupyter, nbclient, ruff, mypy, pylint, tenacity, pydantic, pydantic-settings, loguru, typer, fastapi, FastMCP>=2.0.0, sphinx with Shibuya theme, pnpm, TypeScript, Vitest, Playwright, Fumadocs/Next.js  
**Storage**: N/A (template emits storage-ready interfaces only)  
**Testing**: uv-run pytest + lint suite, notebook smoke checks via nbclient, Vitest + Playwright for TypeScript modules, automated render smoke scripts per sample  
**Target Platform**: GitHub-hosted macOS/Linux/Windows runners and local developer environments on macOS, Linux, Windows  
**Project Type**: Copier template producing configurable single-package or monorepo repositories spanning Python and Node workspaces  
**Performance Goals**: Baseline render (defaults) including quickstart tests completes <10 minutes; optional permutations matrix <15 minutes; deterministic renders across operating systems  
**Constraints**: Hooks avoid network calls, optional modules gated by prompts, governance automation must enforce constitutional gates, samples regenerated on every change  
**Scale/Scope**: Up to five concurrent optional modules, four curated sample variants, downstream teams spanning single-package and monorepo layouts

## Constitution Check

- ✅ Template Sovereignty: Source of truth lives in `template/copier.yml`, `template/prompts/`, `template/hooks/`, `template/files/**`, and mirrored `.github/context/` assets; every change requires regenerating `samples/**` and attaching `copier diff` evidence.
- ✅ Deterministic Generation: Render defaults plus `samples/cli-docs`, `samples/api-monorepo`, and `samples/full-stack` on macOS/Linux/Windows via CI while logging baseline timing metrics via `scripts/ci/run_baseline_quickstart.py`, module success rates via `scripts/ci/record_module_success.py`, and documentation SLA status via `scripts/ci/track_doc_publish.py`; hooks remain idempotent and side-effect free.
- ✅ Minimal Baseline, Optional Depth: Baseline keeps only uv-managed Python quickstart with network-free post-generation guidance; CLI/API/MCP/docs/shared logic modules stay opt-in with documented defaults and compatibility matrix.
- ✅ Documented Scaffolds: Update `docs/quickstart.md.jinja`, `docs/modules/prompt-reference.md.jinja`, `docs/modules/api-python.md.jinja`, `docs/modules/api-node.md.jinja`, `docs/upgrade-guide.md.jinja`, and `docs/modules/sample-matrix.md.jinja`, including context-sync instructions alongside template changes.
- ✅ Automation-Governed Compliance: `.github/workflows/template-ci.yml` runs lint/tests, render matrix, docs build, baseline timing checks, ≥98% module success-rate enforcement, documentation publish SLA verification, and governance compliance scripts posting to automation API checkpoints before merge.

## Project Structure

### Documentation (this feature)

```text
specs/001-build-riso-template/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
template/
├── copier.yml
├── prompts/
├── hooks/
├── files/
│   ├── python/
│   │   ├── pyproject.toml.jinja
│   │   ├── src/{{ package_name }}/
│   │   ├── tests/
│   │   └── docs/shibuya/
│   ├── node/
│   │   ├── package.json.jinja
│   │   ├── apps/api-node/
│   │   ├── docs/fumadocs/
│   │   └── shared-config/
│   └── shared/
│       ├── .github/context/
│       ├── .github/workflows/
│       ├── docs/prompt-reference.md.jinja
│       ├── docs/api-python.md.jinja
│       ├── docs/api-node.md.jinja
│       └── README.md.jinja
scripts/
├── render-samples.sh
├── ci/
│   ├── render_matrix.py
│   ├── run_baseline_quickstart.py
│   ├── verify_context_sync.py
│   ├── record_module_success.py
│   └── track_doc_publish.py
└── compliance/
    └── checkpoints.py
samples/
├── default/
├── cli-docs/
├── api-monorepo/
└── full-stack/
docs/
├── quickstart.md
├── upgrade-guide.md
└── modules/
    ├── prompt-reference.md
    ├── sample-matrix.md
    └── governance.md
```

**Structure Decision**: Keep all copier assets consolidated under `template/`, orchestrate renders and governance in `scripts/`, and track deterministic outputs in `samples/`; supporting documentation for the template lives under `docs/`.

## Complexity Tracking

No constitution gate violations anticipated; prompt-driven optional modules and sample matrix keep scope manageable without duplicating template roots.
