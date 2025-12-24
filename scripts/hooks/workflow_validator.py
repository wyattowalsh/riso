#!/usr/bin/env python3
"""
Actionlint wrapper for post-generation hooks.

Validates generated workflow files during copier render.
Designed to be called from template/hooks/post_gen_project.py.
"""

import subprocess
import sys
from pathlib import Path


def check_actionlint_available() -> bool:
    """
    Check if actionlint is installed and available.
    
    Returns:
        True if actionlint is available, False otherwise
    """
    try:
        subprocess.run(
            ["actionlint", "--version"],
            capture_output=True,
            timeout=5,
            check=False
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def validate_workflow_file(workflow_path: Path) -> tuple[bool, str | None]:
    """
    Validate a single workflow file.

    Args:
        workflow_path: Path to workflow YAML file

    Returns:
        Tuple of (success: bool, error_message: str | None)
    """
    if not workflow_path.exists():
        return False, f"Workflow file not found: {workflow_path}"
    
    try:
        result = subprocess.run(
            ["actionlint", str(workflow_path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stdout + result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Validation timed out after 30 seconds"
    except (OSError, ValueError) as e:
        return False, f"Unexpected error: {e}"


def validate_workflows_directory(workflows_dir: Path, strict: bool = False) -> int:
    """
    Validate all workflows in a directory.
    
    Args:
        workflows_dir: Directory containing workflow files
        strict: If True, fail on any validation error; if False, warn but continue
        
    Returns:
        Exit code (0 for success, 1 for failures)
    """
    # Check if actionlint is available
    if not check_actionlint_available():
        print("⚠️  actionlint not found - skipping workflow validation")
        print("   Install: brew install actionlint (macOS)")
        print("   Or see: https://github.com/rhysd/actionlint")
        return 0 if not strict else 1
    
    # Check if workflows directory exists
    if not workflows_dir.exists():
        print(f"ℹ️  No workflows directory found at {workflows_dir}")
        return 0
    
    # Find workflow files
    workflow_files = list(workflows_dir.glob("riso-*.yml")) + list(workflows_dir.glob("riso-*.yaml"))
    
    if not workflow_files:
        print("✅ No template workflows generated (expected for minimal configs)")
        return 0
    
    # Validate each workflow
    all_valid = True
    for workflow_file in workflow_files:
        success, error_msg = validate_workflow_file(workflow_file)
        
        if success:
            print(f"✅ {workflow_file.name} - validated successfully")
        else:
            all_valid = False
            print(f"❌ {workflow_file.name} - validation failed")
            if error_msg:
                print(f"   {error_msg}")
    
    # Summary
    print(f"\n{'✅' if all_valid else '❌'} Validated {len(workflow_files)} workflow(s)")
    
    if not all_valid:
        if strict:
            print("\n❌ Workflow validation failed in strict mode")
            print("   Fix the errors above and try again")
            return 1
        else:
            print("\n⚠️  Workflow validation failed, but continuing anyway")
            print("   Workflows may not work correctly")
            print("   Run 'actionlint .github/workflows/*.yml' to debug")
            return 0
    
    return 0


if __name__ == "__main__":
    # When run directly, validate workflows in current directory
    target_dir = Path(".github/workflows")
    is_strict = "--strict" in sys.argv
    
    sys.exit(validate_workflows_directory(target_dir, is_strict))
