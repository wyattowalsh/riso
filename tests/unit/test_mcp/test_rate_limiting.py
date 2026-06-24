"""Unit tests for session rate limiting."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from riso.mcp.config import RateLimitConfig
from riso.mcp.errors import TooManyRequestsError
from riso.mcp.session import SessionManager


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_create_session_under_limit(self) -> None:
        """Test that session creation works normally under the limit."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=10,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        # Should be able to create sessions under the limit
        for i in range(5):
            session = manager.create_session(project_name=f"test-{i}")
            assert session.session_id is not None
            assert session.project_name == f"test-{i}"

        assert manager.active_session_count == 5

    def test_rate_limit_per_minute_exceeded(self) -> None:
        """Test that rate limit raises error when minute limit exceeded."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=10,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        # Create 10 sessions - should succeed
        for i in range(10):
            manager.create_session(project_name=f"test-{i}")

        # 11th session should fail
        with pytest.raises(TooManyRequestsError) as exc_info:
            manager.create_session(project_name="test-11")

        assert "too many sessions per minute" in str(exc_info.value).lower()
        assert exc_info.value.data is not None
        assert exc_info.value.data.get("retry_after") == 60

    def test_rate_limit_per_hour_exceeded(self) -> None:
        """Test that rate limit raises error when hour limit exceeded."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=100,  # High minute limit
            max_sessions_per_hour=5,  # Low hour limit for testing
        )
        manager = SessionManager(rate_config=rate_config)

        # Create 5 sessions - should succeed
        for i in range(5):
            manager.create_session(project_name=f"test-{i}")

        # 6th session should fail
        with pytest.raises(TooManyRequestsError) as exc_info:
            manager.create_session(project_name="test-6")

        assert "too many sessions per hour" in str(exc_info.value).lower()
        assert exc_info.value.data is not None
        assert exc_info.value.data.get("retry_after") == 3600

    def test_rate_limit_resets_after_time_passes(self) -> None:
        """Test that rate limit resets after the time window passes."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=3,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        # Mock time to simulate passage of time
        with patch("time.time") as mock_time:
            # Start at t=0
            mock_time.return_value = 0.0

            # Create 3 sessions at t=0
            for i in range(3):
                manager.create_session(project_name=f"test-{i}")

            # 4th session at t=0 should fail
            with pytest.raises(TooManyRequestsError):
                manager.create_session(project_name="test-4")

            # Advance time by 61 seconds (past the 60-second window)
            mock_time.return_value = 61.0

            # Should now be able to create a new session
            session = manager.create_session(project_name="test-new")
            assert session.session_id is not None

    def test_rate_limit_window_sliding(self) -> None:
        """Test that rate limiting uses a sliding window."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=2,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        with patch("time.time") as mock_time:
            # Create session at t=0
            mock_time.return_value = 0.0
            manager.create_session(project_name="test-0")

            # Create session at t=30
            mock_time.return_value = 30.0
            manager.create_session(project_name="test-1")

            # At t=30, both sessions are within the 60-second window
            # so 3rd session should fail
            with pytest.raises(TooManyRequestsError):
                manager.create_session(project_name="test-2")

            # At t=61, first session (t=0) is outside the window
            # but second session (t=30) is still inside
            mock_time.return_value = 61.0
            session = manager.create_session(project_name="test-3")
            assert session.session_id is not None

    def test_default_rate_config_used(self) -> None:
        """Test that default rate config is used if none provided."""
        manager = SessionManager()

        # Should use default config (10 per minute, 50 per hour)
        assert manager._rate_config.max_sessions_per_minute == 10
        assert manager._rate_config.max_sessions_per_hour == 50

    def test_creation_times_deque_max_length(self) -> None:
        """Test that creation times deque has proper max length."""
        manager = SessionManager()
        assert manager._creation_times.maxlen == 100

    def test_rate_limit_thread_safety(self) -> None:
        """Test that rate limiting is thread-safe."""
        import threading
        from concurrent.futures import ThreadPoolExecutor

        rate_config = RateLimitConfig(
            max_sessions_per_minute=10,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        errors = []
        success_count = 0
        lock = threading.Lock()

        def create_session_task(index: int) -> None:
            nonlocal success_count
            try:
                manager.create_session(project_name=f"test-{index}")
                with lock:
                    success_count += 1
            except TooManyRequestsError as e:
                with lock:
                    errors.append(e)

        # Try to create 15 sessions concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_session_task, i) for i in range(15)]
            for future in futures:
                future.result()

        # Should have 10 successful and 5 failed
        assert success_count == 10
        assert len(errors) == 5
        assert all(isinstance(e, TooManyRequestsError) for e in errors)

    def test_rate_limit_check_only_on_creation(self) -> None:
        """Test that rate limit only applies to session creation, not other operations."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=2,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        # Create 2 sessions
        session1 = manager.create_session(project_name="test-1")
        session2 = manager.create_session(project_name="test-2")

        # Rate limit reached, can't create more
        with pytest.raises(TooManyRequestsError):
            manager.create_session(project_name="test-3")

        # But should still be able to retrieve existing sessions
        retrieved1 = manager.get_session(session1.session_id)
        assert retrieved1.session_id == session1.session_id

        retrieved2 = manager.get_session(session2.session_id)
        assert retrieved2.session_id == session2.session_id

        # And list sessions
        sessions = manager.list_sessions()
        assert len(sessions) == 2

        # And delete sessions
        assert manager.delete_session(session1.session_id) is True
        assert manager.active_session_count == 1

    def test_error_message_contains_retry_info(self) -> None:
        """Test that error messages provide helpful retry information."""
        rate_config = RateLimitConfig(
            max_sessions_per_minute=1,
            max_sessions_per_hour=50,
        )
        manager = SessionManager(rate_config=rate_config)

        manager.create_session(project_name="test-1")

        with pytest.raises(TooManyRequestsError) as exc_info:
            manager.create_session(project_name="test-2")

        error = exc_info.value
        assert "Rate limit exceeded" in str(error)
        assert error.data is not None
        assert "retry_after" in error.data
        assert error.data["retry_after"] == 60
