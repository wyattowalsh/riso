# Quickstart: Robust Typer CLI Scaffold

**Feature**: 009-typer-cli-scaffold  
**Audience**: Template maintainers and contributors  
**Prerequisites**: Python 3.11+, uv, basic Copier knowledge

## Overview

This guide walks through implementing and testing the robust CLI scaffold enhancement for the Riso template.

## Phase 1: Setup Development Environment

### 1.1 Check Out Feature Branch

```bash
git checkout 009-typer-cli-scaffold
```

### 1.2 Verify Prerequisites

```bash
# Python version
python --version  # Should be 3.11+

# uv installed
uv --version

# Copier available
copier --version
```

### 1.3 Review Planning Documents

Read these documents in order:

1. [spec.md](./spec.md) - Feature specification with user stories
2. [research.md](./research.md) - Technical decisions and rationale
3. [data-model.md](./data-model.md) - Entity definitions and relationships
4. [contracts/](./contracts/) - Interface contracts for components

## Phase 2: Implement CLI Framework Components

### 2.1 Create Core Framework Files

**File**: `template/files/python/src/{{ package_name }}/cli/core/base.py.jinja`

Implement base command class and registration decorators:

```python
# Key elements:
- BaseCommand class with execute() and validate_params()
- @command() decorator for automatic registration
- Command group support via Typer sub-apps
```

**File**: `template/files/python/src/{{ package_name }}/cli/core/config.py.jinja`

Implement configuration manager:

```python
# Key elements:
- ConfigManager class with TOML parsing
- Precedence: CLI args > env vars > config file > defaults
- get(), set(), save(), reload(), validate() methods
```

**File**: `template/files/python/src/{{ package_name }}/cli/core/plugins.py.jinja`

Implement plugin discovery and loading:

```python
# Key elements:
- PluginManager with entry point discovery
- Lazy loading (discover at startup, load on use)
- Error isolation (failed plugins don't crash CLI)
```

**File**: `template/files/python/src/{{ package_name }}/cli/core/formatters.py.jinja`

Implement output formatters:

```python
# Key elements:
- OutputFormatter with format_table(), format_json()
- Rich console integration
- Format type selection (--format flag)
```

### 2.2 Create Default Commands

**File**: `template/files/python/src/{{ package_name }}/cli/commands/quickstart.py.jinja`

Refactor existing quickstart command to use new framework:

```python
from cli.core.base import command

@command()
def quickstart(dry_run: bool = typer.Option(False)):
    """Execute the baseline quickstart workflow."""
    # Existing quickstart logic
```

**File**: `template/files/python/src/{{ package_name }}/cli/commands/config.py.jinja`

Implement config command group:

```python
config_app = typer.Typer(help="Manage configuration")

@config_app.command()
def set(key: str, value: str):
    """Set configuration value."""
    
@config_app.command()
def get(key: str):
    """Get configuration value."""
    
@config_app.command()
def list():
    """List all configuration."""
```

**File**: `template/files/python/src/{{ package_name }}/cli/commands/version.py.jinja`

Implement version command:

```python
@command()
def version():
    """Show application version."""
    from importlib.metadata import version as pkg_version
    typer.echo(pkg_version("{{ package_name }}"))
```

**File**: `template/files/python/src/{{ package_name }}/cli/commands/init.py.jinja`

Implement example domain command:

```python
@command()
def init(name: str, path: Path = Path(".")):
    """Initialize a new project."""
    # Example showing file operations, validation, etc.
```

### 2.3 Update Main Entry Point

**File**: `template/files/python/src/{{ package_name }}/cli/__main__.py.jinja`

Enhance to support command discovery and groups:

```python
# Key changes:
- Import command modules from commands/
- Register command groups (config_app)
- Add plugin loading via PluginManager
- Keep existing Typer app structure
```

## Phase 3: Add Comprehensive Tests

### 3.1 Command Tests

**File**: `template/files/python/tests/test_cli_commands.py.jinja`

```bash
# Create tests for each command
uv run pytest tests/test_cli_commands.py -v
```

Test structure:

```python
def test_quickstart_command():
    """Test quickstart command execution."""
    
def test_config_set_get():
    """Test config set and get roundtrip."""
    
def test_version_command():
    """Test version display."""
    
def test_init_command():
    """Test init command with various options."""
```

### 3.2 Configuration Tests

**File**: `template/files/python/tests/test_cli_config.py.jinja`

```bash
uv run pytest tests/test_cli_config.py -v
```

Test scenarios:

