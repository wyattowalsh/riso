"""Tests for new sample template configurations."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("yaml")


@pytest.fixture
def samples_dir() -> Path:
    """Get the samples directory."""
    return Path(__file__).parents[2] / "samples"


class TestTauriSample:
    """Tests for Tauri desktop app sample configuration."""

    def test_tauri_sample_exists(self, samples_dir: Path):
        """Tauri sample should have copier-answers.yml."""
        tauri_dir = samples_dir / "tauri-app"
        answers_file = tauri_dir / "copier-answers.yml"
        assert answers_file.exists(), "Tauri sample answers file should exist"

    def test_tauri_sample_valid(self, samples_dir: Path):
        """Tauri sample should have valid configuration."""
        import yaml

        answers_file = samples_dir / "tauri-app" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("Tauri sample not found")

        data = yaml.safe_load(answers_file.read_text())

        # Check basic project metadata
        assert data.get("project_name") == "Tauri Desktop App"
        assert data.get("project_slug") == "tauri-desktop-app"
        assert data.get("project_layout") == "single-package"
        assert data.get("quality_profile") == "standard"

        # Check desktop module configuration
        assert data.get("desktop_module") == "enabled"
        assert data.get("desktop_framework") == "tauri"

        # Check desktop features
        desktop_features = data.get("desktop_features", "")
        if isinstance(desktop_features, str):
            features_list = [f.strip() for f in desktop_features.split(",")]
        else:
            features_list = desktop_features
        assert "auto_updater" in features_list
        assert "tray_icon" in features_list
        assert "custom_titlebar" in features_list

        # Verify other modules are disabled
        assert data.get("cli_module") == "disabled"
        assert data.get("api_module") == "disabled"
        assert data.get("mcp_module") == "disabled"

    def test_tauri_sample_has_ci_platform(self, samples_dir: Path):
        """Tauri sample should specify CI platform."""
        import yaml

        answers_file = samples_dir / "tauri-app" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("Tauri sample not found")

        data = yaml.safe_load(answers_file.read_text())
        assert data.get("ci_platform") == "github-actions"


class TestGitLabCISample:
    """Tests for GitLab CI Python sample configuration."""

    def test_gitlab_ci_sample_exists(self, samples_dir: Path):
        """GitLab CI sample should have copier-answers.yml."""
        gitlab_dir = samples_dir / "gitlab-ci-python"
        answers_file = gitlab_dir / "copier-answers.yml"
        assert answers_file.exists(), "GitLab CI sample answers file should exist"

    def test_gitlab_ci_sample_valid(self, samples_dir: Path):
        """GitLab CI sample should have valid configuration."""
        import yaml

        answers_file = samples_dir / "gitlab-ci-python" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("GitLab CI sample not found")

        data = yaml.safe_load(answers_file.read_text())

        # Check basic project metadata
        assert data.get("project_name") == "GitLab CI Python"
        assert data.get("project_slug") == "gitlab-ci-python"
        assert data.get("project_layout") == "single-package"
        assert data.get("quality_profile") == "strict"

        # Check Python versions
        python_versions = data.get("python_versions", [])
        assert "3.11" in python_versions
        assert "3.12" in python_versions
        assert "3.13" in python_versions

        # Check modules
        assert data.get("cli_module") == "enabled"
        assert "python" in data.get("cli_languages", [])
        assert data.get("api_module") == "enabled"
        assert "python" in data.get("api_languages", [])

        # Check CI platform
        assert data.get("ci_platform") == "gitlab-ci"

    def test_gitlab_ci_has_changelog_module(self, samples_dir: Path):
        """GitLab CI sample should have changelog module enabled."""
        import yaml

        answers_file = samples_dir / "gitlab-ci-python" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("GitLab CI sample not found")

        data = yaml.safe_load(answers_file.read_text())
        assert data.get("changelog_module") == "enabled"

    def test_gitlab_ci_has_docs_module(self, samples_dir: Path):
        """GitLab CI sample should have documentation enabled."""
        import yaml

        answers_file = samples_dir / "gitlab-ci-python" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("GitLab CI sample not found")

        data = yaml.safe_load(answers_file.read_text())
        assert data.get("docs_module") == "enabled"
        assert data.get("docs_framework") == "fumadocs"


class TestRAGEnabledSample:
    """Tests for RAG-enabled SaaS sample configuration."""

    def test_rag_sample_exists(self, samples_dir: Path):
        """RAG sample should have copier-answers.yml."""
        rag_dir = samples_dir / "rag-enabled"
        answers_file = rag_dir / "copier-answers.yml"
        assert answers_file.exists(), "RAG sample answers file should exist"

    def test_rag_sample_valid(self, samples_dir: Path):
        """RAG sample should have valid configuration."""
        import yaml

        answers_file = samples_dir / "rag-enabled" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("RAG sample not found")

        data = yaml.safe_load(answers_file.read_text())

        # Check basic project metadata
        assert data.get("project_name") == "RAG Enabled SaaS"
        assert data.get("project_slug") == "rag-enabled-saas"
        assert data.get("project_layout") == "single-package"

        # Check SaaS infrastructure layer
        assert data.get("saas_infra_module") == "enabled"
        assert data.get("saas_runtime") == "nextjs-16"
        assert data.get("saas_hosting") == "vercel"
        assert data.get("saas_database") == "neon"

        # Check SaaS auth layer
        assert data.get("saas_auth_module") == "enabled"
        assert data.get("saas_auth_provider") == "clerk"

        # Check SaaS billing layer
        assert data.get("saas_billing_module") == "enabled"
        assert data.get("saas_billing_provider") == "stripe"

        # Check SaaS app layer
        assert data.get("saas_app_module") == "enabled"

    def test_rag_sample_has_ai_features(self, samples_dir: Path):
        """RAG sample should have full AI features enabled."""
        import yaml

        answers_file = samples_dir / "rag-enabled" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("RAG sample not found")

        data = yaml.safe_load(answers_file.read_text())

        # Check AI/RAG configuration
        assert data.get("saas_ai_features") == "full"
        assert data.get("vector_db_provider") == "pinecone"
        assert data.get("embedding_provider") == "openai"

    def test_rag_sample_has_auth_and_billing(self, samples_dir: Path):
        """RAG sample should have auth and billing configured."""
        import yaml

        answers_file = samples_dir / "rag-enabled" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("RAG sample not found")

        data = yaml.safe_load(answers_file.read_text())

        # Check auth provider
        assert data.get("saas_auth_provider") == "clerk"

        # Check database provider
        assert data.get("saas_database") == "neon"

    def test_rag_sample_has_observability(self, samples_dir: Path):
        """RAG sample should have observability features."""
        import yaml

        answers_file = samples_dir / "rag-enabled" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("RAG sample not found")

        data = yaml.safe_load(answers_file.read_text())

        # Check observability features
        assert data.get("saas_observability_sentry") is True
        assert data.get("saas_observability_otel") is True
        assert data.get("saas_observability_structured_logging") is True

    def test_rag_sample_has_tenancy_model(self, samples_dir: Path):
        """RAG sample should specify B2B teams tenancy model."""
        import yaml

        answers_file = samples_dir / "rag-enabled" / "copier-answers.yml"
        if not answers_file.exists():
            pytest.skip("RAG sample not found")

        data = yaml.safe_load(answers_file.read_text())
        assert data.get("saas_tenancy_model") == "b2b-teams"


class TestNewSamplesMetadata:
    """Tests for metadata and consistency across new samples."""

    def test_all_new_samples_have_required_fields(self, samples_dir: Path):
        """All new samples should have required fields."""
        import yaml

        new_samples = ["tauri-app", "gitlab-ci-python", "rag-enabled"]

        for sample_name in new_samples:
            answers_file = samples_dir / sample_name / "copier-answers.yml"
            if not answers_file.exists():
                pytest.skip(f"{sample_name} sample not found")

            data = yaml.safe_load(answers_file.read_text())

            # Required fields for all samples
            assert "_commit" in data
            assert "_src_path" in data
            assert "project_name" in data
            assert "project_slug" in data
            assert "project_layout" in data

    def test_all_new_samples_use_valid_layout(self, samples_dir: Path):
        """All new samples should use valid project layout."""
        import yaml

        new_samples = ["tauri-app", "gitlab-ci-python", "rag-enabled"]
        valid_layouts = ["single-package", "monorepo"]

        for sample_name in new_samples:
            answers_file = samples_dir / sample_name / "copier-answers.yml"
            if not answers_file.exists():
                continue

            data = yaml.safe_load(answers_file.read_text())
            assert data.get("project_layout") in valid_layouts

    def test_all_new_samples_have_ai_tools_module(self, samples_dir: Path):
        """All new samples should specify ai_tools_module setting."""
        import yaml

        new_samples = ["tauri-app", "gitlab-ci-python", "rag-enabled"]

        for sample_name in new_samples:
            answers_file = samples_dir / sample_name / "copier-answers.yml"
            if not answers_file.exists():
                continue

            data = yaml.safe_load(answers_file.read_text())
            assert "ai_tools_module" in data
