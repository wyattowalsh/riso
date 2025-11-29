#!/usr/bin/env python3
"""Subprocess security utilities for safe command execution.

This module provides secure subprocess execution helpers that prevent:
- Shell injection attacks
- Command injection attacks
- Arbitrary code execution
- Path traversal attacks

SECURITY BEST PRACTICES:
1. NEVER use shell=True unless absolutely necessary
2. ALWAYS use list-based command arguments
3. ALWAYS validate and sanitize user inputs
4. ALWAYS use timeouts to prevent infinite execution
5. ALWAYS use restricted environments when possible

Example:
    from scripts.subprocess_security import run_command_safe

    # GOOD: Safe command execution
    result = run_command_safe(["ls", "-la", user_directory])

    # BAD: Never do this!
    # subprocess.run(f"ls -la {user_directory}", shell=True)
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any, Optional


class SubprocessSecurityError(Exception):
    """Raised when subprocess security validation fails."""

    pass


def sanitize_path(path: str | Path, allowed_parent: Optional[Path] = None) -> Path:
    """Sanitize and validate a file path to prevent path traversal attacks.

    Args:
        path: Path to sanitize
        allowed_parent: Optional parent directory to restrict access to

    Returns:
        Sanitized absolute Path object

    Raises:
        SubprocessSecurityError: If path is invalid or outside allowed_parent

    Example:
        >>> sanitize_path("../../etc/passwd", allowed_parent=Path("/home/user"))
        SubprocessSecurityError: Path traversal detected

        >>> sanitize_path("docs/file.txt", allowed_parent=Path("/home/user"))
        Path('/home/user/docs/file.txt')
    """
    try:
        sanitized = Path(path).resolve()
    except (ValueError, RuntimeError) as e:
        raise SubprocessSecurityError(f"Invalid path: {e}")

    # Check for path traversal
    if allowed_parent:
        try:
            sanitized.relative_to(allowed_parent.resolve())
        except ValueError:
            raise SubprocessSecurityError(
                f"Path traversal detected: {path} is outside {allowed_parent}"
            )

    return sanitized


def validate_command(command: list[str], allowed_commands: Optional[set[str]] = None) -> None:
    """Validate command arguments for security issues.

    Args:
        command: Command list to validate
        allowed_commands: Optional set of allowed command names

    Raises:
        SubprocessSecurityError: If command is invalid or not allowed

    Example:
        >>> validate_command(["ls", "-la"])  # OK
        >>> validate_command(["rm", "-rf", "/"])  # OK if rm is allowed
        >>> validate_command([], allowed_commands={"ls", "cat"})
        SubprocessSecurityError: Empty command
    """
    if not command:
        raise SubprocessSecurityError("Empty command")

    if not isinstance(command, list):
        raise SubprocessSecurityError("Command must be a list, not a string")

    # Validate all arguments are strings
    if not all(isinstance(arg, str) for arg in command):
        raise SubprocessSecurityError("All command arguments must be strings")

    # Check if command is in allowlist
    if allowed_commands is not None:
        cmd_name = Path(command[0]).name  # Handle both "ls" and "/bin/ls"
        if cmd_name not in allowed_commands:
            raise SubprocessSecurityError(
                f"Command not allowed: {cmd_name}. "
                f"Allowed commands: {', '.join(sorted(allowed_commands))}"
            )


def parse_command_safe(command_string: str) -> list[str]:
    """Safely parse a command string into a list of arguments.

    Uses shlex.split() to handle quoted arguments properly while
    preventing shell injection.

    Args:
        command_string: Shell command string to parse

    Returns:
        List of command arguments

    Raises:
        SubprocessSecurityError: If command string is invalid

    Example:
        >>> parse_command_safe('ls -la "/my folder"')
        ['ls', '-la', '/my folder']

        >>> parse_command_safe('ls && rm -rf /')  # Still unsafe!
        ['ls', '&&', 'rm', '-rf', '/']  # But won't execute as shell
    """
    try:
        return shlex.split(command_string)
    except ValueError as e:
        raise SubprocessSecurityError(f"Invalid command syntax: {e}")


def run_command_safe(
    command: list[str],
    *,
    timeout: int = 120,
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
    allowed_commands: Optional[set[str]] = None,
    check: bool = False,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute a command safely with security validations.

    SECURITY FEATURES:
    - Validates command format and arguments
    - Never uses shell=True
    - Enforces timeout to prevent infinite execution
    - Optionally restricts commands to allowlist
    - Captures output by default to prevent information leakage

    Args:
        command: Command as list of strings (e.g., ["ls", "-la"])
        timeout: Maximum execution time in seconds (default: 120)
        cwd: Working directory for command execution
        env: Environment variables (None = inherit from parent)
        allowed_commands: Optional set of allowed command names
        check: Whether to raise CalledProcessError on non-zero exit
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess with results

    Raises:
        SubprocessSecurityError: If security validation fails
        subprocess.CalledProcessError: If check=True and command fails
        subprocess.TimeoutExpired: If command exceeds timeout

    Example:
        >>> result = run_command_safe(["ls", "-la"], timeout=10)
        >>> print(result.stdout)

        >>> run_command_safe(
        ...     ["pytest", "tests/"],
        ...     allowed_commands={"pytest", "python"},
        ...     timeout=300,
        ... )
    """
    # Validate command
    validate_command(command, allowed_commands=allowed_commands)

    # Validate working directory if provided
    if cwd is not None:
        if not Path(cwd).is_dir():
            raise SubprocessSecurityError(f"Working directory does not exist: {cwd}")

    try:
        return subprocess.run(
            command,
            shell=False,  # CRITICAL: Never use shell=True
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=check,
        )
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(
            cmd=command,
            timeout=timeout,
            output=getattr(e, "output", None),
            stderr=getattr(e, "stderr", None),
        )


