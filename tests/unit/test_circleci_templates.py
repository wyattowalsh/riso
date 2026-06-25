"""Tests for CircleCI template generation."""

import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def jinja_env():
    """Create Jinja2 environment for template rendering."""
    template_dir = Path(__file__).parent.parent.parent / "template" / "files"
    return Environment(loader=FileSystemLoader(str(template_dir)))


class TestCircleCITemplate:
    """Test CircleCI template rendering."""

    def test_circleci_template_exists(self):
        """Verify CircleCI template file exists."""
        template_path = (
            Path(__file__).parent.parent.parent
            / "template"
            / "files"
            / ".circleci"
            / "config.yml.jinja"
        )
        assert template_path.exists(), "CircleCI template should exist"

    def test_circleci_only_renders_when_selected(self, jinja_env):
        """CircleCI should only render when ci_platform is circleci."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        # Should render when ci_platform is circleci
        result = template.render(
            ci_platform="circleci",
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
        assert result.strip(), "Should render content when ci_platform is circleci"
        assert "version: 2.1" in result
        assert "orbs:" in result

        # Should not render when ci_platform is different
        result = template.render(
            ci_platform="github-actions",
            project_name="test-project",
        )
        assert not result.strip(), "Should not render when ci_platform is not circleci"

    def test_python_orb_and_jobs(self, jinja_env):
        """Python orb and jobs should render when Python components are enabled."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "python: circleci/python@2.1" in result
        assert "python-executor:" in result
        assert "lint-python:" in result
        assert "test-python:" in result
        assert "setup-uv:" in result

    def test_node_orb_and_jobs(self, jinja_env):
        """Node orb and jobs should render when Node components are enabled."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "node: circleci/node@5.2" in result
        assert "node-executor:" in result
        assert "lint-node:" in result
        assert "test-node:" in result
        assert "build-node:" in result
        assert "setup-pnpm:" in result

    def test_rust_orb_and_jobs(self, jinja_env):
        """Rust orb and jobs should render when Rust components are enabled."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "rust: circleci/rust@1.6" in result
        assert "rust-executor:" in result
        assert "lint-rust:" in result
        assert "test-rust:" in result
        assert "build-rust:" in result

    def test_go_orb_and_jobs(self, jinja_env):
        """Go orb and jobs should render when Go components are enabled."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "go: circleci/go@1.11" in result
        assert "go-executor:" in result
        assert "lint-go:" in result
        assert "test-go:" in result
        assert "build-go:" in result

    def test_strict_quality_profile_python(self, jinja_env):
        """Strict quality profile should enable ty and pylint."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "uv run ty check" in result
        assert "uv run pylint src/" in result

    def test_parallelism_for_monorepo(self, jinja_env):
        """Monorepo layout should enable parallelism."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
            project_name="test-project",
            package_name="test_project",
            quality_profile="standard",
            project_layout="monorepo",
            cli_module="enabled",
            cli_languages=["python"],
            api_module="disabled",
            mcp_module="disabled",
            docs_module="disabled",
            saas_infra_module="disabled",
            changelog_module="disabled",
        )

        assert "parallelism: 3" in result

    def test_workspace_persistence(self, jinja_env):
        """Node build should persist workspace for downstream jobs."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "persist_to_workspace:" in result
        assert "dist/" in result

    def test_workflow_dependencies(self, jinja_env):
        """Workflows should define job dependencies correctly."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "workflows:" in result
        assert "requires:" in result
        assert "- lint-python" in result

    def test_test_results_storage(self, jinja_env):
        """Tests should store results and artifacts."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "store_test_results:" in result
        assert "store_artifacts:" in result

    def test_saas_e2e_workflow(self, jinja_env):
        """SaaS module should include E2E test job."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "test-e2e:" in result
        assert "attach_workspace:" in result
        assert "pnpm run test:e2e" in result

    def test_docs_build_job(self, jinja_env):
        """Docs module should generate build job."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "build-docs:" in result

    def test_cache_restoration_and_saving(self, jinja_env):
        """Commands should restore and save caches."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        assert "restore_cache:" in result
        assert "save_cache:" in result
        assert "uv-cache-" in result

    def test_mixed_language_workflow(self, jinja_env):
        """Multiple languages should all appear in workflow."""
        template = jinja_env.get_template(".circleci/config.yml.jinja")

        result = template.render(
            ci_platform="circleci",
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

        # Python workflow
        assert "lint-python" in result
        assert "test-python" in result

        # Node workflow
        assert "lint-node" in result
        assert "test-node" in result
        assert "build-node" in result
