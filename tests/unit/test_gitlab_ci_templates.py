"""Tests for GitLab CI template generation."""

import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def jinja_env():
    """Create Jinja2 environment for template rendering."""
    template_dir = Path(__file__).parent.parent.parent / "template" / "files"
    return Environment(loader=FileSystemLoader(str(template_dir)))


class TestGitLabCITemplate:
    """Test GitLab CI template rendering."""

    def test_gitlab_ci_template_exists(self):
        """Verify GitLab CI template file exists."""
        template_path = (
            Path(__file__).parent.parent.parent
            / "template"
            / "files"
            / ".gitlab"
            / ".gitlab-ci.yml.jinja"
        )
        assert template_path.exists(), "GitLab CI template should exist"

    def test_gitlab_ci_only_renders_when_selected(self, jinja_env):
        """GitLab CI should only render when ci_platform is gitlab-ci."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        # Should render when ci_platform is gitlab-ci
        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="disabled",
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )
        assert result.strip(), "Should render content when ci_platform is gitlab-ci"
        assert "stages:" in result

        # Should not render when ci_platform is different
        result = template.render(
            ci_platform="github-actions",
            project_name="test-project",
        )
        assert not result.strip(), "Should not render when ci_platform is not gitlab-ci"

    def test_python_jobs_rendered_when_python_enabled(self, jinja_env):
        """Python jobs should render when Python components are enabled."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="enabled",
            cli_languages=["python"],
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "lint:python" in result
        assert "test:python" in result
        assert ".python-base" in result
        assert "uv sync" in result

    def test_node_jobs_rendered_when_node_enabled(self, jinja_env):
        """Node jobs should render when Node components are enabled."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="disabled",
            api_module="enabled",
            api_languages=["node"],
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "lint:node" in result
        assert "test:node" in result
        assert "build:node" in result
        assert ".node-base" in result
        assert "pnpm install" in result

    def test_rust_jobs_rendered_when_rust_enabled(self, jinja_env):
        """Rust jobs should render when Rust components are enabled."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="enabled",
            cli_languages=["rust"],
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "lint:rust" in result
        assert "test:rust" in result
        assert "build:rust" in result
        assert ".rust-base" in result
        assert "cargo test" in result

    def test_go_jobs_rendered_when_go_enabled(self, jinja_env):
        """Go jobs should render when Go components are enabled."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="enabled",
            cli_languages=["go"],
            go_version="1.24",
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "lint:go" in result
        assert "test:go" in result
        assert "build:go" in result
        assert ".go-base" in result
        assert "go test" in result

    def test_strict_quality_profile(self, jinja_env):
        """Strict quality profile should enable additional checks."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="strict",
            cli_module="enabled",
            cli_languages=["python"],
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "mypy ." in result
        assert "pylint src/" in result

    def test_matrix_builds_for_monorepo(self, jinja_env):
        """Monorepo layout should enable parallel matrix builds."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            project_layout="monorepo",
            cli_module="enabled",
            cli_languages=["python"],
            python_versions=["3.11", "3.12", "3.13"],
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "parallel:" in result
        assert "matrix:" in result

    def test_docs_pages_job(self, jinja_env):
        """Docs module should generate pages deployment job."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="disabled",
            api_module="disabled",
            mcp_module="disabled",
            docs_module="enabled",
            docs_framework="fumadocs",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "pages:" in result
        assert "public/" in result

    def test_cache_configuration(self, jinja_env):
        """Template should configure caching appropriately."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="enabled",
            cli_languages=["python"],
            api_module="enabled",
            api_languages=["node"],
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "cache:" in result
        assert "UV_CACHE_DIR" in result
        assert "PNPM_HOME" in result

    def test_saas_e2e_tests(self, jinja_env):
        """SaaS module should include E2E test job."""
        template = jinja_env.get_template(".gitlab/.gitlab-ci.yml.jinja")

        result = template.render(
            ci_platform="gitlab-ci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            cli_module="disabled",
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="enabled",
            changelog_module="disabled",
        )

        assert "test:e2e" in result
        assert "pnpm run test:e2e" in result
