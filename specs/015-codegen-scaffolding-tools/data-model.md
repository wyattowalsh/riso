# Data Model: Code Generation and Scaffolding Tools

**Feature**: 015-codegen-scaffolding-tools  
**Date**: 2025-11-02  
**Status**: Complete

## Overview

This document defines the data structures and relationships for the code generation and scaffolding system. The model supports template-based project generation, module addition, custom templates, and template updates with conflict resolution.

## Core Entities

### 1. Template

Represents a code generation template that can create projects or modules.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `name` | `str` | Yes | Unique template identifier | Lowercase, alphanumeric + hyphens, 3-50 chars |
| `version` | `str` | Yes | Semantic version | Format: `major.minor.patch` |
| `description` | `str` | Yes | Human-readable description | 10-200 chars |
| `author` | `str` | No | Template author/maintainer | Email or name |
| `template_type` | `TemplateType` | Yes | Type of template | Enum: `project`, `module`, `api_spec` |
| `source_url` | `str` | No | Remote repository URL | Valid Git URL or HTTP(S) |
| `local_path` | `Path` | Yes | Local filesystem path | Absolute path to template directory |
| `size_bytes` | `int` | Yes | Total size in bytes | Max 104,857,600 (100MB) |
| `variables` | `dict[str, VariableDefinition]` | Yes | Template variables | At least one variable |
| `file_patterns` | `list[FilePattern]` | Yes | Files to generate | At least one pattern |
| `hooks` | `HookConfiguration` | No | Pre/post generation hooks | Optional execution scripts |
| `dependencies` | `list[Dependency]` | No | Required tools/packages | Python, Node.js versions, etc. |
| `metadata` | `dict[str, Any]` | No | Additional metadata | Tags, categories, etc. |
| `created_at` | `datetime` | Yes | Template creation time | ISO 8601 format |
| `updated_at` | `datetime` | Yes | Last update time | ISO 8601 format |

**Relationships:**
- One Template can generate many Projects (1:N)
- One Template can generate many Modules (1:N)
- Template belongs to zero or one Registry (N:1)

**State Transitions:**
1. `discovered` → Template found but not validated
2. `validating` → Running syntax and size checks
3. `valid` → Passed all validations, ready to use
4. `invalid` → Failed validation, cannot be used
5. `cached` → Downloaded and stored locally
6. `stale` → Remote version available

**Invariants:**
- `name` must be unique within a registry
- `size_bytes` ≤ 100MB (104,857,600 bytes)
- `version` must follow semantic versioning
- At least one `VariableDefinition` required
- `local_path` must exist and be readable

### 2. Project

Represents a generated project created from a template.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `name` | `str` | Yes | Project name | Valid Python package name |
| `root_path` | `Path` | Yes | Project root directory | Absolute path, must not exist before generation |
| `template_name` | `str` | Yes | Source template identifier | Must reference existing template |
| `template_version` | `str` | Yes | Template version used | Semantic version |
| `variables` | `dict[str, str]` | Yes | Variable values used | All required variables provided |
| `generated_files` | `list[Path]` | Yes | List of generated files | Relative paths from root |
| `metadata_file` | `Path` | Yes | Path to .scaffold-metadata.json | Always `.scaffold-metadata.json` at root |
| `custom_modifications` | `list[ModificationRecord]` | No | Tracked user changes | For update conflict detection |
| `modules` | `list[Module]` | No | Added feature modules | Modules added post-generation |
| `quality_status` | `QualityStatus` | Yes | Quality check results | Pass/warn/fail |
| `created_at` | `datetime` | Yes | Generation timestamp | ISO 8601 format |
| `last_updated_at` | `datetime` | No | Last update timestamp | ISO 8601 format |

**Relationships:**
- One Project generated from one Template (N:1)
- One Project contains many Modules (1:N)
- One Project has one MetadataFile (1:1)

**State Transitions:**
1. `generating` → Files being created
2. `generated` → All files created, tests pass
3. `modified` → User has made changes
4. `updating` → Applying template updates
5. `conflicted` → Merge conflicts exist
6. `up_to_date` → No updates available

**Invariants:**
- `root_path` must be writable
- `metadata_file` always exists at `root_path / ".scaffold-metadata.json"`
- `template_version` must be valid semantic version
- All `generated_files` must exist under `root_path`

### 3. Module

