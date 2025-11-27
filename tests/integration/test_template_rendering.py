"""Integration tests for template rendering with various configurations."""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest


class TestTemplateRendering:
    """Test template rendering with different module combinations."""

    @pytest.fixture
    def template_root(self) -> Path:
        """Get the template root directory."""
        return Path(__file__).parent.parent.parent

    def render_template(
        self,
        template_root: Path,
        destination: Path,
        answers: Dict[str, str],
    ) -> subprocess.CompletedProcess:
        """
        Render the template with given answers.

        Args:
            template_root: Root directory of the template
            destination: Where to render the template
            answers: Copier answers as dictionary

        Returns:
            subprocess.CompletedProcess with render result
        """
        result = subprocess.run(
            [
                "copier",
                "copy",
                "--force",
                "--data-file", "-",
                str(template_root),
                str(destination),
            ],
            input=json.dumps(answers),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result

    def test_minimal_render(self, template_root: Path):
        """Test rendering with minimal configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-project"
            answers = {
                "project_name": "test-minimal",
                "cli_module": "disabled",
                "api_tracks": "none",
                "mcp_module": "disabled",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            assert destination.exists()
            assert (destination / "pyproject.toml").exists()
            assert (destination / ".copier-answers.yml").exists()

    def test_cli_module_render(self, template_root: Path):
        """Test rendering with CLI module enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-cli"
            answers = {
                "project_name": "test-cli",
                "cli_module": "enabled",
                "api_tracks": "none",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            # Verify CLI files exist
            assert (destination / "src").exists()
            # Check for CLI test
            test_files = list(destination.rglob("test_cli.py"))
            assert len(test_files) > 0, "CLI test file should exist"

    def test_python_api_render(self, template_root: Path):
        """Test rendering with Python API module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-api-python"
            answers = {
                "project_name": "test-api-python",
                "api_tracks": "python",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            # Verify API files exist
            api_files = list(destination.rglob("api/main.py"))
            assert len(api_files) > 0, "API main file should exist"

    def test_node_api_render(self, template_root: Path):
        """Test rendering with Node API module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-api-node"
            answers = {
                "project_name": "test-api-node",
                "api_tracks": "node",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            # Verify Node API files exist
            assert (destination / "package.json").exists()

    def test_dual_api_render(self, template_root: Path):
        """Test rendering with both Python and Node APIs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-api-dual"
            answers = {
                "project_name": "test-api-dual",
                "api_tracks": "python+node",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            # Verify both API types exist
            python_api = list(destination.rglob("api/main.py"))
            assert len(python_api) > 0, "Python API should exist"
            assert (destination / "package.json").exists(), "Node package.json should exist"

    def test_graphql_render(self, template_root: Path):
        """Test rendering with GraphQL module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-graphql"
            answers = {
                "project_name": "test-graphql",
                "api_tracks": "python",
                "graphql_api_module": "enabled",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            # Verify GraphQL files exist
            graphql_files = list(destination.rglob("graphql_api"))
            assert len(graphql_files) > 0, "GraphQL directory should exist"

    def test_mcp_module_render(self, template_root: Path):
        """Test rendering with MCP module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-mcp"
            answers = {
                "project_name": "test-mcp",
                "mcp_module": "enabled",
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed: {result.stderr}"
            # Verify MCP files exist
            mcp_files = list(destination.rglob("mcp"))
            assert len(mcp_files) > 0, "MCP directory should exist"

    @pytest.mark.parametrize("docs_variant", ["fumadocs", "sphinx-shibuya", "docusaurus"])
    def test_docs_variants(self, template_root: Path, docs_variant: str):
        """Test rendering with different documentation variants."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / f"test-docs-{docs_variant}"
            answers = {
                "project_name": f"test-docs-{docs_variant}",
                "docs_site": docs_variant,
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed for {docs_variant}: {result.stderr}"

    @pytest.mark.parametrize("layout", ["single-package", "monorepo"])
    def test_project_layouts(self, template_root: Path, layout: str):
        """Test rendering with different project layouts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / f"test-layout-{layout}"
            answers = {
                "project_name": f"test-layout-{layout}",
                "project_layout": layout,
                "docs_site": "none",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Render failed for {layout}: {result.stderr}"

    def test_full_stack_render(self, template_root: Path):
        """Test rendering with all modules enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-full-stack"
            answers = {
                "project_name": "test-full-stack",
                "cli_module": "enabled",
                "api_tracks": "python+node",
                "graphql_api_module": "enabled",
                "mcp_module": "enabled",
                "websocket_module": "enabled",
                "codegen_module": "enabled",
                "changelog_module": "enabled",
                "docs_site": "fumadocs",
                "shared_logic": "enabled",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0, f"Full stack render failed: {result.stderr}"
            # Verify key files exist
            assert (destination / "pyproject.toml").exists()
            assert (destination / "package.json").exists()

    def test_copier_answers_preserved(self, template_root: Path):
        """Test that copier answers are correctly saved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-answers"
            answers = {
                "project_name": "test-answers",
                "cli_module": "enabled",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0
            answers_file = destination / ".copier-answers.yml"
            assert answers_file.exists()

            content = answers_file.read_text()
            assert "project_name: test-answers" in content
            assert "cli_module: enabled" in content

    def test_pyproject_toml_valid(self, template_root: Path):
        """Test that generated pyproject.toml is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir) / "test-pyproject"
            answers = {
                "project_name": "test-pyproject",
            }

            result = self.render_template(template_root, destination, answers)

            assert result.returncode == 0
            pyproject = destination / "pyproject.toml"
            assert pyproject.exists()

            # Try to parse with tomli/tomllib
            try:
                import tomllib
            except ImportError:
                import tomli as tomllib

            content = pyproject.read_bytes()
            config = tomllib.loads(content.decode())
            assert "project" in config
            assert "name" in config["project"]
