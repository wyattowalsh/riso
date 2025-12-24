"""Shared validation utilities for CI scripts.

This module provides common validation patterns used across Riso CI scripts including:
- Standardized validation result types
- YAML file loading with error handling
- Path validation utilities
- Result reporting utilities

Usage:
    from scripts.lib.validation import (
        ValidationResult,
        load_yaml_file,
        validate_path_exists,
        print_validation_summary,
    )
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, TypedDict

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed", file=sys.stderr)
    print("   Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class ValidationResult(TypedDict):
    """Standard validation result structure.

    Attributes:
        file: Path to the validated file (relative or absolute)
        valid: Whether the validation passed
        errors: List of error messages
        warnings: Optional list of warning messages
    """

    file: str
    valid: bool
    errors: list[str]
    warnings: list[str]


class YAMLLoadResult(TypedDict):
    """Result of YAML file loading operation.

    Attributes:
        success: Whether the file was loaded successfully
        data: Parsed YAML data (None if loading failed)
        error: Error message if loading failed (None if successful)
    """

    success: bool
    data: dict[str, Any] | None
    error: str | None


def load_yaml_file(path: Path) -> YAMLLoadResult:
    """Load a YAML file with proper error handling.

    This function attempts to load a YAML file and returns a structured result
    indicating success or failure with appropriate error messages.

    Args:
        path: Path to the YAML file to load

    Returns:
        YAMLLoadResult with success status, data, and error information

    Examples:
        >>> result = load_yaml_file(Path("config.yml"))
        >>> if result["success"]:
        ...     config = result["data"]
        ... else:
        ...     print(f"Error: {result['error']}")
    """
    if not path.exists():
        return YAMLLoadResult(
            success=False,
            data=None,
            error=f"File not found: {path}"
        )

    if not path.is_file():
        return YAMLLoadResult(
            success=False,
            data=None,
            error=f"Path is not a file: {path}"
        )

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            return YAMLLoadResult(
                success=False,
                data=None,
                error="File is empty or contains only null"
            )

        if not isinstance(data, dict):
            return YAMLLoadResult(
                success=False,
                data=None,
                error=f"Expected YAML dictionary, got {type(data).__name__}"
            )

        return YAMLLoadResult(
            success=True,
            data=data,
            error=None
        )

    except yaml.YAMLError as e:
        return YAMLLoadResult(
            success=False,
            data=None,
            error=f"YAML parsing error: {e}"
        )
    except UnicodeDecodeError as e:
        return YAMLLoadResult(
            success=False,
            data=None,
            error=f"File encoding error: {e}"
        )
    except Exception as e:
        return YAMLLoadResult(
            success=False,
            data=None,
            error=f"Unexpected error loading file: {e}"
        )


def validate_path_exists(path: Path, must_be_file: bool = False, must_be_dir: bool = False) -> ValidationResult:
    """Validate that a path exists and optionally check its type.

    Args:
        path: Path to validate
        must_be_file: If True, path must be a file
        must_be_dir: If True, path must be a directory

    Returns:
        ValidationResult indicating whether the path is valid

    Examples:
        >>> result = validate_path_exists(Path("config.yml"), must_be_file=True)
        >>> if not result["valid"]:
        ...     for error in result["errors"]:
        ...         print(error)
    """
    errors = []

    if not path.exists():
        errors.append(f"Path does not exist: {path}")
        return ValidationResult(
            file=str(path),
            valid=False,
            errors=errors,
            warnings=[]
        )

    if must_be_file and not path.is_file():
        errors.append(f"Path exists but is not a file: {path}")

    if must_be_dir and not path.is_dir():
        errors.append(f"Path exists but is not a directory: {path}")

    return ValidationResult(
        file=str(path),
        valid=len(errors) == 0,
        errors=errors,
        warnings=[]
    )


def validate_required_fields(data: dict[str, Any], required_fields: list[str], context: str = "") -> list[str]:
    """Validate that a dictionary contains all required fields.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Optional context string for error messages (e.g., filename)

    Returns:
        List of error messages (empty if all fields present)

    Examples:
        >>> errors = validate_required_fields(
        ...     {"name": "test"},
        ...     ["name", "version"],
        ...     context="config.yml"
        ... )
        >>> if errors:
        ...     print("\\n".join(errors))
    """
    errors = []
    prefix = f"{context}: " if context else ""

    for field in required_fields:
        if field not in data:
            errors.append(f"{prefix}Missing required field: '{field}'")

    return errors


def print_validation_summary(
    results: list[ValidationResult],
    title: str = "Validation Summary",
    show_warnings: bool = True
) -> None:
    """Print a formatted validation summary.

    Args:
        results: List of validation results to summarize
        title: Title for the summary section
        show_warnings: Whether to display warnings in addition to errors

    Examples:
        >>> results = [
        ...     ValidationResult(file="test.yml", valid=True, errors=[], warnings=[]),
        ...     ValidationResult(file="bad.yml", valid=False, errors=["Missing field"], warnings=[])
        ... ]
        >>> print_validation_summary(results)
    """
    total_files = len(results)
    passed_files = sum(1 for r in results if r["valid"])
    failed_files = total_files - passed_files

    print(f"\n{'=' * 70}")
    print(title)
    print(f"{'=' * 70}")
    print(f"Total files: {total_files}")
    print(f"Passed: {passed_files}")
    print(f"Failed: {failed_files}")
    print(f"{'=' * 70}\n")

    for result in results:
        status = "PASS" if result["valid"] else "FAIL"
        status_icon = "✓" if result["valid"] else "✗"
        print(f"{status_icon} {status} - {result['file']}")

        if result["errors"]:
            print(f"  Errors ({len(result['errors'])}):")
            for error in result["errors"]:
                print(f"    - {error}")

        if show_warnings and result.get("warnings"):
            print(f"  Warnings ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                print(f"    - {warning}")

        if result["errors"] or (show_warnings and result.get("warnings")):
            print()


def create_validation_result(
    file_path: Path | str,
    errors: list[str],
    warnings: list[str] | None = None
) -> ValidationResult:
    """Create a ValidationResult from a file path and error/warning lists.

    This is a convenience function to create properly formatted ValidationResult
    objects with automatic validity determination.

    Args:
        file_path: Path to the validated file
        errors: List of error messages
        warnings: Optional list of warning messages

    Returns:
        ValidationResult with validity determined by presence of errors

    Examples:
        >>> result = create_validation_result(
        ...     Path("test.yml"),
        ...     errors=["Missing field: name"],
        ...     warnings=["Deprecated field used"]
        ... )
        >>> assert result["valid"] is False
    """
    return ValidationResult(
        file=str(file_path),
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings or []
    )


def check_yaml_dependency() -> bool:
    """Check if PyYAML is available.

    Returns:
        True if PyYAML is installed, False otherwise

    Examples:
        >>> if not check_yaml_dependency():
        ...     print("Please install PyYAML: pip install pyyaml")
        ...     sys.exit(1)
    """
    try:
        import yaml
        return True
    except ImportError:
        return False


def print_error_list(errors: list[str], title: str = "Validation Errors") -> None:
    """Print a formatted list of errors.

    Args:
        errors: List of error messages to print
        title: Title for the error section

    Examples:
        >>> print_error_list(
        ...     ["Missing field: name", "Invalid value for age"],
        ...     title="Configuration Errors"
        ... )
    """
    if not errors:
        return

    print(f"\n{'=' * 70}")
    print(f"✗ {title}")
    print(f"{'=' * 70}")
    for error in errors:
        print(f"  - {error}")
    print()
