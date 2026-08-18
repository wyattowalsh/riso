"""Tests for generated GitHub Actions workflow templates."""

# pylint: disable=redefined-outer-name,missing-function-docstring,too-few-public-methods

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from jinja2 import Environment, FileSystemLoader

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "template" / "files"

_BASE = {
    "project_name": "test-project",
    "package_name": "test_project",
    "quality_profile": "standard",
    "ci_platform": "github-actions",
    "cli_module": "disabled",
    "cli_languages": [],
    "api_module": "disabled",
    "api_languages": [],
    "mcp_module": "disabled",
    "mcp_languages": [],
    "docs_module": "disabled",
    "docs_framework": "none",
    "saas_infra_module": "disabled",
}


@pytest.fixture
def jinja_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(TEMPLATE_ROOT)))


def _render(jinja_env: Environment, name: str, **overrides: object) -> str:
    ctx = {**_BASE, **overrides}
    return jinja_env.get_template(name).render(**ctx)


def _jobs(rendered: str) -> dict[str, dict[str, object]]:
    data = yaml.safe_load(rendered)
    assert isinstance(data, dict)
    jobs = data.get("jobs")
    assert isinstance(jobs, dict)
    typed: dict[str, dict[str, object]] = {}
    for name, job in jobs.items():
        assert isinstance(name, str)
        assert isinstance(job, dict)
        typed[name] = job
    return typed


class TestContainerWorkflowTemplates:
    """scan / publish-ghcr must never emit needs: [] or an empty matrix."""

    def test_templates_exist(self) -> None:
        workflows = TEMPLATE_ROOT / ".github" / "workflows"
        assert (workflows / "riso-container-build.yml.jinja").is_file()
        assert (workflows / "riso-container-publish.yml.jinja").is_file()

    @pytest.mark.parametrize(
        "api_module,api_languages",
        [
            ("disabled", []),
            ("enabled", ["rust"]),
            ("enabled", ["go"]),
        ],
    )
    def test_omits_scan_and_publish_without_python_or_node(
        self,
        jinja_env: Environment,
        api_module: str,
        api_languages: list[str],
    ) -> None:
        build = _render(
            jinja_env,
            ".github/workflows/riso-container-build.yml.jinja",
            api_module=api_module,
            api_languages=api_languages,
        )
        publish = _render(
            jinja_env,
            ".github/workflows/riso-container-publish.yml.jinja",
            api_module=api_module,
            api_languages=api_languages,
        )
        assert "needs: []" not in build
        assert "needs: []" not in publish
        build_jobs = _jobs(build)
        publish_jobs = _jobs(publish)
        assert "scan" not in build_jobs
        assert "publish-ghcr" not in publish_jobs
        assert "hadolint" in build_jobs
        assert build_jobs["summary"]["needs"] == ["hadolint"]
        assert "needs" not in publish_jobs["summary"]

    def test_python_only_scan_needs_build_python(self, jinja_env: Environment) -> None:
        build = _render(
            jinja_env,
            ".github/workflows/riso-container-build.yml.jinja",
            api_module="enabled",
            api_languages=["python"],
        )
        jobs = _jobs(build)
        assert jobs["scan"]["needs"] == ["build-python"]
        targets = jobs["scan"]["strategy"]["matrix"]["target"]
        assert targets and all(row["name"] == "python" for row in targets)

    def test_node_only_scan_needs_build_node(self, jinja_env: Environment) -> None:
        build = _render(
            jinja_env,
            ".github/workflows/riso-container-build.yml.jinja",
            api_module="enabled",
            api_languages=["node"],
        )
        jobs = _jobs(build)
        assert jobs["scan"]["needs"] == ["build-node"]
        targets = jobs["scan"]["strategy"]["matrix"]["target"]
        assert targets and all(row["name"] == "node" for row in targets)

    def test_python_and_node_scan_needs_both(self, jinja_env: Environment) -> None:
        build = _render(
            jinja_env,
            ".github/workflows/riso-container-build.yml.jinja",
            api_module="enabled",
            api_languages=["python", "node"],
        )
        jobs = _jobs(build)
        assert jobs["scan"]["needs"] == ["build-python", "build-node"]
        names = {row["name"] for row in jobs["scan"]["strategy"]["matrix"]["target"]}
        assert names == {"python", "node"}

    def test_publish_matrix_rows_match_api_languages(
        self, jinja_env: Environment
    ) -> None:
        publish = _render(
            jinja_env,
            ".github/workflows/riso-container-publish.yml.jinja",
            api_module="enabled",
            api_languages=["python", "node"],
        )
        jobs = _jobs(publish)
        assert jobs["publish-ghcr"]["strategy"]["matrix"]["target"]
        names = {
            row["name"] for row in jobs["publish-ghcr"]["strategy"]["matrix"]["target"]
        }
        assert names == {"python", "node"}
        assert jobs["summary"]["needs"] == ["publish-ghcr"]

    def test_publish_uses_docker_dir_dockerfile(self, jinja_env: Environment) -> None:
        publish = _render(
            jinja_env,
            ".github/workflows/riso-container-publish.yml.jinja",
            api_module="enabled",
            api_languages=["python"],
        )
        assert "file: .docker/Dockerfile" in publish
        assert "file: Dockerfile\n" not in publish
        assert "github.ref_type" in publish
        trivy_at = publish.index("Run Trivy scan")
        login_at = publish.index("Log in to GitHub Container Registry")
        push_at = publish.index("Push scanned image")
        assert trivy_at < login_at < push_at

    def test_container_build_path_filters_omit_root_dockerfile(
        self, jinja_env: Environment
    ) -> None:
        build = _render(
            jinja_env,
            ".github/workflows/riso-container-build.yml.jinja",
            api_module="enabled",
            api_languages=["python"],
        )
        assert "'.docker/**'" in build
        assert "\n      - 'Dockerfile'\n" not in build


