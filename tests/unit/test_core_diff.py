"""Unit tests for riso.core.diff FileDiff."""

from __future__ import annotations

import pytest

from riso.core.diff import FileDiff, FileStatus

pytestmark = pytest.mark.unit


def test_filediff_added_empty() -> None:
    diff = FileDiff(path="new.txt", status=FileStatus.ADDED, new_content=None)
    assert "New file: new.txt (empty)" in diff.get_unified_diff()


def test_filediff_added_with_content() -> None:
    diff = FileDiff(
        path="new.txt",
        status=FileStatus.ADDED,
        new_content="hello\nworld\n",
    )
    output = diff.get_unified_diff()
    assert output.startswith("New file: new.txt\n")
    assert "hello" in output


def test_filediff_modified_unified_diff() -> None:
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
    diff = FileDiff(
        path="gone.txt",
        status=FileStatus.DELETED,
        old_content="bye\n",
    )
    output = diff.get_unified_diff()
    assert "Deleted file: gone.txt" in output
    assert "bye" in output


def test_filediff_binary() -> None:
    diff = FileDiff(
        path="image.png",
        status=FileStatus.ADDED,
        is_binary=True,
    )
    assert diff.get_unified_diff() == "Binary file image.png added"


def test_filediff_unchanged() -> None:
    diff = FileDiff(path="same.txt", status=FileStatus.UNCHANGED)
    assert diff.get_unified_diff() == "Unchanged: same.txt"
