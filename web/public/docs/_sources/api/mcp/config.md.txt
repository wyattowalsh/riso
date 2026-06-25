# Configuration

Server configuration and settings management.

```{eval-rst}
.. automodule:: riso.mcp.config
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Configuration Sources

Configuration is loaded from multiple sources in order of precedence:

1. Environment variables
2. Configuration files (`.env`, `mcp.json`)
3. Default values

## Environment Variables

### Server Settings

- `RISO_MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `RISO_MCP_LOG_FILE` - Log file path (optional)
- `RISO_MCP_SESSION_DIR` - Directory for session persistence

### Template Settings

- `RISO_TEMPLATE_DIR` - Path to template directory (default: repo root)
- `RISO_SAMPLES_DIR` - Path to samples directory
- `RISO_VCS_REF` - Git ref to use for template (default: HEAD)

### Behavior Settings

- `RISO_MCP_AUTO_SAVE` - Auto-save wizard sessions (default: true)
- `RISO_MCP_CLEANUP_ON_EXIT` - Cleanup sessions on server exit
- `RISO_MCP_MAX_SESSIONS` - Maximum concurrent sessions

## Configuration File

The server can be configured via `mcp.json`:

```json
{
  "server": {
    "log_level": "INFO",
    "session_dir": "/tmp/riso-mcp"
  },
  "template": {
    "vcs_ref": "main",
    "auto_load_samples": true
  },
  "wizard": {
    "auto_save": true,
    "max_sessions": 10
  }
}
```

## Usage

```python
from riso.mcp.config import get_config, Config

# Get current configuration
config = get_config()

# Access settings
log_level = config.log_level
template_dir = config.template_dir

# Create custom configuration
custom_config = Config(
    log_level="DEBUG",
    session_dir="/custom/path"
)
```

## Validation

Configuration values are validated on load:

- Paths must exist or be creatable
- Log levels must be valid
- Numeric limits are enforced

Invalid configuration triggers a {py:exc}`~riso.mcp.errors.ConfigurationError`.