class TestQualityWorkflowTemplate:
    """Canonical pyproject lives under python/; dest-root uv cannot see it."""

    def test_python_quality_uses_python_directory(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-quality.yml.jinja",
            cli_module="enabled",
            cli_languages=["python"],
            api_module="enabled",
            api_languages=["python"],
        )
        assert "working-directory: python" in rendered
        assert "uv --directory python run task quality" in rendered
        assert "uv run task quality" not in rendered.replace(
            "uv --directory python run task quality", ""
        )
        assert "python/.riso/quality-durations.json" in rendered
        assert "python/htmlcov/" in rendered


class TestMatrixWorkflowTemplate:
    """Python matrix must not ship dest-root uv on docs-only dests."""

    def test_default_dest_omits_matrix_test(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-matrix.yml.jinja",
            docs_module="enabled",
            docs_framework="fumadocs",
        )
        jobs = _jobs(rendered)
        assert "matrix-test" not in jobs
        assert "scaffold-ok" in jobs
        assert "uv sync" not in rendered

    def test_python_track_uses_python_directory(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-matrix.yml.jinja",
            cli_module="enabled",
            cli_languages=["python"],
            python_versions=["3.11", "3.12"],
        )
        jobs = _jobs(rendered)
        assert "matrix-test" in jobs
        assert "working-directory: python" in rendered
        assert "uv --directory python run pytest" in rendered
        assert "uv --directory python run ty check" in rendered


class TestDepsUpdateWorkflowTemplate:
    """update-python-deps is gated on a Python track and points uv at python/."""

    def test_default_dest_omits_python_job(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-deps-update.yml.jinja",
            docs_module="enabled",
            docs_framework="fumadocs",
        )
        jobs = _jobs(rendered)
        assert "update-python-deps" not in jobs
        assert "scaffold-ok" in jobs

    def test_python_job_uses_directory_flag(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-deps-update.yml.jinja",
            cli_module="enabled",
            cli_languages=["python"],
        )
        jobs = _jobs(rendered)
        assert "update-python-deps" in jobs
        assert "uv --directory python lock --upgrade" in rendered
        assert "uv --directory python run task quality" in rendered
        assert "node-version: '20'" not in rendered

    def test_node_job_stays_on_node_20(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-deps-update.yml.jinja",
            api_module="enabled",
            api_languages=["node"],
        )
        jobs = _jobs(rendered)
        assert "update-node-deps" in jobs
        assert "node-version: '20'" in rendered


