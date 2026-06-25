"""Tests for workflow_validator module."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


# Add scripts directories to path for imports
scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
if str(scripts_dir / "hooks") not in sys.path:
    sys.path.insert(0, str(scripts_dir / "hooks"))

from workflow_validator import (  # noqa: E402
    check_actionlint_available,
    validate_workflow_file,
    validate_workflows_directory,
)


class TestCheckActionlintAvailable:
    """Tests for check_actionlint_available function."""

    def test_returns_true_when_actionlint_installed(self):
        """Test returns True when actionlint command succeeds."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert check_actionlint_available() is True
            mock_run.assert_called_once()

    def test_returns_false_when_actionlint_not_found(self):
        """Test returns False when actionlint command not found."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            assert check_actionlint_available() is False

    def test_returns_false_when_timeout(self):
        """Test returns False when actionlint times out."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("actionlint", 5)
            assert check_actionlint_available() is False


class TestValidateWorkflowFile:
    """Tests for validate_workflow_file function."""

    def test_returns_false_when_file_not_exists(self, tmp_path: Path):
        """Test returns False when workflow file doesn't exist."""
        non_existent = tmp_path / "missing.yml"
        success, error = validate_workflow_file(non_existent)
        assert success is False
        assert "not found" in error

    def test_returns_true_when_validation_succeeds(self, tmp_path: Path):
        """Test returns True when actionlint succeeds."""
        workflow = tmp_path / "test.yml"
        workflow.write_text(
            "name: Test\non:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo hi"
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            success, error = validate_workflow_file(workflow)
            assert success is True
            assert error is None

    def test_returns_false_when_validation_fails(self, tmp_path: Path):
        """Test returns False when actionlint fails."""
        workflow = tmp_path / "test.yml"
        workflow.write_text("invalid: yaml: content")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="error: invalid workflow", stderr=""
            )
            success, error = validate_workflow_file(workflow)
            assert success is False
            assert "invalid workflow" in error

    def test_returns_false_on_timeout(self, tmp_path: Path):
        """Test returns False when validation times out."""
        workflow = tmp_path / "test.yml"
        workflow.write_text("name: Test")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("actionlint", 30)
            success, error = validate_workflow_file(workflow)
            assert success is False
            assert "timed out" in error

    def test_returns_false_on_os_error(self, tmp_path: Path):
        """Test returns False on OS error."""
        workflow = tmp_path / "test.yml"
        workflow.write_text("name: Test")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = OSError("Permission denied")
            success, error = validate_workflow_file(workflow)
            assert success is False
            assert "Unexpected error" in error


class TestValidateWorkflowsDirectory:
    """Tests for validate_workflows_directory function."""

    def test_returns_zero_when_actionlint_not_available_non_strict(self):
        """Test returns 0 when actionlint not available in non-strict mode."""
        with patch("workflow_validator.check_actionlint_available") as mock_check:
            mock_check.return_value = False
            result = validate_workflows_directory(Path("/fake"), strict=False)
            assert result == 0

    def test_returns_one_when_actionlint_not_available_strict(self):
        """Test returns 1 when actionlint not available in strict mode."""
        with patch("workflow_validator.check_actionlint_available") as mock_check:
            mock_check.return_value = False
            result = validate_workflows_directory(Path("/fake"), strict=True)
            assert result == 1

    def test_returns_zero_when_directory_not_exists(self, tmp_path: Path):
        """Test returns 0 when workflows directory doesn't exist."""
        with patch("workflow_validator.check_actionlint_available") as mock_check:
            mock_check.return_value = True
            non_existent = tmp_path / "nonexistent"
            result = validate_workflows_directory(non_existent)
            assert result == 0

    def test_returns_zero_when_no_workflow_files(self, tmp_path: Path):
        """Test returns 0 when workflows directory has no YAML files."""
        with patch("workflow_validator.check_actionlint_available") as mock_check:
            mock_check.return_value = True
            workflows_dir = tmp_path / "workflows"
            workflows_dir.mkdir()
            result = validate_workflows_directory(workflows_dir)
            assert result == 0

    def test_validates_all_yaml_workflow_files(self, tmp_path: Path):
        """Test validates every *.yml/*.yaml workflow, not only riso-*."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "other.yml").write_text("name: Other")

        with (
            patch("workflow_validator.check_actionlint_available") as mock_check,
            patch("workflow_validator.validate_workflow_file") as mock_validate,
        ):
            mock_check.return_value = True
            mock_validate.return_value = (True, None)

            result = validate_workflows_directory(workflows_dir)

            assert result == 0
            mock_validate.assert_called_once()

    def test_validates_all_workflow_files(self, tmp_path: Path):
        """Test validates all riso-*.yml files."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "riso-ci.yml").write_text("name: CI")
        (workflows_dir / "riso-deploy.yaml").write_text("name: Deploy")

        with (
            patch("workflow_validator.check_actionlint_available") as mock_check,
            patch("workflow_validator.validate_workflow_file") as mock_validate,
        ):
            mock_check.return_value = True
            mock_validate.return_value = (True, None)

            result = validate_workflows_directory(workflows_dir)

            assert result == 0
            assert mock_validate.call_count == 2

    def test_returns_zero_on_failure_non_strict(self, tmp_path: Path):
        """Test returns 0 on validation failure in non-strict mode."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "riso-ci.yml").write_text("name: CI")

        with (
            patch("workflow_validator.check_actionlint_available") as mock_check,
            patch("workflow_validator.validate_workflow_file") as mock_validate,
        ):
            mock_check.return_value = True
            mock_validate.return_value = (False, "error")

            result = validate_workflows_directory(workflows_dir, strict=False)
            assert result == 0

    def test_returns_one_on_failure_strict(self, tmp_path: Path):
        """Test returns 1 on validation failure in strict mode."""
        workflows_dir = tmp_path / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "riso-ci.yml").write_text("name: CI")

        with (
            patch("workflow_validator.check_actionlint_available") as mock_check,
            patch("workflow_validator.validate_workflow_file") as mock_validate,
        ):
            mock_check.return_value = True
            mock_validate.return_value = (False, "error")

            result = validate_workflows_directory(workflows_dir, strict=True)
            assert result == 1
