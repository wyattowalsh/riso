"""Tests for Go template rendering and validation."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("yaml")
pytest.importorskip("jinja2")


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def template_dir() -> Path:
    """Get the template directory."""
    return Path(__file__).parents[2] / "template"


@pytest.fixture
def go_templates_dir(template_dir) -> Path:
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
        assert (cli_dir / "cmd" / "serve.go.jinja").exists()

    def test_api_templates_exist(self, go_templates_dir):
        """API templates should exist."""
        api_dir = go_templates_dir / "api"
        assert (api_dir / "main.go.jinja").exists()
        assert (api_dir / "internal" / "server" / "server.go.jinja").exists()
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            go_version="1.24",
        )

        assert "module test-project" in rendered
        assert "go 1.24" in rendered
        assert "github.com/spf13/cobra" in rendered
        assert "github.com/knadh/koanf/v2" in rendered

    def test_go_mod_renders_with_api_gin(self):
        """go.mod should include Gin dependencies when API uses gin."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="test-project",
            go_version="1.24",
        )

        assert "github.com/gin-gonic/gin" in rendered
        assert "github.com/rs/cors" in rendered
        assert "github.com/gofiber/fiber" not in rendered

    def test_go_mod_renders_with_api_fiber(self):
        """go.mod should include Fiber dependencies when API uses fiber."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="fiber",
            project_slug="test-project",
            go_version="1.24",
        )

        assert "github.com/gofiber/fiber/v2" in rendered
        assert "github.com/gin-gonic/gin" not in rendered
        assert "github.com/labstack/echo" not in rendered

    def test_go_mod_renders_with_api_echo(self):
        """go.mod should include Echo dependencies when API uses echo."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="echo",
            project_slug="test-project",
            go_version="1.24",
        )

        assert "github.com/labstack/echo/v4" in rendered
        assert "github.com/gin-gonic/gin" not in rendered
        assert "github.com/gofiber/fiber" not in rendered

    def test_go_mod_renders_with_api_chi(self):
        """go.mod should include Chi dependencies when API uses chi."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="chi",
            project_slug="test-project",
            go_version="1.24",
        )

        assert "github.com/go-chi/chi/v5" in rendered
        assert "github.com/go-chi/cors" in rendered
        assert "github.com/gin-gonic/gin" not in rendered

    def test_go_mod_renders_with_both_cli_and_api(self):
        """go.mod should include both CLI and API dependencies."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="test-project",
            go_version="1.24",
        )

        assert "github.com/spf13/cobra" in rendered
        assert "github.com/gin-gonic/gin" in rendered
        assert "github.com/knadh/koanf/v2" in rendered

    def test_go_mod_empty_when_go_not_used(self):
        """go.mod should be empty/minimal when Go is not used."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["python"],
            api_module="enabled",
            api_languages=["python"],
            project_slug="test-project",
        )

        # Should render to empty or whitespace only
        assert rendered.strip() == ""


class TestGoMakefileTemplate:
    """Tests for Makefile.jinja template."""

    def test_makefile_renders_with_cli_targets(self):
        """Makefile should include CLI targets when enabled."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            project_name="Test Project",
            go_version="1.24",
        )

        assert "build-cli:" in rendered
        assert "run-cli:" in rendered
        assert "$(GO) build" in rendered
        assert "./cli" in rendered
        assert "BINARY_NAME=test-project" in rendered

    def test_makefile_renders_with_api_targets(self):
        """Makefile should include API targets when enabled."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            project_slug="test-api",
            project_name="Test API",
            go_version="1.24",
        )

        assert "build-api:" in rendered
        assert "run-api:" in rendered
        assert "run-api-dev:" in rendered
        assert "API_BINARY_NAME=test-api-api" in rendered
        assert "./api" in rendered
        assert "air -c .air.toml" in rendered

    def test_makefile_includes_common_targets(self):
        """Makefile should include common targets for all Go projects."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            project_name="Test Project",
            go_version="1.24",
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("Makefile.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="test-project",
            project_name="Test Project",
            go_version="1.24",
        )

        assert "VERSION?=" in rendered
        assert "BUILD_TIME=" in rendered
        assert "COMMIT=" in rendered
        assert "LDFLAGS=" in rendered


