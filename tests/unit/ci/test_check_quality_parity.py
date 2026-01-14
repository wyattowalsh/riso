"""Unit tests for check_quality_parity.py"""

import pytest
from unittest.mock import patch
from io import StringIO

from check_quality_parity import (
    assert_contains,
    main,
    REQUIRED_PATTERNS,
    NODE_PATTERNS,
)


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestAssertContains:
    """Tests for assert_contains function."""

    def test_all_patterns_present(self, tmp_path):
        """Should return empty list when all patterns are found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff check\nmypy\npylint\n")

        missing = assert_contains(test_file, ["ruff check", "mypy", "pylint"])
        assert missing == []

    def test_missing_single_pattern(self, tmp_path):
        """Should return list with missing pattern."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff check\nmypy\n")

        missing = assert_contains(test_file, ["ruff check", "mypy", "pylint"])
        assert missing == ["pylint"]

    def test_missing_multiple_patterns(self, tmp_path):
        """Should return all missing patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff check\n")

        missing = assert_contains(test_file, ["ruff check", "mypy", "pylint"])
        assert missing == ["mypy", "pylint"]

    def test_all_patterns_missing(self, tmp_path):
        """Should return all patterns when none are found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("some other content\n")

        missing = assert_contains(test_file, ["ruff check", "mypy", "pylint"])
        assert missing == ["ruff check", "mypy", "pylint"]

    def test_empty_file(self, tmp_path):
        """Should return all patterns when file is empty."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("")

        missing = assert_contains(test_file, ["ruff check", "mypy"])
        assert missing == ["ruff check", "mypy"]

    def test_empty_pattern_list(self, tmp_path):
        """Should return empty list when no patterns to check."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        missing = assert_contains(test_file, [])
        assert missing == []

    def test_pattern_with_spaces(self, tmp_path):
        """Should correctly match patterns with spaces."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("coverage run --source=src\n")

        missing = assert_contains(test_file, ["coverage run"])
        assert missing == []

    def test_partial_match_not_counted(self, tmp_path):
        """Should not match partial patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("ruff\n")

        missing = assert_contains(test_file, ["ruff check"])
        assert missing == ["ruff check"]

    def test_case_sensitive_matching(self, tmp_path):
        """Should be case sensitive in matching."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("RUFF CHECK\n")

        missing = assert_contains(test_file, ["ruff check"])
        assert missing == ["ruff check"]

    def test_multiline_content(self, tmp_path):
        """Should find patterns across multiple lines."""
        test_file = tmp_path / "test.txt"
        content = """
        quality:
            ruff check .
            mypy src
            pylint src
            coverage run -m pytest
            coverage report
        """
        test_file.write_text(content)

        missing = assert_contains(test_file, REQUIRED_PATTERNS)
        assert missing == []


@pytest.mark.unit
class TestMainFunction:
    """Tests for main function."""

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_success_case_all_patterns_present(self, mock_uv, mock_make, tmp_path):
        """Should return 0 when all patterns are present in both files."""
        # Create test files with all required patterns
        makefile = tmp_path / "makefile.txt"
        uv_task = tmp_path / "uv_task.txt"

        content = "\n".join(REQUIRED_PATTERNS)
        makefile.write_text(content)
        uv_task.write_text(content)

        mock_make.read_text.return_value = content
        mock_uv.read_text.return_value = content

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main()

        assert result == 0
        assert "Quality parity checks passed" in mock_stdout.getvalue()

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_failure_makefile_missing_patterns(self, mock_uv, mock_make, tmp_path):
        """Should return 1 when Makefile is missing patterns."""
        makefile_content = "ruff check\n"  # Missing most patterns
        uv_content = "\n".join(REQUIRED_PATTERNS)

        mock_make.read_text.return_value = makefile_content
        mock_uv.read_text.return_value = uv_content

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        stderr_output = mock_stderr.getvalue()
        assert "Makefile missing:" in stderr_output
        assert "mypy" in stderr_output

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_failure_uv_task_missing_patterns(self, mock_uv, mock_make, tmp_path):
        """Should return 1 when uv task is missing patterns."""
        makefile_content = "\n".join(REQUIRED_PATTERNS)
        uv_content = "ruff check\n"  # Missing most patterns

        mock_make.read_text.return_value = makefile_content
        mock_uv.read_text.return_value = uv_content

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        stderr_output = mock_stderr.getvalue()
        assert "uv task missing:" in stderr_output
        assert "mypy" in stderr_output

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_failure_both_files_missing_patterns(self, mock_uv, mock_make, tmp_path):
        """Should report errors for both files when both are missing patterns."""
        makefile_content = "ruff check\n"
        uv_content = "ruff check\n"

        mock_make.read_text.return_value = makefile_content
        mock_uv.read_text.return_value = uv_content

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        stderr_output = mock_stderr.getvalue()
        assert "Makefile missing:" in stderr_output
        assert "uv task missing:" in stderr_output

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_node_parity_when_node_in_makefile(self, mock_uv, mock_make, tmp_path):
        """Should check Node parity when Node patterns exist in Makefile."""
        content_with_node = "\n".join(REQUIRED_PATTERNS + NODE_PATTERNS)
        content_without_node = "\n".join(REQUIRED_PATTERNS)

        mock_make.read_text.return_value = content_with_node
        mock_uv.read_text.return_value = content_without_node

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        stderr_output = mock_stderr.getvalue()
        assert "uv task missing Node commands:" in stderr_output
        assert "pnpm --filter api-node" in stderr_output

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_node_parity_not_checked_when_node_not_in_makefile(
        self, mock_uv, mock_make, tmp_path
    ):
        """Should not check Node parity when Node patterns missing from Makefile."""
        content = "\n".join(REQUIRED_PATTERNS)

        mock_make.read_text.return_value = content
        mock_uv.read_text.return_value = content

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main()

        assert result == 0
        assert "Quality parity checks passed" in mock_stdout.getvalue()

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_node_parity_success_when_both_have_node(
        self, mock_uv, mock_make, tmp_path
    ):
        """Should succeed when both files have Node patterns."""
        content = "\n".join(REQUIRED_PATTERNS + NODE_PATTERNS)

        mock_make.read_text.return_value = content
        mock_uv.read_text.return_value = content

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main()

        assert result == 0
        assert "Quality parity checks passed" in mock_stdout.getvalue()

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_error_message_format(self, mock_uv, mock_make, tmp_path):
        """Should format error messages with [quality-parity] prefix."""
        makefile_content = "ruff check\n"
        uv_content = "ruff check\n"

        mock_make.read_text.return_value = makefile_content
        mock_uv.read_text.return_value = uv_content

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            main()

        stderr_output = mock_stderr.getvalue()
        for line in stderr_output.strip().split("\n"):
            assert line.startswith("[quality-parity]")

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_multiple_missing_patterns_listed(self, mock_uv, mock_make, tmp_path):
        """Should list all missing patterns in error messages."""
        makefile_content = "ruff check\n"
        uv_content = "\n".join(REQUIRED_PATTERNS)

        mock_make.read_text.return_value = makefile_content
        mock_uv.read_text.return_value = uv_content

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            main()

        stderr_output = mock_stderr.getvalue()
        assert "mypy" in stderr_output
        assert "pylint" in stderr_output
        assert "coverage run" in stderr_output
        assert "coverage report" in stderr_output


@pytest.mark.unit
class TestConstantsAndPaths:
    """Tests for module constants and path definitions."""

    def test_required_patterns_defined(self):
        """Should have all required quality check patterns."""
        assert "ruff check" in REQUIRED_PATTERNS
        assert "mypy" in REQUIRED_PATTERNS
        assert "pylint" in REQUIRED_PATTERNS
        assert "coverage run" in REQUIRED_PATTERNS
        assert "coverage report" in REQUIRED_PATTERNS

    def test_node_patterns_defined(self):
        """Should have Node-specific patterns."""
        assert "pnpm --filter api-node lint" in NODE_PATTERNS
        assert "pnpm --filter api-node typecheck" in NODE_PATTERNS

    def test_patterns_are_lists(self):
        """Patterns should be defined as lists."""
        assert isinstance(REQUIRED_PATTERNS, list)
        assert isinstance(NODE_PATTERNS, list)

    def test_patterns_non_empty(self):
        """Pattern lists should not be empty."""
        assert len(REQUIRED_PATTERNS) > 0
        assert len(NODE_PATTERNS) > 0


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_empty_files(self, mock_uv, mock_make, tmp_path):
        """Should handle empty files gracefully."""
        mock_make.read_text.return_value = ""
        mock_uv.read_text.return_value = ""

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main()

        assert result == 1
        stderr_output = mock_stderr.getvalue()
        assert "Makefile missing:" in stderr_output
        assert "uv task missing:" in stderr_output

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_patterns_in_comments(self, mock_uv, mock_make, tmp_path):
        """Should find patterns even if they appear in comments."""
        content = "# ruff check is used here\n# mypy\n# pylint\n# coverage run\n# coverage report\n"

        mock_make.read_text.return_value = content
        mock_uv.read_text.return_value = content

        with patch("sys.stdout", new_callable=StringIO):
            result = main()

        assert result == 0

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_patterns_with_extra_whitespace(self, mock_uv, mock_make, tmp_path):
        """Should match patterns with surrounding whitespace."""
        content = "    ruff check    \n\tmypy\t\n  pylint  \n  coverage run  \n  coverage report  \n"

        mock_make.read_text.return_value = content
        mock_uv.read_text.return_value = content

        with patch("sys.stdout", new_callable=StringIO):
            result = main()

        assert result == 0

    def test_assert_contains_preserves_order(self, tmp_path):
        """Should preserve order of missing patterns."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        patterns = ["first", "second", "third"]
        missing = assert_contains(test_file, patterns)

        assert missing == patterns

    @patch("check_quality_parity.MAKEFILE")
    @patch("check_quality_parity.UV_TASK")
    def test_node_partial_match_in_makefile(self, mock_uv, mock_make, tmp_path):
        """Should handle when only some Node patterns are in Makefile."""
        makefile_content = "\n".join(
            REQUIRED_PATTERNS + ["pnpm --filter api-node lint"]
        )
        uv_content = "\n".join(REQUIRED_PATTERNS)

        mock_make.read_text.return_value = makefile_content
        mock_uv.read_text.return_value = uv_content

        with patch("sys.stdout", new_callable=StringIO):
            result = main()

        # Should succeed because not all Node patterns are in Makefile
        # (makefile_node_missing will not be empty)
        assert result == 0
