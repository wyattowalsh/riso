"""Tests for Go template rendering and validation."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("yaml")
jinja2 = pytest.importorskip("jinja2")

GO_CONTEXT = {
    "project_name": "Go Validation",
    "project_slug": "go-validation",
    "package_name": "go_validation",
    "go_version": "1.27",
    "cli_module": "disabled",
    "cli_languages": [],
    "api_module": "disabled",
    "api_languages": [],
    "mcp_module": "disabled",
    "mcp_languages": [],
    "mcp_example_tools": True,
    "mcp_transport": "stdio",
    "go_framework": "gin",
}


@pytest.fixture(name="go_jinja_env")
def _go_jinja_env(template_dir, tmp_path):
    """Use Copier's configured Jinja environment for emitted-code checks."""
    copier_main = pytest.importorskip("copier._main")
    with copier_main.Worker(
        src_path=str(template_dir),
        dst_path=tmp_path / "copier-environment",
        defaults=True,
        quiet=True,
    ) as worker:
        yield worker.jinja_env


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(name="template_dir")
def _template_dir() -> Path:
    """Get the template directory."""
    return Path(__file__).parents[2] / "template"


@pytest.fixture(name="go_templates_dir")
def _go_templates_dir(template_dir) -> Path:
    """Get the Go templates directory."""
    return template_dir / "files" / "go"


@pytest.fixture
def mock_copier_run():
    """Mock copier.run_copy for testing."""
    with patch("copier.run_copy") as mock:
        mock.return_value = MagicMock()
        yield mock


class TestGoTemplateFiles:
    """Tests for Go template file existence and structure."""

    def test_go_templates_directory_exists(self, go_templates_dir):
        """Go templates directory should exist."""
        assert go_templates_dir.exists()
        assert go_templates_dir.is_dir()

    def test_go_mod_template_exists(self, go_templates_dir):
        """go.mod.jinja template should exist."""
        go_mod = go_templates_dir / "go.mod.jinja"
        assert go_mod.exists()

    def test_makefile_template_exists(self, go_templates_dir):
        """Makefile.jinja template should exist."""
        makefile = go_templates_dir / "Makefile.jinja"
        assert makefile.exists()

    def test_cli_templates_exist(self, go_templates_dir):
        """CLI templates should exist."""
        cli_dir = go_templates_dir / "cli"
        assert (cli_dir / "main.go.jinja").exists()
        assert (cli_dir / "cmd" / "root.go.jinja").exists()
        assert (cli_dir / "cmd" / "version.go.jinja").exists()
        assert len(list((cli_dir / "cmd").glob("*serve.go*.jinja"))) == 1

    def test_api_templates_exist(self, go_templates_dir):
        """API templates should exist."""
        api_dir = go_templates_dir / "api"
        assert (api_dir / "main.go.jinja").exists()
        assert (api_dir / "server" / "server.go.jinja").exists()
        assert (api_dir / "internal" / "handlers" / "health.go.jinja").exists()
        assert (api_dir / "internal" / "handlers" / "routes.go.jinja").exists()

    def test_mcp_templates_exist(self, go_templates_dir):
        """MCP templates should exist."""
        mcp_dir = go_templates_dir / "mcp"
        assert (mcp_dir / "go.mod.jinja").exists()
        assert (mcp_dir / "cmd" / "server" / "main.go.jinja").exists()
        assert (mcp_dir / "internal" / "mcp" / "server.go.jinja").exists()


