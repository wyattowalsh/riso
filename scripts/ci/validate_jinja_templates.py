#!/usr/bin/env python3
"""Validate Jinja2 template syntax for Copier templates.

This script checks Jinja2 templates for syntax errors without rendering them.
It's designed to be used as a pre-commit hook to catch template errors early.

Usage:
    python scripts/ci/validate_jinja_templates.py [file1.jinja] [file2.jinja] ...

Exit codes:
    0 - All templates are valid
    1 - One or more templates have syntax errors
"""

from __future__ import annotations

import sys
from pathlib import Path

from jinja2 import BaseLoader, Environment, TemplateSyntaxError, Undefined


def create_permissive_environment() -> Environment:
    """Create a Jinja2 environment that accepts Copier-style templates.

    Returns:
        A Jinja2 Environment configured for syntax validation only.
    """
    env = Environment(
        loader=BaseLoader(),
        # Keep defaults that match Copier's configuration
        block_start_string="{%",
        block_end_string="%}",
        variable_start_string="{{",
        variable_end_string="}}",
        comment_start_string="{#",
        comment_end_string="#}",
        # Don't strip whitespace during parsing
        trim_blocks=False,
        lstrip_blocks=False,
        # Use Undefined class (silently ignores undefined variables)
        undefined=Undefined,
    )
    return env


def validate_template(file_path: Path) -> tuple[bool, str | None]:
    """Validate a single Jinja template for syntax errors.

    Args:
        file_path: Path to the Jinja template file.

    Returns:
        A tuple of (is_valid, error_message).
        If valid, error_message is None.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        env = create_permissive_environment()
        # parse() checks syntax without rendering
        env.parse(content)
        return True, None
    except TemplateSyntaxError as e:
        # Format error message with file:line for easy navigation
        return False, f"{file_path}:{e.lineno}: {e.message}"
    except UnicodeDecodeError as e:
        return False, f"{file_path}: Unicode decode error: {e}"
    except OSError as e:
        return False, f"{file_path}: File read error: {e}"


def main() -> int:
    """Validate all provided Jinja template files.

    Returns:
        Exit code: 0 if all valid, 1 if any errors.
    """
    if len(sys.argv) < 2:
        print("Usage: validate_jinja_templates.py <file1.jinja> [file2.jinja] ...")
        print("No files provided, nothing to validate.")
        return 0

    files = [Path(f) for f in sys.argv[1:]]
    errors: list[str] = []
    validated = 0

    for file_path in files:
        if not file_path.exists():
            errors.append(f"{file_path}: File not found")
            continue

        if not file_path.is_file():
            errors.append(f"{file_path}: Not a file")
            continue

        is_valid, error_msg = validate_template(file_path)
        validated += 1

        if not is_valid and error_msg:
            errors.append(error_msg)

    # Report results
    if errors:
        print(
            f"Jinja template validation failed ({len(errors)} error(s)):",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    if validated > 0:
        print(f"Validated {validated} Jinja template(s): all OK")

    return 0


if __name__ == "__main__":
    sys.exit(main())