- Config file parsing (valid TOML)
- Precedence order (CLI > env > file > defaults)
- Invalid TOML handling
- Config validation

### 3.3 Plugin Tests

**File**: `template/files/python/tests/test_cli_plugins.py.jinja`

```bash
uv run pytest tests/test_cli_plugins.py -v
```

Test scenarios:

- Plugin discovery via entry points
- Lazy loading behavior
- Error isolation (failed plugin doesn't crash)
- Plugin command registration

### 3.4 Formatter Tests

**File**: `template/files/python/tests/test_cli_formatters.py.jinja`

```bash
uv run pytest tests/test_cli_formatters.py -v
```

Test scenarios:

- Table formatting
- JSON output
- Format selection via --format flag
- Terminal capability degradation

## Phase 4: Update Documentation

### 4.1 Module Documentation

**File**: `template/files/shared/docs/modules/cli.md.jinja`

Update with:

- Multi-command structure documentation
- Configuration management guide
- Plugin development guide
- Shell completion setup
- Troubleshooting section

### 4.2 Quickstart Guide

**File**: `docs/quickstart.md.jinja`

Add CLI examples:

```markdown
## Using the CLI

```bash
# Run quickstart
uv run python -m {{ package_name }}.cli quickstart

# Manage configuration
uv run python -m {{ package_name }}.cli config set api.endpoint https://api.example.com
uv run python -m {{ package_name }}.cli config get api.endpoint
uv run python -m {{ package_name }}.cli config list

# Show version
uv run python -m {{ package_name }}.cli version
```
```

## Phase 5: Validate Implementation

### 5.1 Run Quality Checks

```bash
cd template/

# Lint
uv run ruff check files/python/

# Type check
uv run mypy files/python/

# Static analysis
uv run pylint files/python/ --rcfile=files/python/.pylintrc
```

### 5.2 Render Test Sample

```bash
cd /Users/ww/dev/projects/riso

# Render cli-docs sample
./scripts/render-samples.sh --variant cli-docs --answers samples/cli-docs/copier-answers.yml

# Navigate to rendered project
cd samples/cli-docs/render

# Test CLI
uv sync
uv run python -m riso_cli_docs.cli --help
uv run python -m riso_cli_docs.cli quickstart --dry-run
uv run python -m riso_cli_docs.cli config list
uv run python -m riso_cli_docs.cli version

# Run tests
uv run pytest tests/test_cli*.py -v
```

### 5.3 Validate Success Criteria

Check against spec.md success criteria:

- [ ] SC-001: Can add new command in <5 minutes
- [ ] SC-002: Passes all quality checks (ruff, mypy, pylint 10/10)
- [ ] SC-003: Interactive prompts for required parameters
- [ ] SC-004: 100% commands have comprehensive help text
- [ ] SC-005: Shell completion scripts work (bash/zsh/fish)
- [ ] SC-006: Plugin commands work without modifying core
- [ ] SC-007: Clear error messages with non-zero exit codes
- [ ] SC-008: Test coverage ≥90%
- [ ] SC-009: 5+ complete command examples in docs
- [ ] SC-010: 3+ output formats supported (JSON, table, text)

## Phase 6: Submit for Review

### 6.1 Regenerate All Samples

```bash
./scripts/render-samples.sh
```

Verify smoke tests pass:

```bash
cat samples/cli-docs/smoke-results.json
# Should show "success": true for CLI module
```

### 6.2 Generate Copier Diff

```bash
copier diff samples/cli-docs/render
# Save output as evidence of template sovereignty
```

### 6.3 Create Pull Request

Include in PR description:

- Link to spec.md, plan.md, tasks.md
- Success criteria checklist
- Sample render evidence
- Copier diff output
- Test coverage report

## Troubleshooting

### Issue: Commands not discovered

**Solution**: Check that command files are in `commands/` directory and use `@command()` decorator

### Issue: Config file not found

**Solution**: Ensure `config.toml` is in project root or specify path with `--config` flag

### Issue: Plugin won't load

**Solution**: Check entry point registration in plugin's `pyproject.toml` and verify plugin implements required interface

### Issue: Tests failing on CI

**Solution**: Verify all quality tools pass locally first, check Python version matrix (3.11/3.12/3.13)

## Next Steps

After implementation complete:

1. Run `/speckit.tasks` to generate detailed task breakdown
2. Execute tasks following phased approach
3. Validate after each checkpoint
4. Submit PR when all success criteria met

## Resources

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [TOML Specification](https://toml.io/)
- [Entry Points Guide](https://packaging.python.org/specifications/entry-points/)
