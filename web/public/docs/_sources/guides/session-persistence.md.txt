# Session Persistence

The Riso MCP server supports session persistence to maintain wizard sessions across server restarts. This guide covers the available persistence backends and how to configure them.

## Overview

By default, wizard sessions are stored in memory only and are lost when the server stops. Session persistence allows you to:

- Restore active sessions after server restarts
- Share sessions across multiple server instances (SQLite only)
- Debug session state by inspecting persistent storage
- Export and import sessions for backup or migration

## Persistence Backends

### Memory Store (Default)

No persistence - sessions are stored in memory only.

```toml
# riso-mcp.toml
[wizard]
persistence_backend = "memory"
```

**Use cases:**
- Development and testing
- When sessions are short-lived
- Single-use workflows

### JSON File Store

Stores each session as a separate JSON file in `~/.riso/sessions/` (or a custom path).

```toml
# riso-mcp.toml
[wizard]
persistence_backend = "json"
persistence_path = "~/.riso/sessions"  # Optional, this is the default
```

**Advantages:**
- Human-readable format
- Easy to inspect and debug
- Simple backup (just copy the directory)

**Use cases:**
- Development and debugging
- Small number of concurrent sessions
- When you need to inspect session state

### SQLite Store

Stores all sessions in a single SQLite database at `~/.riso/sessions.db` (or a custom path).

```toml
# riso-mcp.toml
[wizard]
persistence_backend = "sqlite"
persistence_path = "~/.riso"  # Database will be at ~/.riso/sessions.db
```

**Advantages:**
- Production-ready with ACID guarantees
- Efficient for many concurrent sessions
- Can be shared across multiple server instances
- Query sessions programmatically

**Use cases:**
- Production deployments
- Multiple concurrent sessions
- When you need to query session data

## Configuration

### Environment Variables

You can configure persistence using environment variables:

```bash
export RISO_MCP_WIZARD__PERSISTENCE_BACKEND=sqlite
export RISO_MCP_WIZARD__PERSISTENCE_PATH=/var/lib/riso/sessions
```

### Configuration File

Create a `riso-mcp.toml` file in one of these locations:
- Current directory: `./riso-mcp.toml`
- Project config: `./.riso/mcp.toml`
- User config: `~/.config/riso/mcp.toml`

```toml
[wizard]
session_ttl_minutes = 120
max_sessions = 200
persistence_backend = "sqlite"
persistence_path = "~/.riso/sessions"
```

### Programmatic Configuration

When creating the server programmatically:

```python
from pathlib import Path
from riso.mcp.config import ServerConfig, WizardConfig

config = ServerConfig(
    wizard=WizardConfig(
        persistence_backend="sqlite",
        persistence_path=Path.home() / ".riso" / "sessions",
    )
)

mcp, session_manager = create_server(config)
```

## Session Recovery

### Automatic Loading

Sessions are automatically loaded from persistence when the server starts:

```python
from riso.mcp.server import create_server

# Create server - sessions are loaded automatically if persistence is enabled
mcp, session_manager = create_server()
```

### Manual Loading

You can also load sessions manually:

```python
loaded_count = session_manager.load_persisted_sessions()
print(f"Loaded {loaded_count} sessions from persistence")
```

**Note:** Expired sessions are automatically cleaned up during loading.

## Export and Import

### Export a Session

Export a session to a dictionary for backup or migration:

```python
session_data = session_manager.export_session(session_id)

# Save to file
import json
with open("session_backup.json", "w") as f:
    json.dump(session_data, f, indent=2, default=str)
```

### Import a Session

Import a session from a dictionary:

```python
import json
with open("session_backup.json") as f:
    session_data = json.load(f)

new_session_id = session_manager.import_session(session_data)
print(f"Imported session: {new_session_id}")
```

## Session Lifecycle

### Creation

Sessions are automatically persisted when created:

```python
session = session_manager.create_session(
    project_name="my-project",
    destination="/tmp/output",
)
# Session is now in both memory and persistence backend
```

### Updates

Session updates are persisted automatically:

```python
session = session_manager.get_session(session_id)
# Session is touched and persisted with updated timestamp
```

### Deletion

Deleting a session removes it from both memory and persistence:

```python
session_manager.delete_session(session_id)
# Session is removed from both memory and storage backend
```

### Expiration

Expired sessions are cleaned up from both memory and persistence:

```python
cleaned = session_manager.cleanup_expired()
print(f"Cleaned {cleaned} expired sessions")
```