class TestGoModTemplate:
    """Tests for go.mod.jinja template."""

    def test_go_mod_renders_with_cli_enabled(self):
        """go.mod should include CLI dependencies when enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            go_version="1.27",
        )

        assert "module test-project" in rendered
        assert "go 1.27" in rendered
        assert "github.com/spf13/cobra" in rendered
        assert "github.com/knadh/koanf/v2" in rendered

    def test_go_mod_renders_with_api_gin(self):
        """go.mod should include Gin dependencies when API uses gin."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="test-project",
            go_version="1.27",
        )

        assert "github.com/gin-gonic/gin" in rendered
        assert "github.com/gofiber/fiber" not in rendered

    def test_go_mod_renders_with_api_fiber(self):
        """go.mod should include Fiber dependencies when API uses fiber."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="fiber",
            project_slug="test-project",
            go_version="1.27",
        )

        assert "github.com/gofiber/fiber/v2" in rendered
        assert "github.com/gin-gonic/gin" not in rendered
        assert "github.com/labstack/echo" not in rendered

    def test_go_mod_renders_with_api_echo(self):
        """go.mod should include Echo dependencies when API uses echo."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="echo",
            project_slug="test-project",
            go_version="1.27",
        )

        assert "github.com/labstack/echo/v4" in rendered
        assert "github.com/gin-gonic/gin" not in rendered
        assert "github.com/gofiber/fiber" not in rendered

    def test_go_mod_renders_with_api_chi(self):
        """go.mod should include Chi dependencies when API uses chi."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="chi",
            project_slug="test-project",
            go_version="1.27",
        )

        assert "github.com/go-chi/chi/v5" in rendered
        assert "github.com/go-chi/cors" in rendered
        assert "github.com/gin-gonic/gin" not in rendered

    def test_go_mod_renders_with_both_cli_and_api(self):
        """go.mod should include both CLI and API dependencies."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="test-project",
            go_version="1.27",
        )

        assert "github.com/spf13/cobra" in rendered
        assert "github.com/gin-gonic/gin" in rendered
        assert "github.com/knadh/koanf/v2" in rendered

    def test_go_mod_empty_when_go_not_used(self):
        """go.mod should be empty/minimal when Go is not used."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["python"],
            api_module="enabled",
            api_languages=["python"],
            mcp_module="disabled",
            mcp_languages=["python"],
            project_slug="test-project",
        )

        # Should render to empty or whitespace only
        assert rendered.strip() == ""

    def test_go_mod_mcp_only_emits_workspace_parent(self):
        """MCP-only Go still needs a valid root module for go.work."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            cli_languages=["python"],
            api_module="disabled",
            api_languages=["python"],
            mcp_module="enabled",
            mcp_languages=["go"],
            project_slug="riso-go-mcp",
            go_version="1.27",
        )

        assert "module riso-go-mcp" in rendered
        assert "go 1.27" in rendered
        assert rendered.strip() != ""


class TestGoWorkTemplate:
    """Tests for go.work.jinja monorepo workspace listing."""

    @pytest.mark.parametrize("track", ["cli", "api", "mcp"])
    @pytest.mark.parametrize("go_version", ["1.26", "1.27"])
    def test_native_go_parser_accepts_rendered_workspace(
        self, track, go_version, go_templates_dir, go_jinja_env, tmp_path
    ):
        """Each enabled Go track emits a workspace the Go tool can parse."""
        go = shutil.which("go")
        if go is None:
            pytest.skip("Go is required for native workspace syntax validation")
        context = GO_CONTEXT | {
            f"{track}_module": "enabled",
            f"{track}_languages": ["go"],
            "go_version": go_version,
        }
        rendered = go_jinja_env.from_string(
            (go_templates_dir / "go.work.jinja").read_text()
        ).render(**context)
        (tmp_path / "go.work").write_text(rendered)
        result = subprocess.run(
            [go, "work", "edit", "-json"],
            cwd=tmp_path,
            env={**os.environ, "GOTOOLCHAIN": "local"},
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        workspace = json.loads(result.stdout)
        assert workspace["Go"] == f"{go_version}.0"
        expected = [".", "./mcp"] if track == "mcp" else ["."]
        assert [entry["DiskPath"] for entry in workspace["Use"]] == expected

    def test_go_work_monorepo_cli_api_mcp_lists_root_and_mcp(self):
        """Monorepo CLI+API+MCP should use `.` and `./mcp`, never `./cli` or `./api`."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.work.jinja")

        rendered = template.render(
            project_layout="monorepo",
            cli_module="enabled",
            cli_languages=["go"],
            api_module="enabled",
            api_languages=["go"],
            mcp_module="enabled",
            mcp_languages=["go"],
            go_version="1.27",
        )

        use_lines = [line.strip() for line in rendered.splitlines()]
        assert "use (" in rendered
        assert "." in use_lines
        assert "./mcp" in use_lines
        assert "./cli" not in use_lines
        assert "./api" not in use_lines

    def test_go_work_monorepo_mcp_only_lists_root_and_mcp(self):
        """MCP-only still emits a workspace parent `.` plus `./mcp`."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.work.jinja")

        rendered = template.render(
            project_layout="monorepo",
            cli_module="disabled",
            cli_languages=["go"],
            api_module="disabled",
            api_languages=["go"],
            mcp_module="enabled",
            mcp_languages=["go"],
            go_version="1.27",
        )

        use_lines = [line.strip() for line in rendered.splitlines()]
        assert "./mcp" in use_lines
        assert "." in use_lines
        assert "use (" in rendered

    def test_go_work_single_package_cli_lists_root(self):
        """single-package + go CLI must emit a non-empty `use (` block."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.work.jinja")

        rendered = template.render(
            project_layout="single-package",
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            api_languages=["go"],
            mcp_module="disabled",
            mcp_languages=["go"],
            go_version="1.27",
        )

        use_lines = [line.strip() for line in rendered.splitlines()]
        assert "use (" in rendered
        assert "." in use_lines
        assert "./mcp" not in use_lines

    def test_go_work_monorepo_cli_only_lists_root(self):
        """Monorepo go CLI-only should list `.` and not `./mcp`."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.work.jinja")

        rendered = template.render(
            project_layout="monorepo",
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            api_languages=["go"],
            mcp_module="disabled",
            mcp_languages=["go"],
            go_version="1.27",
        )

        use_lines = [line.strip() for line in rendered.splitlines()]
        assert "." in use_lines
        assert "./mcp" not in use_lines
        assert "./cli" not in use_lines
        assert "./api" not in use_lines