def build_restricted_env(
    *,
    include_path: bool = True,
    include_home: bool = True,
    extra_vars: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """Build a restricted environment for subprocess execution.

    Creates a minimal environment with only essential variables,
    removing potentially dangerous variables like LD_PRELOAD.

    Args:
        include_path: Whether to include PATH from parent environment
        include_home: Whether to include HOME from parent environment
        extra_vars: Additional variables to include

    Returns:
        Restricted environment dictionary

    Example:
        >>> env = build_restricted_env(extra_vars={"PYTHONPATH": "/app"})
        >>> result = run_command_safe(["python", "script.py"], env=env)
    """
    import os

    env: dict[str, str] = {}

    # Add essential variables
    if include_path:
        env["PATH"] = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
    if include_home:
        env["HOME"] = os.environ.get("HOME", "/tmp")

    # Add safe defaults
    env["LANG"] = os.environ.get("LANG", "en_US.UTF-8")
    env["USER"] = os.environ.get("USER", "unknown")

    # Add extra variables if provided
    if extra_vars:
        env.update(extra_vars)

    # Security: Remove dangerous variables
    dangerous_vars = [
        "LD_PRELOAD",  # Can load malicious shared libraries
        "LD_LIBRARY_PATH",  # Can override library loading
        "DYLD_INSERT_LIBRARIES",  # macOS equivalent of LD_PRELOAD
        "DYLD_LIBRARY_PATH",  # macOS equivalent of LD_LIBRARY_PATH
        "PYTHONPATH",  # Can inject malicious Python modules (unless explicitly set)
    ]

    # Only remove PYTHONPATH if not explicitly set in extra_vars
    if extra_vars and "PYTHONPATH" in extra_vars:
        dangerous_vars.remove("PYTHONPATH")

    for var in dangerous_vars:
        env.pop(var, None)

    return env


# Example usage and tests
if __name__ == "__main__":
    import sys

    # Example 1: Safe command execution
    print("Example 1: Safe command execution")
    result = run_command_safe(["echo", "Hello, World!"], timeout=5)
    print(f"Output: {result.stdout.strip()}")
    print(f"Return code: {result.returncode}\n")

    # Example 2: Command with timeout
    print("Example 2: Path sanitization")
    try:
        safe_path = sanitize_path("docs/../../etc/passwd", allowed_parent=Path.cwd())
        print(f"Safe path: {safe_path}")
    except SubprocessSecurityError as e:
        print(f"Security error (expected): {e}\n")

    # Example 3: Restricted environment
    print("Example 3: Restricted environment")
    env = build_restricted_env(extra_vars={"MY_VAR": "test"})
    print(f"Environment variables: {', '.join(sorted(env.keys()))}\n")

    # Example 4: Allowed commands
    print("Example 4: Command allowlist")
    try:
        run_command_safe(["rm", "-rf", "/"], allowed_commands={"ls", "cat"})
    except SubprocessSecurityError as e:
        print(f"Security error (expected): {e}\n")

    print("✅ All security examples completed successfully!")