class TestFumadocsDeployWorkflow:
    """Docs deploy lives at dest-root .github/workflows, not nested under fumadocs."""

    def test_dest_root_workflow_uses_package_paths(
        self, jinja_env: Environment
    ) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-docs-deploy.yml.jinja",
            docs_module="enabled",
            docs_framework="fumadocs",
        )
        jobs = _jobs(rendered)
        assert "build" in jobs
        assert "working-directory: node/docs/fumadocs" in rendered
        assert "path: node/docs/fumadocs/out" in rendered
        assert "node-version: '20'" in rendered
        assert "path: ./out" not in rendered

    def test_nested_fumadocs_deploy_is_gone(self) -> None:
        nested = (
            TEMPLATE_ROOT
            / "node"
            / "docs"
            / "fumadocs"
            / ".github"
            / "workflows"
            / "deploy.yml.jinja"
        )
        assert not nested.is_file()


class TestSaasDestRootWorkflows:
    """SaaS quality and database jobs load from dest-root .github/workflows."""

    def test_saas_quality_job_on_github_cicd(self, jinja_env: Environment) -> None:
        """saas-quality uses node/saas working-directory and typecheck."""
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-quality.yml.jinja",
            saas_infra_module="enabled",
            saas_cicd="github-actions",
        )
        jobs = _jobs(rendered)
        assert "saas-quality" in jobs
        assert "scaffold-ok" not in jobs
        assert "working-directory: node/saas" in rendered
        assert "pnpm run typecheck" in rendered
        assert "pnpm run type-check" not in rendered
        assert "node-version: '20'" in rendered

    def test_saas_off_keeps_scaffold_ok(self, jinja_env: Environment) -> None:
        """Default _BASE still emits scaffold-ok and no saas-quality."""
        rendered = _render(jinja_env, ".github/workflows/riso-quality.yml.jinja")
        jobs = _jobs(rendered)
        assert "saas-quality" not in jobs
        assert "scaffold-ok" in jobs

    def test_saas_cloudflare_ci_omits_saas_quality(
        self, jinja_env: Environment
    ) -> None:
        """Non-GHA saas_cicd does not emit saas-quality."""
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-quality.yml.jinja",
            saas_infra_module="enabled",
            saas_cicd="cloudflare-ci",
        )
        jobs = _jobs(rendered)
        assert "saas-quality" not in jobs

    def test_database_workflow_prisma_paths(self, jinja_env: Environment) -> None:
        """Dest-root database workflow prefixes ORM paths with node/saas."""
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-saas-database.yml.jinja",
            saas_infra_module="enabled",
            saas_cicd="github-actions",
            saas_orm="prisma",
            saas_include_fixtures=False,
        )
        jobs = _jobs(rendered)
        assert "validate-schema" in jobs
        assert "node/saas/integrations/orm/prisma/**" in rendered
        assert "working-directory: node/saas" in rendered
        assert "PNPM_VERSION: '8'" not in rendered

    def test_database_workflow_drizzle_paths(self, jinja_env: Environment) -> None:
        """Drizzle dest-root paths point at node/saas integrations."""
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-saas-database.yml.jinja",
            saas_infra_module="enabled",
            saas_cicd="github-actions",
            saas_orm="drizzle",
            saas_include_fixtures=False,
        )
        assert "node/saas/integrations/orm/drizzle/**" in rendered
        assert "node/saas/integrations/orm/drizzle/schema.ts" in rendered

    def test_database_workflow_omitted_when_saas_off(
        self, jinja_env: Environment
    ) -> None:
        """Non-SaaS dests render an empty dest-root database workflow."""
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-saas-database.yml.jinja",
        )
        assert rendered.strip() == ""


