#!/usr/bin/env python3
"""
Workflow validation helper script.

Validates GitHub Actions workflow YAML files using actionlint.
Used by CI automation and post-generation hooks.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.lib.logger import logger, configure_logging


def validate_workflow(workflow_path: Path) -> dict[str, Any]:
    """
    Validate a single workflow file using actionlint.
    
    Args:
        workflow_path: Path to workflow YAML file
        
    Returns:
        Validation result dictionary with status and errors
    """
    result = {
        "workflow": str(workflow_path),
        "status": "pending",
        "errors": [],
        "warnings": []
    }
    
    try:
        proc = subprocess.run(
            ["actionlint", "-format", "{{json .}}", str(workflow_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if proc.returncode == 0:
            result["status"] = "pass"
        else:
            result["status"] = "fail"
            # Parse actionlint JSON output
            for line in proc.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    error = json.loads(line)
                    result["errors"].append({
                        "line": error.get("line", 0),
                        "column": error.get("column", 0),
                        "message": error.get("message", "Unknown error"),
                        "kind": error.get("kind", "error")
                    })
                except json.JSONDecodeError:
                    # Fallback for non-JSON output
                    result["errors"].append({"message": line})
                    
    except FileNotFoundError:
        result["status"] = "skipped"
        result["errors"].append({
            "message": "actionlint not found - skipping validation"
        })
    except subprocess.TimeoutExpired:
        result["status"] = "fail"
        result["errors"].append({
            "message": "Validation timed out after 30 seconds"
        })
    
    return result


def validate_workflows(workflows_dir: Path, output_json: bool = False) -> int:
    """
    Validate all workflow files in a directory.

    Args:
        workflows_dir: Directory containing workflow files
        output_json: Whether to output results as JSON

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    if not workflows_dir.exists():
        logger.error(f"Workflow directory not found: {workflows_dir}")
        return 1

    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

    if not workflow_files:
        if output_json:
            print(json.dumps({"status": "no_workflows", "results": []}))
        else:
            logger.info("No workflow files found")
        return 0
    
    results = []
    all_passed = True
    
    for workflow_file in workflow_files:
        result = validate_workflow(workflow_file)
        results.append(result)
        
        if result["status"] == "fail":
            all_passed = False
    
    if output_json:
        print(json.dumps({
            "status": "pass" if all_passed else "fail",
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "pass"),
            "failed": sum(1 for r in results if r["status"] == "fail"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
            "results": results
        }, indent=2))
    else:
        # Human-readable output
        for result in results:
            workflow_name = Path(result["workflow"]).name

            if result["status"] == "pass":
                logger.info(f"{workflow_name} - passed")
            elif result["status"] == "fail":
                logger.error(f"{workflow_name} - failed")
                for error in result["errors"]:
                    if "line" in error:
                        logger.error(f"   Line {error['line']}: {error['message']}")
                    else:
                        logger.error(f"   {error['message']}")
            elif result["status"] == "skipped":
                logger.warning(f"{workflow_name} - skipped")
                for error in result["errors"]:
                    logger.warning(f"   {error['message']}")

        logger.info(f"\nTotal: {len(results)} | Passed: {sum(1 for r in results if r['status'] == 'pass')} | Failed: {sum(1 for r in results if r['status'] == 'fail')} | Skipped: {sum(1 for r in results if r['status'] == 'skipped')}")

    return 0 if all_passed else 1


def main() -> int:
    """Main entry point."""
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Validate GitHub Actions workflow files"
    )
    parser.add_argument(
        "workflows_dir",
        type=Path,
        help="Directory containing workflow files"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    return validate_workflows(args.workflows_dir, args.json)


if __name__ == "__main__":
    sys.exit(main())