class TestGoMakefileTemplate:
    """Tests for Makefile.jinja template."""

    def test_makefile_renders_with_cli_targets(self):
        """Makefile should include CLI targets when enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            project_name="Test Project",
            go_version="1.27",
        )

        assert "build-cli:" in rendered
        assert "run-cli:" in rendered
        assert "$(GO) build" in rendered
        assert "./cli" in rendered
        assert "BINARY_NAME=test-project" in rendered

    def test_makefile_renders_with_api_targets(self):
        """Makefile should include API targets when enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            project_slug="test-api",
            project_name="Test API",
            go_version="1.27",
        )

        assert "build-api:" in rendered
        assert "run-api:" in rendered
        assert "run-api-dev:" in rendered
        assert "API_BINARY_NAME=test-api-api" in rendered
        assert "./api" in rendered
        assert "air -c .air.toml" in rendered

    def test_makefile_includes_common_targets(self):
        """Makefile should include common targets for all Go projects."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            project_name="Test Project",
            go_version="1.27",
        )

        # Common targets
        assert "test:" in rendered
        assert "lint:" in rendered
        assert "fmt:" in rendered
        assert "clean:" in rendered
        assert "mod-tidy:" in rendered
        assert "install-tools:" in rendered
        assert "docker-build:" in rendered
        assert "help:" in rendered

    def test_makefile_has_version_variables(self):
        """Makefile should include version and build variables."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            project_name="Test Project",
            go_version="1.27",
        )

        assert "VERSION?=" in rendered
        assert "BUILD_TIME=" in rendered
        assert "COMMIT=" in rendered
        assert "LDFLAGS=" in rendered


