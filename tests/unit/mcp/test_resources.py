"""Tests for MCP server resources."""
from __future__ import annotations

import pytest


class TestTemplateResources:
    """Tests for template resources."""

    def test_template_resources_registration(self):
        """Test that template resources are registered."""
        from riso.mcp.resources.templates import register_template_resources
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_template_resources(mcp)

        # Check that resources were registered without error
        assert True

    def test_copier_yml_resource_exists(self):
        """Test that copier.yml resource can be loaded."""
        from riso.template import get_template_path, load_copier_config

        template_path = get_template_path()
        assert template_path.exists()

        config = load_copier_config()
        assert config is not None
        assert isinstance(config, dict)


class TestSampleResources:
    """Tests for sample resources."""

    def test_sample_resources_registration(self):
        """Test that sample resources are registered."""
        from riso.mcp.resources.samples import register_sample_resources
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_sample_resources(mcp)

        # Verify registration completed without error
        assert True


class TestCatalogResources:
    """Tests for catalog resources."""

    def test_catalog_resources_registration(self):
        """Test that catalog resources are registered."""
        from riso.mcp.resources.catalog import register_catalog_resources
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_catalog_resources(mcp)

        # Verify registration completed without error
        assert True


class TestResourceIntegration:
    """Integration tests for resource registration."""

    def test_all_resources_registered_on_server(self):
        """Test that all resources are properly set up on server."""
        from riso.mcp.server import mcp as server

        # The server should be properly configured
        assert server is not None
        assert server.name == "riso-mcp"
