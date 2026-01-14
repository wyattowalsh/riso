"""Unit tests for render_client.py automation utilities.

Tests cover:
- Variant name validation
- RenderClient initialization and configuration
- Template rendering functionality
- Module listing
- Compliance checkpoint recording
- Sample variant retrieval
- Error handling for various failure scenarios
- HTTP request construction and authentication
"""
import json
import urllib.error
import urllib.request
from typing import Any, Mapping
from unittest.mock import MagicMock, Mock, patch

import pytest

from automation.render_client import (
    DEFAULT_BASE_URL,
    APIError,
    RenderClient,
    _validate_variant_name,
)


# -----------------------------------------------------------------------------
# Variant Name Validation Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestVariantNameValidation:
    """Tests for variant name validation logic."""

    def test_validate_variant_name_valid_basic(self):
        """Test validation of a simple valid variant name."""
        result = _validate_variant_name("my-variant")
        assert result == "my-variant"

    def test_validate_variant_name_valid_with_numbers(self):
        """Test validation of variant name with numbers."""
        result = _validate_variant_name("variant123")
        assert result == "variant123"

    def test_validate_variant_name_valid_with_underscores(self):
        """Test validation of variant name with underscores and dashes."""
        result = _validate_variant_name("my_variant-name_123")
        assert result == "my_variant-name_123"

    def test_validate_variant_name_empty_raises_error(self):
        """Test that empty variant name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            _validate_variant_name("")

    def test_validate_variant_name_too_long_raises_error(self):
        """Test that variant name longer than 64 chars raises ValueError."""
        long_name = "a" * 65
        with pytest.raises(ValueError, match="too long.*> 64 chars"):
            _validate_variant_name(long_name)

    def test_validate_variant_name_invalid_start_char_raises_error(self):
        """Test that variant name starting with invalid char raises ValueError."""
        with pytest.raises(ValueError, match="Invalid variant name"):
            _validate_variant_name("-invalid")

    def test_validate_variant_name_uppercase_raises_error(self):
        """Test that variant name with uppercase raises ValueError."""
        with pytest.raises(ValueError, match="Invalid variant name"):
            _validate_variant_name("MyVariant")

    def test_validate_variant_name_special_chars_raises_error(self):
        """Test that variant name with special characters raises ValueError."""
        with pytest.raises(ValueError, match="Invalid variant name"):
            _validate_variant_name("my@variant")


# -----------------------------------------------------------------------------
# RenderClient Initialization Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestRenderClientInit:
    """Tests for RenderClient initialization."""

    def test_init_with_defaults(self):
        """Test client initialization with default parameters."""
        client = RenderClient()
        assert client.base_url == DEFAULT_BASE_URL
        assert client.token is None
        assert client.timeout == 30.0

    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        custom_url = "https://custom.api.com/v1"
        client = RenderClient(base_url=custom_url)
        assert client.base_url == custom_url

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        client = RenderClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_init_with_token(self):
        """Test client initialization with authentication token."""
        token = "test-token-12345"
        client = RenderClient(token=token)
        assert client.token == token

    def test_init_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = RenderClient(timeout=60.0)
        assert client.timeout == 60.0


# -----------------------------------------------------------------------------
# Template Rendering Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestRenderTemplate:
    """Tests for template rendering functionality."""

    @patch.object(RenderClient, "_request")
    def test_render_template_success(self, mock_request):
        """Test successful template rendering."""
        mock_response = {"status": "success", "data": {"output": "rendered content"}}
        mock_request.return_value = mock_response

        client = RenderClient()
        prompts = {"key1": "value1", "key2": 42}
        result = client.render_template("test-variant", prompts)

        assert result == mock_response
        mock_request.assert_called_once_with(
            "POST",
            "/templates/riso/render",
            {"variantName": "test-variant", "prompts": prompts},
        )

    @patch.object(RenderClient, "_request")
    def test_render_template_with_complex_prompts(self, mock_request):
        """Test template rendering with nested prompt data."""
        mock_request.return_value = {"status": "success"}

        client = RenderClient()
        prompts = {
            "name": "test",
            "config": {"nested": True, "values": [1, 2, 3]},
            "metadata": None,
        }
        client.render_template("variant", prompts)

        call_args = mock_request.call_args[0]
        assert call_args[2]["prompts"] == prompts

    @patch.object(RenderClient, "_request")
    def test_render_template_error_propagates(self, mock_request):
        """Test that API errors are propagated from render_template."""
        mock_request.side_effect = APIError(message="Render failed", status_code=400)

        client = RenderClient()
        with pytest.raises(APIError, match="Render failed"):
            client.render_template("variant", {})


# -----------------------------------------------------------------------------
# Module Listing Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestListModules:
    """Tests for module listing functionality."""

    @patch.object(RenderClient, "_request")
    def test_list_modules_success(self, mock_request):
        """Test successful module listing."""
        mock_response = {
            "modules": [
                {"name": "module1", "version": "1.0"},
                {"name": "module2", "version": "2.0"},
            ]
        }
        mock_request.return_value = mock_response

        client = RenderClient()
        result = client.list_modules()

        assert result == mock_response
        mock_request.assert_called_once_with("GET", "/templates/riso/modules")

    @patch.object(RenderClient, "_request")
    def test_list_modules_empty_response(self, mock_request):
        """Test module listing with empty response."""
        mock_request.return_value = {"modules": []}

        client = RenderClient()
        result = client.list_modules()

        assert result == {"modules": []}


# -----------------------------------------------------------------------------
# Compliance Checkpoint Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestRecordComplianceCheckpoint:
    """Tests for compliance checkpoint recording."""

    @patch.object(RenderClient, "_request")
    def test_record_checkpoint_minimal_params(self, mock_request):
        """Test recording checkpoint with minimal required parameters."""
        mock_request.return_value = {"id": "checkpoint-123"}

        client = RenderClient()
        result = client.record_compliance_checkpoint(
            principle="security",
            status="pass",
            evidence="All tests passed",
        )

        assert result == {"id": "checkpoint-123"}
        mock_request.assert_called_once()
        call_payload = mock_request.call_args[0][2]
        assert call_payload["principle"] == "security"
        assert call_payload["status"] == "pass"
        assert call_payload["evidence"] == "All tests passed"
        assert "metadata" not in call_payload

    @patch.object(RenderClient, "_request")
    def test_record_checkpoint_with_metadata(self, mock_request):
        """Test recording checkpoint with additional metadata."""
        mock_request.return_value = {"id": "checkpoint-456"}
        metadata = {"test_count": 42, "duration_ms": 1500}

        client = RenderClient()
        result = client.record_compliance_checkpoint(
            principle="performance",
            status="pass",
            evidence="Benchmark completed",
            metadata=metadata,
        )

        assert result == {"id": "checkpoint-456"}
        call_payload = mock_request.call_args[0][2]
        assert call_payload["metadata"] == metadata

    @patch.object(RenderClient, "_request")
    def test_record_checkpoint_empty_response(self, mock_request):
        """Test checkpoint recording when API returns None."""
        mock_request.return_value = None

        client = RenderClient()
        result = client.record_compliance_checkpoint(
            principle="test",
            status="pass",
            evidence="ok",
        )

        assert result is None


# -----------------------------------------------------------------------------
# Sample Variant Retrieval Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestGetSample:
    """Tests for sample variant retrieval."""

    @patch.object(RenderClient, "_request")
    def test_get_sample_success(self, mock_request):
        """Test successful sample variant retrieval."""
        mock_response = {"variant": "test-variant", "data": {"key": "value"}}
        mock_request.return_value = mock_response

        client = RenderClient()
        result = client.get_sample("test-variant")

        assert result == mock_response
        mock_request.assert_called_once()
        assert "/templates/riso/samples/test-variant" in mock_request.call_args[0][1]

    @patch.object(RenderClient, "_request")
    def test_get_sample_url_encoding(self, mock_request):
        """Test that variant name is properly URL-encoded."""
        mock_request.return_value = {}

        client = RenderClient()
        client.get_sample("variant-with-dash")

        call_path = mock_request.call_args[0][1]
        assert "/templates/riso/samples/variant-with-dash" in call_path

    def test_get_sample_invalid_variant_name(self):
        """Test that invalid variant name raises ValueError."""
        client = RenderClient()

        with pytest.raises(ValueError, match="Invalid variant name"):
            client.get_sample("Invalid@Variant")

    def test_get_sample_empty_variant_name(self):
        """Test that empty variant name raises ValueError."""
        client = RenderClient()

        with pytest.raises(ValueError, match="cannot be empty"):
            client.get_sample("")


# -----------------------------------------------------------------------------
# HTTP Request Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestHTTPRequest:
    """Tests for internal HTTP request handling."""

    @patch("urllib.request.urlopen")
    def test_request_get_method(self, mock_urlopen):
        """Test GET request construction."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": "success"}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = RenderClient()
        result = client._request("GET", "/test/path")

        assert result == {"result": "success"}
        request_call = mock_urlopen.call_args[0][0]
        assert request_call.get_method() == "GET"
        assert "/test/path" in request_call.full_url

    @patch("urllib.request.urlopen")
    def test_request_post_with_payload(self, mock_urlopen):
        """Test POST request with JSON payload."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "created"}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = RenderClient()
        payload = {"key": "value", "number": 123}
        result = client._request("POST", "/test/create", payload)

        assert result == {"status": "created"}
        request_call = mock_urlopen.call_args[0][0]
        assert request_call.get_method() == "POST"
        assert request_call.data == json.dumps(payload).encode("utf-8")

    @patch("urllib.request.urlopen")
    def test_request_with_authentication_header(self, mock_urlopen):
        """Test that authentication token is included in headers."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = RenderClient(token="test-token-abc")
        client._request("GET", "/test")

        request_call = mock_urlopen.call_args[0][0]
        assert request_call.headers["Authorization"] == "Bearer test-token-abc"

    @patch("urllib.request.urlopen")
    def test_request_empty_response_returns_none(self, mock_urlopen):
        """Test that empty response body returns None."""
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = RenderClient()
        result = client._request("GET", "/test")

        assert result is None

    @patch("urllib.request.urlopen")
    def test_request_whitespace_only_response_returns_none(self, mock_urlopen):
        """Test that whitespace-only response returns None."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"   \n\t  "
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = RenderClient()
        result = client._request("GET", "/test")

        assert result is None


# -----------------------------------------------------------------------------
# Error Handling Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestErrorHandling:
    """Tests for error handling in API requests."""

    @patch("urllib.request.urlopen")
    def test_http_error_with_json_payload(self, mock_urlopen):
        """Test handling of HTTPError with JSON error payload."""
        error_payload = {"error": "Invalid request", "code": "ERR_400"}
        http_error = urllib.error.HTTPError(
            url="http://test.com",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=None,
        )
        http_error.read = Mock(return_value=json.dumps(error_payload).encode())
        mock_urlopen.side_effect = http_error

        client = RenderClient()
        with pytest.raises(APIError) as exc_info:
            client._request("GET", "/test")

        assert exc_info.value.status_code == 400
        assert exc_info.value.payload == error_payload
        assert "400" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_http_error_without_payload(self, mock_urlopen):
        """Test handling of HTTPError without error payload."""
        http_error = urllib.error.HTTPError(
            url="http://test.com",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=None,
        )
        http_error.read = Mock(return_value=b"")
        mock_urlopen.side_effect = http_error

        client = RenderClient()
        with pytest.raises(APIError) as exc_info:
            client._request("GET", "/test")

        assert exc_info.value.status_code == 500
        assert exc_info.value.payload is None

    @patch("urllib.request.urlopen")
    def test_http_error_invalid_json_payload(self, mock_urlopen):
        """Test handling of HTTPError with malformed JSON."""
        http_error = urllib.error.HTTPError(
            url="http://test.com",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=None,
        )
        http_error.read = Mock(return_value=b"Not valid JSON{{{")
        mock_urlopen.side_effect = http_error

        client = RenderClient()
        with pytest.raises(APIError) as exc_info:
            client._request("GET", "/test")

        assert exc_info.value.status_code == 400
        assert exc_info.value.payload is None  # Failed to parse, so None

    @patch("urllib.request.urlopen")
    def test_url_error_network_failure(self, mock_urlopen):
        """Test handling of URLError (network failures)."""
        url_error = urllib.error.URLError(reason="Connection refused")
        mock_urlopen.side_effect = url_error

        client = RenderClient()
        with pytest.raises(APIError) as exc_info:
            client._request("GET", "/test")

        assert exc_info.value.status_code is None
        assert "Connection refused" in str(exc_info.value)

    def test_api_error_str_with_status_code(self):
        """Test APIError string representation with status code."""
        error = APIError(message="Test error", status_code=404)
        assert str(error) == "Test error (status=404)"

    def test_api_error_str_without_status_code(self):
        """Test APIError string representation without status code."""
        error = APIError(message="Test error")
        assert str(error) == "Test error"

    def test_api_error_with_payload(self):
        """Test APIError with additional payload data."""
        payload = {"field": "username", "error": "already exists"}
        error = APIError(
            message="Validation failed",
            status_code=422,
            payload=payload,
        )
        assert error.payload == payload
        assert error.status_code == 422


# -----------------------------------------------------------------------------
# Integration-Style Tests
# -----------------------------------------------------------------------------


@pytest.mark.unit
class TestRenderClientIntegration:
    """Integration-style tests exercising multiple methods."""

    @patch("urllib.request.urlopen")
    def test_full_workflow_render_and_checkpoint(self, mock_urlopen):
        """Test complete workflow: render template then record checkpoint."""
        # Setup mock responses for multiple calls
        responses = [
            b'{"status": "success", "output": "rendered"}',
            b'{"checkpoint_id": "cp-123"}',
        ]
        response_iter = iter(responses)

        def create_response(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.read.return_value = next(response_iter)
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=False)
            return mock_response

        mock_urlopen.side_effect = create_response

        # Execute workflow
        client = RenderClient(base_url="https://api.test.com", token="test-token")

        # Render template
        render_result = client.render_template(
            "production-variant",
            {"config": "production"},
        )
        assert render_result["status"] == "success"

        # Record checkpoint
        checkpoint_result = client.record_compliance_checkpoint(
            principle="deployment",
            status="pass",
            evidence="Template rendered successfully",
        )
        assert checkpoint_result["checkpoint_id"] == "cp-123"

    @patch("urllib.request.urlopen")
    def test_timeout_configuration(self, mock_urlopen):
        """Test that custom timeout is used in requests."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = RenderClient(timeout=45.0)
        client._request("GET", "/test")

        # Verify timeout was passed to urlopen
        assert mock_urlopen.call_args[1]["timeout"] == 45.0
