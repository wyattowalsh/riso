# Session Management

Session state management for multi-step wizard workflows.

```{eval-rst}
.. automodule:: riso.mcp.session
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Overview

The session module provides state management for wizard workflows, enabling:

- Multi-step project configuration
- Answer validation and persistence
- Step navigation (forward/backward)
- Session lifecycle management

## Session Lifecycle

1. **Start**: Create a new wizard session
2. **Configure**: Submit answers step-by-step
3. **Navigate**: Move forward/backward through steps
4. **Generate**: Create project from completed answers
5. **Cleanup**: Cancel or cleanup session data

## Session Data

Each session maintains:

- Unique session ID
- Current step index
- All submitted answers
- Validation state
- Step completion status

## Usage

```python
from riso.mcp.session import WizardSession

# Create new session
session = WizardSession(
    project_name="My Project",
    template_variant="default"
)

# Submit answers for current step
session.submit_answers({"project_layout": "single-package"})

# Navigate
session.next_step()
session.previous_step()

# Check completion
if session.is_complete():
    # Generate project
    result = session.generate_project(destination="/path/to/project")
```

## State Persistence

Sessions can be persisted to enable:

- Resume interrupted workflows
- Multi-session management
- Session history and replay

```python
# List active sessions
sessions = list_sessions()

# Resume session
session = get_session(session_id)

# Cleanup
cleanup_session(session_id)
```
