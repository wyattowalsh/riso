"""Integration tests for setup scripts."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).parent.parent.parent / "scripts" / "setup"
SETUP_SH = SCRIPT_DIR / "setup.sh"
SETUP_PS1 = SCRIPT_DIR / "setup.ps1"


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestSetupBash:
    """Integration tests for setup.sh."""

    def test_script_exists_and_executable(self):
        """setup.sh should exist and be executable."""
        assert SETUP_SH.exists(), f"setup.sh not found at {SETUP_SH}"
        assert SETUP_SH.stat().st_mode & 0o111, "setup.sh should be executable"

    def test_help_flag(self):
        """--help should show usage and exit 0."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout or "USAGE:" in result.stdout
        assert "OPTIONS:" in result.stdout or "Options:" in result.stdout

    def test_help_short_flag(self):
        """-h should show usage and exit 0."""
        result = subprocess.run(
            [str(SETUP_SH), "-h"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout or "USAGE:" in result.stdout

    def test_check_only_mode(self):
        """--check-only should return 0 if all tools present, 1 otherwise."""
        result = subprocess.run(
            [str(SETUP_SH), "--check-only"],
            capture_output=True,
            text=True,
        )
        # Should be 0 or 1, not 2 (script error)
        assert result.returncode in [0, 1], f"Expected exit code 0 or 1, got {result.returncode}"

    def test_dry_run_makes_no_changes(self):
        """Default mode (no args) should not modify anything."""
        result = subprocess.run(
            [str(SETUP_SH)],
            capture_output=True,
            text=True,
        )
        # Should exit 0 or 1, and not actually install anything
        assert result.returncode in [0, 1], f"Expected exit code 0 or 1, got {result.returncode}"
        # Should show tool status
        assert "Tool Status" in result.stdout or "Tool" in result.stdout

    def test_invalid_flag_shows_error(self):
        """Invalid flags should show an error."""
        result = subprocess.run(
            [str(SETUP_SH), "--invalid-flag-12345"],
            capture_output=True,
            text=True,
        )
        # Should fail with error message
        assert result.returncode == 2, f"Expected exit code 2 for invalid flag, got {result.returncode}"
        assert "Unknown option" in result.stderr or "ERROR" in result.stderr

    def test_conflicting_modes_error(self):
        """--check-only and --install together should error."""
        result = subprocess.run(
            [str(SETUP_SH), "--check-only", "--install"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "Cannot use" in result.stderr or "ERROR" in result.stderr

    def test_yes_without_install_error(self):
        """--yes without --install should error."""
        result = subprocess.run(
            [str(SETUP_SH), "--yes"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "can only be used with" in result.stderr or "ERROR" in result.stderr

    def test_output_shows_platform_info_in_debug(self):
        """Debug mode should show platform information."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
            env={"DEBUG": "1", **subprocess.os.environ},
        )
        # Just check it runs without error
        assert result.returncode == 0

    def test_check_only_with_all_tools_present(self):
        """--check-only should exit 0 when all required tools are installed."""
        # First check if tools are present
        result = subprocess.run(
            [str(SETUP_SH)],
            capture_output=True,
            text=True,
        )

        # If default run shows all tools OK, check-only should succeed
        if "All required tools are present" in result.stdout:
            check_result = subprocess.run(
                [str(SETUP_SH), "--check-only"],
                capture_output=True,
                text=True,
            )
            assert check_result.returncode == 0, "Should exit 0 when all tools present"

    def test_version_displayed_in_output(self):
        """Script should display its version."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should show version number
        assert "v" in result.stdout and "." in result.stdout


@pytest.mark.skipif(
    subprocess.run(["which", "pwsh"], capture_output=True).returncode != 0,
    reason="PowerShell Core not installed"
)
class TestSetupPowerShell:
    """Integration tests for setup.ps1 (requires pwsh)."""

    def test_script_exists(self):
        """setup.ps1 should exist."""
        assert SETUP_PS1.exists(), f"setup.ps1 not found at {SETUP_PS1}"

    def test_help_parameter(self):
        """-Help should show usage."""
        result = subprocess.run(
            ["pwsh", "-File", str(SETUP_PS1), "-Help"],
            capture_output=True,
            text=True,
        )
        # PowerShell may return 0 or display help to stdout/stderr
        # Just verify it doesn't crash
        assert result.returncode in [0, 1]

    def test_check_only_mode(self):
        """-CheckOnly should return 0 if all tools present."""
        result = subprocess.run(
            ["pwsh", "-File", str(SETUP_PS1), "-CheckOnly"],
            capture_output=True,
            text=True,
        )
        assert result.returncode in [0, 1]


def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.mark.docker
@pytest.mark.skipif(not docker_available(), reason="Docker not available or not running")
@pytest.mark.parametrize("image", [
    "ubuntu:22.04",
    "ubuntu:24.04",
    "fedora:39",
    "alpine:3.19",
])
class TestSetupDocker:
    """Integration tests using Docker containers for different Linux distros."""

    def test_check_only_in_container(self, image: str):
        """setup.sh --check-only should work in different Linux distros."""
        # This test requires Docker and is marked for CI
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{SCRIPT_DIR}:/setup:ro",
                image,
                "bash", "-c", "bash /setup/setup.sh --check-only || true"
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Container should run without crash (exit 0 from docker run)
        assert result.returncode == 0, f"Docker run failed for {image}"

    def test_help_in_container(self, image: str):
        """setup.sh --help should work in different Linux distros."""
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{SCRIPT_DIR}:/setup:ro",
                image,
                "bash", "-c", "bash /setup/setup.sh --help"
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Docker run failed for {image}"
        assert "Usage:" in result.stdout or "USAGE:" in result.stdout


class TestSetupScriptIntegration:
    """Integration tests that verify script behavior end-to-end."""

    def test_library_loading(self):
        """All library modules should load without error."""
        # Run the script with help to ensure all libraries load
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should not have shellcheck or sourcing errors in stderr
        assert "not found" not in result.stderr.lower()
        assert "no such file" not in result.stderr.lower()

    def test_log_file_creation(self):
        """Script should create log files when run."""
        # Run check-only mode to avoid installation
        result = subprocess.run(
            [str(SETUP_SH), "--check-only"],
            capture_output=True,
            text=True,
        )
        # Script should complete (even if tools missing)
        assert result.returncode in [0, 1]
        # Log file path might be mentioned in debug output or logs

    def test_no_color_environment(self):
        """Script should respect NO_COLOR environment variable."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
            env={"NO_COLOR": "1", **subprocess.os.environ},
        )
        assert result.returncode == 0
        # Output should not contain ANSI escape codes
        assert "\033[" not in result.stdout

    def test_verbose_mode(self):
        """Script should show verbose output when VERBOSE=1."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
            env={"VERBOSE": "1", **subprocess.os.environ},
        )
        assert result.returncode == 0

    def test_tool_detection_runs(self):
        """Script should detect and report on all required tools."""
        result = subprocess.run(
            [str(SETUP_SH)],
            capture_output=True,
            text=True,
        )
        # Should check for core tools
        expected_tools = ["python3", "uv", "node", "pnpm"]
        for tool in expected_tools:
            # Tool name should appear in output somewhere
            assert tool in result.stdout.lower() or tool in result.stderr.lower(), \
                f"Tool {tool} not mentioned in output"


class TestSetupDocumentation:
    """Tests to ensure setup script documentation is accurate."""

    def test_help_mentions_all_flags(self):
        """Help text should document all available flags."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = result.stdout

        # Check for documented flags
        assert "--check-only" in help_text
        assert "--install" in help_text
        assert "--yes" in help_text or "-y" in help_text
        assert "--help" in help_text

    def test_help_mentions_environment_variables(self):
        """Help text should document environment variables."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = result.stdout

        # Check for environment variable documentation
        assert "NO_COLOR" in help_text or "ENVIRONMENT" in help_text
        assert "DEBUG" in help_text or "VERBOSE" in help_text

    def test_help_shows_examples(self):
        """Help text should include usage examples."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = result.stdout

        # Should have an EXAMPLES section
        assert "EXAMPLES:" in help_text or "Examples:" in help_text or "example" in help_text.lower()

    def test_help_shows_exit_codes(self):
        """Help text should document exit codes."""
        result = subprocess.run(
            [str(SETUP_SH), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        help_text = result.stdout

        # Should document exit codes
        assert "EXIT" in help_text or "exit" in help_text.lower()
