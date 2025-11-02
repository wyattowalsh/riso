# Data Model: Robust Typer CLI Scaffold

**Feature**: 009-typer-cli-scaffold  
**Date**: 2025-11-01  
**Dependencies**: [research.md](./research.md)

## Overview

This document defines the key entities and their relationships for the robust CLI scaffold. Since this is a template enhancement focused on code generation rather than runtime data storage, the "data model" primarily describes the structural entities that compose the CLI framework.

## Core Entities

### CLIApplication

**Description**: The main application entry point that orchestrates command discovery, registration, execution, and configuration management.

**Attributes**:

- `app_name` (str): Application name used for config files and help text
- `version` (str): Application version displayed in `--version`
- `commands` (Dict[str, Command]): Registry of available commands (name → command instance)
- `command_groups` (Dict[str, CommandGroup]): Registry of command groups (name → group instance)
- `config` (ConfigManager): Configuration manager instance
- `console` (rich.console.Console): Rich console for formatted output
- `plugin_manager` (PluginManager): Plugin discovery and loading manager

**Relationships**:

- Contains many Commands (1:N)
- Contains many CommandGroups (1:N)
- Has one ConfigManager (1:1)
- Has one PluginManager (1:1)

**State Transitions**:

1. **Initialization**: Load config, discover commands, discover plugins
2. **Command Execution**: Parse args, validate, execute selected command
3. **Cleanup**: Save config changes, close resources

### Command

**Description**: Individual executable unit with parameters, validation logic, execution handler, and help documentation.

**Attributes**:

- `name` (str): Command name as invoked in CLI
- `callback` (Callable): Function to execute when command is invoked
- `help_text` (str): Description shown in `--help`
- `parameters` (List[Parameter]): Command parameters/options
- `is_async` (bool): Whether callback is async function
- `aliases` (List[str]): Alternative names for this command
- `hidden` (bool): Whether command is hidden from help text (for internal commands)

**Relationships**:

- Belongs to CLIApplication or CommandGroup (N:1)
- Has many Parameters (1:N)
- May belong to a CommandGroup (N:1, optional)

**Validation Rules**:

- `name` must be valid Python identifier (lowercase, underscores allowed)
- `callback` must be callable
- `help_text` should be non-empty for public commands

### CommandGroup

**Description**: Organizational unit that contains related commands (e.g., `config` group with `set`, `get`, `list` subcommands).

**Attributes**:

- `name` (str): Group name as invoked in CLI
- `commands` (Dict[str, Command]): Commands in this group (name → command)
- `help_text` (str): Group description shown in help
- `app` (typer.Typer): Typer sub-application for this group

**Relationships**:

- Belongs to CLIApplication (N:1)
- Contains many Commands (1:N)

**Examples**:

- `config` group: `set`, `get`, `list`, `validate`
- `plugin` group: `list`, `enable`, `disable`, `info`

### Parameter

**Description**: Command input specification with type, default value, validation rules, and help text.

**Attributes**:

- `name` (str): Parameter name
- `param_type` (type): Python type for validation (str, int, Path, etc.)
- `default` (Any): Default value if not provided
- `required` (bool): Whether parameter is required
- `help_text` (str): Description shown in `--help`
- `prompt` (str | bool): Interactive prompt text if value not provided
- `validator` (Callable | None): Custom validation function
- `envvar` (str | None): Environment variable name for default value

**Relationships**:

- Belongs to Command (N:1)

**Validation Rules**:

- `name` must be valid identifier
- `param_type` must be a type that Typer can parse
- If `required=True`, `default` should be `None` or `...`

### ConfigManager

**Description**: Manages application configuration with multi-source precedence (CLI args > env vars > config file > defaults).

**Attributes**:

- `config_file` (Path): Path to TOML configuration file (./config.toml)
- `env_prefix` (str): Prefix for environment variables (e.g., "MYAPP_")
- `defaults` (Dict[str, Any]): Default configuration values
- `cached_config` (Dict[str, Any]): Cached parsed configuration
- `dirty` (bool): Whether config has unsaved changes

**Methods**:

- `get(key: str, cli_override: Any = None) -> Any`: Get config value with precedence
- `set(key: str, value: Any) -> None`: Set config value and mark dirty
- `save() -> None`: Write changes to TOML file
- `reload() -> None`: Re-parse config file and clear cache
- `validate() -> List[str]`: Validate configuration and return errors

**Relationships**:

- Belongs to CLIApplication (N:1)

**File Format** (TOML):

```toml
[general]
verbose = false
color = true

[api]
endpoint = "https://api.example.com"
timeout = 30
api_key = "secret"

[plugins]
enabled = ["plugin1", "plugin2"]
```

