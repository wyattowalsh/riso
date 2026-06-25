"""Diff and preview tools for Copier operations.

Provides functionality to preview changes before applying them,
using a temporary directory approach to generate and compare files.
"""

from __future__ import annotations

import difflib
import logging
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FileStatus(Enum):
    """Status of a file in diff."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


@dataclass
class FileDiff:
    """Diff for a single file."""

    path: str
    status: FileStatus
    old_content: str | None = None
    new_content: str | None = None
    is_binary: bool = False

    def get_unified_diff(self, context_lines: int = 3) -> str:
        """Get unified diff format.

        Parameters
        ----------
        context_lines
            Number of context lines to show around changes

        Returns
        -------
        str
            Unified diff output or binary file indication
        """
        if self.is_binary:
            status_text = "added" if self.status == FileStatus.ADDED else "modified"
            return f"Binary file {self.path} {status_text}"

        if self.status == FileStatus.ADDED:
            if not self.new_content:
                return f"New file: {self.path} (empty)"
            lines = self.new_content.splitlines(keepends=True)
            return f"New file: {self.path}\n{''.join(lines)}"

        if self.status == FileStatus.DELETED:
            if not self.old_content:
                return f"Deleted file: {self.path} (was empty)"
            lines = self.old_content.splitlines(keepends=True)
            return f"Deleted file: {self.path}\n{''.join(lines)}"

        if self.status == FileStatus.MODIFIED:
            old_lines = (self.old_content or "").splitlines(keepends=True)
            new_lines = (self.new_content or "").splitlines(keepends=True)

            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"a/{self.path}",
                tofile=f"b/{self.path}",
                lineterm="",
                n=context_lines,
            )

            return "\n".join(diff)

        return f"Unchanged: {self.path}"


@dataclass
class DiffResult:
    """Result of a diff operation."""

    files: list[FileDiff] = field(default_factory=list)
    summary: str = ""

    @property
    def added_count(self) -> int:
        """Count of added files."""
        return sum(1 for f in self.files if f.status == FileStatus.ADDED)

    @property
    def modified_count(self) -> int:
        """Count of modified files."""
        return sum(1 for f in self.files if f.status == FileStatus.MODIFIED)

    @property
    def deleted_count(self) -> int:
        """Count of deleted files."""
        return sum(1 for f in self.files if f.status == FileStatus.DELETED)

    @property
    def unchanged_count(self) -> int:
        """Count of unchanged files."""
        return sum(1 for f in self.files if f.status == FileStatus.UNCHANGED)

    def generate_summary(self) -> str:
        """Generate human-readable summary.

        Returns
        -------
        str
            Summary text describing the changes
        """
        parts = []

        if self.added_count:
            parts.append(f"{self.added_count} added")
        if self.modified_count:
            parts.append(f"{self.modified_count} modified")
        if self.deleted_count:
            parts.append(f"{self.deleted_count} deleted")
        if self.unchanged_count:
            parts.append(f"{self.unchanged_count} unchanged")

        if not parts:
            return "No changes"

        return f"Files: {', '.join(parts)}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary.

        Returns
        -------
        dict
            Serializable representation of the diff result
        """
        return {
            "summary": self.summary or self.generate_summary(),
            "added_count": self.added_count,
            "modified_count": self.modified_count,
            "deleted_count": self.deleted_count,
            "unchanged_count": self.unchanged_count,
            "files": [
                {
                    "path": f.path,
                    "status": f.status.value,
                    "is_binary": f.is_binary,
                    "diff": f.get_unified_diff() if not f.is_binary else None,
                }
                for f in self.files
            ],
        }


