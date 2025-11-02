# Research: Robust Typer CLI Scaffold

**Feature**: 009-typer-cli-scaffold  
**Date**: 2025-11-01  
**Status**: Complete

## Overview

This document consolidates research findings for enhancing the Riso template's CLI module from a minimal single-command implementation to a robust, production-ready command-line application framework.

## Decision 1: Command Discovery Pattern

**Decision**: Use explicit registration via decorators combined with automatic file-based discovery in `commands/` directory

**Rationale**:
- Typer's `@app.command()` decorator provides clear, explicit command registration
- File-based discovery in `commands/` directory enables "drop a file, get a command" simplicity
- Combining both approaches: commands can self-register via decorator OR be auto-discovered from `commands/*.py` files
- Achieves <5 minute target for adding new commands (create file, use decorator, done)
- Type hints in decorators enable automatic parameter validation and help text generation

**Alternatives Considered**:
- **Pure manual registration**: Rejected because it requires editing `__main__.py` for every new command, violating the simplicity goal
- **Import hooks/metaclasses**: Rejected as too magical and harder to debug; explicit decorators are more maintainable
- **Entry points system**: Rejected for built-in commands (too heavy); reserved for plugins only

**Implementation Pattern**:

```python
# In commands/my_command.py
from cli.core.base import command

@command()
def my_command(name: str = typer.Option(..., help="User name")):
    """Execute my custom command."""
    typer.echo(f"Hello {name}")
```

## Decision 2: Configuration Management Library

**Decision**: Use `tomli` (Python <3.11) / `tomllib` (Python 3.11+) for TOML parsing with custom precedence layering

**Rationale**:
- TOML is Python-native format (used in pyproject.toml), human-readable, and well-supported
- `tomllib` is stdlib in Python 3.11+, `tomli` is the backport for 3.10 (minimal external dependency)
- Simple key-value structure matches CLI configuration needs better than YAML or JSON
- Precedence order (CLI args > env vars > config file > defaults) implemented via custom `ConfigManager` class
- File location in project directory (./config.toml) aligns with version control best practices

**Alternatives Considered**:
- **JSON**: Rejected because no comments support, less human-friendly for editing
- **YAML**: Rejected because adds heavier dependency (PyYAML), more complex parsing, security concerns with `yaml.load()`
- **INI files**: Rejected because limited type support, no nested structures
- **Environment variables only**: Rejected because no persistence, harder to manage 50+ config keys

**Implementation Pattern**:

```python
# Precedence: CLI args > env vars > TOML file > defaults
config = ConfigManager(
    config_file="./config.toml",
    env_prefix="MYAPP_",
    defaults={"timeout": 30, "verbose": False}
)
value = config.get("timeout", cli_override=args.timeout)
```

## Decision 3: Rich Terminal Output Library

**Decision**: Use `rich` library for formatting (tables, progress bars, colors) with graceful fallback for unsupported terminals

**Rationale**:
- `rich` is industry standard for modern Python CLIs (used by Typer, FastAPI docs, many popular tools)
- Provides tables, progress bars, syntax highlighting, panels, trees out-of-the-box
- Automatic color degradation for terminals without ANSI support
- Excellent integration with Typer (Typer uses Rich for help formatting)
- Already a common dependency in Python ecosystem (low addition cost)

**Alternatives Considered**:
- **click-based formatters**: Rejected because more limited formatting options, no built-in tables/progress
- **Colorama**: Rejected because only handles colors, not tables/progress bars
- **blessed/asciimatics**: Rejected as too heavyweight for our needs
- **Plain ANSI codes**: Rejected because requires manual terminal capability detection and formatting logic

**Implementation Pattern**:

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

# Automatic color fallback if terminal doesn't support it
console.print("[bold green]Success![/bold green]")

# Tables
table = Table(title="Commands")
table.add_column("Name", style="cyan")
table.add_column("Description")
table.add_row("quickstart", "Run initial setup")
console.print(table)

# Progress bars
for item in track(items, description="Processing..."):
    process(item)
