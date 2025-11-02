# Implementation Plan: Robust Typer CLI Scaffold

**Branch**: `009-typer-cli-scaffold` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-typer-cli-scaffold/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the Riso template's CLI module to provide a robust, production-ready command-line application scaffold. The current implementation provides only a single `quickstart` command. This feature will expand it into a full CLI framework with multi-command structure, rich interactive formatting (colors, tables, progress bars), configuration management (TOML files + env vars), plugin architecture with lazy loading, shell completion, and comprehensive testing utilities. The scaffold will generate core commands (quickstart, config, version, init) plus patterns for adding custom commands in under 5 minutes.

## Technical Context

**Language/Version**: Python 3.11+ (managed via uv, consistent with template baseline)  
**Primary Dependencies**: Typer ≥0.20.0, Loguru (logging), Rich (formatting), tomli/tomllib (TOML parsing)  
**Storage**: TOML configuration files (config.toml or .app-name.toml in project directory)  
**Testing**: pytest with typer.testing.CliRunner, coverage ≥90% target  
**Target Platform**: Cross-platform (macOS, Linux, Windows) via Python stdlib + uv  
**Project Type**: Template enhancement (single-package Python, modifies existing cli_module scaffold)  
**Performance Goals**: CLI startup <500ms, command execution <100ms overhead, plugin discovery <50ms per plugin  
**Constraints**: Must integrate with existing quality tools (ruff, mypy, pylint), pass all checks with 10/10 pylint score  
**Scale/Scope**: Support 20+ commands per CLI, 10+ plugins, configuration with 50+ keys

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Template Sovereignty

✅ **Pass** - All changes confined to `template/files/python/src/{{ package_name }}/cli/` templates and related test/doc files. Samples will be regenerated via `./scripts/render-samples.sh`. No manual edits to rendered projects required.

**Evidence Required**:

- Template files modified in `template/files/python/src/{{ package_name }}/cli/`
- Updated `template/files/python/tests/test_cli.py.jinja`
- Updated `template/files/shared/docs/modules/cli.md.jinja`
- Regenerated samples: `samples/cli-docs/` and any new CLI-focused variant
- `copier diff` output showing clean template sovereignty

### II. Deterministic Generation

✅ **Pass** - CLI generation is deterministic based on `cli_module=enabled` prompt. All command discovery and plugin loading follows predictable patterns. TOML config format ensures consistent parsing across platforms.

**Validation**:

- Same `cli_module=enabled` always generates identical CLI structure
- Plugin discovery deterministic (alphabetical order, lazy loading)
- No network calls or non-deterministic filesystem operations in hooks
- Smoke tests validate command availability and help text

### III. Minimal Baseline, Optional Depth

✅ **Pass** - Robust CLI features remain behind `cli_module=enabled` prompt (currently defaults to disabled). Baseline render unaffected. All enhancements are opt-in when users explicitly enable CLI module.

**Compliance**:

- `cli_module` defaults to `disabled` in `template/copier.yml`
- No new dependencies added to baseline (Typer, Rich already in optional CLI group)
- CLI enhancements only affect projects with `cli_module=enabled`
- Baseline performance budget unaffected (<10 min render target maintained)

### IV. Documented Scaffolds

✅ **Pass** - Comprehensive documentation required as part of implementation:

- Enhanced `docs/modules/cli.md.jinja` with multi-command examples
- Command authoring guide with <5 minute target
- Configuration management documentation (TOML format, precedence rules)
- Plugin development guide with example implementations
- Troubleshooting section for common CLI issues

**Deliverables**:

- Updated quickstart commands in `docs/quickstart.md.jinja`
- Module-specific docs at `docs/modules/cli.md.jinja`
- Example commands in `template/files/python/src/{{ package_name }}/cli/commands/`
- Shell completion generation documented

### V. Automation-Governed Compliance

✅ **Pass** - CI enforcement through existing workflows:

- `.github/workflows/riso-quality.yml` runs ruff, mypy, pylint, pytest on CLI code
- `.github/workflows/riso-matrix.yml` validates CLI across Python 3.11/3.12/3.13
- Quality checks enforce 10/10 pylint score, 90%+ coverage
- Smoke tests in `test_cli.py.jinja` validate command discovery and execution
- Sample regeneration verified in CI before merge

**Gates**:

- All quality tools pass (ruff, mypy, pylint with 10/10)
- Test coverage ≥90% for CLI module
- Smoke tests pass for all default commands
- `samples/cli-docs/` regenerated and smoke tests green

## Project Structure

### Documentation (this feature)

```text
specs/009-typer-cli-scaffold/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (template modifications)

```text
template/
├── files/
│   ├── python/
│   │   ├── src/
│   │   │   └── {{ package_name }}/
│   │   │       └── cli/
│   │   │           ├── __init__.py.jinja        # Enhanced: CLI package initialization
│   │   │           ├── __main__.py.jinja        # Enhanced: Main app entry point with command groups
│   │   │           │   ├── commands/                # NEW: Command modules directory
│   │   │           │   │   ├── __init__.py.jinja    # Command discovery and registration
│   │   │           │   │   ├── quickstart.py.jinja  # Refactored: Quickstart command
│   │   │           │   │   ├── config.py.jinja      # NEW: Config CommandGroup (set/get/list)
│   │   │           │   │   ├── version.py.jinja     # NEW: Version command
│   │   │           │   │   └── init.py.jinja        # NEW: Example domain command
│   │   │           ├── core/                    # NEW: CLI framework components
│   │   │           │   ├── __init__.py.jinja
│   │   │           │   ├── base.py.jinja        # Base command class/decorators
│   │   │           │   ├── config.py.jinja      # Configuration management (TOML)
│   │   │           │   ├── formatters.py.jinja  # Output formatters (JSON/table/YAML)
│   │   │           │   ├── plugins.py.jinja     # Plugin discovery and loading
│   │   │           │   └── exceptions.py.jinja  # Custom exception hierarchy
│   │   │           └── plugins/                 # NEW: Plugin directory (empty by default)
│   │   │               ├── __init__.py.jinja
│   │   │               └── README.md.jinja      # Plugin development guide
│   │   └── tests/
│   │       ├── test_cli.py.jinja                # Enhanced: Multi-command testing
│   │       ├── test_cli_commands.py.jinja       # NEW: Per-command tests
│   │       ├── test_cli_config.py.jinja         # NEW: Configuration tests
│   │       ├── test_cli_plugins.py.jinja        # NEW: Plugin loading tests
│   │       └── test_cli_formatters.py.jinja     # NEW: Output formatter tests
│   └── shared/
│       └── docs/
│           └── modules/
│               └── cli.md.jinja                  # Enhanced: Comprehensive CLI documentation
├── copier.yml                                    # No changes (cli_module already exists)
└── hooks/
    └── post_gen_project.py                       # Potential enhancement: CLI setup guidance

samples/
└── cli-docs/                                     # Regenerated with enhanced CLI
    └── render/
        └── src/
            └── riso_cli_docs/
                └── cli/                          # Generated CLI structure visible here
```

**Structure Decision**: Single-package Python template enhancement. All CLI scaffold components live under `template/files/python/src/{{ package_name }}/cli/` following the existing template pattern. The `cli/commands/` directory provides modular command organization, `cli/core/` contains framework components, and `cli/plugins/` enables extensibility. This structure maintains template sovereignty while providing clear separation of concerns for CLI functionality.

## Complexity Tracking

> **No violations - all Constitution Check gates pass**

This feature enhances an existing opt-in module (`cli_module`) without introducing architectural complexity or violating constitutional principles. All enhancements remain behind the `cli_module=enabled` prompt, maintaining the minimal baseline principle.
