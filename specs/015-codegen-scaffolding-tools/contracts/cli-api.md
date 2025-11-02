# CLI API Contract

**Feature**: 015-codegen-scaffolding-tools  
**Version**: 1.0.0  
**Date**: 2025-11-02

## Overview

This document defines the command-line interface contract for the scaffolding tool. All commands follow a consistent structure with standard options, error handling, and output formats.

## Global Options

Available for all commands:

```bash
--help, -h              Show help message and exit
--version, -v           Show version and exit
--verbose              Enable verbose output
--quiet, -q            Suppress non-error output
--config FILE          Use custom config file (default: ~/.scaffold/config.yml)
--no-color             Disable colored output
```

## Commands

### 1. scaffold new

Create a new project from a template.

**Synopsis:**
```bash
scaffold new PROJECT_NAME [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PROJECT_NAME` | string | Yes | Name of the project to create |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--template, -t` | string | `default` | Template to use |
| `--output, -o` | path | `.` | Output directory |
| `--interactive/--no-interactive` | flag | `true` | Enable/disable interactive prompts |
| `--dry-run` | flag | `false` | Preview without creating files |
| `--overwrite/--no-overwrite` | flag | `false` | Overwrite existing directory |
| `--skip-quality` | flag | `false` | Skip quality validation |
| `--var KEY=VALUE` | multiple | - | Set template variable |

**Examples:**

```bash
# Interactive mode (default)
scaffold new my-project

# Specify template
scaffold new my-api --template fastapi-api

# Non-interactive with variables
scaffold new my-cli --no-interactive \
  --var author="Jane Doe" \
  --var python_version=3.11

# Dry run to preview
scaffold new my-project --dry-run

# Custom output directory
scaffold new my-project --output ~/projects/
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Template not found |
| 3 | Output directory exists (without --overwrite) |
| 4 | Missing required variables |
| 5 | Quality validation failed (critical errors) |
| 10 | Network error (fetching remote template) |

**Output Format:**

```
[INFO] Creating project: my-project
[INFO] Using template: python-cli (v1.2.3)
[INFO] Collecting variables...
  ✓ project_name: my-project
  ✓ author: Jane Doe
  ✓ python_version: 3.11
[INFO] Generating files...
  ✓ pyproject.toml
  ✓ src/my_project/__init__.py
  ✓ tests/test_main.py
  (47 files created)
[INFO] Running quality checks...
  ⚠ Warning: Unused import in src/main.py:5
[SUCCESS] Project created successfully!
  Location: /home/user/my-project
  Next steps:
    cd my-project
    uv sync
    uv run pytest
```

---

### 2. scaffold add

Add a feature module to an existing project.

**Synopsis:**
```bash
scaffold add MODULE_TYPE MODULE_NAME [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `MODULE_TYPE` | enum | Yes | Type of module (api, cli, docs, auth, etc.) |
| `MODULE_NAME` | string | Yes | Name of the module |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--template, -t` | string | auto | Module template (auto-detected from type) |
| `--project-dir, -p` | path | `.` | Project root directory |
| `--overwrite/--no-overwrite` | flag | `false` | Overwrite existing files |
| `--skip-tests` | flag | `false` | Skip test file generation |
| `--var KEY=VALUE` | multiple | - | Set module variable |

**Examples:**

```bash
# Add API module
scaffold add api users

# Add CLI with custom template
scaffold add cli admin --template rich-cli

# From different directory
scaffold add docs api --project-dir ~/projects/my-app

# With variables
scaffold add api products --var auth_required=true
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Not in a scaffolded project |
| 3 | Module already exists |
| 4 | Template not found |
| 5 | Dependency conflict |

**Output Format:**

```
[INFO] Adding module: api/users
[INFO] Using template: fastapi-module (v2.0.1)
[INFO] Generating files...
  ✓ src/my_project/api/users.py
  ✓ src/my_project/api/models/user.py
  ✓ tests/test_api_users.py
[INFO] Updating configuration...
  ✓ Added dependencies to pyproject.toml
  ✓ Updated src/my_project/api/__init__.py
[SUCCESS] Module added successfully!
  Files created: 5
  Run tests: uv run pytest tests/test_api_users.py
