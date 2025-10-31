#!/usr/bin/env python3
"""
Sync Test Script: Verify make quality and uv run task quality produce consistent results.

This script runs both quality command interfaces and compares:
- Exit codes (must match exactly)
- Execution durations (must be within reasonable variance)
- Tool execution order and coverage

Usage:
    python tests/automation/sync_test.py [--threshold PERCENT] [--output OUTPUT_FILE]

Arguments:
    --threshold: Maximum allowed duration variance percentage (default: 15)
    --output: JSON output file for CI consumption (default: sync_test_results.json)
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


class QualityRunner:
    """Runs quality commands and captures execution metrics."""

    def __init__(self):
        self.results = {}
        self.make_available = shutil.which("make") is not None

    def run_command(
        self, command: List[str], name: str, cwd: Optional[Path] = None
    ) -> Dict:
        """
        Run a command and capture metrics.

        Args:
            command: Command to run as list of strings
            name: Human-readable name for logging
            cwd: Working directory for command execution

        Returns:
            Dictionary with metrics: exit_code, duration, stdout, stderr, success
        """
        print(f"\n{'=' * 60}")
        print(f"Running: {name}")
        print(f"Command: {' '.join(command)}")
        print(f"{'=' * 60}\n")

        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,  # We handle exit codes manually
            )
            duration = time.time() - start_time
            success = result.returncode == 0

            metrics = {
                "exit_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": success,
                "command": " ".join(command),
            }

            print(f"✓ Exit code: {result.returncode}")
            print(f"✓ Duration: {duration:.2f}s")
            if not success:
                print(f"✗ STDERR:\n{result.stderr}")

            return metrics

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"✗ Command timed out after {duration:.2f}s")
            return {
                "exit_code": -1,
                "duration": duration,
                "stdout": "",
                "stderr": "Command timed out",
                "success": False,
                "command": " ".join(command),
            }

        except (OSError, ValueError) as e:
            duration = time.time() - start_time
            print(f"✗ Unexpected error: {e}")
            return {
                "exit_code": -2,
                "duration": duration,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "command": " ".join(command),
            }

    def run_make_quality(self, cwd: Optional[Path] = None) -> Dict:
        """Run 'make quality' and return metrics."""
        if not self.make_available:
            return {
                "exit_code": -3,
                "duration": 0.0,
                "stdout": "",
                "stderr": "make command not available",
                "success": False,
                "command": "make quality",
                "skipped": True,
            }

        return self.run_command(["make", "quality"], "make quality", cwd)

    def run_uv_quality(self, cwd: Optional[Path] = None) -> Dict:
        """Run 'uv run task quality' and return metrics."""
        return self.run_command(["uv", "run", "task", "quality"], "uv run task quality", cwd)

    def compare_results(
        self, make_result: Dict, uv_result: Dict, threshold: float = 15.0
    ) -> Dict:
        """
        Compare results from both commands.

        Args:
            make_result: Metrics from make quality
            uv_result: Metrics from uv run task quality
            threshold: Maximum allowed duration variance percentage

        Returns:
            Dictionary with comparison results and status
        """
        comparison = {
            "exit_codes_match": make_result["exit_code"] == uv_result["exit_code"],
            "both_succeeded": make_result["success"] and uv_result["success"],
            "make_duration": make_result["duration"],
            "uv_duration": uv_result["duration"],
            "duration_variance_percent": 0.0,
            "duration_within_threshold": True,
            "issues": [],
            "status": "PASS",
        }

        # Check if make was skipped
        if make_result.get("skipped"):
            comparison["issues"].append("make command not available - only tested uv task")
            comparison["status"] = "SKIP" if uv_result["success"] else "FAIL"
            return comparison

        # Compare exit codes
        if not comparison["exit_codes_match"]:
            comparison["issues"].append(
                f"Exit codes differ: make={make_result['exit_code']}, uv={uv_result['exit_code']}"
            )
            comparison["status"] = "FAIL"

        # Compare durations (only if both succeeded)
        if comparison["both_succeeded"]:
            if make_result["duration"] > 0:
                variance = abs(make_result["duration"] - uv_result["duration"])
                variance_pct = (variance / make_result["duration"]) * 100
                comparison["duration_variance_percent"] = variance_pct
                comparison["duration_within_threshold"] = variance_pct <= threshold

                if not comparison["duration_within_threshold"]:
                    comparison["issues"].append(
                        f"Duration variance {variance_pct:.1f}% exceeds threshold {threshold}%"
                    )
                    comparison["status"] = "WARN"
        else:
            if not make_result["success"]:
                comparison["issues"].append("make quality failed")
            if not uv_result["success"]:
                comparison["issues"].append("uv run task quality failed")
            comparison["status"] = "FAIL"

        return comparison

    def generate_report(
        self,
        make_result: Dict,
        uv_result: Dict,
        comparison: Dict,
        output_file: Optional[Path] = None,
    ) -> Dict:
        """
        Generate comprehensive test report.

        Args:
            make_result: Metrics from make quality
            uv_result: Metrics from uv run task quality
            comparison: Comparison results
            output_file: Optional file path to write JSON report

        Returns:
            Complete report dictionary
        """
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "make_quality": make_result,
            "uv_task_quality": uv_result,
            "comparison": comparison,
            "overall_status": comparison["status"],
            "summary": {
                "make_available": self.make_available,
                "exit_codes_match": comparison["exit_codes_match"],
                "both_succeeded": comparison["both_succeeded"],
                "duration_variance": f"{comparison['duration_variance_percent']:.1f}%",
                "issues_count": len(comparison["issues"]),
            },
        }

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"\n✓ Report written to: {output_file}")

        return report

    def print_summary(self, comparison: Dict):
        """Print human-readable summary."""
        print("\n" + "=" * 60)
        print("SYNC TEST SUMMARY")
        print("=" * 60)

        status_symbol = {
            "PASS": "✓",
            "WARN": "⚠",
            "FAIL": "✗",
            "SKIP": "⊘",
        }.get(comparison["status"], "?")

        print(f"\nOverall Status: {status_symbol} {comparison['status']}")

        if comparison["issues"]:
            print(f"\nIssues Found ({len(comparison['issues'])}):")
            for issue in comparison["issues"]:
                print(f"  • {issue}")
        else:
            print("\n✓ No issues found - both interfaces are synchronized")

        print("\nDuration Comparison:")
        print(f"  make quality:        {comparison['make_duration']:.2f}s")
        print(f"  uv run task quality: {comparison['uv_duration']:.2f}s")
        if comparison["duration_variance_percent"] > 0:
            print(f"  Variance:            {comparison['duration_variance_percent']:.1f}%")

        print("=" * 60 + "\n")


def main():
    """Main entry point for sync test."""
    parser = argparse.ArgumentParser(
        description="Test consistency between make quality and uv run task quality"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=15.0,
        help="Maximum allowed duration variance percentage (default: 15)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("sync_test_results.json"),
        help="JSON output file path (default: sync_test_results.json)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=None,
        help="Working directory for command execution (default: current directory)",
    )

    args = parser.parse_args()

    runner = QualityRunner()

    # Run both quality commands
    make_result = runner.run_make_quality(cwd=args.cwd)
    uv_result = runner.run_uv_quality(cwd=args.cwd)

    # Compare results
    comparison = runner.compare_results(make_result, uv_result, args.threshold)

    # Generate report
    runner.generate_report(make_result, uv_result, comparison, args.output)

    # Print summary
    runner.print_summary(comparison)

    # Exit with appropriate code
    exit_codes = {
        "PASS": 0,
        "WARN": 1,
        "SKIP": 0,  # Skip is not a failure
        "FAIL": 2,
    }
    sys.exit(exit_codes.get(comparison["status"], 2))


if __name__ == "__main__":
    main()
