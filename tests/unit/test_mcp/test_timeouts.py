"""Unit tests for timeout enforcement functionality."""

from __future__ import annotations

import pytest

from riso.mcp.errors import MCPErrorCode, OperationTimeoutError


class TestOperationTimeoutError:
    """Test OperationTimeoutError exception class."""

    def test_basic_timeout_error(self) -> None:
        """Test basic timeout error creation."""
        error = OperationTimeoutError(
            operation="test_operation",
            timeout_seconds=30,
        )

        assert "test_operation" in str(error)
        assert "30s" in str(error)
        assert error.code == MCPErrorCode.OPERATION_TIMEOUT

    def test_timeout_error_with_details(self) -> None:
        """Test timeout error with details."""
        error = OperationTimeoutError(
            operation="run_copy",
            timeout_seconds=120,
            details="Template rendering took too long",
        )

        assert "run_copy" in str(error)
        assert "120s" in str(error)
        assert "Template rendering took too long" in str(error)

    def test_timeout_error_data(self) -> None:
        """Test timeout error serializes data correctly."""
        error = OperationTimeoutError(
            operation="copier_update",
            timeout_seconds=60,
            details="Git operations slow",
        )

        assert error.data["operation"] == "copier_update"
        assert error.data["timeout_seconds"] == 60
        assert error.data["details"] == "Git operations slow"

    def test_timeout_error_code(self) -> None:
        """Test timeout error uses correct error code."""
        error = OperationTimeoutError(
            operation="test",
            timeout_seconds=10,
        )

        assert error.code == MCPErrorCode.OPERATION_TIMEOUT
        assert error.code == -32008

    def test_timeout_error_mcp_format(self) -> None:
        """Test timeout error converts to MCP format."""
        error = OperationTimeoutError(
            operation="run_generator",
            timeout_seconds=300,
            details="Slow network",
        )

        mcp_error = error.to_dict()

        assert mcp_error["code"] == -32008
        assert "run_generator" in mcp_error["message"]
        assert "300s" in mcp_error["message"]

    def test_timeout_error_without_details(self) -> None:
        """Test timeout error without optional details."""
        error = OperationTimeoutError(
            operation="test_op",
            timeout_seconds=45,
            details=None,
        )

        assert "test_op" in str(error)
        assert error.data["details"] is None


class TestTimeoutEnforcement:
    """Test timeout enforcement in template operations."""

    def test_run_with_timeout_success(self) -> None:
        """Test that fast operations complete within timeout."""
        from riso.template import _run_with_timeout

        def fast_operation() -> str:
            return "success"

        result = _run_with_timeout(fast_operation, 5)
        assert result == "success"

    def test_run_with_timeout_raises_on_timeout(self) -> None:
        """Test that slow operations raise OperationTimeoutError."""
        import time
        from riso.template import _run_with_timeout

        def slow_operation() -> None:
            time.sleep(3)

        with pytest.raises(OperationTimeoutError) as exc_info:
            _run_with_timeout(slow_operation, 1)

        assert exc_info.value.code == MCPErrorCode.OPERATION_TIMEOUT
        assert "slow_operation" in str(exc_info.value)

    def test_run_with_timeout_none_disables_timeout(self) -> None:
        """Test that None timeout disables timeout checking."""
        from riso.template import _run_with_timeout

        def operation() -> str:
            return "no timeout"

        result = _run_with_timeout(operation, None)
        assert result == "no timeout"