class TestGoCliTemplate:
    """Tests for Go CLI templates."""

    def test_cli_main_renders_when_enabled(self):
        """CLI main.go should render correctly when enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "cli"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            project_slug="test-cli",
            project_name="Test CLI",
        )

        assert "package main" in rendered
        assert "import" in rendered
        assert 'test-cli/cli/cmd"' in rendered
        assert "cmd.Execute()" in rendered
        assert "Version" in rendered
        assert "BuildTime" in rendered

    def test_cli_main_disabled_message(self):
        """CLI main.go should show disabled message when CLI not enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "cli"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            cli_module="disabled",
            cli_languages=["go"],
        )

        assert "CLI module is disabled" in rendered
        assert "os.Exit(1)" in rendered

    def test_cli_root_cmd_renders(self):
        """CLI root.go command should render correctly."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "cli" / "cmd"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("root.go.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            project_name="Test CLI",
            project_slug="test-cli",
        )

        assert "package cmd" in rendered
        assert "github.com/spf13/cobra" in rendered
        assert "rootCmd" in rendered
        assert "Test CLI" in rendered


class TestGoApiTemplate:
    """Tests for Go API templates."""

    def test_api_main_renders_when_enabled(self):
        """API main.go should render correctly when enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "api"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            project_slug="test-api",
            project_name="Test API",
        )

        assert "package main" in rendered
        assert 'test-api/api/server"' in rendered
        assert "server.New(cfg)" in rendered
        assert "ListenAndServe()" in rendered
        assert "Shutdown(ctx)" in rendered

    def test_api_main_disabled_message(self):
        """API main.go should show disabled message when API not enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "api"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            api_module="disabled",
            api_languages=["go"],
        )

        assert "API module is disabled" in rendered
        assert "os.Exit(1)" in rendered

    @pytest.mark.parametrize(
        "framework,expected_import",
        [
            ("gin", "github.com/gin-gonic/gin"),
            ("fiber", "github.com/gofiber/fiber/v2"),
            ("echo", "github.com/labstack/echo/v4"),
            ("chi", "github.com/go-chi/chi/v5"),
        ],
    )
    def test_api_server_renders_with_framework(self, framework, expected_import):
        """API server.go should render correctly for each framework."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "api" / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("server.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            go_framework=framework,
            project_slug="test-api",
            project_name="Test API",
        )

        assert "package server" in rendered
        assert expected_import in rendered
        assert "func New(cfg *config.Config)" in rendered
        assert "func (s *Server) ListenAndServe()" in rendered
        assert "func (s *Server) Shutdown(ctx context.Context)" in rendered

    def test_api_server_gin_specific_code(self):
        """API server.go with Gin should have Gin-specific code."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "api" / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("server.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="test-api",
            project_name="Test API",
        )

        assert "gin.New()" in rendered
        assert "gin.SetMode(gin.ReleaseMode)" in rendered
        assert "*gin.Engine" in rendered

    def test_api_server_fiber_specific_code(self):
        """API server.go with Fiber should have Fiber-specific code."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "api" / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("server.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            go_framework="fiber",
            project_slug="test-api",
            project_name="Test API",
        )

        assert "fiber.New(" in rendered
        assert "*fiber.App" in rendered
        assert "ShutdownWithContext(ctx)" in rendered

    def test_api_server_echo_specific_code(self):
        """API server.go with Echo should have Echo-specific code."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "api" / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("server.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            go_framework="echo",
            project_slug="test-api",
            project_name="Test API",
        )

        assert "echo.New()" in rendered
        assert "*echo.Echo" in rendered
        assert "e.HideBanner = true" in rendered

    def test_api_server_chi_specific_code(self):
        """API server.go with Chi should have Chi-specific code."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "api" / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("server.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            go_framework="chi",
            project_slug="test-api",
            project_name="Test API",
        )

        assert "chi.NewRouter()" in rendered
        assert "chi.Router" in rendered


class TestGoMcpTemplate:
    """Tests for Go MCP templates."""

    def test_mcp_go_mod_renders_when_enabled(self):
        """MCP go.mod should render correctly when enabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "mcp"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            mcp_module="enabled",
            mcp_languages=["go"],
            project_slug="test-mcp",
        )

        assert "module test-mcp/mcp" in rendered
        assert "go 1.27" in rendered
        assert "github.com/modelcontextprotocol/go-sdk" in rendered

    def test_mcp_go_mod_empty_when_disabled(self):
        """MCP go.mod should be empty when MCP is disabled."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "mcp"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            mcp_module="disabled",
            mcp_languages=["go"],
        )

        assert rendered.strip() == ""

    def test_mcp_server_main_renders(self):
        """MCP server main.go should render correctly."""
        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "mcp"
            / "cmd"
            / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            mcp_module="enabled",
            mcp_languages=["go"],
            project_slug="test-mcp",
            project_name="Test MCP",
            package_name="test_mcp",
            mcp_transport="stdio",
        )

        assert "package main" in rendered
        assert 'test-mcp/mcp/internal/mcp"' in rendered
        assert "serverName" in rendered


