# Tasks: Robust Typer CLI Scaffold

**Input**: Design documents from `/specs/009-typer-cli-scaffold/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Template modifications use paths relative to repository root:

- Template files: `template/files/python/src/{{ package_name }}/cli/`
- Tests: `template/files/python/tests/`
- Docs: `template/files/shared/docs/modules/`
- Samples: `samples/cli-docs/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Template structure initialization and dependency setup

- [X] T001 Add Rich library to CLI optional dependency group in `template/files/python/pyproject.toml.jinja`
- [X] T002 Add tomli dependency for Python <3.11 backport in `template/files/python/pyproject.toml.jinja`
- [X] T003 [P] Create core framework directory structure in `template/files/python/src/{{ package_name }}/cli/core/`
- [X] T004 [P] Create commands directory structure in `template/files/python/src/{{ package_name }}/cli/commands/`
- [X] T005 [P] Create plugins directory structure in `template/files/python/src/{{ package_name }}/cli/plugins/`
- [X] T006 [P] Update `.gitignore` template to include `config.local.toml` for sensitive overrides (config.toml with defaults should be committed)

**Checkpoint**: Directory structure ready for component implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CLI framework components that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement base command class with execute() and validate_params() in `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja`
- [X] T008 Implement @command() decorator for automatic registration in `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja`
- [X] T008a [P] Add alias parameter support to @command() decorator for command aliasing in `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja`
- [X] T009 Implement ConfigManager with TOML parsing and precedence in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [X] T010 Implement PluginManager with entry point discovery in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T011 Implement lazy plugin loading with error isolation in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T012 Implement OutputFormatter with table/JSON/YAML support in `template/files/python/src/{{ package_name }}/cli/core/formatter.py.jinja`
- [X] T013 Implement Rich console integration with graceful fallback in `template/files/python/src/{{ package_name }}/cli/core/formatter.py.jinja`
- [X] T014 Create core package `__init__` with exports in `template/files/python/src/{{ package_name }}/cli/core/__init__.py.jinja`
- [X] T015 Create commands package `__init__` with discovery logic in `template/files/python/src/{{ package_name }}/cli/commands/__init__.py.jinja`
- [X] T016 Create custom exception hierarchy (CLIError, ConfigError, PluginError) in `template/files/python/src/{{ package_name }}/cli/core/exceptions.py.jinja`

**Checkpoint**: ✅ Core framework ready - command implementation can now begin

---

## Phase 3: User Story 1 - Multi-Command CLI Structure (Priority: P1) 🎯 MVP

**Goal**: Template users can generate a command-line application with multiple subcommands organized in a modular structure, where each command has its own file and is automatically registered with the main CLI application.

**Independent Test**: Render project with `cli_module=enabled`, run `python -m package.cli --help` to see all commands, execute each command to verify they work in isolation, add new command file to verify auto-discovery.

### Implementation for User Story 1

- [X] T017 [P] [US1] Refactor quickstart command to use new framework in `template/files/python/src/{{ package_name }}/cli/commands/quickstart.py.jinja`
- [X] T018 [P] [US1] Create version command showing app version in `template/files/python/src/{{ package_name }}/cli/commands/version.py.jinja`
- [X] T019 [P] [US1] Create init command as domain example in `template/files/python/src/{{ package_name }}/cli/commands/init.py.jinja`
- [X] T020 [US1] Update `__main__.py` to support command discovery from commands/ directory in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T021 [US1] Implement command registration logic using @command() decorator in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T022 [US1] Add help text generation for all commands with examples in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T023 [US1] Implement error handling with appropriate exit codes (0=success, 1=error) in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T024 [P] [US1] Create test for command discovery in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T025 [P] [US1] Create test for quickstart command execution in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T026 [P] [US1] Create test for version command in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T027 [P] [US1] Create test for init command in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T028 [P] [US1] Create test for help text generation in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T029 [US1] Update test_cli.py to validate multi-command structure in `template/files/python/tests/test_cli.py.jinja`
- [X] T029a [P] [US1] Create test for command aliases resolving to primary commands in `template/files/python/tests/test_cli_commands.py.jinja`

**Checkpoint**: ✅ Multi-command CLI structure working - can add commands by dropping files

---

## Phase 4: User Story 2 - Rich Interactive CLI Experience (Priority: P2)

**Goal**: Users can interact with CLI commands that provide rich formatting (colors, tables, progress bars), interactive prompts for missing parameters, and helpful validation messages.

**Independent Test**: Run commands with missing parameters to test prompts, execute long operations to test progress indicators, view output with various formatting (tables, JSON).

### Implementation for User Story 2