```

## Decision 4: Plugin Discovery Mechanism

**Decision**: Use entry points (importlib.metadata) with lazy loading and isolated error handling

**Rationale**:
- Entry points are Python's standard plugin mechanism (used by pytest, setuptools, many frameworks)
- `importlib.metadata.entry_points()` is stdlib in Python 3.10+ (no external dependency)
- Lazy loading: plugins discovered at startup but only loaded when first used (<50ms overhead)
- Error isolation: failed plugin imports logged but don't crash main CLI
- Enables third-party plugins via standard package distribution (pip install user-plugin)

**Alternatives Considered**:
- **Directory scanning**: Rejected because requires plugins in specific directory, harder to distribute
- **Configuration-based registration**: Rejected because adds manual configuration burden
- **Namespace packages**: Rejected as more complex and less explicit than entry points
- **Eager loading**: Rejected because slows startup time proportional to plugin count

**Implementation Pattern**:

```python
# In pyproject.toml (plugin package):
[project.entry-points."myapp.plugins"]
my_plugin = "my_plugin_package:register_commands"

# In CLI core:
from importlib.metadata import entry_points

plugins = entry_points(group="myapp.plugins")
for plugin in plugins:
    try:
        register_func = plugin.load()  # Lazy: only load on first access
        register_func(app)
    except Exception as e:
        logger.error(f"Plugin {plugin.name} failed to load: {e}")
        # Continue execution - isolated error
```

## Decision 5: Shell Completion Generation

**Decision**: Use Typer's built-in `--install-completion` and `--show-completion` commands with documentation for manual setup

**Rationale**:
- Typer provides automatic completion generation for bash, zsh, fish, PowerShell
- Zero implementation effort - works out of the box with properly decorated commands
- Users run `myapp --install-completion` once to set up
- Manual documentation provided for advanced users who want custom completion logic

**Alternatives Considered**:
- **argcomplete**: Rejected because Typer already provides this functionality
- **Custom completion scripts**: Rejected because high maintenance burden, Typer's solution is sufficient
- **No completion**: Rejected because modern CLIs require this feature for good UX

**Implementation**: Typer automatically generates completion scripts. Document in CLI usage guide:

```bash
# Install completion (one-time setup)
myapp --install-completion

# Show completion script for manual installation
myapp --show-completion bash > /etc/bash_completion.d/myapp
```

## Decision 6: Testing Strategy

**Decision**: Use `typer.testing.CliRunner` for command testing with pytest fixtures for common setups

**Rationale**:
- `CliRunner` is Typer's official testing utility (similar to Click's CliRunner)
- Provides isolated test environment with captured stdin/stdout/stderr
- Enables testing interactive prompts via `input` parameter
- Integrates seamlessly with pytest fixtures for reusable test setup
- Coverage target of 90% achievable with command-level and integration tests

**Alternatives Considered**:
- **subprocess testing**: Rejected because slower, harder to mock, less isolated
- **Direct function calls**: Rejected because bypasses CLI parsing and validation
- **Mock-heavy approach**: Rejected because Typer already provides good testing primitives

**Implementation Pattern**:

```python
from typer.testing import CliRunner
from myapp.cli.__main__ import app

runner = CliRunner()

def test_quickstart_dry_run():
    result = runner.invoke(app, ["quickstart", "--dry-run"])
    assert result.exit_code == 0
    assert "quickstart status: ok" in result.stdout.lower()

def test_interactive_prompt():
    # Test prompts by providing input
    result = runner.invoke(app, ["config", "set"], input="key\nvalue\n")
    assert result.exit_code == 0
    assert "Configuration saved" in result.stdout
