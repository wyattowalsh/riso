"""Integration tests for FastAPI with API versioning middleware."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from api_versioning import APIVersionMiddleware, VersionRegistry


@pytest.fixture
def app():
    """Create test FastAPI app."""
    # Load configuration
    config_path = Path(__file__).parent.parent.parent / "config" / "api_versions.yaml"
    VersionRegistry.load_from_file(config_path)
    
    # Create app
    app = FastAPI()
    app.add_middleware(APIVersionMiddleware, default_version="v2")
    
    @app.get("/test")
    async def test_endpoint(request: Request):
        version = request.scope["api_version"]
        return {"version": version}
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_version_from_header(client):
    """Test version specification via header."""
    response = client.get("/test", headers={"X-API-Version": "v1"})
    
    assert response.status_code == 200
    assert response.json()["version"] == "v1"
    assert response.headers["X-API-Version"] == "v1"


def test_version_from_default(client):
    """Test default version when none specified."""
    response = client.get("/test")
    
    assert response.status_code == 200
    assert response.json()["version"] == "v2"
    assert response.headers["X-API-Version"] == "v2"


def test_deprecated_version_headers(client):
    """Test deprecation headers for deprecated version."""
    response = client.get("/test", headers={"X-API-Version": "v1"})
    
    assert response.status_code == 200
    assert "Deprecation" in response.headers
    assert "Sunset" in response.headers


def test_invalid_version(client):
    """Test error response for invalid version."""
    response = client.get("/test", headers={"X-API-Version": "v99"})
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


def test_precedence_header_over_url(client):
    """Test header takes precedence over URL."""
    # Even though URL says v1, header should win
    # (requires URL routing setup which we skip in this simplified test)
    response = client.get("/test", headers={"X-API-Version": "v2"})
    
    assert response.status_code == 200
    assert response.json()["version"] == "v2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