### Plugin

**Description**: External command module that can be dynamically discovered and loaded via entry points.

**Attributes**:

- `name` (str): Plugin name (from entry point)
- `entry_point` (importlib.metadata.EntryPoint): Entry point metadata
- `loaded` (bool): Whether plugin has been loaded
- `commands` (List[Command]): Commands provided by this plugin
- `error` (Exception | None): Load error if plugin failed to load

**Relationships**:

- Managed by PluginManager (N:1)
- Provides many Commands (1:N)

**Lifecycle**:

1. **Discovery**: Found via `importlib.metadata.entry_points(group="myapp.plugins")`
2. **Registration**: Entry point registered but not loaded (lazy)
3. **Loading**: `entry_point.load()` called on first use
4. **Active**: Plugin commands available in CLI
5. **Error**: If loading fails, plugin marked with error but CLI continues

### PluginManager

**Description**: Handles plugin discovery, lazy loading, and error isolation.

**Attributes**:

- `plugin_group` (str): Entry point group name ("myapp.plugins")
- `plugins` (Dict[str, Plugin]): Discovered plugins (name → plugin)
- `load_errors` (List[Tuple[str, Exception]]): Failed plugin loads

**Methods**:

- `discover() -> None`: Scan for plugins via entry points
- `load_plugin(name: str) -> Plugin`: Load specific plugin lazily
- `get_commands() -> List[Command]`: Get all plugin commands (triggers lazy load)
- `list_plugins() -> List[Dict]`: List all plugins with status

**Relationships**:

- Belongs to CLIApplication (N:1)
- Manages many Plugins (1:N)

### OutputFormatter

**Description**: Handles rendering command results in various formats (JSON, table, YAML, plain text).

**Attributes**:

- `format_type` (str): Output format ("json", "table", "yaml", "text")
- `console` (rich.console.Console): Rich console instance
- `color_enabled` (bool): Whether to use colors in output

**Methods**:

- `format(data: Any) -> str`: Format data according to format_type
- `format_table(data: List[Dict]) -> Table`: Create rich table from list of dicts
- `format_json(data: Any) -> str`: Pretty-print JSON
- `format_yaml(data: Any) -> str`: Format as YAML

**Relationships**:

- Used by Commands (N:1)

## Entity Relationships Diagram

```text
CLIApplication
├── ConfigManager (1:1)
├── PluginManager (1:1)
│   └── Plugin (1:N)
│       └── Command (1:N)
├── CommandGroup (1:N)
│   └── Command (1:N)
│       └── Parameter (1:N)
└── Command (1:N)
    └── Parameter (1:N)
```

## Template Generation Mapping

This data model maps to template files as follows:

| Entity | Template File | Purpose |
|--------|---------------|---------|
| CLIApplication | `__main__.py.jinja` | App entry point, command registration |
| Command | `commands/*.py.jinja` | Individual command modules |
| CommandGroup | `__main__.py.jinja` | Group definitions (e.g., config group) |
| Parameter | `commands/*.py.jinja` | Typer decorators for parameters |
| ConfigManager | `core/config.py.jinja` | Configuration management logic |
| Plugin | `core/plugins.py.jinja` | Plugin discovery and loading |
| PluginManager | `core/plugins.py.jinja` | Plugin orchestration |
| OutputFormatter | `core/formatters.py.jinja` | Output formatting utilities |

## Validation Rules Summary

1. **Command Names**: Must be valid Python identifiers, lowercase preferred
2. **Configuration Keys**: Dot-notation supported (e.g., "api.endpoint")
3. **Parameter Types**: Must be Typer-compatible (str, int, float, bool, Path, Enum, etc.)
4. **Plugin Entry Points**: Must follow format `group.name = "package:function"`
5. **TOML Configuration**: Must be valid TOML syntax, nested sections supported
6. **Help Text**: All public commands and parameters must have help text
7. **Exit Codes**: 0=success, 1=general error, 2=usage error, 78=config error, 125-127=system errors

## Performance Considerations

- **Configuration**: Parse TOML once at startup, cache in memory (avoid repeated file I/O)
- **Plugins**: Lazy loading - discover at startup (<50ms), load on first use only
- **Commands**: File-based discovery done once at initialization, not per invocation
- **Rich Formatting**: Console created once, reused across commands (avoid per-command overhead)

## Security Considerations

- **Configuration File**: May contain secrets; document that `config.toml` should be gitignored for sensitive data
- **Plugin Loading**: Plugins execute arbitrary code; warn users to only install from trusted sources
- **Input Validation**: All parameters validated via Typer's type system before execution
- **Error Messages**: Avoid including sensitive data (API keys, passwords) in error output
