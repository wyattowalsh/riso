# Quickstart: Code Generation and Scaffolding Tools

**Feature**: 015-codegen-scaffolding-tools  
**Date**: 2025-11-02  
**For**: Developers implementing this feature

## Overview

This quickstart provides step-by-step instructions for implementing the code generation and scaffolding tools feature. Follow these phases in order.

## Prerequisites

- Python 3.11+
- uv package manager
- Git
- Basic understanding of Jinja2 templates
- Familiarity with Typer CLI framework

## Phase 0: Environment Setup (15 minutes)

### 1. Install Dependencies

```bash
cd /workspaces/riso
uv add jinja2>=3.1.5 typer>=0.20.0 rich>=13.0.0 merge3>=0.0.13 gitpython>=3.1.40
uv add --dev pytest>=7.4.0 pytest-cov>=4.1.0 mypy>=1.7.0
```

### 2. Create Directory Structure

```bash
# From repository root
mkdir -p template/files/python/src/{{package_name}}/codegen/{templates,generation,updates,quality}
mkdir -p template/files/python/tests/codegen/{test_templates,test_generation,test_updates,fixtures}
mkdir -p template/files/shared/docs/modules
```

### 3. Verify Setup

```bash
uv run python -c "import jinja2, typer, rich, merge3; print('All dependencies OK')"
```

## Phase 1: Core Data Models (2 hours)

### 1. Create Base Models

Create `template/files/python/src/{{package_name}}/codegen/models.py`:

```python
"""Data models for code generation system."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, validator


class TemplateType(str, Enum):
    """Type of template."""
    PROJECT = "project"
    MODULE = "module"
    API_SPEC = "api_spec"


class VariableType(str, Enum):
    """Variable data type."""
    STRING = "string"
    INT = "int"
    BOOL = "bool"
    CHOICE = "choice"


class VariableDefinition(BaseModel):
    """Template variable definition."""
    name: str = Field(..., pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    type: VariableType
    required: bool = True
    default: str | int | bool | None = None
    description: str = Field(..., min_length=10, max_length=200)
    pattern: str | None = None
    choices: list[str] | None = None
    prompt_message: str | None = None

    @validator("choices")
    def validate_choices(cls, v, values):
        if values.get("type") == VariableType.CHOICE:
            if not v or len(v) < 2:
                raise ValueError("Choice type requires at least 2 choices")
        return v


class Template(BaseModel):
    """Template metadata."""
    name: str = Field(..., pattern=r"^[a-z][a-z0-9-]*$", min_length=3, max_length=50)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str = Field(..., min_length=10, max_length=200)
    author: str | None = None
    template_type: TemplateType = TemplateType.PROJECT
    source_url: str | None = None
    local_path: Path
    size_bytes: int = Field(..., le=104857600)  # 100MB max
    variables: dict[str, VariableDefinition]
    created_at: datetime
    updated_at: datetime


class Project(BaseModel):
    """Generated project."""
    name: str
    root_path: Path
    template_name: str
    template_version: str
    variables: dict[str, Any]
    generated_files: list[Path]
    metadata_file: Path
    created_at: datetime
    last_updated_at: datetime | None = None
```

### 2. Write Tests First (TDD)

Create `template/files/python/tests/codegen/test_models.py`:

```python
"""Tests for data models."""

import pytest
from pydantic import ValidationError

from {{package_name}}.codegen.models import (
    VariableDefinition,
    VariableType,
    Template,
    TemplateType,
)


def test_variable_definition_string_type():
    """Test string variable definition."""
    var = VariableDefinition(
        name="project_name",
        type=VariableType.STRING,
        description="Name of the project",
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    assert var.name == "project_name"
    assert var.type == VariableType.STRING
    assert var.required is True


def test_variable_definition_choice_requires_choices():
    """Test that choice type requires choices list."""
    with pytest.raises(ValidationError):
        VariableDefinition(
            name="version",
            type=VariableType.CHOICE,
            description="Python version",
            choices=None,  # Should fail
        )


def test_template_name_validation():
    """Test template name must follow pattern."""
    with pytest.raises(ValidationError):
        Template(
            name="Invalid Name",  # Spaces not allowed
            version="1.0.0",
            description="Test template",
            local_path=Path("/tmp/template"),
            size_bytes=1000,
            variables={},
        )
```

### 3. Run Tests (Should Pass)

```bash
uv run pytest template/files/python/tests/codegen/test_models.py -v
```

## Phase 2: Template Loader (3 hours)

### 1. Implement Template Loader

Create `template/files/python/src/{{package_name}}/codegen/templates/loader.py`:

```python
"""Template loading and discovery."""

from __future__ import annotations

from pathlib import Path
import yaml

from ..models import Template, TemplateType, VariableDefinition


class TemplateLoader:
    """Load and validate templates."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def load_template(self, template_path: Path) -> Template:
        """Load template from directory."""
        metadata_file = template_path / "template.yml"
        if not metadata_file.exists():
            raise FileNotFoundError(f"template.yml not found in {template_path}")
        
        with open(metadata_file) as f:
            data = yaml.safe_load(f)
        
        # Parse variables
        variables = {}
        for name, var_data in data.get("variables", {}).items():
            variables[name] = VariableDefinition(
                name=name,
                **var_data
            )
        
        # Calculate size
        size_bytes = sum(
            f.stat().st_size
            for f in template_path.rglob("*")
            if f.is_file()
        )
        
        return Template(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data.get("author"),
            template_type=TemplateType(data.get("template_type", "project")),
            source_url=data.get("source_url"),
            local_path=template_path,
            size_bytes=size_bytes,
            variables=variables,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
```

### 2. Write Tests

Create test fixtures and integration tests for template loading.

### 3. Validate Against Research

