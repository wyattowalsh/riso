"""Unit tests for validate_dockerfiles.py"""

import json
from unittest.mock import MagicMock, patch

import pytest


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
@pytest.mark.parametrize(
    "content,expected_passed,expected_error_codes,expected_warning_codes",
    [
        # Valid Dockerfiles
        pytest.param(
            "FROM python:3.11-slim\nWORKDIR /app\n",
            True,
            [],
            [],
            id="valid-simple-dockerfile",
        ),
        pytest.param(
            "FROM python:3.11\nRUN pip install requests\nCMD ['python', 'app.py']\n",
            True,
            [],
            [],
            id="valid-with-run-and-cmd",
        ),
        pytest.param(
            "FROM alpine:3.18\nRUN apk add --no-cache git=2.40.1-r0\n",
            True,
            [],
            [],
            id="valid-alpine-with-pinned-version",
        ),
        # Dockerfiles with errors
        pytest.param(
            "FROM python\n",
            False,
            ["DL3006"],
            [],
            id="error-missing-version-tag",
        ),
        pytest.param(
            "FROM scratch\nRUN apt-get update\n",
            False,
            ["DL3006", "DL3008"],
            [],
            id="error-scratch-with-apt-get",
        ),
        pytest.param(
            "RUN echo 'no FROM instruction'\n",
            False,
            ["DL3001"],
            [],
            id="error-missing-from",
        ),
        # Dockerfiles with warnings only
        pytest.param(
            "FROM python:3.11-slim\nRUN apt-get update\n",
            True,
            [],
            ["DL3008"],
            id="warning-apt-get-unpinned",
        ),
        pytest.param(
            "FROM node:20\nRUN npm install\n",
            True,
            [],
            ["DL3016"],
            id="warning-npm-unpinned",
        ),
    ],
)
def test_dockerfile_validation_parametrized(
    content,
    expected_passed,
    expected_error_codes,
    expected_warning_codes,
    temp_dir,
    monkeypatch,
):
    """Test Dockerfile validation with various content scenarios."""
    # Resolve temp_dir to avoid symlink issues on macOS
    temp_dir = temp_dir.resolve()
    dockerfile = temp_dir / "Dockerfile"
    dockerfile.write_text(content)

    # Build hadolint response based on expected errors and warnings
    issues = []
    for code in expected_error_codes:
        issues.append(
            {
                "line": 1,
                "code": code,
                "message": f"Error for {code}",
                "column": 1,
                "file": str(dockerfile),
                "level": "error",
            }
        )
    for code in expected_warning_codes:
        issues.append(
            {
                "line": 1,
                "code": code,
                "message": f"Warning for {code}",
                "column": 1,
                "file": str(dockerfile),
                "level": "warning",
            }
        )

    # Mock hadolint
    def mock_run(*args, **kwargs):
        result = MagicMock()
        result.returncode = 1 if expected_error_codes else 0
        result.stdout = json.dumps(issues)
        result.stderr = ""
        return result

    # Change to temp_dir so relative paths work
    monkeypatch.chdir(temp_dir)
    monkeypatch.setattr("subprocess.run", mock_run)
    from validate_dockerfiles import validate_dockerfile

    result = validate_dockerfile(dockerfile)

    assert result["passed"] is expected_passed
    assert len(result["errors"]) == len(expected_error_codes)
    assert len(result["warnings"]) == len(expected_warning_codes)

    # Verify error codes match
    actual_error_codes = [err["code"] for err in result["errors"]]
    assert sorted(actual_error_codes) == sorted(expected_error_codes)

    # Verify warning codes match
    actual_warning_codes = [warn["code"] for warn in result["warnings"]]
    assert sorted(actual_warning_codes) == sorted(expected_warning_codes)


