#!/usr/bin/env python3
"""Summarize benchmark results into a markdown report.

Generates a human-readable summary of benchmark results for display
in pull request comments or documentation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    from scripts.logging_config import setup_script_logging, logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"


def summarize_rendering_benchmarks(data: dict[str, Any]) -> str:
    """Summarize template rendering benchmarks."""
    lines = [
        "### Template Rendering Benchmarks",
        "",
        f"**Total Variants**: {data.get('total_variants', 0)}",
        f"**Successful**: {data.get('successful_variants', 0)}",
        f"**Failed**: {data.get('failed_variants', 0)}",
        f"**Total Time**: {format_time(data.get('total_time_seconds', 0))}",
        "",
    ]

    stats = data.get("statistics", {})
    if stats:
        lines.extend([
            "**Performance Statistics:**",
            f"- Average: {format_time(stats.get('average_time_seconds', 0))}",
            f"- Fastest: {format_time(stats.get('min_time_seconds', 0))}",
            f"- Slowest: {format_time(stats.get('max_time_seconds', 0))}",
            "",
        ])

    # Add results table
    results = data.get("results", [])
    if results:
        lines.extend([
            "| Variant | Time | Files | Size |",
            "|---------|------|-------|------|",
        ])

        for result in results:
            if result.get("success"):
                variant = result.get("variant", "unknown")
                time_str = format_time(result.get("rendering_time_seconds", 0))
                files = result.get("file_count", 0)
                size_mb = result.get("total_size_mb", 0)
                lines.append(f"| {variant} | {time_str} | {files} | {size_mb:.2f} MB |")
            else:
                variant = result.get("variant", "unknown")
                error = result.get("error", "Unknown error")
                lines.append(f"| {variant} | ❌ Failed | - | - |")

    return "\n".join(lines)


def summarize_copier_benchmarks(data: dict[str, Any]) -> str:
    """Summarize copier operation benchmarks."""
    lines = [
        "### Copier Operations Benchmarks",
        "",
        f"**Total Benchmarks**: {data.get('total_benchmarks', 0)}",
        f"**Successful**: {data.get('successful_benchmarks', 0)}",
        f"**Total Time**: {format_time(data.get('total_time_seconds', 0))}",
        "",
    ]

    # Add results table
    results = data.get("results", [])
    if results:
        lines.extend([
            "| Operation | Time | Status |",
            "|-----------|------|--------|",
        ])

        for result in results:
            operation = result.get("operation", "unknown").replace("_", " ").title()
            time_str = format_time(result.get("time_seconds", 0))
            success = result.get("success", True)
            status = "✅" if success else f"❌ {result.get('error', 'Failed')}"
            lines.append(f"| {operation} | {time_str} | {status} |")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-files",
        type=str,
        nargs="+",
        required=True,
        help="Input benchmark JSON files (glob patterns supported)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark-summary.md"),
        help="Output markdown file path",
    )
    args = parser.parse_args()

    try:
        from scripts.logging_config import setup_script_logging
        setup_script_logging("summarize_benchmarks")
    except ImportError:
        pass

    # Collect all input files (handle globs)
    import glob
    input_files: list[Path] = []
    for pattern in args.input_files:
        matches = glob.glob(pattern)
        input_files.extend(Path(f) for f in matches if Path(f).exists())

    if not input_files:
        logger.error("No input files found")
        sys.exit(1)

    logger.info(f"Processing {len(input_files)} benchmark file(s)")

    # Generate summary
    summary_lines = [
        "# 📊 Performance Benchmark Results",
        "",
        f"_Generated: {import_time.strftime('%Y-%m-%d %H:%M:%S UTC', import_time.gmtime())}_",
        "",
    ]

    for input_file in sorted(input_files):
        logger.info(f"Processing: {input_file}")

        try:
            data = json.loads(input_file.read_text())

            if "rendering" in input_file.name:
                summary_lines.append(summarize_rendering_benchmarks(data))
            elif "copier" in input_file.name:
                summary_lines.append(summarize_copier_benchmarks(data))
            else:
                logger.warning(f"Unknown benchmark type: {input_file.name}")
                continue

            summary_lines.append("")  # Add blank line between sections

        except Exception as e:
            logger.error(f"Failed to process {input_file}: {e}")
            continue

    # Add footer
    summary_lines.extend([
        "---",
        "",
        "_Benchmarks run on GitHub Actions (ubuntu-latest, Python 3.12)_",
    ])

    # Write output
    summary_md = "\n".join(summary_lines)
    args.output.write_text(summary_md)
    logger.info(f"Summary written to {args.output}")

    # Print to stdout for GitHub Actions
    print(summary_md)


if __name__ == "__main__":
    import time as import_time
    main()
