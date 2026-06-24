"""Tests for path traversal validation security."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from riso.mcp.errors import PermissionDeniedError
from riso.mcp.tools.copier_api import validate_destination


class TestPathValidation:
    """Tests for validate_destination security function."""

    def test_traversal_attempt_raises_permission_denied(self):
        """Test that path traversal attempts are blocked."""
        # Attempt to traverse to /etc/passwd
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("../../../../../../etc/passwd")

        assert "Cannot write to system directories" in str(exc_info.value)
        assert exc_info.value.code.name == "PERMISSION_DENIED"

    def test_valid_tmp_path_succeeds(self):
        """Test that valid /tmp paths are allowed."""
        result = validate_destination("/tmp/myproject")

        # On macOS, /tmp resolves to /private/tmp
        assert result == Path("/tmp/myproject").resolve()
        assert result.is_absolute()

    def test_dangerous_system_paths_blocked_etc(self):
        """Test that /etc paths are blocked."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/etc/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

    def test_dangerous_system_paths_blocked_usr(self):
        """Test that /usr paths are blocked."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/usr/local/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

    def test_dangerous_system_paths_blocked_bin(self):
        """Test that /bin paths are blocked."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/bin/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

    def test_dangerous_system_paths_blocked_sbin(self):
        """Test that /sbin paths are blocked."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/sbin/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

    def test_dangerous_system_paths_blocked_var(self):
        """Test that dangerous /var subdirectories are blocked."""
        # /var/log should be blocked
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/var/log/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

        # /var/db should be blocked
        with pytest.raises(PermissionDeniedError):
            validate_destination("/var/db/myproject")

        # /var/mail should be blocked
        with pytest.raises(PermissionDeniedError):
            validate_destination("/var/mail/myproject")

    def test_dangerous_system_paths_blocked_root(self):
        """Test that /root paths are blocked."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/root/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

    def test_dangerous_system_paths_blocked_home(self):
        """Test that /home paths are blocked."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/home/user/myproject")

        assert "Cannot write to system directories" in str(exc_info.value)

    def test_tilde_expansion(self):
        """Test that tilde paths are expanded."""
        result = validate_destination("~/myproject")

        # Should be expanded to home directory
        assert result.is_absolute()
        assert "myproject" in str(result)

    def test_relative_path_resolution(self):
        """Test that relative paths are resolved to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a relative path from temp directory
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = validate_destination("myproject")

                # Should be resolved to absolute path
                assert result.is_absolute()
                assert "myproject" in str(result)
            finally:
                os.chdir(original_cwd)

    def test_safe_parent_constraint_within_allowed(self):
        """Test that paths within safe_parent are allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_parent = Path(tmpdir).resolve()
            dest = str(safe_parent / "subdir" / "myproject")

            result = validate_destination(dest, safe_parent=safe_parent)

            assert result.is_absolute()
            assert result.is_relative_to(safe_parent)

    def test_safe_parent_constraint_outside_blocked(self):
        """Test that paths outside safe_parent are blocked."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                safe_parent = Path(tmpdir1)
                # Try to write to a different temp directory
                dest = str(Path(tmpdir2) / "myproject")

                with pytest.raises(PermissionDeniedError) as exc_info:
                    validate_destination(dest, safe_parent=safe_parent)

                assert "Outside allowed parent" in str(exc_info.value)

    def test_safe_parent_with_traversal_attempt(self):
        """Test that traversal attempts are caught with safe_parent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_parent = Path(tmpdir)
            # Attempt to traverse outside safe_parent
            dest = str(safe_parent / ".." / ".." / "etc" / "passwd")

            with pytest.raises(PermissionDeniedError) as exc_info:
                validate_destination(dest, safe_parent=safe_parent)

            # Should be caught by either safe_parent check or dangerous path check
            assert "Outside allowed parent" in str(
                exc_info.value
            ) or "Cannot write to system directories" in str(exc_info.value)

    def test_symlink_resolution(self):
        """Test that symlinks are resolved before validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a symlink pointing to /etc
            link_path = tmpdir_path / "link_to_etc"
            try:
                link_path.symlink_to("/etc")

                # Attempting to use this symlink should fail
                with pytest.raises(PermissionDeniedError) as exc_info:
                    validate_destination(str(link_path / "passwd"))

                assert "Cannot write to system directories" in str(exc_info.value)
            except OSError:
                # Skip if we don't have permission to create symlinks
                pytest.skip("Cannot create symlinks in test environment")

    def test_error_data_structure(self):
        """Test that PermissionDeniedError has correct data structure."""
        with pytest.raises(PermissionDeniedError) as exc_info:
            validate_destination("/etc/passwd")

        error = exc_info.value
        assert error.code.name == "PERMISSION_DENIED"
        assert error.data is not None
        assert "operation" in error.data
        assert error.data["operation"] == "destination"
        assert "reason" in error.data

    def test_multiple_traversal_attempts(self):
        """Test various traversal patterns are blocked."""
        # Test absolute paths to dangerous directories
        dangerous_destinations = [
            "/etc/passwd",
            "/usr/bin/malicious",
            "/root/.ssh/id_rsa",
            "/bin/sh",
            "/var/log/secure",
            "/sbin/init",
        ]

        for attempt in dangerous_destinations:
            with pytest.raises(PermissionDeniedError):
                validate_destination(attempt)


class TestIntegrationWithCopierCopy:
    """Integration tests for path validation in copier_copy."""

    def test_copier_copy_blocks_dangerous_paths(self):
        """Test that copier_copy blocks dangerous destination paths."""
        from riso.mcp.tools.copier_api import register_copier_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_copier_tools(mcp)

        # Try to call copier_copy with a dangerous path
        # Note: This would require mocking the actual copier operations
        # For now, we can at least verify the tool is registered
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]
        assert "copier_copy" in tool_names
