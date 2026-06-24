"""Unit tests for session persistence backends."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pytest

from riso.mcp.persistence import JSONFileStore, MemoryStore, SQLiteStore
from riso.mcp.session import WizardSession, WizardStep


@pytest.fixture
def sample_session() -> WizardSession:
    """Create a sample wizard session for testing."""
    return WizardSession(
        session_id="test-session-123",
        project_name="test-project",
        destination="/tmp/test",
        template_variant="default",
        current_step=1,
        steps=[
            WizardStep(
                name="step1",
                title="Step 1",
                prompts=["prompt1", "prompt2"],
                required=True,
                completed=True,
                data={"key": "value"},
            ),
            WizardStep(
                name="step2",
                title="Step 2",
                prompts=["prompt3"],
                required=False,
                completed=False,
            ),
        ],
        answers={"answer1": "value1", "answer2": 42},
        validation_errors=["error1"],
        is_complete=False,
    )


class TestMemoryStore:
    """Test in-memory storage backend."""

    def test_save_and_load(self, sample_session: WizardSession) -> None:
        """Should save and load sessions from memory."""
        store = MemoryStore()

        store.save(sample_session.session_id, sample_session)
        loaded = store.load(sample_session.session_id)

        assert loaded is not None
        assert loaded.session_id == sample_session.session_id
        assert loaded.project_name == sample_session.project_name
        assert len(loaded.steps) == 2

    def test_load_nonexistent(self) -> None:
        """Should return None for nonexistent session."""
        store = MemoryStore()
        loaded = store.load("nonexistent")

        assert loaded is None

    def test_delete(self, sample_session: WizardSession) -> None:
        """Should delete sessions from memory."""
        store = MemoryStore()

        store.save(sample_session.session_id, sample_session)
        assert store.load(sample_session.session_id) is not None

        deleted = store.delete(sample_session.session_id)
        assert deleted is True
        assert store.load(sample_session.session_id) is None

    def test_delete_nonexistent(self) -> None:
        """Should return False when deleting nonexistent session."""
        store = MemoryStore()
        deleted = store.delete("nonexistent")

        assert deleted is False

    def test_list_sessions(self, sample_session: WizardSession) -> None:
        """Should list all session IDs."""
        store = MemoryStore()

        store.save(sample_session.session_id, sample_session)
        store.save("another-session", sample_session)

        session_ids = store.list_sessions()
        assert len(session_ids) == 2
        assert sample_session.session_id in session_ids
        assert "another-session" in session_ids

    def test_load_all_sessions(self, sample_session: WizardSession) -> None:
        """Should load all sessions."""
        store = MemoryStore()

        store.save(sample_session.session_id, sample_session)
        store.save("another-session", sample_session)

        all_sessions = store.load_all_sessions()
        assert len(all_sessions) == 2
        assert sample_session.session_id in all_sessions
        assert "another-session" in all_sessions


class TestJSONFileStore:
    """Test JSON file storage backend."""

    def test_save_and_load(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should save and load sessions from JSON files."""
        store = JSONFileStore(base_path=tmp_path)

        store.save(sample_session.session_id, sample_session)
        loaded = store.load(sample_session.session_id)

        assert loaded is not None
        assert loaded.session_id == sample_session.session_id
        assert loaded.project_name == sample_session.project_name
        assert len(loaded.steps) == 2
        assert loaded.steps[0].name == "step1"
        assert loaded.steps[0].data == {"key": "value"}
        assert loaded.answers == {"answer1": "value1", "answer2": 42}

    def test_file_created(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should create JSON file on disk."""
        store = JSONFileStore(base_path=tmp_path)

        store.save(sample_session.session_id, sample_session)
        file_path = tmp_path / f"{sample_session.session_id}.json"

        assert file_path.exists()
        with open(file_path) as f:
            data = json.load(f)
        assert data["session_id"] == sample_session.session_id

    def test_datetime_serialization(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should properly serialize and deserialize datetime objects."""
        store = JSONFileStore(base_path=tmp_path)

        original_created_at = sample_session.created_at
        original_last_activity = sample_session.last_activity

        store.save(sample_session.session_id, sample_session)
        loaded = store.load(sample_session.session_id)

        assert loaded is not None
        # Datetimes should be preserved (within microsecond precision)
        assert abs((loaded.created_at - original_created_at).total_seconds()) < 0.001
        assert (
            abs((loaded.last_activity - original_last_activity).total_seconds()) < 0.001
        )

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        """Should return None for nonexistent session."""
        store = JSONFileStore(base_path=tmp_path)
        loaded = store.load("nonexistent")

        assert loaded is None

    def test_delete(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should delete JSON file."""
        store = JSONFileStore(base_path=tmp_path)

        store.save(sample_session.session_id, sample_session)
        file_path = tmp_path / f"{sample_session.session_id}.json"
        assert file_path.exists()

        deleted = store.delete(sample_session.session_id)
        assert deleted is True
        assert not file_path.exists()

    def test_list_sessions(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should list all session IDs."""
        store = JSONFileStore(base_path=tmp_path)

        store.save(sample_session.session_id, sample_session)
        store.save("another-session", sample_session)

        session_ids = store.list_sessions()
        assert len(session_ids) == 2
        assert sample_session.session_id in session_ids
        assert "another-session" in session_ids

    def test_load_all_sessions(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should load all sessions from files."""
        store = JSONFileStore(base_path=tmp_path)

        store.save(sample_session.session_id, sample_session)
        store.save("another-session", sample_session)

        all_sessions = store.load_all_sessions()
        assert len(all_sessions) == 2
        assert sample_session.session_id in all_sessions
        assert "another-session" in all_sessions

    def test_corrupted_json_returns_none(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should return None for corrupted JSON files."""
        store = JSONFileStore(base_path=tmp_path)

        # Create a corrupted JSON file
        file_path = tmp_path / f"{sample_session.session_id}.json"
        file_path.write_text("{corrupted json")

        loaded = store.load(sample_session.session_id)
        assert loaded is None


class TestSQLiteStore:
    """Test SQLite storage backend."""

    def test_save_and_load(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should save and load sessions from SQLite."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        store.save(sample_session.session_id, sample_session)
        loaded = store.load(sample_session.session_id)

        assert loaded is not None
        assert loaded.session_id == sample_session.session_id
        assert loaded.project_name == sample_session.project_name
        assert len(loaded.steps) == 2
        assert loaded.steps[0].name == "step1"
        assert loaded.answers == {"answer1": "value1", "answer2": 42}

    def test_database_created(self, tmp_path: Path) -> None:
        """Should create SQLite database file."""
        db_path = tmp_path / "sessions.db"
        SQLiteStore(db_path=db_path)

        assert db_path.exists()

        # Verify table structure
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            tables = cursor.fetchall()
            assert len(tables) == 1

    def test_upsert_behavior(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should update existing sessions on save."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        # Save initial version
        store.save(sample_session.session_id, sample_session)

        # Modify and save again
        sample_session.project_name = "updated-project"
        store.save(sample_session.session_id, sample_session)

        # Should have only one record
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            assert count == 1

        # Should have updated data
        loaded = store.load(sample_session.session_id)
        assert loaded is not None
        assert loaded.project_name == "updated-project"

    def test_datetime_serialization(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should properly serialize and deserialize datetime objects."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        original_created_at = sample_session.created_at
        original_last_activity = sample_session.last_activity

        store.save(sample_session.session_id, sample_session)
        loaded = store.load(sample_session.session_id)

        assert loaded is not None
        # Datetimes should be preserved (within microsecond precision)
        assert abs((loaded.created_at - original_created_at).total_seconds()) < 0.001
        assert (
            abs((loaded.last_activity - original_last_activity).total_seconds()) < 0.001
        )

    def test_load_nonexistent(self, tmp_path: Path) -> None:
        """Should return None for nonexistent session."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        loaded = store.load("nonexistent")
        assert loaded is None

    def test_delete(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should delete sessions from database."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        store.save(sample_session.session_id, sample_session)
        assert store.load(sample_session.session_id) is not None

        deleted = store.delete(sample_session.session_id)
        assert deleted is True
        assert store.load(sample_session.session_id) is None

    def test_delete_nonexistent(self, tmp_path: Path) -> None:
        """Should return False when deleting nonexistent session."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        deleted = store.delete("nonexistent")
        assert deleted is False

    def test_list_sessions(self, tmp_path: Path, sample_session: WizardSession) -> None:
        """Should list all session IDs."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        store.save(sample_session.session_id, sample_session)
        store.save("another-session", sample_session)

        session_ids = store.list_sessions()
        assert len(session_ids) == 2
        assert sample_session.session_id in session_ids
        assert "another-session" in session_ids

    def test_load_all_sessions(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should load all sessions from database."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        store.save(sample_session.session_id, sample_session)
        store.save("another-session", sample_session)

        all_sessions = store.load_all_sessions()
        assert len(all_sessions) == 2
        assert sample_session.session_id in all_sessions
        assert "another-session" in all_sessions

    def test_corrupted_json_returns_none(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should return None for corrupted JSON data in database."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        # Insert corrupted JSON directly into database
        with closing(sqlite3.connect(db_path)) as conn:
            now = datetime.now().isoformat()
            conn.execute(
                "INSERT INTO sessions (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (sample_session.session_id, "{corrupted json", now, now),
            )
            conn.commit()

        loaded = store.load(sample_session.session_id)
        assert loaded is None

    def test_concurrent_access(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should handle concurrent access safely with SQLite."""
        db_path = tmp_path / "sessions.db"
        store1 = SQLiteStore(db_path=db_path)
        store2 = SQLiteStore(db_path=db_path)

        # Save from first store
        store1.save(sample_session.session_id, sample_session)

        # Load from second store (should work)
        loaded = store2.load(sample_session.session_id)
        assert loaded is not None
        assert loaded.session_id == sample_session.session_id

        # Update from second store
        sample_session.project_name = "updated-concurrent"
        store2.save(sample_session.session_id, sample_session)

        # Load from first store (should see update)
        reloaded = store1.load(sample_session.session_id)
        assert reloaded is not None
        assert reloaded.project_name == "updated-concurrent"


class TestJSONFileStoreRoundtrip:
    """Test comprehensive JSON store save/load roundtrip scenarios."""

    def test_json_store_save_load_roundtrip(
        self, tmp_path: Path, sample_session: WizardSession
    ) -> None:
        """Should preserve all session data through save/load cycle."""
        store = JSONFileStore(base_path=tmp_path)

        # Save original
        store.save(sample_session.session_id, sample_session)

        # Load and verify all fields
        loaded = store.load(sample_session.session_id)
        assert loaded is not None
        assert loaded.session_id == sample_session.session_id
        assert loaded.project_name == sample_session.project_name
        assert loaded.destination == sample_session.destination
        assert loaded.template_variant == sample_session.template_variant
        assert loaded.current_step == sample_session.current_step
        assert loaded.is_complete == sample_session.is_complete
        assert loaded.answers == sample_session.answers
        assert loaded.validation_errors == sample_session.validation_errors

        # Verify steps are preserved
        assert len(loaded.steps) == len(sample_session.steps)
        for i, step in enumerate(loaded.steps):
            assert step.name == sample_session.steps[i].name
            assert step.title == sample_session.steps[i].title
            assert step.data == sample_session.steps[i].data
            assert step.completed == sample_session.steps[i].completed

    def test_json_store_delete_session(self, tmp_path: Path) -> None:
        """Should properly delete sessions from JSON store."""
        store = JSONFileStore(base_path=tmp_path)
        session_id = "delete-test-session"

        # Create session
        session = WizardSession(
            session_id=session_id,
            project_name="to-delete",
            destination="/tmp/delete",
        )
        store.save(session_id, session)

        # Verify it exists
        file_path = tmp_path / f"{session_id}.json"
        assert file_path.exists()
        assert store.load(session_id) is not None

        # Delete
        result = store.delete(session_id)
        assert result is True
        assert not file_path.exists()
        assert store.load(session_id) is None

        # Delete again should return False
        result = store.delete(session_id)
        assert result is False
