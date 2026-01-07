import subprocess
import sys

from scripts.lib.logger import logger, configure_logging

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