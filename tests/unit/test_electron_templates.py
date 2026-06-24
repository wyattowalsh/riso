"""Tests for Electron template rendering."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

pytest.importorskip("jinja2")
pytest.importorskip("yaml")


def create_jinja_env(template_path: Path):
    """Create a Jinja2 environment with custom filters.

    This mimics the filters that copier provides during template rendering.
    """
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(template_path)))

    # Add the strftime filter that copier provides
    def strftime_filter(format_string: str) -> str:
        """Format the current date/time with strftime."""
        return datetime.now().strftime(format_string)

    env.filters["strftime"] = strftime_filter
    return env


@pytest.fixture
def template_dir() -> Path:
    """Get the template directory."""
    return Path(__file__).parents[2] / "template"


@pytest.fixture
def electron_files_dir(template_dir: Path) -> Path:
    """Get the Electron template files directory."""
    return template_dir / "files" / "electron"


@pytest.fixture
def base_electron_context() -> dict[str, Any]:
    """Base context for Electron template rendering."""
    return {
        "project_name": "Test Electron App",
        "project_slug": "test-electron-app",
        "package_name": "test_electron_app",
        "github_username": "testuser",
        "author_name": "Test User",
        "author_email": "test@example.com",
        "project_description": "A test Electron application",
        "desktop_module": "enabled",
        "desktop_framework": "electron-vite",
    }


class TestElectronTemplateRendering:
    """Tests for Electron template rendering with different configurations."""

    def test_electron_module_disabled_no_files(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """When desktop_module is disabled, Electron files should not render."""
        env = create_jinja_env(electron_files_dir)

        context = {**base_electron_context, "desktop_module": "disabled"}

        # Try to render electron-builder.yml.jinja
        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        # Should be empty or just whitespace when desktop_module is disabled
        assert result.strip() == ""

    def test_electron_vite_config_renders_correctly(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """electron.vite.config.ts should render correctly when enabled."""

        env = create_jinja_env(electron_files_dir)
        template = env.get_template("electron.vite.config.ts.jinja")

        result = template.render(base_electron_context)

        # Check for key configuration elements
        assert "import { resolve } from 'path'" in result
        assert "defineConfig" in result
        assert "externalizeDepsPlugin" in result
        assert "@vitejs/plugin-react" in result
        assert "main:" in result
        assert "preload:" in result
        assert "renderer:" in result
        assert "tailwindcss" in result

    def test_package_json_has_required_dependencies(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """package.json should include required Electron dependencies."""
        import json

        env = create_jinja_env(electron_files_dir)
        template = env.get_template("package.json.jinja")

        result = template.render(base_electron_context)
        data = json.loads(result)

        # Check basic metadata
        assert data["name"] == "test-electron-app"
        assert data["version"] == "0.1.0"
        assert data["main"] == "./out/main/index.js"

        # Check required dependencies
        required_deps = [
            "electron-updater",
            "electron-log",
            "electron-store",
            "zustand",
            "react",
            "react-dom",
        ]
        for dep in required_deps:
            assert dep in data["dependencies"]

        # Check required devDependencies
        required_dev_deps = [
            "electron",
            "electron-builder",
            "electron-vite",
            "@vitejs/plugin-react",
            "typescript",
            "tailwindcss",
        ]
        for dep in required_dev_deps:
            assert dep in data["devDependencies"]

        # Check scripts
        assert "dev" in data["scripts"]
        assert "build" in data["scripts"]
        assert "build:mac" in data["scripts"]
        assert "build:win" in data["scripts"]
        assert "build:linux" in data["scripts"]

    @pytest.mark.parametrize(
        "feature,expected_content",
        [
            ("auto_updater", "autoUpdater"),
            ("auto_updater", "electron-updater"),
            ("auto_updater", "checkForUpdates"),
        ],
    )
    def test_auto_updater_feature_included(
        self,
        electron_files_dir: Path,
        base_electron_context: dict[str, Any],
        feature: str,
        expected_content: str,
    ):
        """auto_updater feature should include updater code."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": [feature]}

        # Check updater.ts.jinja
        template = env.get_template("src/main/updater.ts.jinja")
        result = template.render(context)

        assert expected_content in result

        # Check that it's imported in index.ts
        index_template = env.get_template("src/main/index.ts.jinja")
        index_result = index_template.render(context)

        assert "setupAutoUpdater" in index_result

    def test_auto_updater_feature_excluded(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """When auto_updater is not enabled, updater code should not render."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": []}

        # updater.ts.jinja should be empty
        template = env.get_template("src/main/updater.ts.jinja")
        result = template.render(context)
        assert result.strip() == ""

        # index.ts should not import setupAutoUpdater
        index_template = env.get_template("src/main/index.ts.jinja")
        index_result = index_template.render(context)
        assert "setupAutoUpdater" not in index_result

    @pytest.mark.parametrize(
        "feature,expected_content",
        [
            ("tray_icon", "Tray"),
            ("tray_icon", "setupTrayIcon"),
            ("tray_icon", "createTrayContextMenu"),
        ],
    )
    def test_tray_icon_feature_included(
        self,
        electron_files_dir: Path,
        base_electron_context: dict[str, Any],
        feature: str,
        expected_content: str,
    ):
        """tray_icon feature should include tray code."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": [feature]}

        # Check tray.ts.jinja
        template = env.get_template("src/main/tray.ts.jinja")
        result = template.render(context)

        assert expected_content in result

        # Check that it's imported in index.ts
        index_template = env.get_template("src/main/index.ts.jinja")
        index_result = index_template.render(context)

        assert "setupTrayIcon" in index_result

    def test_tray_icon_feature_excluded(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """When tray_icon is not enabled, tray code should not render."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": []}

        # tray.ts.jinja should be empty
        template = env.get_template("src/main/tray.ts.jinja")
        result = template.render(context)
        assert result.strip() == ""

        # index.ts should not import setupTrayIcon
        index_template = env.get_template("src/main/index.ts.jinja")
        index_result = index_template.render(context)
        assert "setupTrayIcon" not in index_result

    @pytest.mark.parametrize(
        "feature,component",
        [
            ("custom_titlebar", "TitleBar"),
            ("custom_titlebar", "minimizeWindow"),
            ("custom_titlebar", "maximizeWindow"),
            ("custom_titlebar", "closeWindow"),
        ],
    )
    def test_custom_titlebar_feature_included(
        self,
        electron_files_dir: Path,
        base_electron_context: dict[str, Any],
        feature: str,
        component: str,
    ):
        """custom_titlebar feature should include TitleBar component."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": [feature]}

        # Check TitleBar.tsx.jinja
        template = env.get_template("src/renderer/components/TitleBar.tsx.jinja")
        result = template.render(context)

        assert component in result

    def test_custom_titlebar_feature_excluded(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """When custom_titlebar is not enabled, TitleBar should not render."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": []}

        # TitleBar.tsx.jinja should be empty
        template = env.get_template("src/renderer/components/TitleBar.tsx.jinja")
        result = template.render(context)
        assert result.strip() == ""

    def test_titlebar_renders_with_project_name(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """TitleBar component should use project name as default title."""

        env = create_jinja_env(electron_files_dir)
        context = {
            **base_electron_context,
            "desktop_features": ["custom_titlebar"],
            "project_name": "My Custom App",
        }

        template = env.get_template("src/renderer/components/TitleBar.tsx.jinja")
        result = template.render(context)

        assert "My Custom App" in result
        assert "DEFAULT_TITLE = 'My Custom App'" in result

    def test_titlebar_has_platform_detection(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """TitleBar should detect platform for traffic light positioning."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": ["custom_titlebar"]}

        template = env.get_template("src/renderer/components/TitleBar.tsx.jinja")
        result = template.render(context)

        # Check for platform detection
        assert "getPlatform" in result
        assert "darwin" in result
        assert "isMac" in result

        # Check for traffic light space on macOS
        assert "w-20" in result  # Empty space for traffic lights


