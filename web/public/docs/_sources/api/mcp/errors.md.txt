# Error Types

Custom exception types for MCP server operations.

```{eval-rst}
.. automodule:: riso.mcp.errors
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Exception Hierarchy

```
MCPError (base)
├── ConfigurationError
├── ValidationError
├── SessionError
│   ├── SessionNotFoundError
│   ├── SessionExpiredError
│   └── SessionStateError
├── TemplateError
│   ├── TemplateNotFoundError
│   ├── TemplateRenderError
│   └── AnswersValidationError
└── ToolExecutionError
    ├── CopierExecutionError
    ├── WizardError
    └── ResourceNotFoundError
```

## Common Exceptions

### Configuration Errors

- {py:exc}`~riso.mcp.errors.ConfigurationError` - Invalid server configuration
- {py:exc}`~riso.mcp.errors.ValidationError` - Invalid input parameters

### Session Errors

- {py:exc}`~riso.mcp.errors.SessionNotFoundError` - Session ID not found
- {py:exc}`~riso.mcp.errors.SessionExpiredError` - Session has expired
- {py:exc}`~riso.mcp.errors.SessionStateError` - Invalid session state transition

### Template Errors

- {py:exc}`~riso.mcp.errors.TemplateNotFoundError` - Template not found
- {py:exc}`~riso.mcp.errors.TemplateRenderError` - Template rendering failed
- {py:exc}`~riso.mcp.errors.AnswersValidationError` - Invalid template answers

### Tool Execution Errors

- {py:exc}`~riso.mcp.errors.CopierExecutionError` - Copier operation failed
- {py:exc}`~riso.mcp.errors.WizardError` - Wizard workflow error
- {py:exc}`~riso.mcp.errors.ResourceNotFoundError` - MCP resource not found

## Error Handling

All exceptions include:

- Human-readable error messages
- Error codes for programmatic handling
- Context information (session ID, file paths, etc.)
- Suggestions for resolution

```python
from riso.mcp.errors import SessionNotFoundError, TemplateRenderError

try:
    session = get_session(session_id)
except SessionNotFoundError as e:
    print(f"Session not found: {e.session_id}")
    print(f"Suggestion: {e.suggestion}")

try:
    result = render_template(answers)
except TemplateRenderError as e:
    print(f"Render failed: {e}")
    print(f"Template: {e.template_path}")
    print(f"Error: {e.original_error}")
```

## Custom Error Handlers

Tools can register custom error handlers:

```python
from riso.mcp.errors import register_error_handler, MCPError

@register_error_handler(TemplateRenderError)
def handle_render_error(error: TemplateRenderError) -> dict:
    return {
        "success": False,
        "error": str(error),
        "recovery": "Check template syntax and try again"
    }
```