@pytest.mark.unit
@pytest.mark.parametrize(
    "level,should_fail",
    [
        pytest.param("error", True, id="error-level-should-fail"),
        pytest.param("warning", False, id="warning-level-should-pass"),
        pytest.param("info", False, id="info-level-should-pass"),
        pytest.param("style", False, id="style-level-should-pass"),
    ],
)
def test_hadolint_error_levels(level, should_fail, temp_dir, monkeypatch):
    """Test that different hadolint severity levels are handled correctly."""
    # Resolve temp_dir to avoid symlink issues on macOS
    temp_dir = temp_dir.resolve()
    dockerfile = temp_dir / "Dockerfile"
    dockerfile.write_text("FROM python:3.11-slim\n")

    # Mock hadolint to return issue with specified level
    def mock_run(*args, **kwargs):
        result = MagicMock()
        result.returncode = 1 if level == "error" else 0
        result.stdout = json.dumps(
            [
                {
                    "line": 1,
                    "code": f"DL{level.upper()}",
                    "message": f"Test {level} message",
                    "column": 1,
                    "file": str(dockerfile),
                    "level": level,
                }
            ]
        )
        result.stderr = ""
        return result

    # Change to temp_dir so relative paths work
    monkeypatch.chdir(temp_dir)
    monkeypatch.setattr("subprocess.run", mock_run)
    from validate_dockerfiles import validate_dockerfile

    result = validate_dockerfile(dockerfile)

    assert result["passed"] is not should_fail

    if should_fail:
        assert len(result["errors"]) == 1
        assert result["errors"][0]["level"] == level
    else:
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["level"] == level


@pytest.mark.unit
@pytest.mark.parametrize(
    "dockerfile_name,should_find",
    [
        pytest.param("Dockerfile", True, id="standard-dockerfile"),
        pytest.param("Dockerfile.python", True, id="dockerfile-with-suffix"),
        pytest.param("Dockerfile.test", True, id="dockerfile-test-suffix"),
        pytest.param("Dockerfile.prod", True, id="dockerfile-prod-suffix"),
        pytest.param("Dockerfile.dev", True, id="dockerfile-dev-suffix"),
        pytest.param(".dockerignore", False, id="dockerignore-excluded"),
        pytest.param("README.md", False, id="non-dockerfile-excluded"),
        pytest.param("test.txt", False, id="text-file-excluded"),
    ],
)
def test_dockerfile_discovery_patterns(dockerfile_name, should_find, temp_dir):
    """Test that Dockerfile discovery finds correct files and excludes others.

    Note: The find_dockerfiles function uses glob patterns '**/Dockerfile' and
    '**/Dockerfile.*', which only matches files named exactly 'Dockerfile' or
    starting with 'Dockerfile.' (case-sensitive).
    """
    file_path = temp_dir / dockerfile_name
    file_path.write_text("FROM python:3.11-slim\n")

    from validate_dockerfiles import find_dockerfiles

    found = find_dockerfiles(temp_dir)

    if should_find:
        assert len(found) >= 1
        assert any(dockerfile_name in str(f) for f in found)
    else:
        assert all(dockerfile_name not in str(f) for f in found)


