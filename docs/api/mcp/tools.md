# MCP Tools

AI-accessible tools for project scaffolding and template management.

## Copier API Tools

Direct access to Copier templating operations.

```{eval-rst}
.. automodule:: riso.mcp.tools.copier_api
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Wizard Tools

Interactive guided project creation workflow.

```{eval-rst}
.. automodule:: riso.mcp.tools.wizard
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Tool Categories

### Project Creation

- {py:func}`~riso.mcp.tools.copier_api.copier_copy` - Generate a new project from the Riso template
- {py:func}`~riso.mcp.tools.wizard.wizard_start` - Start an interactive wizard session
- {py:func}`~riso.mcp.tools.wizard.wizard_step` - Submit answers for current wizard step

### Project Updates

- {py:func}`~riso.mcp.tools.copier_api.copier_update` - Update an existing project with latest template changes
- {py:func}`~riso.mcp.tools.copier_api.copier_recopy` - Regenerate a project from scratch

### Template Discovery

- {py:func}`~riso.mcp.tools.copier_api.list_template_variants` - List available sample configurations
- {py:func}`~riso.mcp.tools.copier_api.get_prompts` - Get template prompt schemas

### Validation

- {py:func}`~riso.mcp.tools.copier_api.validate_template_answers` - Validate answers against template schema

### Session Management

- {py:func}`~riso.mcp.tools.wizard.wizard_status` - Get current wizard session state
- {py:func}`~riso.mcp.tools.wizard.wizard_back` - Go back to previous wizard step
- {py:func}`~riso.mcp.tools.wizard.wizard_generate` - Generate project from completed wizard
- {py:func}`~riso.mcp.tools.wizard.wizard_cancel` - Cancel and cleanup wizard session

## Usage Examples

### Creating a Project

```python
# Using Copier API directly
result = await copier_copy(
    destination="/path/to/project",
    answers={
        "project_name": "My Project",
        "project_layout": "single-package",
        "quality_profile": "standard"
    }
)

# Using Wizard workflow
session = await wizard_start(project_name="My Project")
await wizard_step(
    session_id=session["session_id"],
    answers={"project_layout": "single-package"}
)
```

### Updating a Project

```python
result = await copier_update(
    destination="/path/to/existing/project",
    skip_answered=True
)
```
