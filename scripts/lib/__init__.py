"""Shared utilities for Riso CI scripts."""

# Support both package import (from project root) and direct import (tests)
try:
    from scripts.lib.logger import configure_logging, get_logger, logger
except ModuleNotFoundError:
    from logger import configure_logging, get_logger, logger  # type: ignore[import-not-found]

__version__ = "0.1.0"

__all__ = ["logger", "configure_logging", "get_logger"]
