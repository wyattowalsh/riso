"""Unit tests for validate_workflows.py"""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add scripts/ci to path
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "ci"))


class TestValidateWorkflow:
    """Tests for validate_workflow function."""

    def test_valid_workflow_passes(self, temp_dir, monkeypatch):
        """Valid workflow should pass when actionlint succeeds."""
        workflow = temp_dir / "test.yml"
        workflow.write_text("""
name: Test Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflow
        result = validate_workflow(workflow)

        assert result["status"] == "pass"
        assert result["workflow"] == str(workflow)
        assert result["errors"] == []

    def test_invalid_workflow_fails(self, temp_dir, monkeypatch):
        """Invalid workflow should fail when actionlint finds errors."""
        workflow = temp_dir / "test.yml"
        workflow.write_text("""
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
""")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = json.dumps({
                "line": 7,
                "column": 9,
                "message": "shellcheck reported issue",
                "kind": "error"
            })
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflow
        result = validate_workflow(workflow)

        assert result["status"] == "fail"
        assert len(result["errors"]) > 0
        assert result["errors"][0]["message"] == "shellcheck reported issue"

    def test_actionlint_not_installed(self, temp_dir, monkeypatch):
        """Should handle actionlint not being installed."""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("actionlint not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        workflow = temp_dir / "test.yml"
        workflow.write_text("name: Test\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo test\n")

        from validate_workflows import validate_workflow
        result = validate_workflow(workflow)

        assert result["status"] == "skipped"
        assert any("actionlint not found" in str(e.get("message", "")) for e in result["errors"])

    def test_validation_timeout(self, temp_dir, monkeypatch):
        """Should handle validation timeout."""
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired("actionlint", 30)

        monkeypatch.setattr(subprocess, "run", mock_run)

        workflow = temp_dir / "test.yml"
        workflow.write_text("name: Test\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo test\n")

        from validate_workflows import validate_workflow
        result = validate_workflow(workflow)

        assert result["status"] == "fail"
        assert any("timed out" in str(e.get("message", "")).lower() for e in result["errors"])

    def test_handles_non_json_output(self, temp_dir, monkeypatch):
        """Should handle non-JSON actionlint output gracefully."""
        workflow = temp_dir / "test.yml"
        workflow.write_text("name: Test\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo test\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = "Some error message that is not JSON"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflow
        result = validate_workflow(workflow)

        assert result["status"] == "fail"
        assert len(result["errors"]) > 0


class TestValidateWorkflows:
    """Tests for validate_workflows function."""

    def test_finds_yml_files(self, temp_dir, monkeypatch):
        """Should find and validate .yml workflow files."""
        workflows_dir = temp_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "test.yml").write_text("name: Test\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflows
        exit_code = validate_workflows(workflows_dir)

        assert exit_code == 0

    def test_finds_yaml_files(self, temp_dir, monkeypatch):
        """Should find and validate .yaml workflow files."""
        workflows_dir = temp_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "test.yaml").write_text("name: Test\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflows
        exit_code = validate_workflows(workflows_dir)

        assert exit_code == 0

    def test_nonexistent_directory_fails(self, temp_dir):
        """Should fail for non-existent directory."""
        from validate_workflows import validate_workflows
        exit_code = validate_workflows(temp_dir / "nonexistent")

        assert exit_code == 1

    def test_empty_directory_succeeds(self, temp_dir):
        """Should succeed with exit code 0 for empty directory."""
        workflows_dir = temp_dir / "workflows"
        workflows_dir.mkdir()

        from validate_workflows import validate_workflows
        exit_code = validate_workflows(workflows_dir)

        assert exit_code == 0

    def test_mixed_results(self, temp_dir, monkeypatch):
        """Should return failure exit code when any workflow fails."""
        workflows_dir = temp_dir / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "pass.yml").write_text("name: Pass\n")
        (workflows_dir / "fail.yml").write_text("name: Fail\n")

        call_count = {"count": 0}

        def mock_run(*args, **kwargs):
            result = MagicMock()
            # First call passes, second fails
            if call_count["count"] == 0:
                result.returncode = 0
                result.stdout = ""
            else:
                result.returncode = 1
                result.stdout = json.dumps({
                    "line": 1,
                    "column": 1,
                    "message": "error",
                    "kind": "error"
                })
            result.stderr = ""
            call_count["count"] += 1
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflows
        exit_code = validate_workflows(workflows_dir)

        assert exit_code == 1

    def test_json_output(self, temp_dir, monkeypatch, capsys):
        """Should output results as JSON when requested."""
        workflows_dir = temp_dir / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "test.yml").write_text("name: Test\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflows
        exit_code = validate_workflows(workflows_dir, output_json=True)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert exit_code == 0
        assert output["status"] == "pass"
        assert output["total"] == 1
        assert output["passed"] == 1
        assert output["failed"] == 0

    def test_all_workflows_pass(self, temp_dir, monkeypatch):
        """Should return success when all workflows pass."""
        workflows_dir = temp_dir / "workflows"
        workflows_dir.mkdir()
        (workflows_dir / "test1.yml").write_text("name: Test1\n")
        (workflows_dir / "test2.yaml").write_text("name: Test2\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        from validate_workflows import validate_workflows
        exit_code = validate_workflows(workflows_dir)

        assert exit_code == 0
