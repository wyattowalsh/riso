#!/usr/bin/env python3
"""Benchmark template rendering performance.

Measures the time it takes to render different template variants
to identify performance bottlenecks and track improvements over time.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    from scripts.logging_config import setup_script_logging, logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "samples"


def benchmark_variant_rendering(variant: str, answers_file: Path) -> dict[str, Any]:
    """Benchmark rendering of a single variant.

    Args:
        variant: Variant name
        answers_file: Path to copier answers file

    Returns:
        Benchmark results dictionary
    """
    logger.info(f"Benchmarking variant: {variant}")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "render"

        # Measure rendering time
        start_time = time.perf_counter()
        try:
            result = subprocess.run(
                [
                    "copier",
                    "copy",
                    "--answers-file",
                    str(answers_file),
                    "--force",
                    str(REPO_ROOT),
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
                timeout=300,
                check=True,
            )
            end_time = time.perf_counter()
            success = True
            error = None
        except subprocess.TimeoutExpired:
            end_time = time.perf_counter()
            success = False
            error = "Timeout after 300s"
        except subprocess.CalledProcessError as e:
            end_time = time.perf_counter()
            success = False
            error = f"Exit code {e.returncode}: {e.stderr}"

        rendering_time = end_time - start_time

        # Count generated files
        if success:
            generated_files = list(output_dir.rglob("*"))
            file_count = sum(1 for f in generated_files if f.is_file())
            total_size = sum(f.stat().st_size for f in generated_files if f.is_file())
        else:
            file_count = 0
            total_size = 0

        return {
            "variant": variant,
            "success": success,
            "rendering_time_seconds": round(rendering_time, 3),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "error": error,
        }


def discover_variants() -> list[tuple[str, Path]]:
    """Discover all sample variants.

    Returns:
        List of (variant_name, answers_file_path) tuples
    """
    variants: list[tuple[str, Path]] = []
    for answers_file in SAMPLES_DIR.glob("*/copier-answers.yml"):
        variant = answers_file.parent.name
        variants.append((variant, answers_file))
    return sorted(variants)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark-results-rendering.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--variant",
        type=str,
        help="Benchmark specific variant (default: all variants)",
    )
    args = parser.parse_args()

    try:
        from scripts.logging_config import setup_script_logging
        setup_script_logging("benchmark_rendering")
    except ImportError:
        pass

    # Discover variants
    all_variants = discover_variants()

    if args.variant:
        variants = [(v, p) for v, p in all_variants if v == args.variant]
        if not variants:
            logger.error(f"Variant not found: {args.variant}")
            logger.info(f"Available variants: {', '.join(v for v, _ in all_variants)}")
            sys.exit(1)
    else:
        variants = all_variants

    logger.info(f"Benchmarking {len(variants)} variant(s)")

    # Run benchmarks
    results: list[dict[str, Any]] = []
    total_start = time.perf_counter()

    for variant, answers_file in variants:
        result = benchmark_variant_rendering(variant, answers_file)
        results.append(result)

        if result["success"]:
            logger.info(
                f"✅ {variant}: {result['rendering_time_seconds']}s "
                f"({result['file_count']} files, {result['total_size_mb']} MB)"
            )
        else:
            logger.error(f"❌ {variant}: {result['error']}")

    total_time = time.perf_counter() - total_start

    # Calculate statistics
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        times = [r["rendering_time_seconds"] for r in successful_results]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
    else:
        avg_time = min_time = max_time = 0

    # Create summary
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_variants": len(results),
        "successful_variants": len(successful_results),
        "failed_variants": len(results) - len(successful_results),
        "total_time_seconds": round(total_time, 3),
        "statistics": {
            "average_time_seconds": round(avg_time, 3),
            "min_time_seconds": round(min_time, 3),
            "max_time_seconds": round(max_time, 3),
        },
        "results": results,
    }

    # Write output
    args.output.write_text(json.dumps(summary, indent=2))
    logger.info(f"Benchmark results written to {args.output}")

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("BENCHMARK SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total variants: {summary['total_variants']}")
    logger.info(f"Successful: {summary['successful_variants']}")
    logger.info(f"Failed: {summary['failed_variants']}")
    logger.info(f"Total time: {summary['total_time_seconds']}s")
    logger.info(f"Average time: {avg_time:.3f}s")
    logger.info(f"Min time: {min_time:.3f}s")
    logger.info(f"Max time: {max_time:.3f}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
