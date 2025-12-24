"""Unit tests for pre_gen_project.py hook."""
import json
import os
import pytest
from pathlib import Path
import sys

# Add hooks to path
sys.path.insert(0, str(Path(__file__).parents[3] / "template" / "hooks"))


class TestLoadDocsSite:
    """Tests for _load_docs_site function."""

    def test_default_value_when_no_env(self, monkeypatch):
        """Should return default when no env vars set."""
        monkeypatch.delenv("COPIER_ANSWERS", raising=False)
        monkeypatch.delenv("COPIER_JINJA2_CONTEXT", raising=False)
        monkeypatch.delenv("COPIER_RENDER_CONTEXT", raising=False)

        from pre_gen_project import _load_docs_site
        result = _load_docs_site()
        assert result == "fumadocs"

    def test_custom_default(self, monkeypatch):
        """Should return custom default when specified."""
        monkeypatch.delenv("COPIER_ANSWERS", raising=False)
        monkeypatch.delenv("COPIER_JINJA2_CONTEXT", raising=False)
        monkeypatch.delenv("COPIER_RENDER_CONTEXT", raising=False)

        from pre_gen_project import _load_docs_site
        result = _load_docs_site(default="sphinx-shibuya")
        assert result == "sphinx-shibuya"

    def test_loads_valid_value_from_env(self, monkeypatch):
        """Should load valid docs_site from COPIER_ANSWERS."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps({"docs_site": "docusaurus"}))

        from pre_gen_project import _load_docs_site
        result = _load_docs_site()
        assert result == "docusaurus"

    def test_rejects_invalid_value(self, monkeypatch):
        """Should reject invalid docs_site and return default."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps({"docs_site": "invalid-site"}))

        from pre_gen_project import _load_docs_site
        result = _load_docs_site()
        assert result == "fumadocs"

    def test_handles_invalid_json(self, monkeypatch):
        """Should handle invalid JSON gracefully."""
        monkeypatch.setenv("COPIER_ANSWERS", "not valid json")

        from pre_gen_project import _load_docs_site
        result = _load_docs_site()
        assert result == "fumadocs"

    def test_handles_non_dict_json(self, monkeypatch):
        """Should handle non-dict JSON gracefully."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps(["list", "not", "dict"]))

        from pre_gen_project import _load_docs_site
        result = _load_docs_site()
        assert result == "fumadocs"


class TestLoadCiPlatform:
    """Tests for _load_ci_platform function."""

    def test_default_value(self, monkeypatch):
        """Should return github-actions by default."""
        monkeypatch.delenv("COPIER_ANSWERS", raising=False)
        monkeypatch.delenv("COPIER_JINJA2_CONTEXT", raising=False)
        monkeypatch.delenv("COPIER_RENDER_CONTEXT", raising=False)

        from pre_gen_project import _load_ci_platform
        result = _load_ci_platform()
        assert result == "github-actions"

    def test_loads_valid_value(self, monkeypatch):
        """Should load valid ci_platform from env."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps({"ci_platform": "none"}))

        from pre_gen_project import _load_ci_platform
        result = _load_ci_platform()
        assert result == "none"

    def test_rejects_invalid_value(self, monkeypatch):
        """Should reject invalid ci_platform."""
        monkeypatch.setenv("COPIER_ANSWERS", json.dumps({"ci_platform": "jenkins"}))

        from pre_gen_project import _load_ci_platform
        result = _load_ci_platform()
        assert result == "github-actions"


class TestValidateSaasStarter:
    """Tests for SaaS starter validation."""

    def test_disabled_returns_empty(self):
        """Disabled SaaS module returns no issues."""
        from pre_gen_project import _validate_saas_starter
        context = {"saas_starter_module": "disabled"}
        issues = _validate_saas_starter(context)
        assert issues == []

    def test_neon_supabase_storage_incompatible(self):
        """Neon + Supabase Storage should be error."""
        from pre_gen_project import _validate_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "supabase-storage",
        }
        issues = _validate_saas_starter(context)
        errors = [i for i in issues if i["severity"] == "error"]
        assert len(errors) == 1
        assert "Neon" in errors[0]["message"]

    def test_cloudflare_prisma_warning(self):
        """Cloudflare + Prisma should warn."""
        from pre_gen_project import _validate_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_hosting": "cloudflare",
            "saas_orm": "prisma",
        }
        issues = _validate_saas_starter(context)
        warnings = [i for i in issues if i["severity"] == "warning"]
        assert any("Prisma" in w["message"] for w in warnings)

    def test_valid_combination_no_errors(self):
        """Valid combination should have no errors."""
        from pre_gen_project import _validate_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "r2",
            "saas_hosting": "vercel",
            "saas_orm": "prisma",
        }
        issues = _validate_saas_starter(context)
        errors = [i for i in issues if i["severity"] == "error"]
        assert len(errors) == 0


class TestProvisionResult:
    """Tests for ProvisionResult class."""

    def test_minimal_creation(self):
        """Should create with required fields."""
        from pre_gen_project import ProvisionResult
        result = ProvisionResult(
            tool_name="uv",
            version_requested="0.4",
            status="installed",
        )
        assert result["tool_name"] == "uv"
        assert result["status"] == "installed"
        assert "timestamp" in result

    def test_optional_fields(self):
        """Should include optional fields when provided."""
        from pre_gen_project import ProvisionResult
        result = ProvisionResult(
            tool_name="node",
            version_requested="20",
            status="failed",
            stderr="Error message",
            next_steps="Install manually",
            retry_command="mise install node@20",
        )
        assert result["stderr"] == "Error message"
        assert result["next_steps"] == "Install manually"
        assert result["retry_command"] == "mise install node@20"