class TestGoTemplateConditionals:
    """Tests for complex conditional logic in Go templates."""

    def test_go_version_default(self):
        """Go version should default to 1.27."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            project_slug="test",
        )

        assert "go 1.27" in rendered

    def test_go_version_custom(self):
        """Go version should be customizable."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            project_slug="test",
            go_version="1.26",
        )

        assert "go 1.26" in rendered

    def test_multiple_go_modules_in_workspace(self):
        """Test that multiple Go modules can coexist."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        # Both CLI and API enabled
        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="test-project",
        )

        # Should have both sets of dependencies
        assert "github.com/spf13/cobra" in rendered
        assert "github.com/gin-gonic/gin" in rendered


class TestGoTemplateIntegration:
    """Integration tests for Go template rendering."""

    def test_full_go_cli_project_structure(self):
        """Test rendering a complete Go CLI project."""
        base_dir = Path(__file__).parents[2] / "template" / "files" / "go"

        # Test main files
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(base_dir)))
        go_mod = env.get_template("go.mod.jinja").render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="my-cli",
            go_version="1.27",
        )

        assert "module my-cli" in go_mod
        assert "github.com/spf13/cobra" in go_mod

        makefile = env.get_template("Makefile.jinja").render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="my-cli",
            project_name="My CLI",
            go_version="1.27",
        )

        assert "build-cli:" in makefile
        assert "run-cli:" in makefile

    def test_full_go_api_project_structure(self):
        """Test rendering a complete Go API project."""
        base_dir = Path(__file__).parents[2] / "template" / "files" / "go"

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(base_dir)))
        go_mod = env.get_template("go.mod.jinja").render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="my-api",
            go_version="1.27",
        )

        assert "module my-api" in go_mod
        assert "github.com/gin-gonic/gin" in go_mod

        makefile = env.get_template("Makefile.jinja").render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            project_slug="my-api",
            project_name="My API",
            go_version="1.27",
        )

        assert "build-api:" in makefile
        assert "run-api-dev:" in makefile

    @pytest.mark.parametrize(
        "framework",
        ["gin", "fiber", "echo", "chi"],
    )
    def test_all_frameworks_render_valid_go(self, framework):
        """Test that all supported frameworks render valid Go code."""
        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "api" / "server"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template("server.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            go_framework=framework,
            project_slug="test-api",
            project_name="Test API",
        )

        # Basic Go syntax checks
        assert "package server" in rendered
        assert "import (" in rendered
        assert "func New(" in rendered
        assert "func (s *Server) ListenAndServe()" in rendered
        assert "func (s *Server) Shutdown(" in rendered

        # Should not have syntax errors indicators
        assert "{{" not in rendered
        assert "}}" not in rendered
        assert "{%-" not in rendered
        assert "-%}" not in rendered


class TestGoSharedInternalPackages:
    """QUAL follow-ups from SYS handoff QUAL-go-template-tests."""

    def test_shared_internal_config_and_logger_exist(self, go_templates_dir):
        """Shared go/internal/{config,logger} packages must exist."""
        assert (go_templates_dir / "internal" / "config" / "config.go.jinja").exists()
        assert (go_templates_dir / "internal" / "logger" / "logger.go.jinja").exists()

    def test_api_templates_do_not_import_cli_internal(self, go_templates_dir):
        """API-only templates must not reference cli/internal (use shared internal/)."""
        api_dir = go_templates_dir / "api"
        offenders: list[str] = []
        for path in api_dir.rglob("*.jinja"):
            text = path.read_text(encoding="utf-8")
            if "cli/internal" in text:
                offenders.append(str(path.relative_to(go_templates_dir)))
        assert not offenders, f"API templates still import cli/internal: {offenders}"

    def test_api_main_uses_shared_internal_config(self, go_templates_dir):
        """API main should import project_slug/internal/config (shared package)."""
        main = (go_templates_dir / "api" / "main.go.jinja").read_text(encoding="utf-8")
        assert 'internal/config"' in main or "/internal/config" in main
        assert "cli/internal" not in main

    def test_cli_templates_do_not_import_api_internal(self, go_templates_dir):
        """CLI packages must stay outside the API's Go internal import boundary."""
        for template in (go_templates_dir / "cli").rglob("*.jinja"):
            assert "/api/internal/" not in template.read_text(), template


class TestGoMcpExampleToolsGate:
    """MCP example tool/resource imports must follow mcp_example_tools."""

    def test_server_imports_tools_when_example_tools_enabled(self) -> None:
        """Example tools on: import and register internal/tools and resources."""
        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "mcp"
            / "internal"
            / "mcp"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        rendered = env.get_template("server.go.jinja").render(
            mcp_module="enabled",
            mcp_languages=["go"],
            mcp_example_tools=True,
            project_slug="test-mcp",
            project_name="Test MCP",
        )

        assert "test-mcp/mcp/internal/tools" in rendered
        assert "test-mcp/mcp/internal/resources" in rendered
        assert "tools.RegisterEchoTools" in rendered
        assert "resources.RegisterSystemResources" in rendered
        assert "HasTools:     true" in rendered
        assert "HasResources: true" in rendered

    def test_server_omits_tool_imports_when_example_tools_disabled(self) -> None:
        """Example tools off: no tools/resources imports or registration."""
        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "mcp"
            / "internal"
            / "mcp"
        )
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        rendered = env.get_template("server.go.jinja").render(
            mcp_module="enabled",
            mcp_languages=["go"],
            mcp_example_tools=False,
            project_slug="test-mcp",
            project_name="Test MCP",
        )

        assert "internal/tools" not in rendered
        assert "internal/resources" not in rendered
        assert "RegisterEchoTools" not in rendered
        assert "RegisterSystemResources" not in rendered
        assert "HasTools:     false" in rendered
        assert "HasResources: false" in rendered


