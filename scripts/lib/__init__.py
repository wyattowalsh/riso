"""Shared utilities for Riso CI scripts."""

# Support both package import and direct test imports.
try:
    from .logger import configure_logging, get_logger, logger
except ImportError:
    from logger import configure_logging, get_logger, logger

__version__ = "0.1.0"

__all__ = ["logger", "configure_logging", "get_logger"]