Represents a feature module added to an existing project.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `name` | `str` | Yes | Module identifier | Valid Python module name |
| `module_type` | `ModuleType` | Yes | Type of module | Enum: `api`, `cli`, `docs`, `auth`, etc. |
| `template_name` | `str` | Yes | Source template for module | Must reference module template |
| `template_version` | `str` | Yes | Template version used | Semantic version |
| `variables` | `dict[str, str]` | Yes | Module-specific variables | All required variables |
| `generated_files` | `list[Path]` | Yes | Files created for module | Relative paths |
| `modified_files` | `list[Path]` | No | Existing files updated | Config files, imports, etc. |
| `dependencies_added` | `list[str]` | No | New package dependencies | Added to pyproject.toml, package.json |
| `created_at` | `datetime` | Yes | Module addition timestamp | ISO 8601 format |

**Relationships:**
- One Module belongs to one Project (N:1)
- One Module generated from one Template (N:1)

**State Transitions:**
1. `adding` → Files being generated
2. `added` → Successfully integrated
3. `failed` → Addition failed, rolled back

**Invariants:**
- `name` must be unique within parent project
- All `generated_files` must not already exist (unless overwrite confirmed)
- `module_type` must be supported by template

### 4. VariableDefinition

Defines a template variable that users must provide.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `name` | `str` | Yes | Variable identifier | Valid Python identifier |
| `type` | `VariableType` | Yes | Data type | Enum: `string`, `int`, `bool`, `choice` |
| `required` | `bool` | Yes | Must be provided | Default: `true` |
| `default` | `str \| None` | No | Default value | Must match type |
| `description` | `str` | Yes | Help text for users | 10-200 chars |
| `pattern` | `str \| None` | No | Regex validation pattern | Valid regex |
| `choices` | `list[str] \| None` | No | Valid choices (for choice type) | 2-20 choices |
| `prompt_message` | `str \| None` | No | Interactive prompt text | Override default |

**Validation Rules:**
- If `type=choice`, `choices` must be provided
- If `default` provided, must match `type` and `pattern`
- `pattern` compiled and validated if provided
- `name` must be valid Jinja2 variable name

**Invariants:**
- `choices` required when `type=choice`
- `default` must be in `choices` if both provided

### 5. Generator

The engine that processes templates and produces output.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `template` | `Template` | Yes | Template to render | Must be valid template |
| `variables` | `dict[str, str]` | Yes | Variable values | All required variables |
| `output_dir` | `Path` | Yes | Target directory | Must exist and be writable |
| `dry_run` | `bool` | No | Preview mode (no files created) | Default: `false` |
| `overwrite_mode` | `OverwriteMode` | No | File conflict handling | Enum: `skip`, `overwrite`, `merge`, `prompt` |
| `quality_check` | `bool` | No | Run quality validation | Default: `true` |
| `jinja_env` | `Environment` | Yes | Jinja2 environment | Configured for code generation |

**Methods:**
- `validate_input()` → Validate variables and output_dir
- `render_template()` → Generate all files
- `apply_hooks()` → Execute pre/post hooks
- `check_quality()` → Run quality validation
- `generate_metadata()` → Create .scaffold-metadata.json

**State Transitions:**
1. `initialized` → Generator created
2. `validating` → Checking inputs
3. `rendering` → Generating files
4. `executing_hooks` → Running pre/post scripts
5. `checking_quality` → Running validation
6. `completed` → Generation successful
7. `failed` → Generation failed, rolled back

### 6. TemplateRegistry

Repository or catalog of available templates.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `name` | `str` | Yes | Registry identifier | Unique name |
| `registry_type` | `RegistryType` | Yes | Storage type | Enum: `local`, `git`, `http`, `custom` |
| `location` | `str` | Yes | Registry location | Path, URL, or URI |
| `templates` | `list[Template]` | Yes | Available templates | At least one template |
| `last_sync` | `datetime \| None` | No | Last synchronization time | ISO 8601 format |
| `cache_dir` | `Path` | Yes | Local cache directory | Must be writable |

**Methods:**
- `list_templates()` → Get all available templates
- `get_template(name: str)` → Fetch specific template
- `sync()` → Update from remote source
- `add_template(template: Template)` → Add new template
- `remove_template(name: str)` → Remove template

**Invariants:**
- `name` must be unique across all registries
- `cache_dir` must exist
- All `templates` must have unique names

### 7. MergeResult

Represents the result of a three-way merge operation.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `file_path` | `Path` | Yes | File being merged | Relative path |
| `merged_content` | `str` | Yes | Merged file content | May contain conflict markers |
| `has_conflicts` | `bool` | Yes | Whether conflicts exist | True if markers present |
| `conflict_count` | `int` | Yes | Number of conflicts | ≥ 0 |
| `conflict_regions` | `list[ConflictRegion]` | No | Conflict locations | Line ranges |
| `merge_strategy` | `MergeStrategy` | Yes | Strategy used | Enum: `three_way`, `ours`, `theirs` |