- [X] T030 [P] [US2] Implement table formatter using Rich tables in `template/files/python/src/{{ package_name }}/cli/core/formatters.py.jinja`
- [X] T031 [P] [US2] Implement progress bar/spinner using Rich progress in `template/files/python/src/{{ package_name }}/cli/core/formatters.py.jinja`
- [X] T032 [P] [US2] Implement colored output with ANSI fallback in `template/files/python/src/{{ package_name }}/cli/core/formatters.py.jinja`
- [X] T033 [P] [US2] Add interactive prompt support for missing parameters using Typer prompts in `template/files/python/src/{{ package_name }}/cli/core/prompts.py.jinja`
- [X] T034 [P] [US2] Implement parameter validation with helpful error messages in `template/files/python/src/{{ package_name }}/cli/core/prompts.py.jinja`
- [X] T035 [US2] Add --format flag for output type selection (json/table/yaml/text) in `template/files/python/src/{{ package_name }}/cli/commands/list.py.jinja`
- [X] T036 [US2] Enhance init command to demonstrate table output in `template/files/python/src/{{ package_name }}/cli/commands/init.py.jinja`
- [X] T037 [US2] Enhance init command to show progress bar for long operations in `template/files/python/src/{{ package_name }}/cli/commands/init.py.jinja`
- [X] T038 [US2] Add examples to help text showing rich formatting options in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T039 [P] [US2] Create test for table formatting in `template/files/python/tests/test_cli_formatters.py.jinja`
- [X] T040 [P] [US2] Create test for JSON output formatting in `template/files/python/tests/test_cli_formatters.py.jinja`
- [X] T041 [P] [US2] Create test for interactive prompts in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T042 [P] [US2] Create test for progress indicators in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T043 [P] [US2] Create test for terminal capability fallback in `template/files/python/tests/test_cli_formatters.py.jinja`

**Checkpoint**: ✅ Rich formatting and interactivity working - professional CLI UX

---

## Phase 5: User Story 3 - Configuration Management (Priority: P3)

**Goal**: Users can manage application configuration through CLI commands that read from and write to configuration files, environment variables, and command-line arguments with clear precedence order.

**Independent Test**: Run `config set/get/list` commands, verify persistence across sessions, confirm precedence order (CLI args > env vars > config file > defaults).

### Implementation for User Story 3

- [X] T044 [US3] Create config command group with Typer sub-app in `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`
- [X] T045 [P] [US3] Implement config set command persisting to TOML file in `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`
- [X] T046 [P] [US3] Implement config get command with precedence display in `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`
- [X] T047 [P] [US3] Implement config list command showing all keys and sources in `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`
- [X] T048 [P] [US3] Implement config validate command checking for errors in `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`
- [X] T049 [US3] Add config file path resolution (./config.toml or .app-name.toml) in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [X] T050 [US3] Implement environment variable prefix support (MYAPP_*) in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [X] T051 [US3] Add config file format documentation to help text in `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`
- [X] T052 [US3] Handle invalid TOML with clear error messages in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [X] T053 [P] [US3] Create test for config set/get roundtrip in `template/files/python/tests/test_cli_config.py.jinja`
- [X] T054 [P] [US3] Create test for config precedence order in `template/files/python/tests/test_cli_config.py.jinja`
- [X] T055 [P] [US3] Create test for invalid TOML handling in `template/files/python/tests/test_cli_config.py.jinja`
- [X] T056 [P] [US3] Create test for environment variable prefix in `template/files/python/tests/test_cli_config.py.jinja`
- [X] T057 [P] [US3] Create test for config validation in `template/files/python/tests/test_cli_config.py.jinja`

**Checkpoint**: ✅ Configuration management working - settings persist across sessions

---

## Phase 6: User Story 4 - Plugin Architecture (Priority: P4)

**Goal**: Developers can extend the generated CLI by adding plugin commands that are automatically discovered and loaded, enabling third-party extensions without modifying core CLI code.

**Independent Test**: Create plugin following documented pattern, place in plugins directory, verify it appears in `--help` and executes independently of core commands.

### Implementation for User Story 4

