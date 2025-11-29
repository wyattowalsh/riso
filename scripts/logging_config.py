"""Logging configuration for Riso scripts and hooks.

This module provides structured logging with loguru for all Riso automation
scripts, hooks, and utilities. It includes:
- Structured JSON logging for CI/CD
- Human-friendly console output for local development
- Log rotation and retention policies
- Context injection (script name, timestamp, etc.)
"""

import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# Determine log level from environment
LOG_LEVEL = os.getenv("RISO_LOG_LEVEL", "INFO").upper()

# Determine if running in CI
IS_CI = os.getenv("CI", "false").lower() == "true"

# Log directory
LOG_DIR = Path(".riso/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(
    script_name: str,
    log_file: Optional[str] = None,
    enable_json: bool = False,
) -> None:
    """
    Configure loguru logging for a script.

    Args:
        script_name: Name of the script (for context injection)
        log_file: Optional log file name (saved to .riso/logs/)
        enable_json: Force JSON logging (auto-enabled in CI)

    Example:
        from scripts.logging_config import configure_logging, logger

        configure_logging("validate_saas_combinations")
        logger.info("Starting validation", combinations=3)
    """
    # Remove default handler
    logger.remove()

    # Determine format based on environment
    use_json = enable_json or IS_CI

    if use_json:
        # Structured JSON logging for CI/CD
        log_format = (
            '{"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"script": "' + script_name + '", '
            '"message": "{message}", '
            '"extra": {extra}}'
        )
    else:
        # Human-friendly logging for local development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>" + script_name + "</cyan> | "
            "<level>{message}</level>"
        )

    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=LOG_LEVEL,
        colorize=not use_json,
    )

    # File handler (if specified)
    if log_file:
        log_path = LOG_DIR / log_file
        logger.add(
            str(log_path),
            format=log_format,
            level="DEBUG",  # Always log everything to file
            rotation="10 MB",  # Rotate at 10MB
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated logs
        )
        logger.debug(f"Logging to file: {log_path}")


def get_logger():
    """Get configured logger instance."""
    return logger


# Convenience function for quick setup
def setup_script_logging(script_name: str) -> None:
    """
    Quick setup for script logging with sensible defaults.

    Args:
        script_name: Name of the script
    """
    log_file = f"{script_name}.log" if not IS_CI else None
    configure_logging(script_name, log_file=log_file)
