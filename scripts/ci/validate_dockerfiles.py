#!/usr/bin/env python3
"""Dockerfile validation script using hadolint.

This script scans all Dockerfile* files in a given directory (recursively) and
validates them using hadolint. Designed for CI/CD integration with JSON output
and clear exit codes.

Exit Codes:
    0: All Dockerfiles pass hadolint (zero errors)
    1: One or more Dockerfiles have hadolint errors
    2: hadolint not installed or execution error

Requirements:
    - Python 3.11+
    - hadolint binary installed (brew install hadolint on macOS, wget on Linux)

Usage:
    python validate_dockerfiles.py <directory>
    python validate_dockerfiles.py /path/to/samples/default/render
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, TypedDict


class ValidationResult(TypedDict):
    """Validation result for a single Dockerfile."""
    
    file: str
    passed: bool
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]


def check_hadolint_installed() -> bool:
    """Check if hadolint is installed and accessible.
    
    Returns:
        True if hadolint is available, False otherwise
    """
    try:
        subprocess.run(
            ["hadolint", "--version"],
            capture_output=True,
            check=True,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def find_dockerfiles(directory: Path) -> list[Path]:
    """Find all Dockerfile* files recursively in a directory.
    
    Args:
        directory: Root directory to search
    
    Returns:
        List of Dockerfile paths
    """
    dockerfiles: list[Path] = []
    
    # Search for Dockerfile and Dockerfile.* patterns
    for pattern in ["**/Dockerfile", "**/Dockerfile.*"]:
        dockerfiles.extend(directory.glob(pattern))
    
    # Remove .dockerignore files if accidentally matched
    dockerfiles = [f for f in dockerfiles if f.name != ".dockerignore"]
    
    return sorted(set(dockerfiles))  # Deduplicate and sort


def validate_dockerfile(dockerfile_path: Path) -> ValidationResult:
    """Run hadolint on a Dockerfile and return validation result.
    
    Args:
        dockerfile_path: Path to Dockerfile to validate
    
    Returns:
        ValidationResult with errors, warnings, and pass/fail status
    
    Raises:
        FileNotFoundError: If dockerfile_path does not exist
        RuntimeError: If hadolint execution fails
    """
    if not dockerfile_path.exists():
        raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")
    
    try:
        result = subprocess.run(
            ["hadolint", "--format", "json", str(dockerfile_path)],
            capture_output=True,
            text=True,
            check=False,  # Don't raise on non-zero exit (hadolint returns 1 for linting errors)
        )
        
        # Parse JSON output from hadolint
        issues: list[dict[str, Any]] = []
        if result.stdout.strip():
            issues = json.loads(result.stdout)
        
        # Separate errors from warnings
        errors = [issue for issue in issues if issue.get("level") == "error"]
        warnings = [issue for issue in issues if issue.get("level") in ("warning", "info", "style")]
        
        return ValidationResult(
            file=str(dockerfile_path.relative_to(Path.cwd())),
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse hadolint JSON output: {e}")
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"hadolint execution failed: {e}")


def print_validation_summary(results: list[ValidationResult]) -> None:
    """Print human-readable validation summary.
    
    Args:
        results: List of validation results
    """
    total_files = len(results)
    passed_files = sum(1 for r in results if r["passed"])
    failed_files = total_files - passed_files
    
    print(f"\n{'=' * 60}")
    print("Dockerfile Validation Summary")
    print(f"{'=' * 60}")
    print(f"Total files scanned: {total_files}")
    print(f"Passed: {passed_files}")
    print(f"Failed: {failed_files}")
    print(f"{'=' * 60}\n")
    
    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} - {result['file']}")
        
        if result["errors"]:
            print(f"  Errors: {len(result['errors'])}")
            for error in result["errors"]:
                rule = error.get("code", "UNKNOWN")
                line = error.get("line", "?")
                message = error.get("message", "No message")
                print(f"    - [{rule}] Line {line}: {message}")
        
        if result["warnings"]:
            print(f"  Warnings: {len(result['warnings'])}")
            for warning in result["warnings"]:
                rule = warning.get("code", "UNKNOWN")
                line = warning.get("line", "?")
                message = warning.get("message", "No message")
                print(f"    - [{rule}] Line {line}: {message}")
        
        print()


def main() -> int:
    """Main entry point for Dockerfile validation.
    
    Returns:
        Exit code (0=success, 1=validation failures, 2=tool error)
    """
    if len(sys.argv) != 2:
        print("Usage: python validate_dockerfiles.py <directory>", file=sys.stderr)
        return 2
    
    directory = Path(sys.argv[1])
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        return 2
    
    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}", file=sys.stderr)
        return 2
    
    # Check hadolint is installed
    if not check_hadolint_installed():
        print(
            "Error: hadolint not installed. Install with:\n"
            "  macOS: brew install hadolint\n"
            "  Linux: wget -O /usr/local/bin/hadolint "
            "https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 "
            "&& chmod +x /usr/local/bin/hadolint",
            file=sys.stderr,
        )
        return 2
    
    # Find all Dockerfiles
    dockerfiles = find_dockerfiles(directory)
    
    if not dockerfiles:
        print(f"Warning: No Dockerfiles found in {directory}", file=sys.stderr)
        return 0
    
    print(f"Found {len(dockerfiles)} Dockerfile(s) in {directory}")
    
    # Validate each Dockerfile
    results: list[ValidationResult] = []
    for dockerfile in dockerfiles:
        try:
            result = validate_dockerfile(dockerfile)
            results.append(result)
        except Exception as e:
            print(f"Error validating {dockerfile}: {e}", file=sys.stderr)
            return 2
    
    # Print summary
    print_validation_summary(results)
    
    # Output JSON for CI parsing
    json_output = {
        "total_files": len(results),
        "passed_files": sum(1 for r in results if r["passed"]),
        "failed_files": sum(1 for r in results if not r["passed"]),
        "results": results,
    }
    
    json_file = Path.cwd() / "dockerfile-validation.json"
    json_file.write_text(json.dumps(json_output, indent=2))
    print(f"JSON report written to: {json_file}")
    
    # Return exit code based on validation results
    if all(r["passed"] for r in results):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
