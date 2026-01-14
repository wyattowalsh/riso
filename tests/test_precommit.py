"""Tests for pre-commit configuration generation.

These tests verify that the pre-commit configuration is correctly generated
based on the template options (quality profile, api_tracks, etc.).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def template_config_path() -> Path:
    """Return path to the template pre-commit config."""
    return (
        Path(__file__).parents[1]
        / "template"
        / "files"
        / "shared"
        / "quality"
        / ".pre-commit-config.yaml.jinja"
    )


@pytest.fixture
def root_config_path() -> Path:
    """Return path to the root pre-commit config."""
    return Path(__file__).parents[1] / ".pre-commit-config.yaml"


class TestRootPrecommitConfig:
    """Tests for the root project pre-commit configuration."""

    def test_root_config_exists(self, root_config_path: Path) -> None:
        """Verify root .pre-commit-config.yaml exists."""
        assert root_config_path.exists(), "Root .pre-commit-config.yaml should exist"

    def test_root_config_valid_yaml(self, root_config_path: Path) -> None:
        """Verify root config is valid YAML."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        assert isinstance(config, dict), "Config should be a dictionary"
        assert "repos" in config, "Config should have 'repos' key"

    def test_root_config_has_ruff(self, root_config_path: Path) -> None:
        """Verify root config includes ruff hooks."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        ruff_repos = [r for r in repos if "ruff" in str(r.get("repo", ""))]
        assert len(ruff_repos) > 0, "Should have ruff pre-commit repo"

    def test_root_config_has_actionlint(self, root_config_path: Path) -> None:
        """Verify root config includes actionlint for workflow validation."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        actionlint_repos = [r for r in repos if "actionlint" in str(r.get("repo", ""))]
        assert len(actionlint_repos) > 0, "Should have actionlint pre-commit repo"

    def test_root_config_has_conventional_commits(self, root_config_path: Path) -> None:
        """Verify root config includes conventional commit validation."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        conventional_repos = [
            r for r in repos if "conventional" in str(r.get("repo", ""))
        ]
        assert len(conventional_repos) > 0, "Should have conventional-pre-commit repo"

    def test_root_config_has_local_hooks(self, root_config_path: Path) -> None:
        """Verify root config includes local hooks (ty, pylint, etc.)."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        local_repos = [r for r in repos if r.get("repo") == "local"]
        assert len(local_repos) > 0, "Should have local hooks"

        # Collect all local hook IDs
        local_hook_ids = []
        for repo in local_repos:
            for hook in repo.get("hooks", []):
                local_hook_ids.append(hook.get("id"))

        assert "ty-check" in local_hook_ids, "Should have ty-check hook"
        assert "pylint" in local_hook_ids, "Should have pylint hook"
        assert "pytest" in local_hook_ids, "Should have pytest hook"

    def test_root_config_has_gitleaks(self, root_config_path: Path) -> None:
        """Verify root config includes gitleaks for secrets detection."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        gitleaks_repos = [r for r in repos if "gitleaks" in str(r.get("repo", ""))]
        assert len(gitleaks_repos) > 0, "Should have gitleaks pre-commit repo"

    def test_root_config_has_shellcheck(self, root_config_path: Path) -> None:
        """Verify root config includes shellcheck for bash linting."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        shellcheck_repos = [r for r in repos if "shellcheck" in str(r.get("repo", ""))]
        assert len(shellcheck_repos) > 0, "Should have shellcheck pre-commit repo"

    def test_root_config_has_codespell(self, root_config_path: Path) -> None:
        """Verify root config includes codespell for spell checking."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        codespell_repos = [r for r in repos if "codespell" in str(r.get("repo", ""))]
        assert len(codespell_repos) > 0, "Should have codespell pre-commit repo"

    def test_root_config_has_vulture(self, root_config_path: Path) -> None:
        """Verify root config includes vulture for dead code detection."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        vulture_repos = [r for r in repos if "vulture" in str(r.get("repo", ""))]
        assert len(vulture_repos) > 0, "Should have vulture pre-commit repo"

    def test_root_config_has_mdformat(self, root_config_path: Path) -> None:
        """Verify root config includes mdformat for markdown formatting."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        mdformat_repos = [r for r in repos if "mdformat" in str(r.get("repo", ""))]
        assert len(mdformat_repos) > 0, "Should have mdformat pre-commit repo"

    def test_root_config_has_check_jsonschema(self, root_config_path: Path) -> None:
        """Verify root config includes check-jsonschema for schema validation."""
        content = root_config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)
        repos = config.get("repos", [])

        jsonschema_repos = [
            r for r in repos if "check-jsonschema" in str(r.get("repo", ""))
        ]
        assert len(jsonschema_repos) > 0, "Should have check-jsonschema pre-commit repo"


class TestTemplatePrecommitConfig:
    """Tests for the template pre-commit configuration."""

    def test_template_config_exists(self, template_config_path: Path) -> None:
        """Verify template .pre-commit-config.yaml.jinja exists."""
        assert template_config_path.exists(), "Template config should exist"

    def test_template_has_profile_conditionals(
        self, template_config_path: Path
    ) -> None:
        """Verify template has quality_profile conditionals."""
        content = template_config_path.read_text(encoding="utf-8")

        # Check for profile conditionals
        assert "quality_profile == 'strict'" in content, (
            "Should have strict profile conditional"
        )
        assert "ty-check" in content, "Should reference ty-check hook"
        assert "pylint" in content, "Should reference pylint hook"

    def test_template_has_node_conditionals(self, template_config_path: Path) -> None:
        """Verify template has api_tracks conditionals for Node.js."""
        content = template_config_path.read_text(encoding="utf-8")

        # Check for Node.js conditionals
        assert "api_tracks" in content, "Should have api_tracks conditional"
        assert "prettier" in content, "Should reference prettier hook"
        assert "eslint" in content, "Should reference eslint hook"

    def test_template_has_monorepo_conditionals(
        self, template_config_path: Path
    ) -> None:
        """Verify template has project_layout conditionals for monorepo."""
        content = template_config_path.read_text(encoding="utf-8")

        # Check for monorepo conditionals
        assert "project_layout == 'monorepo'" in content, (
            "Should have monorepo conditional"
        )
        assert "apps|packages" in content, "Should have monorepo path pattern"

    def test_template_has_changelog_conditionals(
        self, template_config_path: Path
    ) -> None:
        """Verify template has changelog_module conditionals."""
        content = template_config_path.read_text(encoding="utf-8")

        # Check for changelog conditionals
        assert "changelog_module" in content, "Should have changelog_module conditional"
        assert "conventional-pre-commit" in content, (
            "Should reference conventional commits"
        )

    def test_template_has_prepush_hooks(self, template_config_path: Path) -> None:
        """Verify template includes pre-push hooks for strict profile."""
        content = template_config_path.read_text(encoding="utf-8")

        # Check for pre-push hooks
        assert "pre-push" in content, "Should have pre-push stage hooks"
        assert "pytest-prepush" in content, "Should have pytest pre-push hook"
        assert "pip-audit" in content, "Should have pip-audit hook"

    def test_template_has_ci_section(self, template_config_path: Path) -> None:
        """Verify template has CI configuration section."""
        content = template_config_path.read_text(encoding="utf-8")

        # Check for CI configuration
        assert "ci:" in content, "Should have ci configuration section"
        assert "autofix_prs" in content, "Should have autofix_prs setting"
        assert "autoupdate_schedule" in content, (
            "Should have autoupdate_schedule setting"
        )

    def test_template_has_gitleaks(self, template_config_path: Path) -> None:
        """Verify template includes gitleaks for secrets detection."""
        content = template_config_path.read_text(encoding="utf-8")
        assert "gitleaks" in content, "Should reference gitleaks hook"

    def test_template_has_shellcheck(self, template_config_path: Path) -> None:
        """Verify template includes shellcheck for bash linting."""
        content = template_config_path.read_text(encoding="utf-8")
        assert "shellcheck" in content, "Should reference shellcheck hook"

    def test_template_has_codespell(self, template_config_path: Path) -> None:
        """Verify template includes codespell for spell checking."""
        content = template_config_path.read_text(encoding="utf-8")
        assert "codespell" in content, "Should reference codespell hook"

    def test_template_has_mdformat(self, template_config_path: Path) -> None:
        """Verify template includes mdformat for markdown formatting."""
        content = template_config_path.read_text(encoding="utf-8")
        assert "mdformat" in content, "Should reference mdformat hook"

    def test_template_has_vulture_for_strict(self, template_config_path: Path) -> None:
        """Verify template includes vulture for dead code detection in strict profile."""
        content = template_config_path.read_text(encoding="utf-8")
        assert "vulture" in content, "Should reference vulture hook"

    def test_template_has_check_jsonschema(self, template_config_path: Path) -> None:
        """Verify template includes check-jsonschema for schema validation."""
        content = template_config_path.read_text(encoding="utf-8")
        assert "check-jsonschema" in content or "check-github-workflows" in content, (
            "Should reference check-jsonschema or check-github-workflows hook"
        )


class TestJinjaValidator:
    """Tests for the Jinja template validator script."""

    @pytest.fixture
    def validator_path(self) -> Path:
        """Return path to the validator script."""
        return (
            Path(__file__).parents[1] / "scripts" / "ci" / "validate_jinja_templates.py"
        )

    def test_validator_exists(self, validator_path: Path) -> None:
        """Verify the validator script exists."""
        assert validator_path.exists(), "Validator script should exist"

    def test_validator_is_executable_python(self, validator_path: Path) -> None:
        """Verify the validator script is valid Python."""
        content = validator_path.read_text(encoding="utf-8")
        # Should compile without syntax errors
        compile(content, validator_path, "exec")


class TestMakefileIntegration:
    """Tests for Makefile pre-commit targets."""

    @pytest.fixture
    def makefile_path(self) -> Path:
        """Return path to the root Makefile."""
        return Path(__file__).parents[1] / "Makefile"

    @pytest.fixture
    def template_makefile_path(self) -> Path:
        """Return path to the template makefile.quality.jinja."""
        return (
            Path(__file__).parents[1]
            / "template"
            / "files"
            / "shared"
            / "quality"
            / "makefile.quality.jinja"
        )

    def test_root_makefile_has_hooks_target(self, makefile_path: Path) -> None:
        """Verify root Makefile has hooks target."""
        content = makefile_path.read_text(encoding="utf-8")
        assert "hooks:" in content, "Makefile should have hooks target"
        assert "pre-commit run --all-files" in content, (
            "hooks target should run pre-commit"
        )

    def test_root_makefile_has_setup_with_hooks(self, makefile_path: Path) -> None:
        """Verify root Makefile setup installs all hook types."""
        content = makefile_path.read_text(encoding="utf-8")
        assert "pre-commit install --install-hooks" in content, (
            "setup should install hooks"
        )
        assert "--hook-type commit-msg" in content, (
            "setup should install commit-msg hooks"
        )
        assert "--hook-type pre-push" in content, "setup should install pre-push hooks"

    def test_template_makefile_has_hooks_targets(
        self, template_makefile_path: Path
    ) -> None:
        """Verify template makefile has hooks targets."""
        content = template_makefile_path.read_text(encoding="utf-8")
        assert "hooks:" in content, "Template should have hooks target"
        assert "hooks-run:" in content, "Template should have hooks-run target"
        assert "hooks-update:" in content, "Template should have hooks-update target"
