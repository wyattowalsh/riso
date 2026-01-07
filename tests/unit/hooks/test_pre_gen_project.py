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


class TestValidateAndReportSaasStarter:
    """Tests for _validate_and_report_saas_starter function."""

    def test_returns_true_when_saas_disabled(self, capsys):
        """Test returns True when SaaS starter is not enabled."""
        from pre_gen_project import _validate_and_report_saas_starter
        context = {"saas_starter_module": "disabled"}
        result = _validate_and_report_saas_starter(context)
        assert result is True
        # Should not write validation messages
        captured = capsys.readouterr()
        assert "Validating SaaS Starter" not in captured.err

    def test_returns_true_when_valid_config(self, capsys):
        """Test returns True for valid SaaS starter configuration."""
        from pre_gen_project import _validate_and_report_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "r2",
        }
        result = _validate_and_report_saas_starter(context)
        assert result is True
        captured = capsys.readouterr()
        assert "validated successfully" in captured.err

    def test_returns_false_when_errors_present(self, capsys):
        """Test returns False when validation errors exist."""
        from pre_gen_project import _validate_and_report_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "neon",
            "saas_storage": "supabase-storage",
        }
        result = _validate_and_report_saas_starter(context)
        assert result is False
        captured = capsys.readouterr()
        assert "Configuration errors found" in captured.err

    def test_reports_warnings_but_returns_true(self, capsys):
        """Test that warnings are reported but don't fail validation."""
        from pre_gen_project import _validate_and_report_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_hosting": "cloudflare",
            "saas_orm": "prisma",
        }
        result = _validate_and_report_saas_starter(context)
        assert result is True
        captured = capsys.readouterr()
        assert "Configuration warnings" in captured.err
        assert "Prisma" in captured.err

    def test_reports_info_notices(self, capsys):
        """Test that info notices are displayed."""
        from pre_gen_project import _validate_and_report_saas_starter
        context = {
            "saas_starter_module": "enabled",
            "saas_database": "supabase",
            "saas_auth": "clerk",
        }
        result = _validate_and_report_saas_starter(context)
        assert result is True
        captured = capsys.readouterr()
        assert "Configuration notes" in captured.err or "Supabase Auth" in captured.err


class TestBuildToolMatrix:
    """Tests for _build_tool_matrix function."""

    def test_always_includes_uv(self):
        """Test that uv is always in the tool matrix."""
        from pre_gen_project import _build_tool_matrix
        result = _build_tool_matrix("none", {})
        assert any(tool[0] == "uv" for tool in result)
        assert result[0] == ("uv", "0.4", "uv@0.4")

    def test_includes_node_for_docs_site(self):
        """Test that node/pnpm are included when docs_site is not 'none'."""
        from pre_gen_project import _build_tool_matrix
        result = _build_tool_matrix("fumadocs", {})
        tool_names = [tool[0] for tool in result]
        assert "node" in tool_names
        assert "pnpm" in tool_names

    def test_includes_node_for_saas_enabled(self):
        """Test that node/pnpm are included when saas_starter is enabled."""
        from pre_gen_project import _build_tool_matrix
        result = _build_tool_matrix("none", {"saas_starter_module": "enabled"})
        tool_names = [tool[0] for tool in result]
        assert "node" in tool_names
        assert "pnpm" in tool_names

    def test_excludes_node_when_not_needed(self):
        """Test that node/pnpm are excluded when not needed."""
        from pre_gen_project import _build_tool_matrix
        result = _build_tool_matrix("none", {"saas_starter_module": "disabled"})
        tool_names = [tool[0] for tool in result]
        assert "node" not in tool_names
        assert "pnpm" not in tool_names

    def test_correct_versions(self):
        """Test that correct versions are specified."""
        from pre_gen_project import _build_tool_matrix
        result = _build_tool_matrix("fumadocs", {})
        # Check uv version
        uv_entry = [tool for tool in result if tool[0] == "uv"][0]
        assert uv_entry[1] == "0.4"
        assert uv_entry[2] == "uv@0.4"
        # Check node version
        node_entry = [tool for tool in result if tool[0] == "node"][0]
        assert node_entry[1] == "20"
        assert node_entry[2] == "node@20"


class TestCheckAndLogActionlint:
    """Tests for _check_and_log_actionlint function."""

    def test_skips_for_non_github_platform(self, capsys, tmp_path, monkeypatch):
        """Test that function does nothing for non-GitHub CI platforms."""
        from pre_gen_project import _check_and_log_actionlint, LOG_PATH
        # Change to temp directory to avoid writing real log
        monkeypatch.chdir(tmp_path)

        _check_and_log_actionlint("none")

        captured = capsys.readouterr()
        assert "actionlint" not in captured.err
        # No log should be created
        assert not (tmp_path / ".riso" / "toolchain_provisioning.jsonl").exists()

    def test_logs_actionlint_not_found(self, capsys, tmp_path, monkeypatch):
        """Test that actionlint unavailability is logged for GitHub Actions."""
        from pre_gen_project import _check_and_log_actionlint
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        with patch("shutil.which", return_value=None):
            _check_and_log_actionlint("github-actions")

        captured = capsys.readouterr()
        assert "actionlint not found" in captured.err

        # Check log file
        log_file = tmp_path / ".riso" / "toolchain_provisioning.jsonl"
        assert log_file.exists()
        log_content = log_file.read_text()
        assert "actionlint" in log_content
        assert "not_found" in log_content

    def test_logs_actionlint_present(self, capsys, tmp_path, monkeypatch):
        """Test that actionlint availability is logged when present."""
        from pre_gen_project import _check_and_log_actionlint
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        with patch("shutil.which", return_value="/usr/local/bin/actionlint"):
            _check_and_log_actionlint("github-actions")

        # Check log file
        log_file = tmp_path / ".riso" / "toolchain_provisioning.jsonl"
        assert log_file.exists()
        log_content = log_file.read_text()
        assert "actionlint" in log_content
        assert "already_present" in log_content