- [X] T058 [US4] Implement plugin command discovery via entry points in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T059 [US4] Add plugin loading at CLI startup with lazy evaluation in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T060 [US4] Implement plugin error isolation (failed plugins don't crash CLI) in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T061 [US4] Add plugin status reporting (loaded/failed/disabled) in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T062 [P] [US4] Create plugin development guide in `template/files/python/src/{{ package_name }}/cli/plugins/README.md.jinja`
- [X] T063 [P] [US4] Create example plugin template in `template/files/python/src/{{ package_name }}/cli/plugins/example_plugin.py.jinja`
- [X] T064 [US4] Add plugin list command showing installed plugins in `template/files/python/src/{{ package_name }}/cli/commands/plugin.py.jinja`
- [X] T065 [US4] Mark plugin commands distinctly in help output in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T066 [US4] Handle plugin dependency conflicts with clear messages in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T067 [US4] Handle plugin name conflicts (two plugins with same command name) in `template/files/python/src/{{ package_name }}/cli/core/plugin_manager.py.jinja`
- [X] T068 [P] [US4] Create test for plugin discovery in `template/files/python/tests/test_cli_plugins.py.jinja`
- [X] T069 [P] [US4] Create test for lazy plugin loading in `template/files/python/tests/test_cli_plugins.py.jinja`
- [X] T070 [P] [US4] Create test for plugin error isolation in `template/files/python/tests/test_cli_plugins.py.jinja`
- [X] T071 [P] [US4] Create test for plugin name conflict detection in `template/files/python/tests/test_cli_plugins.py.jinja`

**Checkpoint**: ✅ Plugin architecture working - third-party commands can be added

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, shell completion, edge case handling, quality validation

### Documentation

- [X] T072 [P] Add CLI module feature overview to `docs/modules/cli.md.jinja`
- [X] T073 [P] Add command authoring guide (<5 minute target) in `template/files/shared/docs/modules/cli.md.jinja`
- [X] T074 [P] Add configuration management documentation in `template/files/shared/docs/modules/cli.md.jinja`
- [X] T075 [P] Add plugin development guide with examples in `template/files/shared/docs/modules/cli.md.jinja`
- [X] T076 [P] Add troubleshooting section for common issues in `template/files/shared/docs/modules/cli.md.jinja`
- [ ] T077 [P] Update quickstart guide with CLI usage examples in `docs/quickstart.md.jinja`

### Shell Completion

- [X] T078 Verify Typer's built-in --install-completion works in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T079 [P] Document shell completion setup for bash/zsh/fish in `template/files/shared/docs/modules/cli.md.jinja`
- [ ] T080 [P] Add shell completion generation to CI validation in `.github/workflows/riso-quality.yml`

### Edge Case Handling

- [X] T081 [P] Handle Ctrl+C interruption gracefully (cleanup and exit) in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [ ] T081a [P] Create test for Ctrl+C handling with cleanup verification in `template/files/python/tests/test_cli_commands.py.jinja`
- [X] T082 [P] Handle read-only filesystem errors with clear messages in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [X] T083 [P] Handle invalid environment variable values with warnings in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [X] T084 [P] Show help when CLI invoked without commands in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [X] T085 [P] Validate parameter types with helpful messages in `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja`

### Async Command Support

- [ ] T086 [P] Add async command example demonstrating pattern in `template/files/python/src/{{ package_name }}/cli/commands/example_async.py.jinja`
- [X] T087 [P] Document async command pattern in CLI docs in `template/files/shared/docs/modules/cli.md.jinja`
- [ ] T088 [P] Create test for async command execution in `template/files/python/tests/test_cli_commands.py.jinja`

### Shell Completion

- [ ] T078 Verify Typer's built-in --install-completion works in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [ ] T079 [P] Document shell completion setup for bash/zsh/fish in `template/files/shared/docs/modules/cli.md.jinja`
- [ ] T080 [P] Add shell completion generation to CI validation in `.github/workflows/riso-quality.yml`

### Edge Case Handling

- [ ] T081 [P] Handle Ctrl+C interruption gracefully (cleanup and exit) in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [ ] T081a [P] Create test for Ctrl+C handling with cleanup verification in `template/files/python/tests/test_cli_commands.py.jinja`
- [ ] T082 [P] Handle read-only filesystem errors with clear messages in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [ ] T083 [P] Handle invalid environment variable values with warnings in `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`
- [ ] T084 [P] Show help when CLI invoked without commands in `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`
- [ ] T085 [P] Validate parameter types with helpful messages in `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja`

### Async Command Support

- [ ] T086 [P] Add async command example demonstrating pattern in `template/files/python/src/{{ package_name }}/cli/commands/example_async.py.jinja`
- [ ] T087 [P] Document async command pattern in CLI docs in `template/files/shared/docs/modules/cli.md.jinja`
- [ ] T088 [P] Create test for async command execution in `template/files/python/tests/test_cli_commands.py.jinja`

### Command Versioning (Deferred to v2.0)

**Note**: FR-018 (command versioning and backward compatibility patterns) is explicitly deferred to a future iteration. The following placeholder tasks are included for reference but NOT required for this feature:

- [ ] DEFERRED: Create deprecation warning template for old command names
- [ ] DEFERRED: Document semantic versioning strategy for CLI commands
- [ ] DEFERRED: Create migration guide template for breaking changes

### Quality & Validation

- [ ] T089 Run ruff linting on all CLI template files and fix issues (zero errors required)
- [ ] T090 Run mypy strict mode on CLI code and resolve type errors (zero errors required)
- [ ] T091 Run pylint on CLI code targeting 10/10 score (must achieve 10/10)
- [ ] T092 Verify test coverage ≥90% for CLI module
- [ ] T096 Generate copier diff evidence of template sovereignty (CRITICAL: must pass before sample regeneration)
- [ ] T093 Regenerate samples/cli-docs with enhanced CLI using `./scripts/render-samples.sh`
- [ ] T094 Run smoke tests on rendered CLI-docs sample
- [ ] T095 Validate all success criteria from spec.md are met
- [ ] T097 Update AGENTS.md with CLI enhancement details
- [ ] T098 Update copilot-instructions.md with new technologies

---

## Dependencies & Execution Order

### User Story Dependencies

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundation) ← BLOCKING - must complete before user stories
    ↓
    ├─→ Phase 3 (US1: Multi-Command) ← MVP, independent
    ├─→ Phase 4 (US2: Rich UX) ← depends on US1 (needs commands to format)
    ├─→ Phase 5 (US3: Config) ← independent of US1/US2
    └─→ Phase 6 (US4: Plugins) ← depends on US1 (needs command registration)
    ↓