class TestGoCliTemplate:
    """Tests for Go CLI templates."""

    def test_cli_main_renders_when_enabled(self):
        """CLI main.go should render correctly when enabled."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "cli"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "cli"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            cli_module="disabled",
            cli_languages=["go"],
        )

        assert "CLI module is disabled" in rendered
        assert "os.Exit(1)" in rendered

    def test_cli_root_cmd_renders(self):
        """CLI root.go command should render correctly."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2] / "template" / "files" / "go" / "cli" / "cmd"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "api"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("main.go.jinja")

        rendered = template.render(
            api_module="enabled",
            api_languages=["go"],
            project_slug="test-api",
            project_name="Test API",
        )

        assert "package main" in rendered
        assert 'test-api/api/internal/server"' in rendered
        assert "server.New(cfg)" in rendered
        assert "ListenAndServe()" in rendered
        assert "Shutdown(ctx)" in rendered

    def test_api_main_disabled_message(self):
        """API main.go should show disabled message when API not enabled."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "api"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "api"
            / "internal"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "api"
            / "internal"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "api"
            / "internal"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "api"
            / "internal"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "api"
            / "internal"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "mcp"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            mcp_module="enabled",
            mcp_languages=["go"],
            project_slug="test-mcp",
        )

        assert "module test-mcp" in rendered
        assert "go 1.22" in rendered
        assert "github.com/modelcontextprotocol/go-sdk" in rendered

    def test_mcp_go_mod_empty_when_disabled(self):
        """MCP go.mod should be empty when MCP is disabled."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go" / "mcp"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            mcp_module="disabled",
            mcp_languages=["go"],
        )

        assert rendered.strip() == ""

    def test_mcp_server_main_renders(self):
        """MCP server main.go should render correctly."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "mcp"
            / "cmd"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        assert 'test-mcp/internal/mcp"' in rendered
        assert "serverName" in rendered


class TestGoTemplateConditionals:
    """Tests for complex conditional logic in Go templates."""

    def test_go_version_default(self):
        """Go version should default to 1.24."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            project_slug="test",
        )

        assert "go 1.24" in rendered

    def test_go_version_custom(self):
        """Go version should be customizable."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("go.mod.jinja")

        rendered = template.render(
            cli_module="enabled",
            cli_languages=["go"],
            project_slug="test",
            go_version="1.23",
        )

        assert "go 1.23" in rendered

    def test_multiple_go_modules_in_workspace(self):
        """Test that multiple Go modules can coexist."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = Path(__file__).parents[2] / "template" / "files" / "go"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
        from jinja2 import Environment, FileSystemLoader

        base_dir = Path(__file__).parents[2] / "template" / "files" / "go"

        # Test main files
        env = Environment(loader=FileSystemLoader(str(base_dir)))
        go_mod = env.get_template("go.mod.jinja").render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="my-cli",
            go_version="1.24",
        )

        assert "module my-cli" in go_mod
        assert "github.com/spf13/cobra" in go_mod

        makefile = env.get_template("Makefile.jinja").render(
            cli_module="enabled",
            cli_languages=["go"],
            api_module="disabled",
            project_slug="my-cli",
            project_name="My CLI",
            go_version="1.24",
        )

        assert "build-cli:" in makefile
        assert "run-cli:" in makefile

    def test_full_go_api_project_structure(self):
        """Test rendering a complete Go API project."""
        from jinja2 import Environment, FileSystemLoader

        base_dir = Path(__file__).parents[2] / "template" / "files" / "go"

        env = Environment(loader=FileSystemLoader(str(base_dir)))
        go_mod = env.get_template("go.mod.jinja").render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            go_framework="gin",
            project_slug="my-api",
            go_version="1.24",
        )

        assert "module my-api" in go_mod
        assert "github.com/gin-gonic/gin" in go_mod

        makefile = env.get_template("Makefile.jinja").render(
            cli_module="disabled",
            api_module="enabled",
            api_languages=["go"],
            project_slug="my-api",
            project_name="My API",
            go_version="1.24",
        )

        assert "build-api:" in makefile
        assert "run-api-dev:" in makefile

    @pytest.mark.parametrize(
        "framework",
        ["gin", "fiber", "echo", "chi"],
    )
    def test_all_frameworks_render_valid_go(self, framework):
        """Test that all supported frameworks render valid Go code."""
        from jinja2 import Environment, FileSystemLoader

        template_dir = (
            Path(__file__).parents[2]
            / "template"
            / "files"
            / "go"
            / "api"
            / "internal"
            / "server"
        )
        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
