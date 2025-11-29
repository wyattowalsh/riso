#!/usr/bin/env python3
"""Check for performance regressions in benchmark results.

Compares current benchmark results against baseline to detect
performance regressions that exceed the acceptable threshold.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    from scripts.logging_config import setup_script_logging, logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def load_benchmark_results(file_path: Path) -> dict[str, Any]:
    """Load benchmark results from JSON file."""
    return json.loads(file_path.read_text())


def check_rendering_regressions(
    current: dict[str, Any],
    baseline: dict[str, Any],
    threshold_percent: float,
) -> list[str]:
    """Check for rendering performance regressions."""
    regressions: list[str] = []

    # Compare overall statistics
    current_avg = current.get("statistics", {}).get("average_time_seconds", 0)
    baseline_avg = baseline.get("statistics", {}).get("average_time_seconds", 0)

    if baseline_avg > 0:
        percent_change = ((current_avg - baseline_avg) / baseline_avg) * 100

        if percent_change > threshold_percent:
            regressions.append(
                f"Average rendering time increased by {percent_change:.1f}% "
                f"(baseline: {baseline_avg:.3f}s → current: {current_avg:.3f}s)"
            )

    # Compare per-variant results
    current_results = {r["variant"]: r for r in current.get("results", [])}
    baseline_results = {r["variant"]: r for r in baseline.get("results", [])}

    for variant, current_result in current_results.items():
        if variant not in baseline_results:
            continue

        baseline_result = baseline_results[variant]

        if not current_result.get("success") or not baseline_result.get("success"):
            continue

        current_time = current_result.get("rendering_time_seconds", 0)
        baseline_time = baseline_result.get("rendering_time_seconds", 0)

        if baseline_time > 0:
            percent_change = ((current_time - baseline_time) / baseline_time) * 100

            if percent_change > threshold_percent:
                regressions.append(
                    f"Variant '{variant}' rendering time increased by {percent_change:.1f}% "
                    f"(baseline: {baseline_time:.3f}s → current: {current_time:.3f}s)"
                )

    return regressions


def check_copier_regressions(
    current: dict[str, Any],
    baseline: dict[str, Any],
    threshold_percent: float,
) -> list[str]:
    """Check for copier operation performance regressions."""
    regressions: list[str] = []

    current_results = {r["operation"]: r for r in current.get("results", [])}
    baseline_results = {r["operation"]: r for r in baseline.get("results", [])}

    for operation, current_result in current_results.items():
        if operation not in baseline_results:
            continue

        baseline_result = baseline_results[operation]

        if not current_result.get("success", True) or not baseline_result.get("success", True):
            continue

        current_time = current_result.get("time_seconds", 0)
        baseline_time = baseline_result.get("time_seconds", 0)

        if baseline_time > 0:
            percent_change = ((current_time - baseline_time) / baseline_time) * 100

            if percent_change > threshold_percent:
                regressions.append(
                    f"Operation '{operation}' time increased by {percent_change:.1f}% "
                    f"(baseline: {baseline_time:.3f}s → current: {current_time:.3f}s)"
                )

    return regressions


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--current",
        type=str,
        nargs="+",
        required=True,
        help="Current benchmark result files (glob patterns supported)",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Baseline benchmark results directory (optional)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Regression threshold percentage (default: 10%%)",
    )
    args = parser.parse_args()

    try:
        from scripts.logging_config import setup_script_logging
        setup_script_logging("check_regressions")
    except ImportError:
        pass

    # Collect current files
    import glob
    current_files: list[Path] = []
    for pattern in args.current:
        matches = glob.glob(pattern)
        current_files.extend(Path(f) for f in matches if Path(f).exists())

    if not current_files:
        logger.warning("No current benchmark files found")
        sys.exit(0)

    # If no baseline provided, just log current results
    if not args.baseline or not args.baseline.exists():
        logger.info("No baseline provided - skipping regression check")
        logger.info(f"Current benchmark files: {len(current_files)}")
        sys.exit(0)

    logger.info(f"Checking {len(current_files)} benchmark file(s) for regressions")
    logger.info(f"Threshold: {args.threshold}%")

    all_regressions: list[str] = []

    for current_file in current_files:
        # Find corresponding baseline file
        baseline_file = args.baseline / current_file.name

        if not baseline_file.exists():
            logger.warning(f"No baseline found for {current_file.name}")
            continue

        logger.info(f"Comparing: {current_file.name}")

        try:
            current_data = load_benchmark_results(current_file)
            baseline_data = load_benchmark_results(baseline_file)

            if "rendering" in current_file.name:
                regressions = check_rendering_regressions(
                    current_data,
                    baseline_data,
                    args.threshold,
                )
            elif "copier" in current_file.name:
                regressions = check_copier_regressions(
                    current_data,
                    baseline_data,
                    args.threshold,
                )
            else:
                logger.warning(f"Unknown benchmark type: {current_file.name}")
                continue

            all_regressions.extend(regressions)

        except Exception as e:
            logger.error(f"Failed to process {current_file.name}: {e}")
            continue

    # Report results
    if all_regressions:
        logger.error("\n" + "=" * 60)
        logger.error("PERFORMANCE REGRESSIONS DETECTED")
        logger.error("=" * 60)
        for regression in all_regressions:
            logger.error(f"  ❌ {regression}")
        logger.error("=" * 60)
        sys.exit(1)
    else:
        logger.info("\n" + "=" * 60)
        logger.info("✅ NO PERFORMANCE REGRESSIONS DETECTED")
        logger.info("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
