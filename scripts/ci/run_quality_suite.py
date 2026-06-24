import subprocess
import sys
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


def run_command(command, cwd=None):
    """Runs a command and exits if it fails."""
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error(f"Command `{' '.join(command)}` failed.")
        sys.exit(1)


def main():
    """Runs the quality suite."""
    configure_logging()

    logger.info("Running Ruff...")
    run_command(["ruff", "check", "."])
    logger.info("Running Mypy...")
    run_command(["mypy", "."])
    logger.info("Running Pylint...")
    run_command(["pylint", "template", "scripts"])


if __name__ == "__main__":
    main()
