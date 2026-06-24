"""Unit tests for SessionManager cleanup functionality."""

from __future__ import annotations

import time
from datetime import datetime, timedelta

import pytest

from riso.mcp.session import SessionManager


class TestSessionCleanupTimer:
    """Test automatic cleanup timer functionality."""

    def test_timer_starts_with_valid_interval(self) -> None:
        """Timer should start when auto_cleanup_interval is provided."""
        manager = SessionManager(auto_cleanup_interval=300)

        assert manager.is_auto_cleanup_enabled is True
        assert manager.cleanup_interval_seconds == 300
        assert manager._cleanup_timer is not None

        manager.shutdown()

    def test_timer_not_started_without_interval(self) -> None:
        """Timer should not start when auto_cleanup_interval is None."""
        manager = SessionManager(auto_cleanup_interval=None)

        assert manager.is_auto_cleanup_enabled is False
        assert manager.cleanup_interval_seconds is None
        assert manager._cleanup_timer is None

    def test_timer_not_started_with_zero_interval(self) -> None:
        """Timer should not start when auto_cleanup_interval is 0."""
        manager = SessionManager(auto_cleanup_interval=0)

        assert manager.is_auto_cleanup_enabled is False

    def test_cleanup_executes_and_removes_expired(self) -> None:
        """Cleanup should remove expired sessions."""
        manager = SessionManager(ttl_minutes=1, auto_cleanup_interval=1)

        # Create a session and make it expired
        session = manager.create_session(project_name="test")
        session.last_activity = datetime.now() - timedelta(minutes=2)

        assert manager.active_session_count == 1

        # Wait for cleanup to execute
        time.sleep(1.5)

        assert manager.active_session_count == 0

        manager.shutdown()

    def test_enable_auto_cleanup_starts_timer(self) -> None:
        """Enabling auto cleanup should start the timer."""
        manager = SessionManager(auto_cleanup_interval=None)

        assert manager.is_auto_cleanup_enabled is False

        manager.enable_auto_cleanup(interval=300)

        assert manager.is_auto_cleanup_enabled is True
        assert manager.cleanup_interval_seconds == 300
        assert manager._cleanup_timer is not None

        manager.shutdown()

    def test_enable_auto_cleanup_validates_interval(self) -> None:
        """Enable should validate interval is in valid range."""
        manager = SessionManager(auto_cleanup_interval=None)

        with pytest.raises(ValueError, match="between 60 and 3600"):
            manager.enable_auto_cleanup(interval=30)

        with pytest.raises(ValueError, match="between 60 and 3600"):
            manager.enable_auto_cleanup(interval=5000)

    def test_disable_auto_cleanup_stops_timer(self) -> None:
        """Disabling auto cleanup should stop the timer."""
        manager = SessionManager(auto_cleanup_interval=300)

        assert manager.is_auto_cleanup_enabled is True

        manager.disable_auto_cleanup()

        assert manager.is_auto_cleanup_enabled is False
        assert manager._cleanup_timer is None

    def test_shutdown_stops_timer(self) -> None:
        """Shutdown should stop cleanup timer."""
        manager = SessionManager(auto_cleanup_interval=300)

        assert manager._cleanup_timer is not None

        manager.shutdown()

        assert manager._cleanup_timer is None

    def test_cleanup_preserves_active_sessions(self) -> None:
        """Auto cleanup should only remove expired sessions."""
        manager = SessionManager(ttl_minutes=5, auto_cleanup_interval=1)

        # Create active sessions
        active1 = manager.create_session(project_name="active1")
        active2 = manager.create_session(project_name="active2")

        # Create expired session
        expired = manager.create_session(project_name="expired")
        expired.last_activity = datetime.now() - timedelta(minutes=10)

        assert manager.active_session_count == 3

        # Wait for cleanup
        time.sleep(1.5)

        # Only expired session should be removed
        assert manager.active_session_count == 2
        assert manager.get_session_or_none(active1.session_id) is not None
        assert manager.get_session_or_none(active2.session_id) is not None
        assert manager.get_session_or_none(expired.session_id) is None

        manager.shutdown()

    def test_cleanup_timer_is_daemon(self) -> None:
        """Cleanup timer should be daemon thread."""
        manager = SessionManager(auto_cleanup_interval=300)

        timer = manager._cleanup_timer
        assert timer is not None
        assert timer.daemon is True

        manager.shutdown()