```

## Decision 7: Async Command Support

**Decision**: Support both sync and async command functions via Typer's async detection with asyncio runtime

**Rationale**:
- Some commands need async operations (API calls, file I/O, concurrent tasks)
- Typer automatically detects `async def` and runs with `asyncio.run()`
- Zero overhead for sync commands - only async commands pay the runtime cost
- Enables modern async/await patterns for I/O-bound operations

**Alternatives Considered**:
- **Sync-only**: Rejected because limits CLI utility for modern async workflows
- **Separate async CLI app**: Rejected as unnecessary duplication
- **Manual event loop management**: Rejected because Typer handles this automatically

**Implementation Pattern**:

```python
@command()
async def fetch_data(url: str):
    """Fetch data from remote API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Decision 8: Error Handling Strategy

**Decision**: Use structured exception hierarchy with rich error formatting and appropriate exit codes

**Rationale**:
- Custom exception classes (`CLIError`, `ConfigError`, `PluginError`) provide clear error categories
- Rich console formatting makes errors readable with color-coded severity
- Exit codes follow conventions: 0=success, 1=general error, 2=usage error, 125-127=system errors
- Errors include actionable guidance (e.g., "Run 'myapp config set api_key <value>' to fix")

**Alternatives Considered**:
- **Generic exceptions**: Rejected because harder to handle different error types appropriately
- **Plain text errors**: Rejected because less readable, no color coding
- **Single exit code**: Rejected because automation scripts need to distinguish error types

**Implementation Pattern**:

```python
class CLIError(Exception):
    """Base exception for CLI errors."""
    exit_code = 1

class ConfigError(CLIError):
    """Configuration-related errors."""
    exit_code = 78  # EX_CONFIG in sysexits.h

try:
    config = load_config()
except ConfigError as e:
    console.print(f"[bold red]Configuration Error:[/bold red] {e}")
    console.print("[yellow]Hint:[/yellow] Run 'myapp config validate' to check your configuration")
    raise typer.Exit(code=e.exit_code)
```

## Best Practices Findings

### Command Organization

- **One command per file** in `commands/` directory for maintainability
- **Command groups** for related commands (e.g., `config set/get/list`)
- **Shared utilities** in `core/` to avoid duplication
- **Example commands** demonstrating common patterns (API calls, file operations, async tasks)

### Parameter Validation

- Use Typer's type hints for automatic validation (`int`, `Path`, `Enum`)
- Custom validators via `typer.Option(callback=validate_func)` for complex rules
- Helpful error messages that explain what's wrong and how to fix it
- Interactive prompts for missing required parameters (better UX than cryptic errors)

### Documentation Standards

- Every command has comprehensive docstring (becomes `--help` text)
- Examples in help text show common usage patterns
- Quick reference guide generated from all command helps
- Troubleshooting section documents common issues and solutions

### Performance Optimization

- Lazy imports for heavy dependencies (only load when command needs them)
- Plugin lazy loading (discover at startup, load on first use)
- Configuration caching (parse TOML once, cache in memory)
- Progress indicators for operations >2 seconds

## Integration Points

### Existing Riso Template

- **Quality Tools**: All CLI code must pass ruff, mypy (strict mode), pylint (10/10)
- **Testing**: Integrate with existing pytest setup, add CLI-specific fixtures
- **Documentation**: Follow existing Jinja template patterns in `docs/modules/cli.md.jinja`
- **CI/CD**: Leverage existing GitHub Actions workflows for validation

### Dependencies Already in Template

- **Typer ≥0.20.0**: Already in pyproject.toml CLI optional group
- **Loguru**: Already used for logging in current CLI implementation
- **Rich**: Need to add to CLI optional group (widely used, stable)
- **tomli/tomllib**: Stdlib in 3.11+, add tomli for 3.10 backport

## Security Considerations

- **Configuration file permissions**: Document that config.toml may contain secrets, should be gitignored if sensitive
- **Plugin security**: Warn that plugins execute arbitrary code, only install from trusted sources
- **Input validation**: All user input validated before processing (prevent injection attacks)
- **Error messages**: Avoid leaking sensitive information in error messages

## Summary

Research establishes technical foundation for robust CLI scaffold:

1. **Command discovery**: Decorator + file-based pattern (achieves <5 min new command target)
2. **Configuration**: TOML with precedence layering (CLI > env > file > defaults)
3. **Rich formatting**: Rich library with graceful fallback
4. **Plugins**: Entry points + lazy loading + error isolation
5. **Shell completion**: Typer built-in (bash/zsh/fish support)
6. **Testing**: CliRunner + pytest fixtures (90% coverage target)
7. **Async support**: Typer automatic detection
8. **Error handling**: Structured exceptions + rich formatting + standard exit codes

All decisions align with constitutional principles (template sovereignty, minimal baseline, documented scaffolds) and integrate cleanly with existing Riso template infrastructure.
