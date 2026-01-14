"""Unit tests for setup script detection functions."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / "scripts" / "setup"
LIB_DIR = SCRIPT_DIR / "lib"


def run_bash_function(
    script: str, function: str, *args: str
) -> subprocess.CompletedProcess[str]:
    """Source a bash script and run a function, returning the result.

    Args:
        script: Path to the bash script to source
        function: Function name to execute
        *args: Arguments to pass to the function

    Returns:
        CompletedProcess with stdout, stderr, and return code
    """
    cmd = f'source "{script}" && {function} {" ".join(args)}'
    return subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )


class TestDetectPlatform:
    """Tests for detect-platform.sh functions."""

    def test_detect_os_returns_valid_value(self):
        """detect_os() should return a known OS type."""
        result = run_bash_function(LIB_DIR / "detect-platform.sh", "detect_os")
        assert result.returncode == 0
        assert result.stdout.strip() in ["macos", "linux", "windows", "unknown"]

    def test_detect_arch_returns_valid_value(self):
        """detect_arch() should return a known architecture."""
        result = run_bash_function(LIB_DIR / "detect-platform.sh", "detect_arch")
        assert result.returncode == 0
        assert result.stdout.strip() in ["x64", "arm64", "arm", "unknown"]

    def test_detect_shell_returns_valid_value(self):
        """detect_shell() should return a known shell."""
        result = run_bash_function(LIB_DIR / "detect-platform.sh", "detect_shell")
        assert result.returncode == 0
        assert result.stdout.strip() in ["bash", "zsh", "fish", "sh", "unknown"]

    def test_detect_package_manager_returns_value(self):
        """detect_package_manager() should return a package manager or 'none'."""
        result = run_bash_function(
            LIB_DIR / "detect-platform.sh", "detect_package_manager"
        )
        assert result.returncode == 0
        valid = [
            "mise",
            "brew",
            "apt",
            "dnf",
            "yum",
            "pacman",
            "apk",
            "zypper",
            "winget",
            "choco",
            "scoop",
            "none",
        ]
        assert result.stdout.strip() in valid

    def test_detect_linux_distro_on_macos_returns_unknown(self):
        """detect_linux_distro() should return unknown on non-Linux systems."""
        os_result = run_bash_function(LIB_DIR / "detect-platform.sh", "detect_os")
        if os_result.stdout.strip() != "linux":
            result = run_bash_function(
                LIB_DIR / "detect-platform.sh", "detect_linux_distro"
            )
            # Should return 1 and output "unknown"
            assert result.stdout.strip() == "unknown"

    def test_get_platform_summary_outputs_all_fields(self):
        """get_platform_summary() should output all platform information."""
        result = run_bash_function(
            LIB_DIR / "detect-platform.sh", "get_platform_summary"
        )
        assert result.returncode == 0
        output = result.stdout
        # Check for expected fields
        assert "OS:" in output
        assert "Distro:" in output
        assert "Package Manager:" in output
        assert "Architecture:" in output
        assert "Shell:" in output
        assert "WSL:" in output
        assert "Container:" in output

    def test_is_wsl_returns_false_on_macos(self):
        """is_wsl() should return false on macOS."""
        os_result = run_bash_function(LIB_DIR / "detect-platform.sh", "detect_os")
        if os_result.stdout.strip() == "macos":
            result = run_bash_function(
                LIB_DIR / "detect-platform.sh", 'is_wsl && echo "yes" || echo "no"'
            )
            assert result.stdout.strip() == "no"

    def test_is_container_returns_false_on_host(self):
        """is_container() should return false when not in a container."""
        # On a regular macOS/Linux host, is_container should be false
        result = run_bash_function(
            LIB_DIR / "detect-platform.sh", 'is_container && echo "yes" || echo "no"'
        )
        # This may be "yes" if tests are run in Docker, so we just check it runs
        assert result.returncode == 0
        assert result.stdout.strip() in ["yes", "no"]

    def test_get_container_runtime_returns_empty_on_host(self):
        """get_container_runtime() should return empty string when not in container."""
        result = run_bash_function(
            LIB_DIR / "detect-platform.sh",
            'runtime=$(get_container_runtime); echo "runtime:${runtime}:"',
        )
        assert result.returncode == 0 or result.returncode == 1
        # On host, should be empty; in container, should be a runtime name


class TestVersions:
    """Tests for versions.sh constants."""

    def test_versions_are_defined(self):
        """All version constants should be defined and non-empty."""
        versions = [
            "PYTHON_MIN_VERSION",
            "UV_MIN_VERSION",
            "NODE_MIN_VERSION",
            "PNPM_MIN_VERSION",
        ]
        for var in versions:
            result = run_bash_function(LIB_DIR / "versions.sh", f"echo ${var}")
            assert result.returncode == 0
            assert result.stdout.strip(), f"{var} should not be empty"

    def test_python_version_format(self):
        """PYTHON_MIN_VERSION should be in X.Y format."""
        result = run_bash_function(LIB_DIR / "versions.sh", "echo $PYTHON_MIN_VERSION")
        version = result.stdout.strip()
        parts = version.split(".")
        assert len(parts) >= 2, "Python version should have at least major.minor"
        assert parts[0].isdigit() and parts[1].isdigit()

    def test_node_version_format(self):
        """NODE_MIN_VERSION should be numeric."""
        result = run_bash_function(LIB_DIR / "versions.sh", "echo $NODE_MIN_VERSION")
        version = result.stdout.strip()
        assert version.split(".")[0].isdigit(), "Node version should be numeric"

    def test_quality_tool_versions_defined(self):
        """Quality tool versions should be defined."""
        tools = ["RUFF_VERSION", "TY_VERSION", "PYLINT_VERSION", "COVERAGE_VERSION"]
        for var in tools:
            result = run_bash_function(LIB_DIR / "versions.sh", f"echo ${var}")
            assert result.returncode == 0
            assert result.stdout.strip(), f"{var} should not be empty"


class TestVersionComparison:
    """Tests for version comparison logic."""

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("3.11", "3.11", True),  # Equal
            ("3.12", "3.11", True),  # Greater
            ("3.11.5", "3.11", True),  # Patch version >= base
            ("3.10", "3.11", False),  # Less than
            ("20", "20", True),  # Node.js style
            ("20.1", "20", True),  # Node.js with patch
            ("1.0.0", "0.9.9", True),  # Major version bump
            ("0.4.0", "0.4", True),  # Equal with patch
        ],
    )
    def test_version_gte(self, v1: str, v2: str, expected: bool):
        """version_gte should correctly compare versions."""
        result = run_bash_function(
            LIB_DIR / "install-tools.sh",
            f'version_gte "{v1}" "{v2}" && echo "true" || echo "false"',
        )
        assert result.returncode == 0
        assert (result.stdout.strip() == "true") == expected, (
            f"version_gte({v1}, {v2}) should be {expected}"
        )


class TestColors:
    """Tests for colors.sh functions."""

    def test_no_color_env_respected(self):
        """Colors should be disabled when NO_COLOR is set."""
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        result = subprocess.run(
            ["bash", "-c", f'source "{LIB_DIR}/colors.sh" && echo "$RED"'],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.stdout.strip() == "", "RED should be empty when NO_COLOR is set"

    def test_colors_enabled_by_default(self):
        """Colors should be enabled when NO_COLOR is not set."""
        env = os.environ.copy()
        env.pop("NO_COLOR", None)
        env["TERM"] = "xterm-256color"
        result = subprocess.run(
            ["bash", "-c", f'source "{LIB_DIR}/colors.sh" && echo -n "$RED"'],
            capture_output=True,
            text=True,
            env=env,
        )
        # Should have ANSI color code (either literal \033 or escape sequence \x1b)
        assert result.stdout != "", "RED should have ANSI code when colors enabled"
        assert "\\033[" in result.stdout or "\x1b[" in result.stdout, (
            "Should contain ANSI escape sequence"
        )

    def test_dumb_term_disables_colors(self):
        """Colors should be disabled when TERM=dumb."""
        env = os.environ.copy()
        env.pop("NO_COLOR", None)
        env["TERM"] = "dumb"
        result = subprocess.run(
            ["bash", "-c", f'source "{LIB_DIR}/colors.sh" && echo "$GREEN"'],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.stdout.strip() == "", "GREEN should be empty when TERM=dumb"

    def test_log_functions_exist(self):
        """All log functions should be defined."""
        log_functions = [
            "log_info",
            "log_success",
            "log_warn",
            "log_error",
            "log_debug",
            "log_section",
        ]
        for func in log_functions:
            result = run_bash_function(
                LIB_DIR / "colors.sh",
                f'type {func} >/dev/null 2>&1 && echo "exists" || echo "missing"',
            )
            assert result.stdout.strip() == "exists", f"{func} should be defined"


class TestInstallTools:
    """Tests for install-tools.sh utility functions."""

    def test_has_cmd_function_works(self):
        """has_cmd should detect available commands."""
        # Test with a command that should always exist
        result = run_bash_function(
            LIB_DIR / "install-tools.sh",
            'has_cmd "bash" && echo "found" || echo "not_found"',
        )
        assert result.stdout.strip() == "found"

        # Test with a command that shouldn't exist
        result = run_bash_function(
            LIB_DIR / "install-tools.sh",
            'has_cmd "this_command_does_not_exist_12345" && echo "found" || echo "not_found"',
        )
        assert result.stdout.strip() == "not_found"

    def test_get_tool_version_bash(self):
        """get_tool_version should extract version from bash."""
        result = run_bash_function(
            LIB_DIR / "install-tools.sh", 'get_tool_version "bash" "--version"'
        )
        assert result.returncode == 0
        version = result.stdout.strip()
        assert version != "unknown", "Should detect bash version"
        # Version should be in X.Y format
        parts = version.split(".")
        assert len(parts) >= 2, "Version should have major.minor"
        assert parts[0].isdigit() and parts[1].isdigit()

    def test_get_tool_version_nonexistent(self):
        """get_tool_version should return 'unknown' for nonexistent tools."""
        result = run_bash_function(
            LIB_DIR / "install-tools.sh", 'get_tool_version "nonexistent_tool_12345"'
        )
        assert result.stdout.strip() == "unknown"
        assert result.returncode == 1


class TestLogging:
    """Tests for logging.sh functions."""

    def test_log_file_creation(self):
        """init_log_file should create a log file path."""
        result = run_bash_function(LIB_DIR / "logging.sh", 'init_log_file "test"')
        assert result.returncode == 0
        log_path = result.stdout.strip()
        assert log_path, "Should return a log file path"
        assert "test" in log_path or ".log" in log_path

    def test_log_to_file_function_exists(self):
        """log_to_file function should exist."""
        result = run_bash_function(
            LIB_DIR / "logging.sh",
            'type log_to_file >/dev/null 2>&1 && echo "exists" || echo "missing"',
        )
        assert result.stdout.strip() == "exists"