**Relationships:**
- One MergeResult per updated file (1:1)
- Multiple MergeResults per UpdateOperation (N:1)

**Invariants:**
- `has_conflicts = true` iff `conflict_count > 0`
- `conflict_regions` length must equal `conflict_count`

### 8. ConflictRegion

Represents a single merge conflict region.

**Attributes:**

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `start_line` | `int` | Yes | Starting line number (1-indexed) | > 0 |
| `end_line` | `int` | Yes | Ending line number (1-indexed) | ≥ start_line |
| `user_content` | `str` | Yes | User's version | Lines between start and separator |
| `template_content` | `str` | Yes | Template's version | Lines between separator and end |
| `base_content` | `str \| None` | No | Original version (diff3) | Optional base reference |

**Invariants:**
- `end_line >= start_line`
- At least one of `user_content` or `template_content` non-empty

## Supporting Types

### Enums

```python
class TemplateType(Enum):
    PROJECT = "project"      # Full project scaffolding
    MODULE = "module"        # Feature module
    API_SPEC = "api_spec"    # Generated from OpenAPI/GraphQL

class ModuleType(Enum):
    API = "api"
    CLI = "cli"
    DOCS = "docs"
    AUTH = "auth"
    DATABASE = "database"
    WEBSOCKET = "websocket"
    CUSTOM = "custom"

class VariableType(Enum):
    STRING = "string"
    INT = "int"
    BOOL = "bool"
    CHOICE = "choice"

class OverwriteMode(Enum):
    SKIP = "skip"            # Skip existing files
    OVERWRITE = "overwrite"  # Replace existing files
    MERGE = "merge"          # Three-way merge
    PROMPT = "prompt"        # Ask user for each file

class RegistryType(Enum):
    LOCAL = "local"          # Filesystem directory
    GIT = "git"              # Git repository
    HTTP = "http"            # HTTP(S) URL
    CUSTOM = "custom"        # Custom protocol

class MergeStrategy(Enum):
    THREE_WAY = "three_way"  # Standard three-way merge
    OURS = "ours"            # Keep user version
    THEIRS = "theirs"        # Keep template version
    UNION = "union"          # Combine both

class QualityStatus(Enum):
    PASS = "pass"            # All checks passed
    WARN = "warn"            # Warnings present, non-blocking
    FAIL = "fail"            # Critical errors found
```

### Value Objects

```python
class FilePattern:
    """Pattern for files to generate from template."""
    pattern: str              # Glob pattern (e.g., "src/**/*.py.jinja")
    exclude: list[str]        # Exclusion patterns
    preserve_permissions: bool # Copy file mode bits

class Dependency:
    """Required tool or package for template."""
    name: str                 # Tool name (e.g., "python", "node")
    version_constraint: str   # Version spec (e.g., ">=3.11,<4.0")
    optional: bool            # Can be skipped

class HookConfiguration:
    """Pre/post generation hook scripts."""
    pre_gen: list[str]        # Scripts before generation
    post_gen: list[str]       # Scripts after generation
    timeout_seconds: int      # Max execution time
    env_vars: dict[str, str]  # Environment variables

class ModificationRecord:
    """Tracks user modification for conflict detection."""
    file_path: Path           # Modified file
    original_hash: str        # SHA256 of original
    modified_hash: str        # SHA256 after modification
    modified_at: datetime     # Modification timestamp
```

## Data Flow

### 1. Project Generation Flow

```
User Input → Variable Collection → Template Loading → 
Variable Validation → File Generation → Hook Execution → 
Quality Validation → Metadata Creation → Project Ready
```

**Data Transformations:**
1. User provides: `project_name`, `template`, CLI args
2. System collects: All required `VariableDefinition` values
3. System validates: Variables against patterns/choices
4. Template + Variables → Generator
5. Generator renders: Jinja2 templates with variables
6. System creates: All files in `generated_files`
7. System writes: `.scaffold-metadata.json` with metadata
8. System runs: Quality checks (optional warnings)
9. Result: `Project` entity with status

### 2. Module Addition Flow

```
Project Detection → Module Template Loading → 
Variable Collection → File Generation → 
Dependency Update → Import Update → 
Quality Validation → Module Integrated
```

**Data Transformations:**
1. System locates: Existing project via `.scaffold-metadata.json`
2. User selects: `module_type` and provides `name`
3. System loads: Module template
4. System collects: Module-specific variables
5. System generates: Module files
6. System updates: Config files (pyproject.toml, etc.)
7. System adds: Import statements if needed
8. Result: `Module` entity added to `Project.modules`

