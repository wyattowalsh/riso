# Implementation Plan: Code Generation and Scaffolding Tools

**Branch**: `015-codegen-scaffolding-tools` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-codegen-scaffolding-tools/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a CLI-based code generation and scaffolding tool that enables developers to quickly create new projects and add feature modules using template-based generation. The tool will support local cached templates with remote sync, three-way merge for updates, upfront variable validation, and quality checks with warnings. Primary use cases include project bootstrapping, module addition, custom templates, template updates, and API spec-based generation.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Jinja2 (template engine), Typer (CLI framework), Loguru (logging), Rich (terminal UI), GitPython (template fetching), diff-match-patch (three-way merge)  
**Storage**: Local filesystem cache (~/.scaffold/templates/), file-based metadata (.scaffold-metadata.json)  
**Testing**: pytest with fixtures for filesystem operations, integration tests with real templates  
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)  
**Project Type**: Single Python CLI package with plugin architecture  
**Performance Goals**: <30 seconds for project generation, <5 seconds for template list operations, <100ms CLI startup time  
**Constraints**: 100MB max template size, support Python 3.11-3.13, no external services required for core functionality  
**Scale/Scope**: Support 100+ templates in registry, handle projects up to 1000 files, 10K+ lines generated code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Module Sovereignty**: This is a new CLI tool module for the Riso template, controlled by `cli_module=enabled` in copier.yml. It's optional and self-contained.

✅ **Deterministic Generation**: Template rendering will be deterministic - same inputs produce same outputs. The scaffolding tool itself generates projects deterministically.

✅ **Minimal Baseline**: This feature is optional via module flag. When disabled, baseline template remains unchanged (<50 files, <10 dependencies).

✅ **Quality Integration**: Generated code will integrate with ruff, mypy, pylint, pytest. The scaffolding tool itself will follow quality standards (FR-021).

✅ **Test-First Development**: Implementation will follow TDD - write tests before implementation, achieve 80%+ coverage.

✅ **Documentation Standards**: Will include docs/modules/codegen-scaffolding.md.jinja with examples, quickstart guide, and API reference.

✅ **Technology Consistency**: Uses Python 3.11+ with uv (consistent with Riso baseline), approved dependencies (Jinja2, Typer, Rich).

**GATE STATUS**: ✅ PASS - All constitution principles satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/015-codegen-scaffolding-tools/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── cli-api.md       # CLI command interface contract
│   ├── template-schema.json  # Template metadata schema
│   └── config-schema.json    # .scaffold-metadata.json schema
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
template/files/python/src/{{package_name}}/
├── codegen/
│   ├── __init__.py
│   ├── cli.py           # Typer CLI commands (new, add, update, list, etc.)
│   ├── engine.py        # Core generation engine
│   ├── templates/
│   │   ├── loader.py    # Template discovery and loading
│   │   ├── cache.py     # Local cache management (~/.scaffold/templates/)
│   │   ├── registry.py  # Template registry operations
│   │   └── validator.py # Template syntax and size validation
│   ├── generation/
│   │   ├── generator.py # File generation with Jinja2
│   │   ├── variables.py # Variable collection and validation
│   │   ├── hooks.py     # Pre/post generation hook execution
│   │   └── atomic.py    # Atomic file operations
│   ├── updates/
│   │   ├── differ.py    # Template version diffing
│   │   ├── merger.py    # Three-way merge with conflict markers
│   │   └── conflict.py  # Conflict detection and validation
│   ├── quality/
│   │   ├── checker.py   # Quality validation (syntax, linting)
│   │   └── reporter.py  # Warning/error reporting
│   └── models.py        # Data classes (Template, Project, Module, etc.)

template/files/python/tests/codegen/
├── test_cli.py
├── test_engine.py
├── test_templates/
│   ├── test_loader.py
│   ├── test_cache.py
│   └── test_validator.py
├── test_generation/
│   ├── test_generator.py
│   ├── test_variables.py
│   └── test_atomic.py
├── test_updates/
│   ├── test_merger.py
│   └── test_conflict.py
├── fixtures/
│   ├── sample_templates/  # Test templates
│   └── mock_projects/     # Test project structures
└── integration/
    ├── test_new_project.py
    ├── test_add_module.py
    └── test_update_project.py

template/files/shared/docs/modules/
└── codegen-scaffolding.md.jinja  # User-facing documentation
```

**Structure Decision**: Single Python package structure chosen because this is a CLI tool that will be part of the Riso template's Python package. The modular organization (templates/, generation/, updates/, quality/) allows for clean separation of concerns and independent testing of each subsystem.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. This section intentionally left empty.
