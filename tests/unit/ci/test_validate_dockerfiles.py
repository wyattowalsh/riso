"""Unit tests for validate_dockerfiles.py"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "ci"))


class TestCheckHadolintInstalled:
    """Tests for hadolint installation check."""

    def test_hadolint_installed(self, monkeypatch):
        """Should return True when hadolint is installed."""
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            return result

        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import check_hadolint_installed
        assert check_hadolint_installed() is True

    def test_hadolint_not_found(self, monkeypatch):
        """Should return False when hadolint is not found."""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("hadolint not found")

        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import check_hadolint_installed
        assert check_hadolint_installed() is False

    def test_hadolint_execution_error(self, monkeypatch):
        """Should return False when hadolint execution fails."""
        import subprocess

        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, "hadolint")

        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import check_hadolint_installed
        assert check_hadolint_installed() is False


class TestDockerfileDiscovery:
    """Tests for Dockerfile discovery."""

    def test_finds_dockerfile_in_root(self, temp_dir):
        """Should find Dockerfile in project root."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\n")

        from validate_dockerfiles import find_dockerfiles
        found = find_dockerfiles(temp_dir)
        assert len(found) >= 1
        assert any("Dockerfile" in str(f) for f in found)

    def test_finds_dockerfile_in_subdirectory(self, temp_dir):
        """Should find Dockerfiles in subdirectories."""
        docker_dir = temp_dir / ".docker"
        docker_dir.mkdir()
        dockerfile = docker_dir / "Dockerfile.python"
        dockerfile.write_text("FROM python:3.11-slim\n")

        from validate_dockerfiles import find_dockerfiles
        found = find_dockerfiles(temp_dir)
        assert len(found) >= 1
        assert any("Dockerfile.python" in str(f) for f in found)

    def test_finds_multiple_dockerfiles(self, temp_dir):
        """Should find multiple Dockerfiles."""
        (temp_dir / "Dockerfile").write_text("FROM python:3.11\n")
        docker_dir = temp_dir / ".docker"
        docker_dir.mkdir()
        (docker_dir / "Dockerfile.test").write_text("FROM node:20\n")
        (docker_dir / "Dockerfile.prod").write_text("FROM python:3.11\n")

        from validate_dockerfiles import find_dockerfiles
        found = find_dockerfiles(temp_dir)
        assert len(found) == 3

    def test_ignores_dockerignore_files(self, temp_dir):
        """Should not include .dockerignore files."""
        (temp_dir / "Dockerfile").write_text("FROM python:3.11\n")
        (temp_dir / ".dockerignore").write_text("*.pyc\n__pycache__\n")

        from validate_dockerfiles import find_dockerfiles
        found = find_dockerfiles(temp_dir)
        assert all(".dockerignore" not in str(f) for f in found)

    def test_returns_empty_when_no_dockerfiles(self, temp_dir):
        """Should return empty list when no Dockerfiles exist."""
        from validate_dockerfiles import find_dockerfiles
        found = find_dockerfiles(temp_dir)
        assert found == []

    def test_deduplicates_results(self, temp_dir):
        """Should deduplicate and sort results."""
        (temp_dir / "Dockerfile").write_text("FROM python:3.11\n")

        from validate_dockerfiles import find_dockerfiles
        found = find_dockerfiles(temp_dir)
        # Run twice to ensure deduplication works
        found2 = find_dockerfiles(temp_dir)
        assert found == found2
        assert len(found) == 1


class TestDockerfileValidation:
    """Tests for Dockerfile validation logic."""

    def test_valid_dockerfile_passes(self, temp_dir, monkeypatch):
        """Valid Dockerfile should pass basic validation."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("""FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