class TestInstallRequiredTools:
    """Tests for _install_required_tools function."""

    def test_returns_empty_list_on_success(self, tmp_path, monkeypatch):
        """Test returns empty list when all tools install successfully."""
        from pre_gen_project import _install_required_tools
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        tool_matrix = [("uv", "0.4", "uv@0.4")]

        with patch("shutil.which", return_value="/usr/bin/uv"):
            failures = _install_required_tools(tool_matrix)

        assert failures == []

    def test_returns_failures(self, tmp_path, monkeypatch):
        """Test returns list of failures for failed installations."""
        from pre_gen_project import _install_required_tools
        from unittest.mock import patch, MagicMock

        monkeypatch.chdir(tmp_path)

        tool_matrix = [
            ("missing-tool", "1.0", "missing-tool@1.0"),
        ]

        with patch("shutil.which", return_value=None):
            failures = _install_required_tools(tool_matrix)

        assert len(failures) == 1
        assert failures[0]["tool_name"] == "missing-tool"
        assert failures[0]["status"] == "failed"

    def test_logs_all_attempts(self, tmp_path, monkeypatch):
        """Test that all installation attempts are logged."""
        from pre_gen_project import _install_required_tools
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        tool_matrix = [
            ("uv", "0.4", "uv@0.4"),
            ("node", "20", "node@20"),
        ]

        with patch("shutil.which", return_value="/usr/bin/tool"):
            _install_required_tools(tool_matrix)

        log_file = tmp_path / ".riso" / "toolchain_provisioning.jsonl"
        assert log_file.exists()
        log_content = log_file.read_text()
        # Should have 2 log entries
        assert log_content.count("\n") == 2


class TestCheckPythonQualityTools:
    """Tests for _check_python_quality_tools function."""

    def test_returns_empty_when_all_present(self, tmp_path, monkeypatch):
        """Test returns empty list when all quality tools are present."""
        from pre_gen_project import _check_python_quality_tools, ToolCheck
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        mock_checks = [
            ToolCheck(name="ruff", status="present", command="uv tool run"),
            ToolCheck(name="mypy", status="present", command="uv tool run"),
        ]

        with patch("pre_gen_project.ensure_python_quality_tools", return_value=mock_checks):
            failures = _check_python_quality_tools()

        assert failures == []

    def test_returns_failures_for_missing_tools(self, tmp_path, monkeypatch):
        """Test returns failures when tools are missing."""
        from pre_gen_project import _check_python_quality_tools, ToolCheck
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        mock_checks = [
            ToolCheck(name="ruff", status="present", command="uv tool run"),
            ToolCheck(
                name="mypy",
                status="failed",
                command="uv tool install",
                stderr="Installation failed",
            ),
        ]

        with patch("pre_gen_project.ensure_python_quality_tools", return_value=mock_checks):
            failures = _check_python_quality_tools()

        assert len(failures) == 1
        assert failures[0]["tool_name"] == "mypy"

    def test_handles_toolcheck_none(self, tmp_path, monkeypatch):
        """Test handles case when ToolCheck is None (during template linting)."""
        from pre_gen_project import _check_python_quality_tools
        from unittest.mock import patch

        monkeypatch.chdir(tmp_path)

        # Simulate ToolCheck being None
        with patch("pre_gen_project.ToolCheck", None):
            failures = _check_python_quality_tools()

        assert failures == []


class TestReportFailuresAndExit:
    """Tests for _report_failures_and_exit function."""

    def test_does_nothing_for_empty_failures(self, capsys):
        """Test function returns early for empty failures list."""
        from pre_gen_project import _report_failures_and_exit

        # Should not raise SystemExit
        _report_failures_and_exit([])

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_exits_with_code_1_on_failures(self, capsys):
        """Test function calls sys.exit(1) when there are failures."""
        from pre_gen_project import _report_failures_and_exit, ProvisionResult

        failures = [
            ProvisionResult(
                tool_name="uv",
                version_requested="0.4",
                status="failed",
                stderr="Error installing",
                next_steps="Install manually",
                retry_command="mise install uv@0.4",
            )
        ]

        with pytest.raises(SystemExit) as exc_info:
            _report_failures_and_exit(failures)

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "prerequisite check failed" in captured.err
        assert "uv" in captured.err
        assert "0.4" in captured.err

    def test_reports_all_failure_details(self, capsys):
        """Test that all failure details are reported."""
        from pre_gen_project import _report_failures_and_exit, ProvisionResult

        failures = [
            ProvisionResult(
                tool_name="node",
                version_requested="20",
                status="failed",
                stderr="Installation failed",
                next_steps="Install Node.js manually",
                retry_command="mise install node@20",
            )
        ]

        with pytest.raises(SystemExit):
            _report_failures_and_exit(failures)

        captured = capsys.readouterr()
        assert "stderr: Installation failed" in captured.err
        assert "retry: mise install node@20" in captured.err
        assert "help: Install Node.js manually" in captured.err

    def test_handles_multiple_failures(self, capsys):
        """Test reporting multiple failures."""
        from pre_gen_project import _report_failures_and_exit, ProvisionResult

        failures = [
            ProvisionResult(
                tool_name="uv",
                version_requested="0.4",
                status="failed",
            ),
            ProvisionResult(
                tool_name="node",
                version_requested="20",
                status="failed",
            ),
        ]

        with pytest.raises(SystemExit):
            _report_failures_and_exit(failures)

        captured = capsys.readouterr()
        assert "uv" in captured.err
        assert "node" in captured.err
