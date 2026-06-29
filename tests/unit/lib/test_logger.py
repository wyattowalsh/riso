"""Tests for logger module."""

from __future__ import annotations

import sys
from pathlib import Path

# Add scripts/lib to path
scripts_lib = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if str(scripts_lib) not in sys.path:
    sys.path.insert(0, str(scripts_lib))

from logger import configure_logging, get_logger, logger  # noqa: E402


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_default(self):
        """Should configure with default INFO level."""
        configure_logging()
        # Should not raise
        logger.info("Test message")

    def test_configure_logging_debug_level(self):
        """Should configure with DEBUG level."""
        configure_logging(level="DEBUG")
        logger.debug("Debug message")

    def test_configure_logging_json_format(self):
        """Should configure with JSON format."""
        configure_logging(json_format=True)
        logger.info("JSON message")
        # Reset to default for other tests
        configure_logging()


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_bound_logger(self):
        """Should return a logger bound with the given name."""
        named_logger = get_logger("test_module")
        assert named_logger is not None
        # Should be callable for logging
        named_logger.info("Test from named logger")

    def test_get_logger_different_names(self):
        """Should create separate bound loggers for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        # Both should work independently
        logger1.info("From module1")
        logger2.info("From module2")
