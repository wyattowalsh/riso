"""Unit tests for check_quality_parity.py"""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from check_quality_parity import (
    MAKEFILE_PATTERNS,
    NODE_MAKEFILE_PATTERNS,
    NODE_TASK_PATTERNS,
    TASK_PATTERNS,
    _has_unconditional_patterns,
    assert_contains,
    main,
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestAssertContains:
    """Tests for assert_contains function."""

    def test_all_patterns_present(self, tmp_path):
        """Should return empty list when all patterns are found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff check\nty check\npylint\n")

        missing = assert_contains(test_file, ["ruff check", "ty check", "pylint"])
        assert missing == []

    def test_missing_single_pattern(self, tmp_path):
        """Should return list with missing pattern."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff check\nty check\n")

        missing = assert_contains(test_file, ["ruff check", "ty check", "pylint"])
        assert missing == ["pylint"]

    def test_partial_match_not_counted(self, tmp_path):
        """Should not match partial patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff\n")

        missing = assert_contains(test_file, ["ruff check"])
        assert missing == ["ruff check"]


@pytest.mark.unit
class TestMainFunction:
    """Tests for main function."""

    @patch("check_quality_parity.JUSTFILE")
    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.PYTHON_TASK")
    def test_success_case_all_patterns_present(self, mock_task, mock_make, mock_just):
        """Should return 0 when all patterns are present in both files."""
        makefile_content = "\n".join(MAKEFILE_PATTERNS)
        task_content = "\n".join(TASK_PATTERNS)

        mock_make.read_text.return_value = makefile_content
        mock_just.read_text.return_value = makefile_content
        mock_task.read_text.return_value = task_content

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main()

        assert result == 0
        assert "Quality parity checks passed" in mock_stdout.getvalue()

    @patch("check_quality_parity.JUSTFILE")
    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.PYTHON_TASK")
    def test_failure_makefile_missing_patterns(self, mock_task, mock_make, mock_just):
        """Should return 1 when Makefile is missing patterns."""
        mock_make.read_text.return_value = "ruff check\n"
        mock_just.read_text.return_value = "ruff check\n"
        mock_task.read_text.return_value = "\n".join(TASK_PATTERNS)

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        assert "Makefile missing:" in mock_stderr.getvalue()

    @patch("check_quality_parity.JUSTFILE")
    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.PYTHON_TASK")
    def test_failure_python_task_missing_patterns(
        self, mock_task, mock_make, mock_just
    ):
        """Should return 1 when python task is missing patterns."""
        mock_make.read_text.return_value = "\n".join(MAKEFILE_PATTERNS)
        mock_just.read_text.return_value = "\n".join(MAKEFILE_PATTERNS)
        mock_task.read_text.return_value = '"ruff"\n'

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        assert "python task missing:" in mock_stderr.getvalue()

    @patch("check_quality_parity.JUSTFILE")
    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.PYTHON_TASK")
    def test_node_parity_when_node_in_makefile(self, mock_task, mock_make, mock_just):
        """Should check Node parity when Node patterns exist in Makefile."""
        mock_make.read_text.return_value = "\n".join(
            MAKEFILE_PATTERNS + NODE_MAKEFILE_PATTERNS
        )
        mock_just.read_text.return_value = "\n".join(MAKEFILE_PATTERNS)
        mock_task.read_text.return_value = "\n".join(TASK_PATTERNS)

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        stderr_output = mock_stderr.getvalue()
        assert "python task missing Node commands:" in stderr_output
        assert '"api-node", "lint"' in stderr_output

    @patch("check_quality_parity.JUSTFILE")
    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.PYTHON_TASK")
    def test_node_parity_not_checked_when_node_not_in_makefile(
        self, mock_task, mock_make, mock_just
    ):
        """Should not check Node parity when Node patterns missing from Makefile."""
        content = "\n".join(MAKEFILE_PATTERNS)
        mock_make.read_text.return_value = content
        mock_just.read_text.return_value = content
        mock_task.read_text.return_value = "\n".join(TASK_PATTERNS)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main()

        assert result == 0
        assert "Quality parity checks passed" in mock_stdout.getvalue()

    @patch("check_quality_parity.JUSTFILE")
    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.PYTHON_TASK")
    def test_node_parity_success_when_both_have_node(
        self, mock_task, mock_make, mock_just
    ):
        """Should succeed when both files have Node patterns."""
        mock_make.read_text.return_value = "\n".join(
            MAKEFILE_PATTERNS + NODE_MAKEFILE_PATTERNS
        )
        mock_just.read_text.return_value = "\n".join(
            MAKEFILE_PATTERNS + NODE_MAKEFILE_PATTERNS
        )
        mock_task.read_text.return_value = "\n".join(TASK_PATTERNS + NODE_TASK_PATTERNS)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main()

        assert result == 0
        assert "Quality parity checks passed" in mock_stdout.getvalue()


@pytest.mark.unit
class TestNodeParityDetection:
    """Tests for conditional Node parity detection."""

    def test_node_patterns_inside_jinja_block_are_conditional(self):
        """Node targets behind api_module guards should not force parity."""
        text = (
            "quality-python:\n"
            "  ruff check\n"
            "{% if api_module == 'enabled' and 'node' in api_languages %}\n"
            "quality-node:\n"
            "  pnpm --filter api-node lint\n"
            "  pnpm --filter api-node typecheck\n"
            "{% endif %}\n"
        )
        assert not _has_unconditional_patterns(text, NODE_MAKEFILE_PATTERNS)

    def test_node_patterns_outside_jinja_block_require_parity(self):
        text = "\n".join(MAKEFILE_PATTERNS + NODE_MAKEFILE_PATTERNS)
        assert _has_unconditional_patterns(text, NODE_MAKEFILE_PATTERNS)


@pytest.mark.unit
class TestConstantsAndPaths:
    """Tests for module constants and path definitions."""

    def test_makefile_patterns_defined(self):
        """Should have Makefile quality check patterns."""
        assert "ruff check" in MAKEFILE_PATTERNS
        assert "ty check" in MAKEFILE_PATTERNS
        assert "pylint" in MAKEFILE_PATTERNS

    def test_task_patterns_defined(self):
        """Should have uv task quality check patterns."""
        assert '"ruff"' in TASK_PATTERNS
        assert '"ty"' in TASK_PATTERNS
        assert '"pylint"' in TASK_PATTERNS
        assert '"coverage"' in TASK_PATTERNS

    def test_node_patterns_defined(self):
        """Should have Node-specific patterns for both template formats."""
        assert "pnpm --filter api-node lint" in NODE_MAKEFILE_PATTERNS
        assert '"api-node", "lint"' in NODE_TASK_PATTERNS