class TestWorkflowPermissionsAndInstallHardening:
    """Dest workflows declare contents: read and never curl|sh uv."""

    def test_dest_github_workflows_omit_uv_install_sh(self) -> None:
        workflows = TEMPLATE_ROOT / ".github" / "workflows"
        for path in workflows.glob("*.yml.jinja"):
            text = path.read_text(encoding="utf-8")
            assert "astral.sh/uv/install.sh" not in text, path.name

    def test_quality_workflow_has_contents_read(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-quality.yml.jinja",
            cli_module="enabled",
            cli_languages=["python"],
        )
        data = yaml.safe_load(rendered)
        assert data["permissions"]["contents"] == "read"
        assert "$HOME/.cargo/bin" not in rendered

    def test_matrix_workflow_has_contents_read(self, jinja_env: Environment) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-matrix.yml.jinja",
            cli_module="enabled",
            cli_languages=["python"],
            python_versions=["3.11", "3.12"],
        )
        data = yaml.safe_load(rendered)
        assert data["permissions"]["contents"] == "read"
        assert "$HOME/.cargo/bin" not in rendered

    def test_deps_update_uses_setup_uv_and_job_pr_write(
        self, jinja_env: Environment
    ) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-deps-update.yml.jinja",
            cli_module="enabled",
            cli_languages=["python"],
        )
        data = yaml.safe_load(rendered)
        assert data["permissions"]["contents"] == "read"
        jobs = _jobs(rendered)
        assert jobs["update-python-deps"]["permissions"]["pull-requests"] == "write"
        assert "astral-sh/setup-uv@" in rendered
        assert "astral.sh/uv/install.sh" not in rendered
        assert "$HOME/.cargo/bin" not in rendered

    def test_saas_database_workflow_has_contents_read(
        self, jinja_env: Environment
    ) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-saas-database.yml.jinja",
            saas_infra_module="enabled",
            saas_cicd="github-actions",
            saas_orm="prisma",
            saas_include_fixtures=False,
        )
        data = yaml.safe_load(rendered)
        assert data["permissions"]["contents"] == "read"

    def test_rust_quality_job_does_not_cache_cargo_bin(
        self, jinja_env: Environment
    ) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-quality.yml.jinja",
            mcp_module="enabled",
            mcp_languages=["rust"],
        )
        assert "rust-quality" in rendered
        assert "~/.cargo/bin/" not in rendered
        assert "~/.cargo/registry/index/" in rendered

    def test_tauri_ci_has_contents_read(self, jinja_env: Environment) -> None:
        rendered = jinja_env.get_template(
            "tauri/.github/workflows/ci.yml.jinja"
        ).render(
            **{
                **_BASE,
                "desktop_module": "enabled",
                "desktop_framework": "tauri",
                "project_slug": "test-project",
            }
        )
        data = yaml.safe_load(rendered)
        assert data["permissions"]["contents"] == "read"

    def test_docusaurus_docs_build_has_contents_read(
        self, jinja_env: Environment
    ) -> None:
        rendered = jinja_env.get_template(
            "node/docs/docusaurus/.github/workflows/docs-build.yml.jinja"
        ).render(
            **{
                **_BASE,
                "docs_module": "enabled",
                "docs_framework": "docusaurus",
            }
        )
        data = yaml.safe_load(rendered)
        assert data["permissions"]["contents"] == "read"


class TestReleaseWorkflowTemplate:
    """Dest release must not cancel in-progress runs; write perms stay on the job."""

    def test_cancel_in_progress_false_and_least_privilege(
        self, jinja_env: Environment
    ) -> None:
        rendered = _render(
            jinja_env,
            ".github/workflows/riso-release.yml.jinja",
            changelog_module="enabled",
            python_versions=["3.11"],
        )
        data = yaml.safe_load(rendered)
        assert data["concurrency"]["cancel-in-progress"] is False
        assert data["permissions"]["contents"] == "read"
        release_perms = data["jobs"]["release"]["permissions"]
        assert release_perms["contents"] == "write"
        assert release_perms["pull-requests"] == "write"
