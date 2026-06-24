"""Unit tests for SessionManager persistence integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path


from riso.mcp.persistence import JSONFileStore, MemoryStore, SQLiteStore
from riso.mcp.session import SessionManager


class TestSessionManagerWithMemoryStore:
    """Test SessionManager with MemoryStore (baseline functionality)."""

    def test_creates_session_without_persistence(self) -> None:
        """Should create sessions without persistence backend."""
        manager = SessionManager(store=None)
        session = manager.create_session(project_name="test")

        assert session is not None
        assert session.project_name == "test"
        assert manager.active_session_count == 1

    def test_creates_session_with_memory_store(self) -> None:
        """Should create sessions with MemoryStore."""
        store = MemoryStore()
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")

        assert session is not None
        # Should be in both memory and store
        assert manager.get_session(session.session_id) is not None
        assert store.load(session.session_id) is not None


class TestSessionManagerWithJSONStore:
    """Test SessionManager with JSON file persistence."""

    def test_creates_and_persists_session(self, tmp_path: Path) -> None:
        """Should persist session to JSON file on creation."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test-project")

        # Should exist in both memory and file
        assert manager.get_session(session.session_id) is not None
        assert store.load(session.session_id) is not None

        # File should exist
        file_path = tmp_path / f"{session.session_id}.json"
        assert file_path.exists()

    def test_persists_session_updates(self, tmp_path: Path) -> None:
        """Should persist updates when session is touched."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        original_activity = session.last_activity

        # Retrieve session (which touches it)
        updated_session = manager.get_session(session.session_id)

        # Should have updated timestamp
        assert updated_session.last_activity > original_activity

        # Should be persisted
        loaded = store.load(session.session_id)
        assert loaded is not None
        assert loaded.last_activity > original_activity

    def test_deletes_from_persistence(self, tmp_path: Path) -> None:
        """Should delete from both memory and persistence."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        session_id = session.session_id

        # Verify it exists
        file_path = tmp_path / f"{session_id}.json"
        assert file_path.exists()

        # Delete
        deleted = manager.delete_session(session_id)

        assert deleted is True
        assert manager.get_session_or_none(session_id) is None
        assert not file_path.exists()

    def test_cleanup_removes_from_persistence(self, tmp_path: Path) -> None:
        """Should remove expired sessions from persistence during cleanup."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(ttl_minutes=1, store=store)

        # Create expired session
        session = manager.create_session(project_name="test")
        session.last_activity = datetime.now() - timedelta(minutes=2)
        session_id = session.session_id

        # Manually persist the expired state
        store.save(session_id, session)

        # Cleanup
        cleaned = manager.cleanup_expired()

        assert cleaned == 1
        assert not (tmp_path / f"{session_id}.json").exists()

    def test_loads_persisted_sessions_on_startup(self, tmp_path: Path) -> None:
        """Should load existing sessions from persistence on startup."""
        store = JSONFileStore(base_path=tmp_path)

        # Create and persist sessions in first manager
        manager1 = SessionManager(store=store)
        session1 = manager1.create_session(project_name="project1")
        session2 = manager1.create_session(project_name="project2")
        session1_id = session1.session_id
        session2_id = session2.session_id

        # Create new manager with same store
        manager2 = SessionManager(store=store)
        loaded = manager2.load_persisted_sessions()

        assert loaded == 2
        assert manager2.active_session_count == 2
        assert manager2.get_session_or_none(session1_id) is not None
        assert manager2.get_session_or_none(session2_id) is not None

    def test_skips_expired_sessions_on_load(self, tmp_path: Path) -> None:
        """Should not load expired sessions on startup."""
        store = JSONFileStore(base_path=tmp_path)

        # Create sessions
        manager1 = SessionManager(ttl_minutes=5, store=store)
        active = manager1.create_session(project_name="active")
        expired = manager1.create_session(project_name="expired")

        # Make one expired
        expired.last_activity = datetime.now() - timedelta(minutes=10)
        store.save(expired.session_id, expired)

        # Load with new manager
        manager2 = SessionManager(ttl_minutes=5, store=store)
        loaded = manager2.load_persisted_sessions()

        assert loaded == 1
        assert manager2.get_session_or_none(active.session_id) is not None
        assert manager2.get_session_or_none(expired.session_id) is None

    def test_export_session(self, tmp_path: Path) -> None:
        """Should export session as dictionary."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        session = manager.create_session(
            project_name="test",
            destination="/tmp/test",
            template_variant="default",
        )

        exported = manager.export_session(session.session_id)

        assert exported["session_id"] == session.session_id
        assert exported["project_name"] == "test"
        assert exported["destination"] == "/tmp/test"
        assert "steps" in exported
        assert "answers" in exported

    def test_import_session(self, tmp_path: Path) -> None:
        """Should import session from dictionary."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        # Export a session
        original = manager.create_session(project_name="original")
        exported = manager.export_session(original.session_id)

        # Modify the export
        exported["session_id"] = "imported-session-123"
        exported["project_name"] = "imported"

        # Import
        new_id = manager.import_session(exported)

        assert new_id == "imported-session-123"
        loaded = manager.get_session(new_id)
        assert loaded.project_name == "imported"

        # Should be persisted
        assert store.load(new_id) is not None


class TestSessionManagerWithSQLiteStore:
    """Test SessionManager with SQLite persistence."""

    def test_creates_and_persists_session(self, tmp_path: Path) -> None:
        """Should persist session to SQLite on creation."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test-project")

        # Should exist in both memory and database
        assert manager.get_session(session.session_id) is not None
        assert store.load(session.session_id) is not None

    def test_persists_session_updates(self, tmp_path: Path) -> None:
        """Should persist updates when session is touched."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        original_activity = session.last_activity

        # Retrieve session (which touches it)
        updated_session = manager.get_session(session.session_id)

        # Should have updated timestamp
        assert updated_session.last_activity > original_activity

        # Should be persisted
        loaded = store.load(session.session_id)
        assert loaded is not None
        assert loaded.last_activity > original_activity

    def test_deletes_from_persistence(self, tmp_path: Path) -> None:
        """Should delete from both memory and persistence."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        session_id = session.session_id

        # Verify it exists
        assert store.load(session_id) is not None

        # Delete
        deleted = manager.delete_session(session_id)

        assert deleted is True
        assert manager.get_session_or_none(session_id) is None
        assert store.load(session_id) is None

    def test_loads_persisted_sessions_on_startup(self, tmp_path: Path) -> None:
        """Should load existing sessions from persistence on startup."""
        db_path = tmp_path / "sessions.db"
        store = SQLiteStore(db_path=db_path)

        # Create and persist sessions in first manager
        manager1 = SessionManager(store=store)
        session1 = manager1.create_session(project_name="project1")
        session2 = manager1.create_session(project_name="project2")
        session1_id = session1.session_id
        session2_id = session2.session_id

        # Create new manager with same store
        manager2 = SessionManager(store=store)
        loaded = manager2.load_persisted_sessions()

        assert loaded == 2
        assert manager2.active_session_count == 2
        assert manager2.get_session_or_none(session1_id) is not None
        assert manager2.get_session_or_none(session2_id) is not None

    def test_concurrent_managers_share_persistence(self, tmp_path: Path) -> None:
        """Multiple managers should share the same SQLite database."""
        db_path = tmp_path / "sessions.db"
        store1 = SQLiteStore(db_path=db_path)
        store2 = SQLiteStore(db_path=db_path)

        manager1 = SessionManager(store=store1)
        manager2 = SessionManager(store=store2)

        # Create session in manager1
        session = manager1.create_session(project_name="shared")
        session_id = session.session_id

        # Load in manager2
        manager2.load_persisted_sessions()
        loaded = manager2.get_session_or_none(session_id)

        assert loaded is not None
        assert loaded.project_name == "shared"


