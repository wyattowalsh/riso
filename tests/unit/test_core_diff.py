"""Unit tests for riso.core.diff FileDiff."""

from __future__ import annotations

import pytest

from riso.core.diff import FileDiff, FileStatus

pytestmark = pytest.mark.unit


def test_filediff_added_empty() -> None:
    """Describe added files without content as empty."""
    diff = FileDiff(path="new.txt", status=FileStatus.ADDED, new_content=None)
    assert "New file: new.txt (empty)" in diff.get_unified_diff()


def test_filediff_added_with_content() -> None:
    """Include the new file name and content in an added-file diff."""
    diff = FileDiff(
        path="new.txt",
        status=FileStatus.ADDED,
        new_content="hello\nworld\n",
    )
    output = diff.get_unified_diff()
    assert output.startswith("New file: new.txt\n")
    assert "hello" in output


def test_filediff_modified_unified_diff() -> None:
    """Include unified diff headers and changed lines for modified files."""
    diff = FileDiff(
        path="app.py",
        status=FileStatus.MODIFIED,
        old_content="a = 1\n",
        new_content="a = 2\n",
    )
    output = diff.get_unified_diff()
    assert "--- a/app.py" in output or "+++ b/app.py" in output
    assert "-a = 1" in output
    assert "+a = 2" in output


def test_filediff_deleted() -> None:
    """Include the removed file name and its previous content."""
    diff = FileDiff(
        path="gone.txt",
        status=FileStatus.DELETED,
        old_content="bye\n",
    )
    output = diff.get_unified_diff()
    assert "Deleted file: gone.txt" in output
    assert "bye" in output


def test_filediff_binary() -> None:
    """Describe binary additions without attempting a textual diff."""
    diff = FileDiff(
        path="image.png",
        status=FileStatus.ADDED,
        is_binary=True,
    )
    assert diff.get_unified_diff() == "Binary file image.png added"


def test_filediff_unchanged() -> None:
    """Report an unchanged file without a patch."""
    diff = FileDiff(path="same.txt", status=FileStatus.UNCHANGED)
    assert diff.get_unified_diff() == "Unchanged: same.txt"