@pytest.mark.unit
class TestDockerfileValidation:
    """Tests for Dockerfile validation logic."""

    def test_valid_dockerfile_passes(self, temp_dir, monkeypatch):
        """Valid Dockerfile should pass basic validation."""
        # Resolve temp_dir to avoid symlink issues on macOS
        temp_dir = temp_dir.resolve()
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
        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        result = validate_dockerfile(dockerfile)

        assert result["passed"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_dockerfile_with_errors(self, temp_dir, monkeypatch):
        """Dockerfile with errors should fail validation."""
        # Resolve temp_dir to avoid symlink issues on macOS
        temp_dir = temp_dir.resolve()
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python\n")  # Missing specific version tag

        # Mock hadolint to return errors
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = json.dumps(
                [
                    {
                        "line": 1,
                        "code": "DL3006",
                        "message": "Always tag the version of an image explicitly",
                        "column": 1,
                        "file": str(dockerfile),
                        "level": "error",
                    }
                ]
            )
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        result = validate_dockerfile(dockerfile)

        assert result["passed"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "DL3006"
        assert result["errors"][0]["level"] == "error"

    def test_dockerfile_with_warnings(self, temp_dir, monkeypatch):
        """Dockerfile with warnings should pass but show warnings."""
        # Resolve temp_dir to avoid symlink issues on macOS
        temp_dir = temp_dir.resolve()
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\nRUN apt-get update\n")

        # Mock hadolint to return warnings only
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(
                [
                    {
                        "line": 2,
                        "code": "DL3008",
                        "message": "Pin versions in apt-get install",
                        "column": 1,
                        "file": str(dockerfile),
                        "level": "warning",
                    }
                ]
            )
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        result = validate_dockerfile(dockerfile)

        assert result["passed"] is True  # Warnings don't fail validation
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["code"] == "DL3008"

    def test_dockerfile_with_mixed_issues(self, temp_dir, monkeypatch):
        """Dockerfile with errors and warnings should categorize correctly."""
        # Resolve temp_dir to avoid symlink issues on macOS
        temp_dir = temp_dir.resolve()
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\n")

        # Mock hadolint to return mixed issues
        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 1
            result.stdout = json.dumps(
                [
                    {
                        "line": 1,
                        "code": "DL3006",
                        "message": "Error message",
                        "level": "error",
                    },
                    {
                        "line": 2,
                        "code": "DL3008",
                        "message": "Warning message",
                        "level": "warning",
                    },
                    {
                        "line": 3,
                        "code": "DL3009",
                        "message": "Info message",
                        "level": "info",
                    },
                    {
                        "line": 4,
                        "code": "DL3010",
                        "message": "Style message",
                        "level": "style",
                    },
                ]
            )
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        result = validate_dockerfile(dockerfile)

        assert result["passed"] is False
        assert len(result["errors"]) == 1
        assert len(result["warnings"]) == 3  # warning, info, and style

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
        # Resolve temp_dir to avoid symlink issues on macOS
        temp_dir = temp_dir.resolve()
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11-slim\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""  # Empty output
            result.stderr = ""
            return result

        # Change to temp_dir so relative paths work
        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr("subprocess.run", mock_run)
        from validate_dockerfiles import validate_dockerfile

        result = validate_dockerfile(dockerfile)

        assert result["passed"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0


@pytest.mark.unit
class TestPrintValidationSummary:
    """Tests for validation summary printing."""

    def test_prints_summary_for_all_passed(self, capfd):
        """Should print summary when all files pass."""
        from logger import configure_logging

        configure_logging()  # Reset logger to ensure clean capture
        from validate_dockerfiles import print_validation_summary

        results = [
            {"file": "Dockerfile", "passed": True, "errors": [], "warnings": []},
            {
                "file": ".docker/Dockerfile.test",
                "passed": True,
                "errors": [],
                "warnings": [],
            },
        ]

        print_validation_summary(results)
        captured = capfd.readouterr()

        # Loguru writes to stderr at file descriptor level
        assert "Total files scanned: 2" in captured.err
        assert "Passed: 2" in captured.err
        assert "Failed: 0" in captured.err
        assert "✅ PASS" in captured.err

    def test_prints_summary_with_failures(self, capfd):
        """Should print summary with failure details."""
        from logger import configure_logging

        configure_logging()  # Reset logger to ensure clean capture
        from validate_dockerfiles import print_validation_summary

        results = [
            {
                "file": "Dockerfile",
                "passed": False,
                "errors": [
                    {"code": "DL3006", "line": 1, "message": "Always tag the version"}
                ],
                "warnings": [],
            }
        ]

        print_validation_summary(results)
        captured = capfd.readouterr()

        # Loguru writes to stderr at file descriptor level
        assert "Total files scanned: 1" in captured.err
        assert "Passed: 0" in captured.err
        assert "Failed: 1" in captured.err
        assert "❌ FAIL" in captured.err
        assert "DL3006" in captured.err
        assert "Always tag the version" in captured.err

    def test_prints_warnings(self, capfd):
        """Should print warning details."""
        from logger import configure_logging

        configure_logging()  # Reset logger to ensure clean capture
        from validate_dockerfiles import print_validation_summary

        results = [
            {
                "file": "Dockerfile",
                "passed": True,
                "errors": [],
                "warnings": [
                    {"code": "DL3008", "line": 5, "message": "Pin versions in apt-get"}
                ],
            }
        ]

        print_validation_summary(results)
        captured = capfd.readouterr()

        # Loguru writes to stderr at file descriptor level
        assert "Warnings: 1" in captured.err
        assert "DL3008" in captured.err
        assert "Pin versions in apt-get" in captured.err


@pytest.mark.unit
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


@pytest.mark.unit
class TestMainWithResults:
    """Tests for main function with validation results."""

    def test_main_with_passing_dockerfile(self, monkeypatch, temp_dir):
        """Should return exit code 0 and write JSON when all pass."""
        import subprocess
        from validate_dockerfiles import main

        temp_dir = temp_dir.resolve()
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11\n")

        # Track which calls we've made
        calls = []

        def mock_run(*args, **kwargs):
            result = MagicMock()
            calls.append(args)
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "hadolint" and "--version" in cmd:
                # hadolint version check
                result.returncode = 0
                result.stdout = "hadolint 2.12.0"
                return result
            # hadolint validation call - pass
            result.returncode = 0
            result.stdout = "[]"
            result.stderr = ""
            return result

        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(temp_dir)])

        exit_code = main()

        assert exit_code == 0
        json_file = temp_dir / "dockerfile-validation.json"
        assert json_file.exists()
        data = json.loads(json_file.read_text())
        assert data["passed_files"] == 1

    def test_main_with_failing_dockerfile(self, monkeypatch, temp_dir):
        """Should return exit code 1 when any dockerfile fails."""
        import subprocess
        from validate_dockerfiles import main

        temp_dir = temp_dir.resolve()
        dockerfile = temp_dir / "Dockerfile"
        dockerfile.write_text("FROM python:3.11\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "hadolint" and "--version" in cmd:
                result.returncode = 0
                return result
            # Validation fails
            result.returncode = 1
            result.stdout = json.dumps(
                [
                    {
                        "line": 1,
                        "code": "DL3006",
                        "message": "Error",
                        "column": 1,
                        "file": str(dockerfile),
                        "level": "error",
                    }
                ]
            )
            result.stderr = ""
            return result

        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(temp_dir)])

        exit_code = main()

        assert exit_code == 1

    def test_main_writes_json_report(self, monkeypatch, temp_dir):
        """Should write JSON report with results."""
        import subprocess
        from validate_dockerfiles import main

        temp_dir = temp_dir.resolve()
        (temp_dir / "Dockerfile").write_text("FROM python:3.11\n")
        (temp_dir / "Dockerfile.test").write_text("FROM node:20\n")

        def mock_run(*args, **kwargs):
            result = MagicMock()
            cmd = args[0] if args else kwargs.get("args", [])
            if cmd[0] == "hadolint" and "--version" in cmd:
                result.returncode = 0
                return result
            result.returncode = 0
            result.stdout = "[]"
            result.stderr = ""
            return result

        monkeypatch.chdir(temp_dir)
        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr("sys.argv", ["validate_dockerfiles.py", str(temp_dir)])

        main()

        json_file = temp_dir / "dockerfile-validation.json"
        assert json_file.exists()
        data = json.loads(json_file.read_text())
        assert data["total_files"] == 2
        assert data["passed_files"] == 2
        assert data["failed_files"] == 0
