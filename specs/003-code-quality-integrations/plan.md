# Implementation Plan: Code Quality Integration Suite

**Branch**: `003-code-quality-integrations` | **Date**: 2025-10-30 | **Spec**: `.specify/specs/003-code-quality-integrations/spec.md` (symlinked at `specs/003-code-quality-integrations/spec.md`)
**Input**: Feature specification from `/.specify/specs/003-code-quality-integrations/spec.md`

## Summary

Unify Riso’s quality automation with a single `make quality` / `uv run task quality` entry point, auto-heal missing Ruff/Mypy/Pylint/ESLint tooling once via `uv` and `corepack pnpm install`, parallelize CI jobs per tool/profile, and retain lint/type evidence for 90 days across baseline and full-stack renders.

## Technical Context

**Language/Version**: Python 3.11 (uv-managed), optional Node.js 20 LTS  
**Primary Dependencies**: ruff, mypy, pylint, pytest, coverage, optional eslint + typescript  
**Storage**: N/A (evidence stored as CI artifacts)  
**Testing**: pytest suite, ruff lint, mypy type checks, pylint lint, optional eslint/type-check tasks  
**Target Platform**: Local macOS (Apple Silicon) renders and GitHub Actions macOS/ubuntu runners  
**Project Type**: Copier template + automation scripts (monorepo)  
**Performance Goals**: `<4m` local quality run, `<6m` CI runtime in ≥95% executions  
**Constraints**: One auto-install attempt per missing tool, CI jobs split per tool/profile with shared caches, quality artifacts retained 90 days, deterministic smoke metrics required  
**Scale/Scope**: Applies to baseline (`samples/default`) and full-stack (`samples/full-stack`) renders plus matrix regeneration via `scripts/render_matrix.py`

## Constitution Check

*GATE (Pre-Phase 0)*: Constitution file remains a placeholder with unnamed principles. Record follow-up for maintainers to codify principles; proceed assuming existing governance (automation, determinism, documentation, optional depth) — PASS with note.

## Project Structure

### Documentation (this feature)

```text
.specify/specs/003-code-quality-integrations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── quality-suite.commands.md
│   └── quality-evidence.schema.json
└── tasks.md (created by /speckit.tasks)
```

> The top-level `specs/` symlink points here for tools that still expect the legacy path.

### Source Code (repository root)

```text
template/
├── files/
│   ├── shared/
│   │   ├── quality/
│   │   │   ├── ruff.toml.jinja
│   │   │   ├── mypy.ini.jinja
│   │   │   ├── pylintrc.jinja
│   │   │   ├── coverage.cfg.jinja
│   │   │   ├── makefile.quality.jinja
│   │   │   └── uv_tasks/quality.py.jinja
│   │   └── .github/workflows/quality-matrix.yml.jinja
│   └── python/
│       └── shared/hooks/quality_tool_check.py.jinja
scripts/
├── render-samples.sh
├── ci/
│   ├── render_matrix.py
│   └── run_quality_suite.py
└── hooks/
    └── quality_tool_check.py
samples/
├── default/
│   ├── baseline_quickstart_metrics.json
│   └── smoke-results.json
└── full-stack/
    ├── baseline_quickstart_metrics.json
    └── smoke-results.json
```

**Structure Decision**: Extend shared template scaffolding with a dedicated `quality/` bundle, update CI workflows under `.github/workflows` to run parallelized jobs, and ensure scripts + samples capture new quality evidence.

## Complexity Tracking

No constitution violations identified.

## Constitution Check (Post-Phase 1)

Re-affirm governance alignment after design: automated installs remain single-attempt with explicit failure paths, CI jobs remain deterministic and evidence is retained 90 days. Constitution still placeholder — PASS with same follow-up note.
