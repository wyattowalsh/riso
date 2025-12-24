#!/usr/bin/env python3
"""Client utilities for interacting with the Riso automation API.

The functions intentionally rely on the Python standard library so that
downstream renders are not forced to install additional dependencies before
running governance automation.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, TypedDict


# Valid variant name pattern
VALID_VARIANT_PATTERN = re.compile(r'^[a-z0-9][a-z0-9_-]*$')


def _validate_variant_name(name: str) -> str:
    """Validate variant name is safe for URL construction.

    Args:
        name: The variant name to validate

    Returns:
        The validated name

    Raises:
        ValueError: If the name is invalid
    """
    if not name:
        raise ValueError("Variant name cannot be empty")
    if len(name) > 64:
        raise ValueError(f"Variant name too long: {len(name)} > 64 chars")
    if not VALID_VARIANT_PATTERN.match(name):
        raise ValueError(
            f"Invalid variant name: {name}. "
            f"Must match pattern: {VALID_VARIANT_PATTERN.pattern}"
        )
    return name


class RenderRequest(TypedDict):
    """Request payload for template rendering."""
    variantName: str
    prompts: dict[str, Any]


class ComplianceCheckpointRequest(TypedDict, total=False):
    """Request payload for recording a compliance checkpoint."""
    principle: str
    status: str
    evidence: str
    metadata: dict[str, Any]


DEFAULT_BASE_URL = "https://ci.example.com/api"


@dataclass(slots=True)
class APIError(Exception):
    """Raised when the automation API returns an error response."""

    message: str
    status_code: int | None = None
    payload: Mapping[str, Any] | None = None

    def __str__(self) -> str:
        """Format error message with optional status code.

        Returns:
            String representation of the error with status code if available.
        """
        suffix = f" (status={self.status_code})" if self.status_code else ""
        return f"{self.message}{suffix}"


class RenderClient:
    """Minimal automation client covering render, module listing, and compliance endpoints."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize a new render client.

        Args:
            base_url: Base URL for the automation API. Defaults to DEFAULT_BASE_URL.
            token: Optional authentication token for API requests.
            timeout: Request timeout in seconds. Defaults to 30.0.
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def render_template(self, variant_name: str, prompts: Mapping[str, Any]) -> Mapping[str, Any]:
        """Render a template with the given variant and prompts.

        Args:
            variant_name: Name of the variant to render.
            prompts: Dictionary of prompt values for template generation.

        Returns:
            Response data from the render endpoint.

        Raises:
            APIError: If the API request fails.
        """
        payload: RenderRequest = {"variantName": variant_name, "prompts": dict(prompts)}
        return self._request("POST", "/templates/riso/render", payload)

    def list_modules(self) -> Mapping[str, Any]:
        """List all available modules for the Riso template.

        Returns:
            Response data containing module information.

        Raises:
            APIError: If the API request fails.
        """
        return self._request("GET", "/templates/riso/modules")

    def record_compliance_checkpoint(
        self,
        *,
        principle: str,
        status: str,
        evidence: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        """Record a compliance checkpoint for governance tracking.

        Args:
            principle: Name of the compliance principle being checked.
            status: Status of the compliance check (e.g., "pass", "fail").
            evidence: Evidence supporting the compliance status.
            metadata: Optional additional metadata for the checkpoint.

        Returns:
            Response data from the compliance endpoint, or None if empty response.

        Raises:
            APIError: If the API request fails.
        """
        payload: ComplianceCheckpointRequest = {
            "principle": principle,
            "status": status,
            "evidence": evidence,
        }
        if metadata:
            payload["metadata"] = dict(metadata)
        return self._request("POST", "/templates/riso/compliance-checks", payload)

    def get_sample(self, variant_name: str) -> Mapping[str, Any]:
        """Retrieve information about a specific sample variant.

        Args:
            variant_name: Name of the sample variant to retrieve.

        Returns:
            Response data containing sample variant information.

        Raises:
            ValueError: If the variant name is invalid.
            APIError: If the API request fails.
        """
        validated_name = _validate_variant_name(variant_name)
        path = f"/templates/riso/samples/{urllib.parse.quote(validated_name)}"
        return self._request("GET", path)

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any] | None:
        """Execute an HTTP request to the automation API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path (will be appended to base_url).
            payload: Optional request body to send as JSON.

        Returns:
            Parsed JSON response, or None if response is empty.

        Raises:
            APIError: If the HTTP request fails or returns an error status.
        """
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # type: ignore[arg-type]
                body = response.read().decode("utf-8").strip()
                if not body:
                    return None
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            try:
                details = exc.read().decode("utf-8")
                payload = json.loads(details) if details else None
            except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:  # pragma: no cover - defensive
                # Failed to parse error response - continue with None payload
                payload = None
            raise APIError(message=str(exc), status_code=exc.code, payload=payload) from exc
        except urllib.error.URLError as exc:
            raise APIError(message=str(exc.reason)) from exc


__all__ = ["RenderClient", "APIError", "DEFAULT_BASE_URL"]
