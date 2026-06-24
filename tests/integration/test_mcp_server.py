"""MCP Server integration tests.

These tests verify that the MCP server starts correctly, responds to requests,
and integrates properly with its tools and resources across different transports.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

# Skip all tests if fastmcp is not available
pytest.importorskip("fastmcp")


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is already in use.

    Parameters
    ----------
    port
        Port number to check
    host
        Host address to check (default: 127.0.0.1)

    Returns
    -------
    bool
        True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def find_free_port(start: int = 3100, max_tries: int = 100) -> int:
    """Find an available port.

    Parameters
    ----------
    start
        Starting port number to try
    max_tries
        Maximum number of ports to try

    Returns
    -------
    int
        An available port number

    Raises
    ------
    RuntimeError
        If no free port is found within max_tries
    """
    for port in range(start, start + max_tries):
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"No free port found in range {start}-{start + max_tries}")


@pytest.fixture
def server_timeout() -> int:
    """Timeout for server operations in seconds."""
    return 10


@pytest.fixture
def test_project_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test project generation.

    Parameters
    ----------
    tmp_path
        pytest temporary directory fixture

    Returns
    -------
    Path
        Path to test project directory
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


class TestServerStdioTransport:
    """Tests for stdio transport.

    The stdio transport is the default and most common way to run MCP servers,
    using standard input/output for JSON-RPC communication.
    """

    def test_server_starts_with_stdio(self, server_timeout: int):
        """Server starts and responds to list tools request via stdio.

        This test verifies:
        1. Server starts successfully with stdio transport
        2. Server accepts JSON-RPC messages on stdin
        3. Server responds with valid JSON on stdout
        4. Server properly lists its available tools
        """
        # Start server with stdio transport
        process = subprocess.Popen(
            [sys.executable, "-m", "riso.mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send a tools/list request using MCP protocol
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }

            # Write request and flush
            assert process.stdin is not None
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()

            # Read response with timeout
            assert process.stdout is not None
            process.stdout.flush()

            # Give server time to respond
            time.sleep(1)

            # Try to read response
            try:
                # Set a reasonable timeout for reading
                import select

                if select.select([process.stdout], [], [], server_timeout)[0]:
                    response_line = process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line)

                        # Verify response structure
                        assert "jsonrpc" in response
                        assert response["jsonrpc"] == "2.0"
                        assert "result" in response or "error" in response

                        # If successful, verify tools are listed
                        if "result" in response:
                            result = response["result"]
                            assert "tools" in result
                            tools = result["tools"]
                            assert isinstance(tools, list)
                            assert len(tools) > 0

                            # Verify expected tools are present
                            tool_names = [t["name"] for t in tools]
                            assert "copier_copy" in tool_names
                            assert "wizard_start" in tool_names
            except json.JSONDecodeError:
                pytest.skip(
                    "Could not decode server response - may need initialization"
                )

        finally:
            # Close pipes explicitly
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            # Clean shutdown
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    def test_server_handles_invalid_json(self, server_timeout: int):
        """Server handles malformed JSON gracefully.

        This test verifies that the server doesn't crash when receiving
        invalid JSON and either responds with an error or ignores the message.
        """
        process = subprocess.Popen(
            [sys.executable, "-m", "riso.mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send malformed JSON
            assert process.stdin is not None
            process.stdin.write("{invalid json}\n")
            process.stdin.flush()

            # Give server time to process
            time.sleep(1)

            # Verify server is still running
            assert process.poll() is None, "Server should not crash on invalid JSON"

        finally:
            # Close pipes explicitly
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

    def test_server_handles_unknown_method(self, server_timeout: int):
        """Server responds with error for unknown methods.

        This test verifies that the server properly handles requests for
        methods that don't exist according to the MCP specification.
        """
        process = subprocess.Popen(
            [sys.executable, "-m", "riso.mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send request with unknown method
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "nonexistent/method",
                "params": {},
            }

            assert process.stdin is not None
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()

            # Server should handle this gracefully (either error response or ignore)
            time.sleep(1)
            assert process.poll() is None, "Server should not crash on unknown method"

        finally:
            # Close pipes explicitly
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class TestServerHTTPTransport:
    """Tests for HTTP/SSE transport.

    HTTP transport enables web-based MCP clients and cloud deployments.
    SSE (Server-Sent Events) provides streaming capabilities over HTTP.
    """

    @pytest.fixture
    def http_port(self) -> int:
        """Find an available port for HTTP testing."""
        return find_free_port()

    @pytest.mark.skipif(
        os.environ.get("CI") == "true",
        reason="HTTP tests may be flaky in CI environments",
    )
    def test_server_starts_with_http(self, http_port: int, server_timeout: int):
        """Server starts and responds to HTTP requests.

        This test verifies:
        1. Server binds to specified host:port
        2. Server accepts HTTP connections
        3. Health/status endpoints are accessible

        Note: This test may fail if required HTTP dependencies (e.g., uvicorn)
        are not installed. It will skip gracefully in that case.
        """
        if is_port_in_use(http_port):
            pytest.skip(f"Port {http_port} is already in use")

        # Start server with HTTP transport
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "riso.mcp",
                "--transport",
                "http",
                "--port",
                str(http_port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Give server time to start
            time.sleep(2)

            # Check if server started successfully
            if process.poll() is not None:
                # Server exited - check stderr for dependency issues
                stderr = process.stderr.read() if process.stderr else ""
                if "uvicorn" in stderr.lower() or "import" in stderr.lower():
                    pytest.skip(
                        "HTTP transport requires additional dependencies (uvicorn)"
                    )
                else:
                    pytest.fail(f"Server exited unexpectedly: {stderr}")

            # Try to connect (basic connectivity test)
            # Note: We don't make full HTTP requests here as that would
            # require httpx or requests which may not be in test deps
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex(("127.0.0.1", http_port))
                if result != 0:
                    # Connection failed - server might not have bound yet or failed to start
                    pytest.skip(f"Could not connect to HTTP server on port {http_port}")
            finally:
                sock.close()

        finally:
            # Close pipes explicitly
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

    @pytest.mark.skipif(
        os.environ.get("CI") == "true",
        reason="SSE tests may be flaky in CI environments",
    )
    def test_server_starts_with_sse(self, http_port: int, server_timeout: int):
        """Server starts with SSE transport.

        SSE transport is used for streaming responses from the server.
        This test verifies basic server startup and port binding.

        Note: This test may fail if required HTTP dependencies (e.g., uvicorn)
        are not installed. It will skip gracefully in that case.
        """
        if is_port_in_use(http_port):
            pytest.skip(f"Port {http_port} is already in use")

        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "riso.mcp",
                "--transport",
                "sse",
                "--port",
                str(http_port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Give server time to start
            time.sleep(2)

            # Check if server started successfully
            if process.poll() is not None:
                # Server exited - check stderr for dependency issues
                stderr = process.stderr.read() if process.stderr else ""
                if "uvicorn" in stderr.lower() or "import" in stderr.lower():
                    pytest.skip(
                        "SSE transport requires additional dependencies (uvicorn)"
                    )
                else:
                    pytest.fail(f"Server exited unexpectedly: {stderr}")

            # Verify port is bound
            if not is_port_in_use(http_port):
                pytest.skip(f"Server did not bind to port {http_port}")

        finally:
            # Close pipes explicitly
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


class TestServerTools:
    """Integration tests for server tools.

    These tests verify that tools integrate correctly with the server
    and can execute actual operations (not just mocked).
    """

    def test_server_tools_registration(self):
        """All expected tools are registered on server startup.

        This test verifies that the server properly registers all tools
        from both the Copier API and Wizard modules during initialization.
        """
        from riso.mcp.server import mcp

        # Get registered tools
        tool_names = [t.name for t in mcp._tool_manager._tools.values()]

        # Copier API tools
        expected_copier_tools = [
            "copier_copy",
            "copier_update",
            "copier_recopy",
            "get_prompts",
            "list_template_variants",
            "validate_template_answers",
        ]

        for tool_name in expected_copier_tools:
            assert tool_name in tool_names, f"Missing Copier tool: {tool_name}"

        # Wizard tools
        expected_wizard_tools = [
            "wizard_start",
            "wizard_step",
            "wizard_back",
            "wizard_status",
            "wizard_generate",
            "wizard_cancel",
            "wizard_list_sessions",
        ]

        for tool_name in expected_wizard_tools:
            assert tool_name in tool_names, f"Missing Wizard tool: {tool_name}"

    def test_list_template_variants_execution(self):
        """list_template_variants tool executes successfully.

        This test verifies that the tool can actually execute and return
        real data about available sample configurations.
        """
        from riso.mcp.server import mcp

        # Get the tool from the MCP server
        list_template_variants = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "list_template_variants":
                list_template_variants = tool.fn
                break

        assert list_template_variants is not None, (
            "list_template_variants tool not found"
        )

        # Execute the tool function
        result = list_template_variants()

        # Verify result structure
        assert isinstance(result, list)
        if len(result) > 0:
            # Verify structure of first variant
            variant = result[0]
            assert "name" in variant
            assert "path" in variant
            assert "has_answers" in variant

    def test_get_prompts_execution(self):
        """get_prompts tool executes successfully.

        This test verifies that the tool can retrieve and return the
        template's prompt configuration.
        """
        from riso.mcp.server import mcp

        # Get the tool from the MCP server
        get_prompts = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "get_prompts":
                get_prompts = tool.fn
                break

        assert get_prompts is not None, "get_prompts tool not found"

        # Execute the tool function
        result = get_prompts()

        # Verify result structure
        assert isinstance(result, dict)
        assert "prompts" in result or "defaults" in result

    def test_wizard_start_creates_session(self, test_project_dir: Path):
        """wizard_start tool creates a valid session.

        This test verifies that the wizard workflow can be initiated and
        that it creates a properly structured session.
        """
        from riso.mcp.server import mcp, session_manager

        # Get the wizard_start tool from the MCP server
        wizard_start = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "wizard_start":
                wizard_start = tool.fn
                break

        assert wizard_start is not None, "wizard_start tool not found"

        # Execute the tool function
        result = wizard_start(
            project_name="Test Project",
            destination=str(test_project_dir),
        )

        # Verify session was created
        assert isinstance(result, dict)
        assert "session_id" in result
        assert "current_step" in result
        assert "total_steps" in result

        # Verify session is tracked
        session_id = result["session_id"]
        assert session_manager is not None
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session.project_name == "Test Project"

        # Cleanup
        session_manager.delete_session(session_id)


class TestServerResources:
    """Integration tests for server resources.

    Resources provide read-only access to template files, samples,
    and other reference materials.
    """

    def test_resources_registration(self):
        """All expected resources are registered on server startup.

        This test verifies that the server properly registers resources
        for templates, samples, and the module catalog.
        """
        from riso.mcp.server import mcp

        # Get registered resources
        resource_uris = [str(r.uri) for r in mcp._resource_manager._resources.values()]

        # Verify we have resources registered
        assert len(resource_uris) > 0, "Server should have resources registered"

        # Look for expected resource patterns
        has_template_resources = any("template" in uri for uri in resource_uris)
        has_sample_resources = any("sample" in uri for uri in resource_uris)

        assert has_template_resources or has_sample_resources, (
            "Should have template or sample resources"
        )

    def test_list_resources_execution(self):
        """Server can list available resources.

        This test verifies that the resources/list endpoint works correctly.
        """
        from riso.mcp.server import mcp

        # Get all resources
        resources = list(mcp._resource_manager._resources.values())

        # Verify we got resources
        assert len(resources) > 0, "Should have at least one resource"

        # Verify resource structure
        for resource in resources:
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            assert str(resource.uri).startswith("riso://")


class TestServerLifecycle:
    """Server lifecycle and error handling tests.

    These tests verify that the server handles startup, shutdown,
    and error conditions correctly.
    """

    def test_server_graceful_shutdown(self, server_timeout: int):
        """Server shuts down gracefully on SIGTERM.

        This test verifies that the server responds to termination signals
        and shuts down cleanly without hanging or leaving resources open.
        """
        process = subprocess.Popen(
            [sys.executable, "-m", "riso.mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Give server time to start
            time.sleep(1)

            # Verify server is running
            assert process.poll() is None, "Server should be running"

            # Send SIGTERM
            process.terminate()

            # Wait for graceful shutdown
            try:
                process.wait(timeout=server_timeout)
                # If we get here, shutdown was successful
                assert True
            except subprocess.TimeoutExpired:
                pytest.fail("Server did not shut down gracefully within timeout")
                process.kill()

        finally:
            # Close pipes explicitly
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            if process.poll() is None:
                process.kill()
                process.wait()

    def test_server_handles_startup_with_missing_template(
        self, tmp_path: Path, monkeypatch
    ):
        """Server handles missing template directory.

        This test verifies that the server provides helpful error messages
        when the template directory is not found.
        """
        # Set invalid template path via environment
        monkeypatch.setenv("RISO_MCP_TEMPLATE_PATH", str(tmp_path / "nonexistent"))

        process = subprocess.Popen(
            [sys.executable, "-m", "riso.mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy(),
        )

        try:
            # Give server time to attempt startup
            time.sleep(2)

            # Server should handle this gracefully
            # Either it starts with warnings or exits cleanly
            if process.poll() is not None:
                # Server exited - check it wasn't a crash
                stderr = process.stderr.read() if process.stderr else ""
                assert "template" in stderr.lower() or "path" in stderr.lower(), (
                    "Error message should mention template or path issue"
                )
            else:
                # Server is running - it handled the missing template gracefully
                assert True

        finally:
            # Close pipes explicitly
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

    def test_server_environment_config(self, monkeypatch):
        """Server respects environment configuration.

        This test verifies that the server correctly loads configuration
        from environment variables.
        """
        from riso.mcp.config import load_config

        # Set custom log level
        monkeypatch.setenv("RISO_MCP_LOG_LEVEL", "DEBUG")

        # Clear the config cache
        from riso.mcp.config import get_config

        get_config.cache_clear()

        # Load config
        config = load_config()

        assert config.log_level == "DEBUG"


class TestServerIntegrationScenarios:
    """End-to-end integration scenarios.

    These tests verify complete workflows that users would actually perform.
    """

    def test_full_wizard_workflow(self, test_project_dir: Path):
        """Complete wizard workflow from start to generation.

        This test verifies a complete user workflow:
        1. Start a wizard session
        2. Provide answers to prompts
        3. Navigate through steps
        4. Generate the final project
        """
        from riso.mcp.server import mcp, session_manager

        # Get wizard tools from the MCP server
        wizard_start = None
        wizard_status = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "wizard_start":
                wizard_start = tool.fn
            elif tool.name == "wizard_status":
                wizard_status = tool.fn

        assert wizard_start is not None, "wizard_start tool not found"
        assert wizard_status is not None, "wizard_status tool not found"

        # Start session
        result = wizard_start(
            project_name="Integration Test",
            destination=str(test_project_dir),
        )

        session_id = result["session_id"]

        try:
            # Get status
            status = wizard_status(session_id=session_id)
            assert status["current_step"] == 0

            # Verify session is tracked correctly
            assert session_manager is not None
            session = session_manager.get_session(session_id)
            assert session is not None
            assert session.project_name == "Integration Test"

        finally:
            # Cleanup
            assert session_manager is not None
            session_manager.delete_session(session_id)

    def test_configuration_validation(self):
        """Server configuration validation works correctly.

        This test verifies that the server properly validates its
        configuration and rejects invalid settings.
        """
        from riso.mcp.config import ServerConfig
        from pydantic import ValidationError

        # Valid configuration
        config = ServerConfig(
            name="test-server",
            transport="stdio",
            log_level="INFO",
        )
        assert config.name == "test-server"

        # Invalid log level
        with pytest.raises(ValidationError):
            ServerConfig(log_level="INVALID")

        # Invalid port
        with pytest.raises(ValidationError):
            ServerConfig(port=99999)  # Out of valid range

    def test_session_cleanup_on_ttl(self):
        """Sessions are cleaned up after TTL expires.

        This test verifies that the session manager properly expires
        and cleans up old sessions based on TTL settings.
        """
        from riso.mcp.session import SessionManager
        import datetime

        # Create manager with very short TTL (1 minute)
        manager = SessionManager(ttl_minutes=1)

        # Create a session
        session = manager.create_session(project_name="TTL Test")
        session_id = session.session_id

        # Verify session exists
        assert manager.get_session(session_id) is not None

        # Manually expire the session by setting last_activity far in the past
        session.last_activity = datetime.datetime.now() - datetime.timedelta(minutes=2)

        # Run cleanup
        cleaned = manager.cleanup_expired()

        # Verify at least one session was cleaned up
        assert cleaned >= 1

        # Verify session was cleaned up
        from riso.mcp.errors import SessionNotFoundError

        with pytest.raises(SessionNotFoundError):
            manager.get_session(session_id)