class TestSessionManagerPersistenceErrorHandling:
    """Test error handling in persistence operations."""

    def test_continues_on_save_error(self, tmp_path: Path, monkeypatch) -> None:
        """Should continue operation even if persistence fails."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        # Make save fail
        def failing_save(*args, **kwargs):
            raise OSError("Disk full")

        monkeypatch.setattr(store, "save", failing_save)

        # Should still create session in memory
        session = manager.create_session(project_name="test")
        assert session is not None
        assert manager.get_session_or_none(session.session_id) is not None

    def test_continues_on_delete_error(self, tmp_path: Path, monkeypatch) -> None:
        """Should continue operation even if persistence delete fails."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        session_id = session.session_id

        # Make delete fail
        def failing_delete(*args, **kwargs):
            raise OSError("Permission denied")

        monkeypatch.setattr(store, "delete", failing_delete)

        # Should still delete from memory
        deleted = manager.delete_session(session_id)
        assert deleted is True
        assert manager.get_session_or_none(session_id) is None

    def test_handles_load_errors_gracefully(self, tmp_path: Path, monkeypatch) -> None:
        """Should handle errors during session loading gracefully."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        # Create a session first
        manager.create_session(project_name="test")

        # Make load_all_sessions fail
        def failing_load_all(*args, **kwargs):
            raise OSError("Disk read error")

        monkeypatch.setattr(store, "load_all_sessions", failing_load_all)

        # Should return 0 without crashing
        loaded = manager.load_persisted_sessions()
        assert loaded == 0


class TestSessionManagerAutoRecovery:
    """Test session manager auto-recovery scenarios."""

    def test_session_manager_auto_recovery(self, tmp_path: Path) -> None:
        """Should recover sessions from persistence after restart."""
        store = JSONFileStore(base_path=tmp_path)

        # Create sessions in first manager
        manager1 = SessionManager(store=store)
        session1 = manager1.create_session(
            project_name="recovery-test-1",
            destination="/tmp/test1",
        )
        session2 = manager1.create_session(
            project_name="recovery-test-2",
            destination="/tmp/test2",
        )
        session1_id = session1.session_id
        session2_id = session2.session_id

        # Create new manager (simulating restart)
        manager2 = SessionManager(store=store)

        # Sessions should not be loaded automatically
        assert manager2.active_session_count == 0

        # Load persisted sessions
        loaded_count = manager2.load_persisted_sessions()
        assert loaded_count == 2
        assert manager2.active_session_count == 2

        # Verify sessions are accessible
        recovered1 = manager2.get_session(session1_id)
        recovered2 = manager2.get_session(session2_id)
        assert recovered1.project_name == "recovery-test-1"
        assert recovered2.project_name == "recovery-test-2"


class TestSessionManagerExportImport:
    """Test session export and import functionality."""

    def test_session_manager_export_import(self, tmp_path: Path) -> None:
        """Should export and import sessions correctly."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        # Create original session
        original = manager.create_session(
            project_name="export-test",
            destination="/tmp/export",
            template_variant="full-stack",
        )
        original_id = original.session_id

        # Update session with some answers
        original.answers = {"key1": "value1", "key2": "value2"}
        original.current_step = 3
        store.save(original_id, original)

        # Export
        exported = manager.export_session(original_id)
        assert exported is not None
        assert exported["session_id"] == original_id
        assert exported["project_name"] == "export-test"
        assert exported["answers"] == {"key1": "value1", "key2": "value2"}

        # Modify export for reimport
        exported["session_id"] = "reimported-session-id"
        exported["project_name"] = "reimported-project"

        # Import
        new_id = manager.import_session(exported)
        assert new_id == "reimported-session-id"

        # Verify imported session
        imported = manager.get_session(new_id)
        assert imported.project_name == "reimported-project"
        assert imported.answers == {"key1": "value1", "key2": "value2"}

        # Verify persistence
        persisted = store.load(new_id)
        assert persisted is not None
        assert persisted.project_name == "reimported-project"

    def test_session_export_preserves_metadata(self, tmp_path: Path) -> None:
        """Should preserve session metadata during export/import."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        original = manager.create_session(
            project_name="metadata-test",
            destination="/tmp/metadata",
        )

        # Export
        exported = manager.export_session(original.session_id)

        # Verify metadata
        assert exported["destination"] == "/tmp/metadata"
        assert "created_at" in exported
        assert "last_activity" in exported

        # Import with same session ID to verify all data
        exported["session_id"] = "metadata-imported"
        new_id = manager.import_session(exported)

        imported = manager.get_session(new_id)
        assert imported.destination == "/tmp/metadata"


class TestPersistenceConfigValidation:
    """Test persistence configuration validation."""

    def test_persistence_config_validation_memory_store(self) -> None:
        """Should accept MemoryStore for development."""
        store = MemoryStore()
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        assert session is not None
        assert isinstance(store, MemoryStore)

    def test_persistence_config_validation_json_store(self, tmp_path: Path) -> None:
        """Should validate JSONFileStore initialization."""
        store = JSONFileStore(base_path=tmp_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        assert session is not None

        # Verify store is properly configured
        assert store._base_path == tmp_path
        assert tmp_path.exists()

    def test_persistence_config_validation_sqlite_store(self, tmp_path: Path) -> None:
        """Should validate SQLiteStore initialization."""
        db_path = tmp_path / "test.db"
        store = SQLiteStore(db_path=db_path)
        manager = SessionManager(store=store)

        session = manager.create_session(project_name="test")
        assert session is not None

        # Verify database is properly configured
        assert db_path.exists()

    def test_persistence_config_validation_invalid_path(self, tmp_path: Path) -> None:
        """Should handle invalid database paths gracefully."""
        invalid_path = tmp_path / "nonexistent" / "nested" / "path" / "sessions.db"

        # SQLiteStore should create parent directories
        SQLiteStore(db_path=invalid_path)
        assert invalid_path.parent.exists()

    def test_persistence_store_protocol_compliance(self, tmp_path: Path) -> None:
        """Should verify stores comply with SessionStore protocol."""
        from riso.mcp.persistence import SessionStore

        stores = [
            MemoryStore(),
            JSONFileStore(base_path=tmp_path),
            SQLiteStore(db_path=tmp_path / "test.db"),
        ]

        for store in stores:
            # Verify store implements protocol methods
            assert hasattr(store, "save")
            assert hasattr(store, "load")
            assert hasattr(store, "delete")
            assert hasattr(store, "list_sessions")
            assert hasattr(store, "load_all_sessions")
            assert isinstance(store, SessionStore)