### 3. Template Update Flow

```
Version Check → Base Retrieval → User File Read → 
Template Fetch → Three-Way Merge → Conflict Detection → 
User Resolution → Validation → Update Complete
```

**Data Transformations:**
1. System reads: Current `template_version` from metadata
2. System fetches: Latest template version
3. System retrieves: Original template (base) from cache
4. System reads: User's current file (with modifications)
5. System performs: Three-way merge (base, user, template)
6. System detects: Conflicts via `merge3` library
7. If conflicts: Insert markers, prompt user to resolve
8. System validates: No unresolved markers remain
9. Result: `MergeResult` per file, updated `Project`

## Data Validation Rules

### Cross-Entity Validation

1. **Template → Project**:
   - `Project.template_version` must match a valid `Template.version`
   - All `Project.variables` must satisfy `Template.variables` definitions

2. **Project → Module**:
   - `Module.name` must be unique within `Project.modules`
   - `Module.generated_files` must not conflict with existing files

3. **Template → Module**:
   - `Module.template_name` must reference a template with `template_type=module`
   - All `Module.variables` must satisfy module template's variable definitions

### Data Integrity

1. **Filesystem Consistency**:
   - All `Path` fields must be valid and accessible
   - `generated_files` must exist on disk
   - `.scaffold-metadata.json` must be present and parseable

2. **Version Consistency**:
   - All `version` fields must follow semantic versioning
   - `template_version` in projects must match actual template when generated

3. **Variable Consistency**:
   - All required variables must have values
   - Variable values must match defined types and patterns
   - Choice variables must select from valid choices

## Persistence

### .scaffold-metadata.json Schema

```json
{
  "$schema": "https://scaffold.dev/schema/v1/metadata.json",
  "version": "1.0.0",
  "project": {
    "name": "my-project",
    "template": {
      "name": "python-cli",
      "version": "1.2.3",
      "source_url": "https://github.com/org/templates"
    },
    "variables": {
      "project_name": "my_project",
      "author": "Jane Developer",
      "python_version": "3.11"
    },
    "generated_at": "2025-11-02T10:30:00Z",
    "last_updated_at": "2025-11-02T14:15:00Z"
  },
  "modules": [
    {
      "name": "api",
      "type": "fastapi",
      "template": {
        "name": "fastapi-module",
        "version": "2.0.1"
      },
      "added_at": "2025-11-02T14:15:00Z"
    }
  ],
  "quality_status": {
    "last_check": "2025-11-02T10:30:00Z",
    "status": "warn",
    "warnings": ["Unused import in src/main.py:5"]
  }
}
```

### Template Cache Structure

```
~/.scaffold/
├── templates/
│   ├── python-cli/
│   │   ├── template.yml          # Template metadata
│   │   ├── cookiecutter.json     # Variable definitions
│   │   ├── {{cookiecutter}}/     # Template files
│   │   └── hooks/                # Pre/post generation scripts
│   └── fastapi-api/
└── cache/
    └── versions/
        └── python-cli/
            ├── 1.0.0/            # Cached base versions for updates
            └── 1.2.3/
```

## Entity Relationships Diagram

```
┌──────────────┐
│   Registry   │
└──────┬───────┘
       │ 1:N
       │
       ▼
┌──────────────┐         ┌──────────────┐
│   Template   │────────►│VariableDefn  │
└──────┬───────┘   1:N   └──────────────┘
       │ 1:N
       │
       ▼
┌──────────────┐         ┌──────────────┐
│   Project    │────────►│   Module     │
└──────┬───────┘   1:N   └──────────────┘
       │ 1:1
       │
       ▼
┌──────────────┐
│  Metadata    │
│    File      │
└──────────────┘

Update Flow:
┌──────────────┐         ┌──────────────┐
│   Project    │────────►│ MergeResult  │
│ (base + user)│   1:N   └──────┬───────┘
└──────────────┘                │ 1:N
                                 │
                                 ▼
                          ┌──────────────┐
                          │ConflictRegion│
                          └──────────────┘
```

## Summary

This data model supports all user stories from the specification:
- **US1 (Generate Project)**: Template + Variables → Project
- **US2 (Add Module)**: Project + Module Template → Enhanced Project
- **US3 (Custom Templates)**: Custom Template → Registry → Generation
- **US4 (Update Project)**: Base + User + Template → MergeResult
- **US5 (API Spec)**: API Spec → Template → Generated Code

All entities include proper validation rules, state transitions, and invariants to ensure data consistency and reliable operation.