Ensure implementation follows research.md guidelines for:
- Jinja2 configuration
- File permission handling
- Size validation (100MB limit)

## Phase 3: CLI Implementation (4 hours)

### 1. Create CLI Entry Point

Create `template/files/python/src/{{package_name}}/codegen/cli.py`:

```python
"""CLI commands for scaffolding tool."""

import typer
from pathlib import Path
from rich.console import Console

app = typer.Typer(
    name="scaffold",
    help="Code generation and scaffolding tool",
    add_completion=True
)
console = Console()


@app.command()
def new(
    project_name: str = typer.Argument(..., help="Project name"),
    template: str = typer.Option("default", "--template", "-t"),
    output_dir: Path = typer.Option(Path.cwd(), "--output", "-o"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Create a new project from template."""
    console.print(f"[cyan]Creating project:[/cyan] {project_name}")
    # Implementation in next phase


@app.command()
def add(
    module_type: str = typer.Argument(...),
    module_name: str = typer.Argument(...),
):
    """Add a feature module to existing project."""
    console.print(f"[cyan]Adding {module_type}:[/cyan] {module_name}")
    # Implementation in next phase


if __name__ == "__main__":
    app()
```

### 2. Test CLI Interface

```bash
uv run python -m {{package_name}}.codegen.cli --help
uv run python -m {{package_name}}.codegen.cli new --help
```

## Phase 4: Generation Engine (5 hours)

### 1. Implement Jinja2 Generator

Follow research.md patterns for:
- Environment configuration
- Variable substitution
- Template inheritance
- Bytecode caching

### 2. Implement File Operations

- Atomic file generation (all-or-nothing)
- Permission preservation
- Binary file handling

### 3. Quality Validation

Implement warning-based quality checks (from clarifications).

## Phase 5: Merge Support (4 hours)

### 1. Implement Three-Way Merge

Use `merge3` library as specified in research.md.

### 2. Conflict Detection

Implement conflict marker insertion and validation.

### 3. Test Merge Scenarios

- Clean merge (no conflicts)
- Simple conflicts (same lines)
- Complex conflicts (overlapping regions)

## Phase 6: Integration Tests (3 hours)

### 1. End-to-End Tests

```python
def test_create_project_from_template(tmp_path):
    """Test full project generation flow."""
    # Given a template
    # When generating a project
    # Then all files created
    # And quality checks pass
    pass


def test_add_module_to_project(tmp_path):
    """Test adding module to existing project."""
    # Given an existing project
    # When adding a module
    # Then module files created
    # And config updated
    pass


def test_update_project_with_conflicts(tmp_path):
    """Test project update with merge conflicts."""
    # Given a project with user modifications
    # When template updates
    # Then conflicts marked
    # And user can resolve
    pass
```

### 2. Run Full Test Suite

```bash
uv run pytest template/files/python/tests/codegen/ -v --cov={{package_name}}.codegen
```

## Phase 7: Documentation (2 hours)

### 1. Write User Documentation

Create `template/files/shared/docs/modules/codegen-scaffolding.md.jinja`.

### 2. Add Examples

Include working examples for:
- Creating projects
- Adding modules
- Customizing templates
- Updating projects

## Phase 8: Quality Gates (1 hour)

### 1. Run Quality Suite

```bash
cd samples/default/render
QUALITY_PROFILE=standard make quality
```

### 2. Fix Issues

Address any ruff/mypy/pylint violations.

## Phase 9: Integration with Riso Template (2 hours)

### 1. Add Module Flag

Update `template/copier.yml`:

```yaml
codegen_module:
  type: str
  help: "Enable code generation and scaffolding tools?"
  default: disabled
  choices:
    - enabled
    - disabled
```

### 2. Conditional File Generation

Wrap all codegen files in Jinja2 conditionals:

```jinja2
{% if codegen_module == 'enabled' %}
{# Template content #}
{% endif %}
```

### 3. Test Rendering

```bash
./scripts/render-samples.sh
cd samples/default/render
# Verify module appears when enabled
```

## Validation Checklist

- [ ] All tests passing (80%+ coverage)
- [ ] Quality checks passing (ruff, mypy, pylint)
- [ ] CLI commands functional
- [ ] Documentation complete
- [ ] Spec requirements met (FR-001 through FR-024)
- [ ] Success criteria achievable (SC-001 through SC-010)
- [ ] Constitution principles followed
- [ ] Integration with Riso template working

## Next Steps

After completing this quickstart:

1. Review implementation against spec.md
2. Run `/speckit.tasks` to get detailed task breakdown
3. Begin implementation following TDD approach
4. Create PR when ready for review

## Troubleshooting

**Import errors:**
```bash
uv sync  # Re-sync dependencies
```

**Test failures:**
```bash
uv run pytest -v --tb=short  # Verbose output with short tracebacks
```

**Quality check failures:**
```bash
uv run ruff check --fix .  # Auto-fix ruff issues
uv run mypy --show-error-codes .  # Show mypy error codes
```

## Time Estimates

| Phase | Estimated Time | Cumulative |
|-------|---------------|------------|
| Environment Setup | 15 min | 15 min |
| Core Data Models | 2 hours | 2h 15m |
| Template Loader | 3 hours | 5h 15m |
| CLI Implementation | 4 hours | 9h 15m |
| Generation Engine | 5 hours | 14h 15m |
| Merge Support | 4 hours | 18h 15m |
| Integration Tests | 3 hours | 21h 15m |
| Documentation | 2 hours | 23h 15m |
| Quality Gates | 1 hour | 24h 15m |
| Riso Integration | 2 hours | 26h 15m |
| **Total** | **~26 hours** | **~3-4 days** |

This estimate assumes focused development time with TDD approach.
