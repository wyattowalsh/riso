"""Run the maintainer quality suite with optional profile and log directory."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.lib.logger import configure_logging, logger
except ModuleNotFoundError:
    scripts_dir = REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from lib.logger import configure_logging, logger

PYTHON_TARGETS = ["scripts", "template/hooks", "src", "tests"]
STRICT_ONLY = ["pylint"]


def run_command(command: list[str], *, cwd: Path | None = None) -> float:
    """Run a command and exit if it fails. Returns elapsed seconds."""
    started = time.monotonic()
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Command `%s` failed.", " ".join(command))
        sys.exit(1)
    return time.monotonic() - started


def write_results(log_dir: Path, profile: str, durations: dict[str, float]) -> None:
    """Persist quality durations for CI artifacts."""
    log_dir.mkdir(parents=True, exist_ok=True)
    payload = {"profile": profile, "durations": durations}
    (log_dir / "quality-results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Run ruff, ty, and optional strict checks."""
    parser = argparse.ArgumentParser(description="Run the Riso quality suite")
    parser.add_argument(
        "--profile",
        choices=["standard", "strict"],
        default="standard",
        help="Quality profile (strict adds pylint)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Directory for quality-results.json artifact output",
    )
    args = parser.parse_args()

    configure_logging()
    durations: dict[str, float] = {}

    logger.info("Running Ruff...")
    durations["ruff"] = run_command(["uv", "run", "ruff", "check", *PYTHON_TARGETS])

    logger.info("Running ty...")
    durations["ty"] = run_command(
        [
            "uv",
            "run",
            "ty",
            "check",
            "--extra-search-path",
            "scripts",
            "--extra-search-path",
            "template",
            *PYTHON_TARGETS,
        ]
    )

    if args.profile == "strict":
        logger.info("Running Pylint...")
        durations["pylint"] = run_command(
            [
                "uv",
                "run",
                "pylint",
                "scripts",
                "template/hooks",
                "--disable=duplicate-code",
                "--fail-under=9.5",
            ]
        )

    if args.log_dir is not None:
        write_results(args.log_dir, args.profile, durations)

    logger.info("Quality suite passed (profile=%s).", args.profile)


if __name__ == "__main__":
    main()
