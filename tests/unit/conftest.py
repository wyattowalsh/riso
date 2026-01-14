"""Unit test specific fixtures for riso tests.

This module provides fixtures specific to unit tests, including mocking
utilities for subprocess calls, logger functionality, and git repository setup.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_logger(mocker):
    """Mock the logger module to capture log calls.

    Returns:
        MagicMock: Mocked logger instance that can be used to verify log calls
    """
    return mocker.patch("scripts.lib.logger.logger")


@pytest.fixture
def subprocess_success(mocker):
    """Create a subprocess mock that returns success.

    Returns:
        MagicMock: Mocked subprocess.run that returns returncode=0
    """
    mock = mocker.patch("subprocess.run")
    mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
    return mock


@pytest.fixture
def subprocess_failure(mocker):
    """Create a subprocess mock that returns failure.

    Returns:
        MagicMock: Mocked subprocess.run that returns returncode=1
    """
    mock = mocker.patch("subprocess.run")
    mock.return_value = MagicMock(returncode=1, stdout="", stderr="error")
    return mock


@pytest.fixture
def temp_git_repo(tmp_path, subprocess_success):
    """Create a temporary directory initialized as a git repo.

    Args:
        tmp_path: pytest's built-in temporary directory fixture
        subprocess_success: Mocked subprocess for git operations

    Returns:
        Path: Path to the temporary git repository directory
    """
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    return tmp_path
