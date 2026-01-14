"""Centralized logging for RISO scripts using Loguru.

This module provides a configured Loguru logger for all RISO scripts,
replacing print() statements with structured, colorized logging.

Usage:
    from scripts.lib.logger import logger, configure_logging

    configure_logging(level="DEBUG")  # Optional, defaults to INFO
    logger.info("Processing file...")
    logger.error("Validation failed")
"""
import sys
from loguru import logger


def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Configure Loguru for CLI scripts.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, output logs as JSON for machine parsing
    """
    logger.remove()  # Remove default handler

    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    if json_format:
        logger.add(sys.stderr, serialize=True, level=level)
    else:
        logger.add(sys.stderr, format=format_str, level=level, colorize=True)


def get_logger(name: str):
    """Get a named logger for compatibility with migration pattern.

    Args:
        name: Logger name (typically module name)

    Returns:
        A bound logger instance with the given name
    """
    return logger.bind(name=name)


__all__ = ["logger", "configure_logging", "get_logger"]
