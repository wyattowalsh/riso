"""Session persistence backends for Riso MCP server.

Provides multiple storage backends for wizard session persistence:
- MemoryStore: In-memory storage (no persistence, testing/development)
- JSONFileStore: JSON file-based storage (simple, human-readable)
- SQLiteStore: SQLite database storage (production-ready, queryable)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from .logging import log_event
from .session import WizardSession, WizardStep

logger = logging.getLogger("riso.mcp.persistence")


@runtime_checkable
class SessionStore(Protocol):
    """Protocol for session storage backends.

    All storage backends must implement these methods for session CRUD operations.
    """

    def save(self, session_id: str, session: WizardSession) -> None:
        """Save or update a session.

        Parameters
        ----------
        session_id
            Unique session identifier
        session
            Session data to persist

        Raises
        ------
        Exception
            If save operation fails
        """
        ...

    def load(self, session_id: str) -> WizardSession | None:
        """Load a session by ID.

        Parameters
        ----------
        session_id
            Session identifier to load

        Returns
        -------
        WizardSession | None
            Session if found, None otherwise
        """
        ...

    def delete(self, session_id: str) -> bool:
        """Delete a session by ID.

        Parameters
        ----------
        session_id
            Session identifier to delete

        Returns
        -------
        bool
            True if deleted, False if not found
        """
        ...

    def list_sessions(self) -> list[str]:
        """List all session IDs.

        Returns
        -------
        list[str]
            List of all stored session IDs
        """
        ...

    def load_all_sessions(self) -> dict[str, WizardSession]:
        """Load all sessions.

        Returns
        -------
        dict[str, WizardSession]
            Dictionary mapping session IDs to sessions
        """
        ...


class MemoryStore:
    """In-memory session store (no persistence).

    Useful for testing, development, or when persistence is not needed.
    Data is lost when the process terminates.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, WizardSession] = {}
        log_event(logger, "memory_store_initialized", level="debug")

    def save(self, session_id: str, session: WizardSession) -> None:
        """Save session to memory."""
        self._sessions[session_id] = session
        log_event(
            logger,
            "session_saved",
            level="debug",
            session_id=session_id,
            backend="memory",
        )

    def load(self, session_id: str) -> WizardSession | None:
        """Load session from memory."""
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        """Delete session from memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            log_event(
                logger,
                "session_deleted",
                level="debug",
                session_id=session_id,
                backend="memory",
            )
            return True
        return False

    def list_sessions(self) -> list[str]:
        """List all session IDs in memory."""
        return list(self._sessions.keys())

    def load_all_sessions(self) -> dict[str, WizardSession]:
        """Load all sessions from memory."""
        return self._sessions.copy()


class JSONFileStore:
    """JSON file-based session store.

    Stores each session as a separate JSON file in ~/.riso/sessions/ by default.
    Human-readable and easy to inspect/debug.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize JSON file store.

        Parameters
        ----------
        base_path
            Directory for session files. Defaults to ~/.riso/sessions
        """
        self._base_path = base_path or Path.home() / ".riso" / "sessions"
        self._base_path.mkdir(parents=True, exist_ok=True)
        log_event(
            logger,
            "json_store_initialized",
            level="info",
            path=str(self._base_path),
        )

    def _session_path(self, session_id: str) -> Path:
        """Get path for a session file."""
        return self._base_path / f"{session_id}.json"

    def _serialize_session(self, session: WizardSession) -> dict:
        """Convert session to JSON-serializable dict."""
        data = asdict(session)

        # Convert datetime objects to ISO format
        data["created_at"] = session.created_at.isoformat()
        data["last_activity"] = session.last_activity.isoformat()

        # Convert step timestamps
        for step in data["steps"]:
            if "timestamp" in step:
                step["timestamp"] = step["timestamp"].isoformat()

        return data

    def _deserialize_session(self, data: dict) -> WizardSession:
        """Convert JSON dict back to WizardSession."""
        # Parse datetime fields
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])

        # Parse step timestamps
        steps = []
        for step_data in data["steps"]:
            if "timestamp" in step_data:
                step_data["timestamp"] = datetime.fromisoformat(step_data["timestamp"])
            steps.append(WizardStep(**step_data))
        data["steps"] = steps

        return WizardSession(**data)

    def save(self, session_id: str, session: WizardSession) -> None:
        """Save session to JSON file."""
        path = self._session_path(session_id)
        data = self._serialize_session(session)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        log_event(
            logger,
            "session_saved",
            level="debug",
            session_id=session_id,
            backend="json",
            path=str(path),
        )

    def load(self, session_id: str) -> WizardSession | None:
        """Load session from JSON file."""
        path = self._session_path(session_id)
        if not path.exists():
            return None

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return self._deserialize_session(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            log_event(
                logger,
                "session_load_failed",
                level="error",
                session_id=session_id,
                error=str(e),
                backend="json",
            )
            return None

    def delete(self, session_id: str) -> bool:
        """Delete session JSON file."""
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()
            log_event(
                logger,
                "session_deleted",
                level="debug",
                session_id=session_id,
                backend="json",
            )
            return True
        return False

    def list_sessions(self) -> list[str]:
        """List all session IDs from JSON files."""
        return [p.stem for p in self._base_path.glob("*.json")]

    def load_all_sessions(self) -> dict[str, WizardSession]:
        """Load all sessions from JSON files."""
        sessions = {}
        for session_id in self.list_sessions():
            session = self.load(session_id)
            if session is not None:
                sessions[session_id] = session
        return sessions


class SQLiteStore:
    """SQLite-based session store.

    Stores sessions in a SQLite database at ~/.riso/sessions.db by default.
    Production-ready with ACID guarantees and efficient querying.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialize SQLite store.

        Parameters
        ----------
        db_path
            Path to SQLite database file. Defaults to ~/.riso/sessions.db
        """
        self._db_path = db_path or Path.home() / ".riso" / "sessions.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        log_event(
            logger,
            "sqlite_store_initialized",
            level="info",
            path=str(self._db_path),
        )

    def _init_database(self) -> None:
        """Create sessions table if it doesn't exist."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def _serialize_session(self, session: WizardSession) -> str:
        """Convert session to JSON string."""
        data = asdict(session)
        data["created_at"] = session.created_at.isoformat()
        data["last_activity"] = session.last_activity.isoformat()

        for step in data["steps"]:
            if "timestamp" in step:
                step["timestamp"] = step["timestamp"].isoformat()

        return json.dumps(data)

    def _deserialize_session(self, json_str: str) -> WizardSession:
        """Convert JSON string back to WizardSession."""
        data = json.loads(json_str)
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])

        steps = []
        for step_data in data["steps"]:
            if "timestamp" in step_data:
                step_data["timestamp"] = datetime.fromisoformat(step_data["timestamp"])
            steps.append(WizardStep(**step_data))
        data["steps"] = steps

        return WizardSession(**data)

    def save(self, session_id: str, session: WizardSession) -> None:
        """Save session to SQLite database."""
        json_data = self._serialize_session(session)
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                """
                INSERT INTO sessions (id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    data = excluded.data,
                    updated_at = excluded.updated_at
                """,
                (session_id, json_data, now, now),
            )
            conn.commit()
        finally:
            conn.close()

        log_event(
            logger,
            "session_saved",
            level="debug",
            session_id=session_id,
            backend="sqlite",
        )

    def load(self, session_id: str) -> WizardSession | None:
        """Load session from SQLite database."""
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.execute(
                "SELECT data FROM sessions WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        try:
            return self._deserialize_session(row[0])
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            log_event(
                logger,
                "session_load_failed",
                level="error",
                session_id=session_id,
                error=str(e),
                backend="sqlite",
            )
            return None

    def delete(self, session_id: str) -> bool:
        """Delete session from SQLite database."""
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.execute(
                "DELETE FROM sessions WHERE id = ?",
                (session_id,),
            )
            conn.commit()
            deleted = cursor.rowcount > 0
        finally:
            conn.close()

        if deleted:
            log_event(
                logger,
                "session_deleted",
                level="debug",
                session_id=session_id,
                backend="sqlite",
            )

        return deleted

    def list_sessions(self) -> list[str]:
        """List all session IDs from SQLite database."""
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.execute("SELECT id FROM sessions")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def load_all_sessions(self) -> dict[str, WizardSession]:
        """Load all sessions from SQLite database."""
        sessions = {}
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.execute("SELECT id, data FROM sessions")
            for session_id, json_data in cursor.fetchall():
                try:
                    sessions[session_id] = self._deserialize_session(json_data)
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    log_event(
                        logger,
                        "session_load_failed",
                        level="error",
                        session_id=session_id,
                        error=str(e),
                        backend="sqlite",
                    )
        finally:
            conn.close()
        return sessions
