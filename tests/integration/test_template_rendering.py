"""Integration tests for template rendering."""
import json
import subprocess
import pytest
from pathlib import Path


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestDefaultSampleRendering:
    """Tests for default sample rendering."""

    @pytest.fixture
    def samples_dir(self) -> Path:
        """Get the samples directory."""
        return Path(__file__).parents[2] / "samples"

    def test_default_sample_exists(self, samples_dir):
        """Default sample should have copier-answers.yml."""
        default_dir = samples_dir / "default"
        answers_file = default_dir / "copier-answers.yml"
        assert answers_file.exists(), "Default sample answers file should exist"

    def test_default_answers_valid_yaml(self, samples_dir):
        """Default sample answers should be valid YAML."""
        import yaml

        answers_file = samples_dir / "default" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("Default sample not found")

        content = answers_file.read_text()
        data = yaml.safe_load(content)

        assert isinstance(data, dict)
        assert "project_name" in data

    def test_all_samples_have_answers(self, samples_dir):
        """All sample directories should have copier-answers.yml."""
        if not samples_dir.exists():
            pytest.skip("Samples directory not found")

        for sample_dir in samples_dir.iterdir():
            if sample_dir.is_dir() and sample_dir.name != "metadata":
                answers_file = sample_dir / "copier-answers.yml"
                assert answers_file.exists(), f"{sample_dir.name} missing copier-answers.yml"


class TestSampleConfiguration:
    """Tests for sample configuration validity."""

    @pytest.fixture
    def samples_dir(self) -> Path:
        """Get the samples directory."""
        return Path(__file__).parents[2] / "samples"

    def test_api_python_sample_has_correct_tracks(self, samples_dir):
        """API Python sample should have python api_tracks."""
        import yaml

        answers_file = samples_dir / "api-python" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("api-python sample not found")

        data = yaml.safe_load(answers_file.read_text())
        assert data.get("api_tracks") == "python"

    def test_full_stack_sample_has_strict_quality(self, samples_dir):
        """Full stack sample should use strict quality profile."""
        import yaml

        answers_file = samples_dir / "full-stack" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("full-stack sample not found")

        data = yaml.safe_load(answers_file.read_text())
        assert data.get("quality_profile") == "strict"

    def test_monorepo_samples_have_correct_layout(self, samples_dir):
        """Monorepo samples should have monorepo layout."""
        import yaml

        for sample_name in ["api-monorepo", "changelog-monorepo"]:
            answers_file = samples_dir / sample_name / "copier-answers.yml"
            if not answers_file.exists():
                continue

            data = yaml.safe_load(answers_file.read_text())
            assert data.get("project_layout") == "monorepo", f"{sample_name} should be monorepo"


class TestTemplateFiles:
    """Tests for template file validity."""

    @pytest.fixture
    def template_dir(self) -> Path:
        """Get the template directory."""
        return Path(__file__).parents[2] / "template"

    def test_copier_yml_exists(self, template_dir):
        """Template should have copier.yml configuration."""
        copier_config = template_dir / "copier.yml"
        assert copier_config.exists()

    def test_copier_yml_valid_yaml(self, template_dir):
        """copier.yml should be valid YAML."""
        import yaml

        copier_config = template_dir / "copier.yml"
        content = copier_config.read_text()
        data = yaml.safe_load(content)

        assert isinstance(data, dict)
        assert "prompts" in data or "defaults" in data

    def test_hooks_exist(self, template_dir):
        """Template hooks should exist."""
        hooks_dir = template_dir / "hooks"
        assert hooks_dir.exists()
        assert (hooks_dir / "pre_gen_project.py").exists()
        assert (hooks_dir / "post_gen_project.py").exists()