def is_binary_file(path: Path) -> bool:
    """Check if file is binary.

    Uses a simple heuristic: reads first 8192 bytes and checks for null bytes.

    Parameters
    ----------
    path
        Path to file to check

    Returns
    -------
    bool
        True if file appears to be binary
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except (OSError, IOError):
        return False


def compare_directories(
    dir1: Path,
    dir2: Path,
    include_unchanged: bool = False,
) -> list[FileDiff]:
    """Compare two directories recursively.

    Parameters
    ----------
    dir1
        First directory (typically the existing destination)
    dir2
        Second directory (typically the temporary generated output)
    include_unchanged
        Whether to include unchanged files in the result

    Returns
    -------
    list[FileDiff]
        List of file differences
    """
    diffs: list[FileDiff] = []

    # Get all files in both directories relative to their roots
    def get_files(directory: Path) -> set[Path]:
        if not directory.exists():
            return set()
        return {
            p.relative_to(directory)
            for p in directory.rglob("*")
            if p.is_file() and not _should_ignore(p)
        }

    files1 = get_files(dir1)
    files2 = get_files(dir2)

    # Added files (in dir2 but not dir1)
    for rel_path in sorted(files2 - files1):
        file2 = dir2 / rel_path
        is_binary = is_binary_file(file2)

        new_content = None
        if not is_binary:
            try:
                new_content = file2.read_text(encoding="utf-8", errors="replace")
            except (OSError, IOError) as e:
                logger.warning("Failed to read %s: %s", file2, e)

        diffs.append(
            FileDiff(
                path=str(rel_path),
                status=FileStatus.ADDED,
                old_content=None,
                new_content=new_content,
                is_binary=is_binary,
            )
        )

    # Deleted files (in dir1 but not dir2)
    for rel_path in sorted(files1 - files2):
        file1 = dir1 / rel_path
        is_binary = is_binary_file(file1)

        old_content = None
        if not is_binary:
            try:
                old_content = file1.read_text(encoding="utf-8", errors="replace")
            except (OSError, IOError) as e:
                logger.warning("Failed to read %s: %s", file1, e)

        diffs.append(
            FileDiff(
                path=str(rel_path),
                status=FileStatus.DELETED,
                old_content=old_content,
                new_content=None,
                is_binary=is_binary,
            )
        )

    # Modified or unchanged files (in both)
    for rel_path in sorted(files1 & files2):
        file1 = dir1 / rel_path
        file2 = dir2 / rel_path

        is_binary = is_binary_file(file1) or is_binary_file(file2)

        if is_binary:
            # For binary files, just check if they differ by size/mtime
            # or use a simple byte comparison
            try:
                content1 = file1.read_bytes()
                content2 = file2.read_bytes()
                if content1 != content2:
                    diffs.append(
                        FileDiff(
                            path=str(rel_path),
                            status=FileStatus.MODIFIED,
                            is_binary=True,
                        )
                    )
                elif include_unchanged:
                    diffs.append(
                        FileDiff(
                            path=str(rel_path),
                            status=FileStatus.UNCHANGED,
                            is_binary=True,
                        )
                    )
            except (OSError, IOError) as e:
                logger.warning("Failed to compare binary files %s: %s", rel_path, e)
        else:
            try:
                old_content = file1.read_text(encoding="utf-8", errors="replace")
                new_content = file2.read_text(encoding="utf-8", errors="replace")

                if old_content != new_content:
                    diffs.append(
                        FileDiff(
                            path=str(rel_path),
                            status=FileStatus.MODIFIED,
                            old_content=old_content,
                            new_content=new_content,
                            is_binary=False,
                        )
                    )
                elif include_unchanged:
                    diffs.append(
                        FileDiff(
                            path=str(rel_path),
                            status=FileStatus.UNCHANGED,
                            old_content=old_content,
                            new_content=new_content,
                            is_binary=False,
                        )
                    )
            except (OSError, IOError) as e:
                logger.warning("Failed to compare text files %s: %s", rel_path, e)

    return diffs


def _should_ignore(path: Path) -> bool:
    """Check if file should be ignored in diff.

    Parameters
    ----------
    path
        File path to check

    Returns
    -------
    bool
        True if file should be ignored
    """
    # Ignore common VCS and build artifacts
    ignore_patterns = {
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        "Thumbs.db",
        ".copier-answers.yml",  # Don't diff the answers file itself
    }

    path_str = str(path)
    for pattern in ignore_patterns:
        if pattern.startswith("*"):
            if path.name.endswith(pattern[1:]):
                return True
        elif pattern in path.parts or pattern in path_str:
            return True

    return False


def compute_diff(
    answers: dict[str, Any],
    destination: Path,
    template_path: Path,
    operation: str = "copy",
) -> DiffResult:
    """Compute diff between current state and what Copier would generate.

    Creates a temporary directory, runs Copier there with the same answers,
    then compares the output with the destination.

    Parameters
    ----------
    answers
        Template answers dictionary
    destination
        Target destination path
    template_path
        Path to the template
    operation
        Type of operation: "copy", "update", or "recopy"

    Returns
    -------
    DiffResult
        Diff result with all changes

    Raises
    ------
    Exception
        If Copier operation fails or comparison fails
    """
    from riso.core.answers import prepare_copier_data

    if operation not in {"copy", "update", "recopy"}:
        raise ValueError(f"Unknown operation: {operation}")

    # Create temporary directory
    with tempfile.TemporaryDirectory(prefix="riso_diff_") as tmpdir:
        temp_dest = Path(tmpdir) / "output"
        # Don't create the directory - let Copier do it

        logger.info("Computing diff for %s operation", operation)
        logger.debug("Temp directory: %s", temp_dest)

        try:
            # Run Copier in temp directory
            from copier import run_copy

            preview_answers = prepare_copier_data(answers)
            if operation in {"update", "recopy"}:
                answers_path = destination / ".copier-answers.yml"
                if answers_path.exists():
                    import yaml

                    stored = (
                        yaml.safe_load(answers_path.read_text(encoding="utf-8")) or {}
                    )
                    if isinstance(stored, dict):
                        preview_answers = prepare_copier_data(
                            {**stored, **preview_answers}
                        )

            run_copy(
                str(template_path),
                str(temp_dest),
                data=preview_answers,
                unsafe=True,
                defaults=True,
                overwrite=True,
                skip_tasks=True,
                quiet=True,
            )

            # Compare directories
            diffs = compare_directories(
                dir1=destination if destination.exists() else Path("/nonexistent"),
                dir2=temp_dest,
                include_unchanged=False,
            )

            result = DiffResult(files=diffs)
            result.summary = result.generate_summary()

            logger.info("Diff computed: %s", result.summary)
            return result

        except Exception as e:
            logger.error("Failed to compute diff: %s", e)
            raise


__all__ = [
    "FileStatus",
    "FileDiff",
    "DiffResult",
    "compute_diff",
    "compare_directories",
    "is_binary_file",
]
