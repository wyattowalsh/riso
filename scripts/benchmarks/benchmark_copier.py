#!/usr/bin/env python3
"""Benchmark core copier operations.

Measures performance of key copier operations like answer validation,
template discovery, and hook execution.
"""

from __future__ import annotations

import argparse
import json
import time
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


REPO_ROOT = Path(__file__).resolve().parents[2]


def benchmark_template_discovery() -> dict[str, Any]:
    """Benchmark template file discovery."""
    start_time = time.perf_counter()

    # Count template files
    template_dir = REPO_ROOT / "template"
    jinja_files = list(template_dir.rglob("*.jinja"))
    py_files = list(template_dir.rglob("*.py"))
    yml_files = list(template_dir.rglob("*.yml"))
    all_files = list(template_dir.rglob("*"))

    end_time = time.perf_counter()

    return {
        "operation": "template_discovery",
        "time_seconds": round(end_time - start_time, 3),
        "jinja_files": len(jinja_files),
        "py_files": len(py_files),
        "yml_files": len(yml_files),
        "total_files": sum(1 for f in all_files if f.is_file()),
    }


def benchmark_hook_import() -> dict[str, Any]:
    """Benchmark hook module imports."""
    start_time = time.perf_counter()

    try:
        # Import validation module
        sys.path.insert(0, str(REPO_ROOT / "template"))
        from hooks import validation  # noqa: F401
        success = True
        error = None
    except Exception as e:
        success = False
        error = str(e)

    end_time = time.perf_counter()

    return {
        "operation": "hook_import",
        "time_seconds": round(end_time - start_time, 3),
        "success": success,
        "error": error,
    }


def benchmark_pydantic_validation() -> dict[str, Any]:
    """Benchmark Pydantic model validation."""
    start_time = time.perf_counter()

    try:
        sys.path.insert(0, str(REPO_ROOT / "template"))
        from hooks.validation import ProjectConfig, ModuleConfig, SaaSConfig

        # Validate typical configuration
        project = ProjectConfig(
            project_name="Test Project",
            project_slug="test-project",
            package_name="test_project",
            project_layout="single-package",
            quality_profile="standard",
            python_versions=["3.11", "3.12", "3.13"],
        )

        modules = ModuleConfig(
            cli_module="enabled",
            api_tracks="python",
            graphql_api_module="disabled",
            mcp_module="disabled",
            websocket_module="disabled",
            codegen_module="disabled",
            changelog_module="disabled",
            notebook_module="disabled",
            docs_site="fumadocs",
            shared_logic="disabled",
            ci_platform="github-actions",
            saas_starter_module="disabled",
        )

        success = True
        error = None
    except Exception as e:
        success = False
        error = str(e)

    end_time = time.perf_counter()

    return {
        "operation": "pydantic_validation",
        "time_seconds": round(end_time - start_time, 3),
        "success": success,
        "error": error,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark-results-copier.json"),
        help="Output JSON file path",
    )
    args = parser.parse_args()

    try:
        from scripts.logging_config import setup_script_logging
        setup_script_logging("benchmark_copier")
    except ImportError:
        pass

    logger.info("Running copier benchmarks")

    # Run benchmarks
    benchmarks = [
        benchmark_template_discovery,
        benchmark_hook_import,
        benchmark_pydantic_validation,
    ]

    results: list[dict[str, Any]] = []
    total_start = time.perf_counter()

    for benchmark_func in benchmarks:
        logger.info(f"Running: {benchmark_func.__name__}")
        result = benchmark_func()
        results.append(result)

        if result.get("success", True):
            logger.info(f"✅ {result['operation']}: {result['time_seconds']}s")
        else:
            logger.error(f"❌ {result['operation']}: {result.get('error', 'Unknown error')}")

    total_time = time.perf_counter() - total_start

    # Create summary
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_benchmarks": len(results),
        "successful_benchmarks": sum(1 for r in results if r.get("success", True)),
        "total_time_seconds": round(total_time, 3),
        "results": results,
    }

    # Write output
    args.output.write_text(json.dumps(summary, indent=2))
    logger.info(f"Benchmark results written to {args.output}")


if __name__ == "__main__":
    main()