class TestGoDockerfile:
    """Go Dockerfile copies go.mod from the go/ build context, not go.sum."""

    def test_dockerfile_copies_go_mod_without_go_sum(self) -> None:
        """No go.sum.jinja exists; COPY go.mod then go mod download."""
        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        rendered = env.get_template("Dockerfile.jinja").render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            api_languages=[],
            project_slug="test-go",
            go_version="1.27",
        )

        copy_lines = [
            line.strip()
            for line in rendered.splitlines()
            if line.lstrip().startswith("COPY ")
        ]
        assert copy_lines, "expected COPY instructions in Dockerfile"
        assert any(line.startswith("COPY go.mod") for line in copy_lines)
        assert all("go.sum" not in line for line in copy_lines)
        assert all("COPY go/go.mod" not in line for line in copy_lines)
        assert "go mod download" in rendered

    def test_template_has_no_go_sum_lockfile(self, go_templates_dir: Path) -> None:
        """Copier payload must not ship go.sum; Dockerfiles must not COPY it."""
        assert not list(go_templates_dir.rglob("go.sum*"))
        dockerfile = (go_templates_dir / "Dockerfile.jinja").read_text(encoding="utf-8")
        copy_lines = [
            line.strip()
            for line in dockerfile.splitlines()
            if line.lstrip().startswith("COPY ")
        ]
        assert copy_lines, "expected COPY instructions in Dockerfile.jinja"
        assert all("go.sum" not in line for line in copy_lines)
        assert any(line.startswith("COPY go.mod") for line in copy_lines)
        assert "go mod download" in dockerfile


@pytest.mark.parametrize(
    "cli_languages,api_languages",
    [(["go"], []), ([], ["go"]), (["go"], ["python"]), (["go"], ["go"])],
)
def test_copier_omits_serve_file_unless_both_tracks_use_go(
    go_templates_dir, tmp_path, cli_languages, api_languages
):
    """Disabled serve commands are absent files, never empty Go source files."""
    copier = pytest.importorskip("copier")
    source = tmp_path / "source"
    source.mkdir()
    template = next((go_templates_dir / "cli" / "cmd").glob("*serve.go*.jinja"))
    shutil.copyfile(template, source / template.name)
    context = GO_CONTEXT | {
        "cli_module": "enabled" if cli_languages else "disabled",
        "cli_languages": cli_languages,
        "api_module": "enabled" if api_languages else "disabled",
        "api_languages": api_languages,
    }
    destination = tmp_path / "output"
    copier.run_copy(str(source), destination, data=context, defaults=True, quiet=True)
    serve = destination / "serve.go"
    assert serve.is_file() == ("go" in cli_languages and "go" in api_languages)
    assert all(path.read_text().strip() for path in destination.rglob("*.go"))


@pytest.mark.parametrize(
    "track,framework",
    [("cli", "gin"), ("mcp", "gin")]
    + [
        (track, framework)
        for track in ("api", "combined")
        for framework in ("gin", "fiber", "echo", "chi")
    ],
)
def test_native_gofmt_accepts_rendered_sources(
    go_templates_dir, go_jinja_env, track, framework
):
    """Native formatting checks cover conditional branches with Copier whitespace."""
    gofmt = shutil.which("gofmt")
    if gofmt is None:
        pytest.skip("gofmt is required for native source formatting validation")
    context = GO_CONTEXT | {"go_framework": framework}
    for module in ("cli", "api", "mcp"):
        if track == module or (track == "combined" and module in {"cli", "api"}):
            context |= {f"{module}_module": "enabled", f"{module}_languages": ["go"]}
    for template in sorted(go_templates_dir.rglob("*.jinja")):
        if not (template.name.endswith(".go.jinja") or "serve.go" in template.name):
            continue
        rendered = go_jinja_env.from_string(template.read_text()).render(**context)
        if not rendered.strip():
            continue
        result = subprocess.run(
            [gofmt], input=rendered, text=True, capture_output=True, check=False
        )
        assert result.returncode == 0, f"{template}: {result.stderr}"
        assert result.stdout == rendered, (
            f"{template} needs gofmt for {track}/{framework}"
        )