```

---

### 3. scaffold update

Update project from template changes.

**Synopsis:**
```bash
scaffold update [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project-dir, -p` | path | `.` | Project root directory |
| `--dry-run` | flag | `false` | Preview changes without applying |
| `--auto-merge` | flag | `false` | Auto-merge without conflicts |
| `--strategy` | enum | `three_way` | Merge strategy (three_way, ours, theirs) |
| `--skip-conflicts` | flag | `false` | Skip files with conflicts |

**Examples:**

```bash
# Update current project
scaffold update

# Preview changes
scaffold update --dry-run

# Auto-merge (only if no conflicts)
scaffold update --auto-merge

# Use "ours" strategy (keep user changes)
scaffold update --strategy ours

# From different directory
scaffold update --project-dir ~/projects/my-app
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success (clean merge) |
| 1 | Invalid arguments |
| 2 | Not in a scaffolded project |
| 3 | No updates available |
| 4 | Conflicts detected (manual resolution required) |
| 5 | Unresolved conflict markers found |
| 10 | Network error (fetching template) |

**Output Format (clean merge):**

```
[INFO] Checking for updates...
[INFO] Current version: 1.0.0
[INFO] Latest version: 1.2.0
[INFO] Applying updates...
  ✓ pyproject.toml (merged)
  ✓ src/my_project/__init__.py (no changes)
  ✓ README.md (updated)
[SUCCESS] Project updated successfully!
  Files updated: 2
  No conflicts detected
```

**Output Format (with conflicts):**

```
[INFO] Checking for updates...
[INFO] Applying updates...
  ✓ pyproject.toml (merged)
  ⚠ src/my_project/config.py (CONFLICT)
  ✓ README.md (updated)
[WARNING] Conflicts detected in 1 file(s)
  
Conflicted files:
  - src/my_project/config.py (lines 15-23)

To resolve:
  1. Edit conflicted files
  2. Remove conflict markers (<<<<<<<, =======, >>>>>>>)
  3. Run: scaffold update --continue

[EXIT 4] Manual conflict resolution required
```

---

### 4. scaffold list

List available templates.

**Synopsis:**
```bash
scaffold list [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format, -f` | enum | `table` | Output format (table, json, yaml) |
| `--registry, -r` | string | `default` | Registry to query |
| `--type, -t` | enum | all | Filter by type (project, module, api_spec) |
| `--search, -s` | string | - | Search template names/descriptions |

**Examples:**

```bash
# List all templates (table format)
scaffold list

# JSON output
scaffold list --format json

# Filter by type
scaffold list --type module

# Search
scaffold list --search fastapi
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 10 | Network error (remote registry) |

**Output Format (table):**

```
Available Templates (default registry)

Name              Type      Version   Description
─────────────────────────────────────────────────────────────
python-cli        project   1.2.3     Python CLI application
fastapi-api       project   2.0.1     FastAPI REST API
react-app         project   3.1.0     React web application
fastapi-module    module    2.0.1     FastAPI endpoint module
docs-mkdocs       module    1.5.0     MkDocs documentation

Total: 5 templates
```

**Output Format (json):**

```json
{
  "registry": "default",
  "templates": [
    {
      "name": "python-cli",
      "type": "project",
      "version": "1.2.3",
      "description": "Python CLI application",
      "author": "template-team",
      "size_mb": 2.5,
      "variables": ["project_name", "author", "python_version"],
      "cached": true,
      "last_updated": "2025-10-15T10:30:00Z"
    }
  ],
  "count": 5
}
```

---

### 5. scaffold info

Show detailed information about a template.

**Synopsis:**
```bash
scaffold info TEMPLATE_NAME [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `TEMPLATE_NAME` | string | Yes | Template to inspect |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--version, -v` | string | `latest` | Template version |
| `--format, -f` | enum | `text` | Output format (text, json, yaml) |

**Examples:**

```bash
# Show template info
scaffold info python-cli

# Specific version
scaffold info python-cli --version 1.0.0

# JSON output
scaffold info fastapi-api --format json
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Template not found |

**Output Format:**

```
Template: python-cli
─────────────────────────────────────────────

Version:      1.2.3
Type:         project
Author:       template-team
Description:  Python CLI application with Typer and Rich
Size:         2.5 MB
Cached:       Yes
Last Updated: 2025-10-15 10:30:00

Variables:
  - project_name (string, required)
    Description: Name of the Python package
    Pattern: ^[a-z][a-z0-9_]*$

  - author (string, required)
    Description: Author name and email
    Default: Current user

  - python_version (choice, required)
    Description: Target Python version
    Choices: 3.11, 3.12, 3.13
    Default: 3.11

Dependencies:
  - Python >=3.11
  - uv >=0.4.0

Generated Files: ~47 files
  - src/{{project_name}}/*.py
  - tests/*.py
  - pyproject.toml
  - README.md
  - ...

Source: https://github.com/org/templates
```

---

### 6. scaffold cache

Manage template cache.

**Synopsis:**
```bash
scaffold cache COMMAND [OPTIONS]
```

**Subcommands:**

#### cache list
List cached templates.

```bash
scaffold cache list [--format FORMAT]
```

#### cache update
Update all cached templates.

```bash
scaffold cache update [TEMPLATE_NAME]
```

#### cache clear
Clear template cache.

```bash
scaffold cache clear [--all] [TEMPLATE_NAME]
```

**Examples:**

```bash
# List cached templates
scaffold cache list

# Update specific template
scaffold cache update python-cli

# Update all
scaffold cache update

# Clear specific template
scaffold cache clear python-cli

# Clear all cache
scaffold cache clear --all
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 10 | Network error |

---

### 7. scaffold config

Manage configuration.

**Synopsis:**
```bash
scaffold config COMMAND [KEY] [VALUE]
```

**Subcommands:**

#### config get
Get configuration value.

```bash
scaffold config get KEY
```

#### config set
Set configuration value.

```bash
scaffold config set KEY VALUE
```

#### config list
List all configuration.

```bash
scaffold config list
```

**Examples:**

```bash
# Get value
scaffold config get default_template

# Set value
scaffold config set default_template python-cli

# List all
scaffold config list
```

---

## Error Handling

### Standard Error Format

All errors follow this format:

```
[ERROR] Error message
  Context: Additional context
  Suggestion: How to fix

Exit code: N
```

### Common Errors

**Template Not Found (Exit 2):**
```
[ERROR] Template not found: invalid-template
  Available templates: python-cli, fastapi-api, react-app
  Suggestion: Run 'scaffold list' to see all templates

Exit code: 2
```

**Missing Variables (Exit 4):**
```
[ERROR] Missing required variables
  Missing: author, python_version
  Suggestion: Provide via --var or use --interactive mode

Exit code: 4
```

**Network Error (Exit 10):**
```
[ERROR] Failed to fetch template from registry
  URL: https://registry.example.com/templates/python-cli
  Reason: Connection timeout
  Suggestion: Check network connection or use cached template

Exit code: 10
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCAFFOLD_HOME` | Configuration directory | `~/.scaffold` |
| `SCAFFOLD_CACHE_DIR` | Template cache directory | `~/.scaffold/templates` |
| `SCAFFOLD_REGISTRY` | Default registry URL | `default` |
| `SCAFFOLD_NO_COLOR` | Disable colored output | `false` |
| `SCAFFOLD_VERBOSE` | Enable verbose logging | `false` |

---

## Configuration File

**Location:** `~/.scaffold/config.yml`

**Schema:**

```yaml
# Default settings
default_template: python-cli
default_output_dir: .
interactive: true

# Registries
registries:
  default:
    type: local
    path: ~/.scaffold/templates
  
  remote:
    type: git
    url: https://github.com/org/templates

# Quality checks
quality:
  enabled: true
  strict_mode: false
  tools: [ruff, mypy, pylint]

# Update behavior
updates:
  merge_strategy: three_way
  auto_merge: false
  skip_conflicts: false

# Logging
logging:
  level: info
  file: ~/.scaffold/scaffold.log
```

---

## Shell Completion

Install shell completion for your shell:

```bash
# Bash
scaffold --install-completion bash
source ~/.bashrc

# Zsh
scaffold --install-completion zsh
source ~/.zshrc

# Fish
scaffold --install-completion fish

# PowerShell
scaffold --install-completion powershell
```

After installation:

```bash
# Tab completion works
scaffold new <TAB>
scaffold add api <TAB>
scaffold info <TAB>
```

---

## Version

The CLI follows semantic versioning:

```bash
$ scaffold --version
scaffold version 1.0.0
Python 3.11.5
Jinja2 3.1.5
```

---

## Contract Guarantees

1. **Backward Compatibility**: Minor version updates preserve CLI interface
2. **Exit Codes**: Consistent exit codes across versions
3. **Output Format**: JSON/YAML output schemas remain stable
4. **Error Messages**: Error format and codes remain consistent
5. **Help Text**: `--help` always available and up-to-date