## Best Practices

### Development

- Use **memory** backend for fast iteration
- Enable **json** backend when you need to inspect session state
- Keep `session_ttl_minutes` short (10-15 minutes)

### Production

- Use **sqlite** backend for reliability
- Set appropriate `session_ttl_minutes` based on workflow (60-120 minutes)
- Enable `auto_cleanup_interval` for automatic cleanup
- Monitor session count with `session_manager.active_session_count`

### Backup and Recovery

```bash
# JSON backend - copy the directory
cp -r ~/.riso/sessions ~/.riso/sessions.backup

# SQLite backend - backup the database
cp ~/.riso/sessions.db ~/.riso/sessions.db.backup
```

### Cleanup

```bash
# JSON backend - remove session files
rm ~/.riso/sessions/*.json

# SQLite backend - remove database
rm ~/.riso/sessions.db
```

## Monitoring

### Check Active Sessions

```python
count = session_manager.active_session_count
print(f"Active sessions: {count}")
```

### List Sessions

```python
sessions = session_manager.list_sessions()
for session_info in sessions:
    print(f"Session {session_info['session_id']}: {session_info['project_name']}")
```

### Storage Size

```bash
# JSON backend
du -sh ~/.riso/sessions

# SQLite backend
du -h ~/.riso/sessions.db
```

## Troubleshooting

### Sessions Not Loading

Check the server logs for persistence errors:

```bash
# Look for "session_load_failed" or "session_persist_failed" events
grep "session_load" /path/to/logs
```

### Permission Errors

Ensure the persistence directory is writable:

```bash
mkdir -p ~/.riso/sessions
chmod 755 ~/.riso/sessions
```

### Database Corruption

If the SQLite database is corrupted, you can recreate it:

```bash
# Backup first
cp ~/.riso/sessions.db ~/.riso/sessions.db.backup

# Remove and restart server
rm ~/.riso/sessions.db
# Server will create a new database on startup
```

### JSON Parse Errors

If a JSON file is corrupted, remove it:

```bash
rm ~/.riso/sessions/<session-id>.json
```

The server will log the error and continue with other sessions.

## API Reference

### SessionStore Protocol

All persistence backends implement the `SessionStore` protocol:

```python
class SessionStore(Protocol):
    def save(self, session_id: str, session: WizardSession) -> None: ...
    def load(self, session_id: str) -> WizardSession | None: ...
    def delete(self, session_id: str) -> bool: ...
    def list_sessions(self) -> list[str]: ...
    def load_all_sessions(self) -> dict[str, WizardSession]: ...
```

### SessionManager Methods

```python
# Load persisted sessions on startup
loaded_count = session_manager.load_persisted_sessions()

# Export session to dictionary
session_data = session_manager.export_session(session_id)

# Import session from dictionary
new_session_id = session_manager.import_session(session_data)
```

## Examples

### Development Setup

```toml
# .riso/mcp.toml
[wizard]
session_ttl_minutes = 15
persistence_backend = "json"
auto_cleanup_interval = 300  # 5 minutes
```

### Production Setup

```toml
# .riso/mcp.toml
[wizard]
session_ttl_minutes = 120
max_sessions = 500
persistence_backend = "sqlite"
persistence_path = "/var/lib/riso/sessions"
auto_cleanup_interval = 600  # 10 minutes

[wizard.rate_limit]
max_sessions_per_minute = 20
max_sessions_per_hour = 200
```

### Custom Persistence Backend

You can implement a custom backend by following the `SessionStore` protocol:

```python
from riso.mcp.persistence import SessionStore
from riso.mcp.session import WizardSession

class RedisStore:
    """Redis-based session store."""

    def __init__(self, redis_url: str):
        import redis
        self.redis = redis.from_url(redis_url)

    def save(self, session_id: str, session: WizardSession) -> None:
        data = serialize_session(session)  # Your serialization logic
        self.redis.set(f"session:{session_id}", data)

    def load(self, session_id: str) -> WizardSession | None:
        data = self.redis.get(f"session:{session_id}")
        if data:
            return deserialize_session(data)  # Your deserialization logic
        return None

    # Implement other methods...

# Use custom store
store = RedisStore("redis://localhost:6379")
session_manager = SessionManager(store=store)
```

## See Also

- [MCP Configuration API](../api/mcp/config.md)
- [Session Management API](../api/mcp/session.md)
- [MCP Server Setup](../tools/riso-mcp-server.md)
