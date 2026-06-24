"""Tests for MCP server configuration."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

pytest.importorskip("fastmcp")
pytest.importorskip("pydantic_settings")


class TestServerConfig:
    """Tests for server configuration."""

    def test_default_config_values(self):
        """Test that default config values are set correctly."""
        from riso.mcp.config import ServerConfig

        config = ServerConfig()

        assert config.transport == "stdio"
        assert config.port == 3000
        assert config.host == "127.0.0.1"
        assert config.log_level == "INFO"
        assert config.name == "riso-mcp"

    def test_config_from_env_vars(self):
        """Test that config can be loaded from environment variables."""
        from riso.mcp.config import ServerConfig

        with patch.dict(
            os.environ,
            {
                "RISO_MCP_TRANSPORT": "http",
                "RISO_MCP_PORT": "8080",
                "RISO_MCP_HOST": "0.0.0.0",
                "RISO_MCP_LOG_LEVEL": "DEBUG",
            },
        ):
            config = ServerConfig()

            assert config.transport == "http"
            assert config.port == 8080
            assert config.host == "0.0.0.0"
            assert config.log_level == "DEBUG"

    def test_transport_validation(self):
        """Test that transport is validated correctly."""
        from riso.mcp.config import ServerConfig

        # Valid transports should work
        for transport in ["stdio", "sse", "http"]:
            with patch.dict(os.environ, {"RISO_MCP_TRANSPORT": transport}, clear=False):
                config = ServerConfig()
                assert config.transport == transport

    def test_timeout_config(self):
        """Test TimeoutConfig defaults."""
        from riso.mcp.config import TimeoutConfig

        config = TimeoutConfig()

        assert config.tool == 30
        assert config.resource == 10
        assert config.prompt == 5
        assert config.copier_copy == 120

    def test_wizard_config(self):
        """Test WizardConfig defaults."""
        from riso.mcp.config import WizardConfig

        config = WizardConfig()

        assert config.session_ttl_minutes == 60
        assert config.max_sessions == 100
        assert config.auto_cleanup_interval == 300

    def test_get_config_cached(self):
        """Test that get_config returns cached configuration."""
        from riso.mcp.config import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2


class TestMCPErrors:
    """Tests for MCP error types."""

    def test_mcp_error_base(self):
        """Test MCPError base class."""
        from riso.mcp.errors import MCPError, MCPErrorCode

        error = MCPError("Test error", code=MCPErrorCode.INTERNAL_ERROR)
        assert str(error) == "Test error"
        assert error.code == MCPErrorCode.INTERNAL_ERROR

    def test_mcp_error_to_dict(self):
        """Test MCPError to_dict method."""
        from riso.mcp.errors import MCPError, MCPErrorCode

        error = MCPError(
            "Test error", code=MCPErrorCode.INTERNAL_ERROR, data={"key": "value"}
        )
        result = error.to_dict()

        assert result["code"] == int(MCPErrorCode.INTERNAL_ERROR)
        assert result["message"] == "Test error"
        assert result["data"] == {"key": "value"}

    def test_validation_failed_error(self):
        """Test ValidationFailedError."""
        from riso.mcp.errors import ValidationFailedError, MCPErrorCode

        error = ValidationFailedError(["field1 is required", "field2 invalid"])
        assert "2 error(s)" in str(error)
        assert error.code == MCPErrorCode.VALIDATION_FAILED
        assert error.data is not None
        assert error.data["errors"] == ["field1 is required", "field2 invalid"]

    def test_template_not_found_error(self):
        """Test TemplateNotFoundError."""
        from riso.mcp.errors import TemplateNotFoundError, MCPErrorCode

        error = TemplateNotFoundError("/path/to/template")
        assert "Template not found" in str(error)
        assert error.code == MCPErrorCode.TEMPLATE_NOT_FOUND
        assert error.data is not None
        assert error.data["path"] == "/path/to/template"

    def test_session_not_found_error(self):
        """Test SessionNotFoundError."""
        from riso.mcp.errors import SessionNotFoundError, MCPErrorCode

        error = SessionNotFoundError("abc123")
        assert "Session not found" in str(error)
        assert error.code == MCPErrorCode.SESSION_NOT_FOUND
        assert error.data is not None
        assert error.data["session_id"] == "abc123"

    def test_session_expired_error(self):
        """Test SessionExpiredError."""
        from riso.mcp.errors import SessionExpiredError, MCPErrorCode

        error = SessionExpiredError("abc123")
        assert "Session expired" in str(error)
        assert error.code == MCPErrorCode.SESSION_EXPIRED
        assert error.data is not None
        assert error.data["session_id"] == "abc123"

    def test_copier_operation_error(self):
        """Test CopierOperationError."""
        from riso.mcp.errors import CopierOperationError, MCPErrorCode

        error = CopierOperationError("copy", "destination not found")
        assert "Copier copy failed" in str(error)
        assert error.code == MCPErrorCode.COPIER_ERROR
        assert error.data is not None
        assert error.data["operation"] == "copy"


class TestSessionManager:
    """Tests for session management."""

    def test_session_manager_creation(self):
        """Test SessionManager initialization."""
        from riso.mcp.session import SessionManager

        manager = SessionManager(ttl_minutes=30, max_sessions=50)
        assert manager._ttl_minutes == 30
        assert manager._max_sessions == 50
        assert manager.active_session_count == 0

    def test_session_manager_create_session(self):
        """Test creating a new session."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        session = manager.create_session(
            project_name="test-project",
            destination="/tmp/test",
            template_variant="default",
        )

        assert session.session_id is not None
        assert session.project_name == "test-project"
        assert session.destination == "/tmp/test"
        assert session.current_step == 0
        assert len(session.steps) > 0  # Has default wizard steps

    def test_session_manager_get_session(self):
        """Test retrieving an existing session."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        created = manager.create_session()

        retrieved = manager.get_session(created.session_id)
        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    def test_session_manager_delete_session(self):
        """Test deleting a session."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        session = manager.create_session()
        session_id = session.session_id

        result = manager.delete_session(session_id)
        assert result is True

        # Should raise SessionNotFoundError now
        from riso.mcp.errors import SessionNotFoundError

        with pytest.raises(SessionNotFoundError):
            manager.get_session(session_id)

    def test_session_manager_list_sessions(self):
        """Test listing all sessions."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        manager.create_session(project_name="project1")
        manager.create_session(project_name="project2")

        sessions = manager.list_sessions()
        assert len(sessions) == 2
        project_names = [s["project_name"] for s in sessions]
        assert "project1" in project_names
        assert "project2" in project_names

    def test_wizard_session_set_answers(self):
        """Test setting answers on a wizard session."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        session = manager.create_session()

        original_time = session.last_activity
        import time

        time.sleep(0.05)

        session.set_answers({"project_name": "test", "cli_module": "enabled"})

        assert session.answers["project_name"] == "test"
        assert session.answers["cli_module"] == "enabled"
        assert session.last_activity > original_time

    def test_wizard_session_advance_step(self):
        """Test advancing wizard step."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        session = manager.create_session()

        assert session.current_step == 0
        new_step = session.advance_step()
        assert new_step == 1
        assert session.current_step == 1

    def test_wizard_session_go_back(self):
        """Test going back in wizard."""
        from riso.mcp.session import SessionManager

        manager = SessionManager()
        session = manager.create_session()

        session.advance_step()
        session.advance_step()
        assert session.current_step == 2

        session.go_back()
        assert session.current_step == 1

    def test_session_expiry(self):
        """Test that sessions respect TTL."""
        from riso.mcp.session import SessionManager
        import time

        # Use very short TTL
        manager = SessionManager(ttl_minutes=0)  # Immediate expiry

        manager.create_session()

        # Wait briefly for expiry
        time.sleep(0.1)

        # Cleanup should remove expired session
        cleaned = manager.cleanup_expired()
        assert cleaned >= 1