class TestElectronBuilderConfiguration:
    """Tests for electron-builder.yml configuration."""

    def test_electron_builder_basic_config(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """electron-builder.yml should have basic configuration."""

        env = create_jinja_env(electron_files_dir)
        template = env.get_template("electron-builder.yml.jinja")

        result = template.render(base_electron_context)

        # Check basic config
        assert "appId: com.testuser.testelectronapp" in result
        assert "productName: Test Electron App" in result
        assert "buildResources: resources" in result
        assert "output: dist" in result

    def test_electron_builder_auto_updater_config(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """electron-builder.yml should include publish config when auto_updater is enabled."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": ["auto_updater"]}

        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        # Check for publish configuration
        assert "publish:" in result
        assert "provider: github" in result
        assert "owner: testuser" in result
        assert "repo: test-electron-app" in result

    def test_electron_builder_no_publish_without_updater(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """electron-builder.yml should not include publish config without auto_updater."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_features": []}

        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        # Should not have publish configuration
        assert "publish:" not in result

    @pytest.mark.parametrize(
        "platform,expected_content",
        [
            ("mac", "mac:"),
            ("mac", "target: dmg"),
            ("mac", "target: zip"),
            ("mac", "icon: resources/icon.icns"),
        ],
    )
    def test_electron_builder_mac_platform(
        self,
        electron_files_dir: Path,
        base_electron_context: dict[str, Any],
        platform: str,
        expected_content: str,
    ):
        """electron-builder.yml should include macOS configuration."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_platforms": [platform]}

        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        assert expected_content in result

    @pytest.mark.parametrize(
        "platform,expected_content",
        [
            ("windows", "win:"),
            ("windows", "target: nsis"),
            ("windows", "target: portable"),
            ("windows", "icon: resources/icon.ico"),
        ],
    )
    def test_electron_builder_windows_platform(
        self,
        electron_files_dir: Path,
        base_electron_context: dict[str, Any],
        platform: str,
        expected_content: str,
    ):
        """electron-builder.yml should include Windows configuration."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_platforms": [platform]}

        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        assert expected_content in result

    @pytest.mark.parametrize(
        "platform,expected_content",
        [
            ("linux", "linux:"),
            ("linux", "target: AppImage"),
            ("linux", "target: deb"),
            ("linux", "target: rpm"),
            ("linux", "icon: resources/icon.png"),
        ],
    )
    def test_electron_builder_linux_platform(
        self,
        electron_files_dir: Path,
        base_electron_context: dict[str, Any],
        platform: str,
        expected_content: str,
    ):
        """electron-builder.yml should include Linux configuration."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_platforms": [platform]}

        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        assert expected_content in result

    def test_electron_builder_multiple_platforms(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """electron-builder.yml should support multiple platforms."""

        env = create_jinja_env(electron_files_dir)
        context = {
            **base_electron_context,
            "desktop_platforms": ["mac", "windows", "linux"],
        }

        template = env.get_template("electron-builder.yml.jinja")
        result = template.render(context)

        # All platform sections should be present
        assert "mac:" in result
        assert "win:" in result
        assert "linux:" in result


class TestElectronFeatureCombinations:
    """Tests for combinations of Electron features."""

    def test_all_features_enabled(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """All Electron features should work together."""

        env = create_jinja_env(electron_files_dir)
        context = {
            **base_electron_context,
            "desktop_features": ["auto_updater", "tray_icon", "custom_titlebar"],
            "desktop_platforms": ["mac", "windows", "linux"],
        }

        # Check index.ts has all imports
        index_template = env.get_template("src/main/index.ts.jinja")
        index_result = index_template.render(context)

        assert "setupAutoUpdater" in index_result
        assert "setupTrayIcon" in index_result

        # Check electron-builder.yml has all configurations
        builder_template = env.get_template("electron-builder.yml.jinja")
        builder_result = builder_template.render(context)

        assert "publish:" in builder_result
        assert "mac:" in builder_result
        assert "win:" in builder_result
        assert "linux:" in builder_result

    def test_no_features_enabled(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """Electron should work without optional features."""

        env = create_jinja_env(electron_files_dir)
        context = {
            **base_electron_context,
            "desktop_features": [],
            "desktop_platforms": ["mac"],
        }

        # index.ts should not have optional feature imports
        index_template = env.get_template("src/main/index.ts.jinja")
        index_result = index_template.render(context)

        assert "setupAutoUpdater" not in index_result
        assert "setupTrayIcon" not in index_result

        # electron-builder.yml should not have publish config
        builder_template = env.get_template("electron-builder.yml.jinja")
        builder_result = builder_template.render(context)

        assert "publish:" not in builder_result


class TestElectronMainIndex:
    """Tests for the main process index.ts file."""

    def test_main_index_basic_structure(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """Main index.ts should have proper structure."""

        env = create_jinja_env(electron_files_dir)
        template = env.get_template("src/main/index.ts.jinja")

        result = template.render(base_electron_context)

        # Check for basic imports
        assert "import { app, BrowserWindow" in result
        assert "from 'electron'" in result

        # Check for window creation
        assert "createMainWindow" in result

        # Check for event handlers
        assert "app.whenReady()" in result
        assert "app.on('activate'" in result
        assert "app.on('window-all-closed'" in result

    def test_main_index_security_headers(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """Main index.ts should include security configurations."""

        env = create_jinja_env(electron_files_dir)
        template = env.get_template("src/main/index.ts.jinja")

        result = template.render(base_electron_context)

        # Check for security-related code
        assert "setWindowOpenHandler" in result
        assert "will-navigate" in result

    def test_main_index_conditional_imports(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """Main index.ts should conditionally import features."""

        env = create_jinja_env(electron_files_dir)

        # With auto_updater
        context_with_updater = {
            **base_electron_context,
            "desktop_features": ["auto_updater"],
        }
        template = env.get_template("src/main/index.ts.jinja")
        result = template.render(context_with_updater)

        assert "import { setupAutoUpdater } from './updater'" in result

        # Without auto_updater
        context_without = {**base_electron_context, "desktop_features": []}
        result_without = template.render(context_without)

        assert "import { setupAutoUpdater }" not in result_without


class TestElectronTemplateIntegration:
    """Integration tests for Electron templates with copier."""

    @pytest.fixture
    def mock_copier_worker(self):
        """Mock copier worker for testing."""
        with patch("copier.run_copy") as mock_copy:
            mock_copy.return_value = None
            yield mock_copy

    def test_electron_sample_rendering(self, tmp_path: Path):
        """Test that an Electron sample can be rendered successfully."""

        template_root = Path(__file__).parents[2] / "template" / "files" / "electron"
        env = create_jinja_env(template_root)

        context = {
            "project_name": "Sample Electron App",
            "project_slug": "sample-electron-app",
            "github_username": "sampleuser",
            "author_name": "Sample User",
            "desktop_module": "enabled",
            "desktop_framework": "electron-vite",
            "desktop_features": ["auto_updater", "tray_icon", "custom_titlebar"],
            "desktop_platforms": ["mac", "windows", "linux"],
        }

        # Render key templates
        templates_to_test = [
            "package.json.jinja",
            "electron-builder.yml.jinja",
            "electron.vite.config.ts.jinja",
            "src/main/index.ts.jinja",
        ]

        for template_name in templates_to_test:
            template = env.get_template(template_name)
            result = template.render(context)
            # Should produce non-empty output
            assert result.strip(), f"{template_name} produced empty output"

    def test_electron_disabled_produces_no_output(
        self, electron_files_dir: Path, base_electron_context: dict[str, Any]
    ):
        """When desktop_module is disabled, templates should produce no output."""

        env = create_jinja_env(electron_files_dir)
        context = {**base_electron_context, "desktop_module": "disabled"}

        key_templates = [
            "package.json.jinja",
            "electron-builder.yml.jinja",
            "electron.vite.config.ts.jinja",
        ]

        for template_name in key_templates:
            template = env.get_template(template_name)
            result = template.render(context)
            assert result.strip() == "", (
                f"{template_name} should be empty when disabled"
            )
