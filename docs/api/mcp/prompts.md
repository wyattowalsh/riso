# Prompts Module

Template prompt workflows and schema management.

## Workflows

```{eval-rst}
.. automodule:: riso.mcp.prompts.workflows
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The prompts module provides utilities for working with Copier template prompts:

- Prompt schema extraction and validation
- Workflow orchestration (step definitions)
- Conditional prompt logic
- Answer validation against schemas

## Prompt Schemas

Template prompts are defined in `copier.yml` with rich schemas:

```yaml
project_name:
  type: str
  help: Human-friendly project name

project_layout:
  type: str
  choices:
    - single-package
    - monorepo
  default: single-package

quality_profile:
  type: str
  choices:
    - standard
    - strict
  when: "{{ project_layout == 'single-package' }}"
```

## Workflow Definition

Prompts are organized into logical steps for wizard workflows:

```python
from riso.mcp.prompts.workflows import get_workflow_steps

# Get step definitions
steps = get_workflow_steps()

# Each step contains:
# - step_id: Unique identifier
# - title: Display title
# - description: Step description
# - prompts: List of prompt names for this step
# - conditions: When this step should be shown
```

## Validation

Answers are validated against prompt schemas:

```python
from riso.mcp.prompts.workflows import validate_answers

errors = validate_answers(
    answers={
        "project_name": "My Project",
        "project_layout": "invalid-choice"
    },
    prompts=prompt_schemas
)

if errors:
    print("Validation errors:", errors)
```

## Conditional Logic

Prompts can be conditionally shown based on previous answers:

```python
from riso.mcp.prompts.workflows import should_show_prompt

# Check if prompt should be shown
show = should_show_prompt(
    prompt_name="quality_profile",
    answers={"project_layout": "single-package"},
    prompt_schema=prompts["quality_profile"]
)
```