""")

        # Mock hadolint to return no issues
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "[]"  # No issues
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            monkeypatch.setattr("subprocess.run", mock_run)
            from validate_dockerfiles import validate_dockerfile
            result = validate_dockerfile(dockerfile)

            assert result["passed"] is True
            assert len(result["errors"]) == 0
            assert len(result["warnings"]) == 0
        finally:
            os.chdir(original_cwd)

    def test_dockerfile_with_errors(self, temp_dir, monkeypatch):
        """Dockerfile with errors should fail validation."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python\n")  # Missing specific version tag

        # Mock hadolint to return errors
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = json.dumps([
                {
                    "line": 1,
                    "code": "DL3006",
                    "message": "Always tag the version of an image explicitly",
                    "column": 1,
                    "file": str(dockerfile),
                    "level": "error"
                }
            ])
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            monkeypatch.setattr("subprocess.run", mock_run)
            from validate_dockerfiles import validate_dockerfile
            result = validate_dockerfile(dockerfile)

            assert result["passed"] is False
            assert len(result["errors"]) == 1
            assert result["errors"][0]["code"] == "DL3006"
            assert result["errors"][0]["level"] == "error"
        finally:
            os.chdir(original_cwd)

    def test_dockerfile_with_warnings(self, temp_dir, monkeypatch):
        """Dockerfile with warnings should pass but show warnings."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\nRUN apt-get update\n")

        # Mock hadolint to return warnings only
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps([
                {
                    "line": 2,
                    "code": "DL3008",
                    "message": "Pin versions in apt-get install",
                    "column": 1,
                    "file": str(dockerfile),
                    "level": "warning"
                }
            ])
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            monkeypatch.setattr("subprocess.run", mock_run)
            from validate_dockerfiles import validate_dockerfile
            result = validate_dockerfile(dockerfile)

            assert result["passed"] is True  # Warnings don't fail validation
            assert len(result["errors"]) == 0
            assert len(result["warnings"]) == 1
            assert result["warnings"][0]["code"] == "DL3008"
        finally:
            os.chdir(original_cwd)

    def test_dockerfile_with_mixed_issues(self, temp_dir, monkeypatch):
        """Dockerfile with errors and warnings should categorize correctly."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\n")

        # Mock hadolint to return mixed issues
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = json.dumps([
                {
                    "line": 1,
                    "code": "DL3006",
                    "message": "Error message",
                    "level": "error"
                },
                {
                    "line": 2,
                    "code": "DL3008",
                    "message": "Warning message",
                    "level": "warning"
                },
                {
                    "line": 3,
                    "code": "DL3009",
                    "message": "Info message",
                    "level": "info"
                },
                {
                    "line": 4,
                    "code": "DL3010",
                    "message": "Style message",
                    "level": "style"
                }
            ])
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            monkeypatch.setattr("subprocess.run", mock_run)
            from validate_dockerfiles import validate_dockerfile
            result = validate_dockerfile(dockerfile)

            assert result["passed"] is False
            assert len(result["errors"]) == 1
            assert len(result["warnings"]) == 3  # warning, info, and style
        finally:
            os.chdir(original_cwd)

    def test_handles_missing_file(self, temp_dir):
        """Should handle missing file gracefully."""
        from validate_dockerfiles import validate_dockerfile
        non_existent = temp_dir / "NonExistent"

        with pytest.raises(FileNotFoundError):
            validate_dockerfile(non_existent)

    def test_handles_invalid_json_output(self, temp_dir, monkeypatch):
        """Should raise RuntimeError when hadolint returns invalid JSON."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = "invalid json"
            result.stderr = ""
            return result

        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        with pytest.raises(RuntimeError, match="Failed to parse hadolint JSON output"):
            validate_dockerfile(dockerfile)

    def test_handles_subprocess_error(self, temp_dir, monkeypatch):
        """Should raise RuntimeError on subprocess errors."""
        import subprocess
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11\n")

        def mock_run(*args, **kwargs):
            raise subprocess.SubprocessError("Subprocess failed")

        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        with pytest.raises(RuntimeError, match="hadolint execution failed"):
            validate_dockerfile(dockerfile)

    def test_empty_hadolint_output(self, temp_dir, monkeypatch):
        """Should handle empty hadolint output correctly."""
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""  # Empty output
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            monkeypatch.setattr("subprocess.run", mock_run)
            from validate_dockerfiles import validate_dockerfile
            result = validate_dockerfile(dockerfile)

            assert result["passed"] is True
            assert len(result["errors"]) == 0
            assert len(result["warnings"]) == 0
        finally:
            os.chdir(original_cwd)


class TestPrintValidationSummary:
    """Tests for validation summary printing."""

    def test_prints_summary_for_all_passed(self, capsys):
        """Should print summary when all files pass."""
        from validate_dockerfiles import print_validation_summary

        results = [
            {
                "file": "Dockerfile",
                "passed": True,
                "errors": [],
                "warnings": []
            },
            {
                "file": ".docker/Dockerfile.test",
                "passed": True,
                "errors": [],
                "warnings": []
            }
        ]

        print_validation_summary(results)
        captured = capsys.readouterr()

        assert "Total files scanned: 2" in captured.out
        assert "Passed: 2" in captured.out
        assert "Failed: 0" in captured.out
        assert "✅ PASS" in captured.out

    def test_prints_summary_with_failures(self, capsys):
        """Should print summary with failure details."""
        from validate_dockerfiles import print_validation_summary

        results = [
            {
                "file": "Dockerfile",
                "passed": False,
                "errors": [
                    {
                        "code": "DL3006",
                        "line": 1,
                        "message": "Always tag the version"
                    }
                ],
                "warnings": []
            }
        ]

        print_validation_summary(results)
        captured = capsys.readouterr()

        assert "Total files scanned: 1" in captured.out
        assert "Passed: 0" in captured.out
        assert "Failed: 1" in captured.out
        assert "❌ FAIL" in captured.out
        assert "DL3006" in captured.out
        assert "Always tag the version" in captured.out

    def test_prints_warnings(self, capsys):
        """Should print warning details."""
        from validate_dockerfiles import print_validation_summary

        results = [
            {
                "file": "Dockerfile",
                "passed": True,
                "errors": [],
                "warnings": [
                    {
                        "code": "DL3008",
                        "line": 5,
                        "message": "Pin versions in apt-get"
                    }
                ]
            }
        ]

        print_validation_summary(results)
        captured = capsys.readouterr()

        assert "Warnings: 1" in captured.out
        assert "DL3008" in captured.out
        assert "Pin versions in apt-get" in captured.out


class TestMain:
    """Tests for main entry point."""

    def test_main_with_no_args(self, monkeypatch):
        """Should return exit code 2 when no arguments provided."""
        from validate_dockerfiles import main

        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py"])
        exit_code = main()
        assert exit_code == 2

    def test_main_with_nonexistent_directory(self, monkeypatch, temp_dir):
        """Should return exit code 2 for nonexistent directory."""
        from validate_dockerfiles import main

        nonexistent = temp_dir / "nonexistent"
        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(nonexistent)])
        exit_code = main()
        assert exit_code == 2

    def test_main_with_file_instead_of_directory(self, monkeypatch, temp_dir):
        """Should return exit code 2 when given a file instead of directory."""
        from validate_dockerfiles import main

        file_path = temp_dir / "file.txt"
        file_path.write_text("content")
        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(file_path)])
        exit_code = main()
        assert exit_code == 2

    def test_main_without_hadolint(self, monkeypatch, temp_dir):
        """Should return exit code 2 when hadolint is not installed."""
        from validate_dockerfiles import main

        # Create a Dockerfile
        (temp_dir / "Dockerfile").write_text("FROM python:3.11\n")

        # Mock hadolint check to fail
        def mock_check():
            return False

        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(temp_dir)])
        with patch("validate_dockerfiles.check_hadolint_installed", mock_check):
            exit_code = main()
        assert exit_code == 2

    def test_main_with_no_dockerfiles(self, monkeypatch, temp_dir):
        """Should return exit code 0 when no Dockerfiles found."""
        from validate_dockerfiles import main

        # Mock hadolint check to succeed
        def mock_check():
            return True

        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(temp_dir)])
        with patch("validate_dockerfiles.check_hadolint_installed", mock_check):
            exit_code = main()
        assert exit_code == 0