Phase 7 (Polish) ← all stories complete
```

### Parallel Execution Opportunities

**Phase 1**: T003, T004, T005, T006 can run in parallel

**Phase 2**: T007-T016 sequential (interdependent framework components)

**Phase 3 (US1)**:

- T017, T018, T019 can run in parallel (independent command files)
- T024-T028 can run in parallel (independent test files)
- T020-T023 sequential (main app changes)
- T029 after T020-T023 complete

**Phase 4 (US2)**:

- T030, T031, T032 can run in parallel (independent formatter methods)
- T033, T034 can run in parallel (base command enhancements)
- T036, T037 can run in parallel (init command enhancements)
- T039-T043 can run in parallel (independent test files)

**Phase 5 (US3)**:

- T045, T046, T047, T048 can run in parallel (config subcommands)
- T053-T057 can run in parallel (independent test files)

**Phase 6 (US4)**:

- T062, T063 can run in parallel (documentation)
- T068-T071 can run in parallel (independent test files)

**Phase 7**:

- T072-T077 can run in parallel (documentation)
- T079, T080 can run in parallel (completion docs)
- T081-T088 can run in parallel (edge cases and examples)

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**Deliver Phase 1 + Phase 2 + Phase 3 (User Story 1) as MVP:**

This provides:

- ✅ Multi-command CLI structure
- ✅ Core framework (base, config, plugins, formatters)
- ✅ Default commands (quickstart, version, init)
- ✅ Command discovery and registration
- ✅ Comprehensive tests
- ✅ Basic help text and error handling

**Value**: Users can immediately start building CLIs with multiple commands organized in maintainable structure. Each additional command takes <5 minutes to add.

### Incremental Delivery After MVP

1. **Phase 4 (US2 - Rich UX)**: Adds professional formatting, progress bars, interactive prompts
2. **Phase 5 (US3 - Config)**: Adds persistent configuration management
3. **Phase 6 (US4 - Plugins)**: Adds extensibility for third-party commands
4. **Phase 7 (Polish)**: Adds documentation, completion, edge cases

Each phase delivers independently testable value and can be released separately.

### Task Execution Guidelines

1. **Complete Phase 2 first** - foundation blocks all user stories
2. **Implement US1 (Phase 3) as MVP** - core value, enables testing
3. **Parallelize US2/US3** - independent stories, can develop simultaneously
4. **US4 after US1** - plugins need command registration from US1
5. **Polish after all stories** - comprehensive docs need all features complete

### Testing Strategy

- Write tests alongside implementation (not after)
- Each user story phase includes its test tasks
- Target ≥90% coverage before moving to next phase
- Validate acceptance scenarios from spec.md at each checkpoint

## Summary

- **Total Tasks**: 102 (98 original + 3 new implementation tasks + 1 test task)
- **Parallelizable**: 56 tasks marked [P]
- **User Stories**: 4 (P1-P4)
- **Test Tasks**: 32 (covering all components including edge cases)
- **MVP Tasks**: 30 (Phase 1 + Phase 2 + Phase 3, including T008a and T029a)
- **Estimated MVP Effort**: 3-4 days (with parallel execution)
- **Full Feature Effort**: 7-10 days (all phases)
- **Deferred Items**: FR-018 command versioning (documented for v2.0)

**Next Step**: Begin with Phase 1 (Setup) tasks T001-T006
