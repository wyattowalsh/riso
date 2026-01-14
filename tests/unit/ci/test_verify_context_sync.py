"""Unit tests for verify_context_sync.py"""

import hashlib
import pytest
from unittest.mock import patch

from verify_context_sync import file_digest, collect_digests, main


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestFileDigest:
    """Tests for file_digest function."""

    def test_digest_empty_file(self, tmp_path):
        """Should compute SHA256 hash for empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_bytes(b"")

        digest = file_digest(test_file)
        expected = hashlib.sha256(b"").hexdigest()
        assert digest == expected

    def test_digest_simple_content(self, tmp_path):
        """Should compute correct SHA256 hash for simple content."""
        test_file = tmp_path / "test.txt"
        content = b"Hello, World!"
        test_file.write_bytes(content)

        digest = file_digest(test_file)
        expected = hashlib.sha256(content).hexdigest()
        assert digest == expected

    def test_digest_binary_content(self, tmp_path):
        """Should handle binary content correctly."""
        test_file = tmp_path / "binary.bin"
        content = bytes(range(256))
        test_file.write_bytes(content)

        digest = file_digest(test_file)
        expected = hashlib.sha256(content).hexdigest()
        assert digest == expected

    def test_digest_multiline_content(self, tmp_path):
        """Should compute hash for multiline content."""
        test_file = tmp_path / "multiline.txt"
        content = b"Line 1\nLine 2\nLine 3\n"
        test_file.write_bytes(content)

        digest = file_digest(test_file)
        expected = hashlib.sha256(content).hexdigest()
        assert digest == expected

    def test_digest_different_files_different_hashes(self, tmp_path):
        """Different file contents should produce different hashes."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_bytes(b"content1")
        file2.write_bytes(b"content2")

        digest1 = file_digest(file1)
        digest2 = file_digest(file2)
        assert digest1 != digest2

    def test_digest_identical_content_same_hash(self, tmp_path):
        """Identical content should produce the same hash."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = b"identical content"
        file1.write_bytes(content)
        file2.write_bytes(content)

        digest1 = file_digest(file1)
        digest2 = file_digest(file2)
        assert digest1 == digest2


@pytest.mark.unit
class TestCollectDigests:
    """Tests for collect_digests function."""

    def test_collect_empty_directory(self, tmp_path):
        """Should return empty dict for empty directory."""
        digests = collect_digests(tmp_path)
        assert digests == {}

    def test_collect_single_file(self, tmp_path):
        """Should collect digest for single file."""
        test_file = tmp_path / "single.txt"
        test_file.write_bytes(b"content")

        digests = collect_digests(tmp_path)
        assert len(digests) == 1
        assert "single.txt" in digests
        assert digests["single.txt"] == hashlib.sha256(b"content").hexdigest()

    def test_collect_multiple_files(self, tmp_path):
        """Should collect digests for multiple files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.md"
        file1.write_bytes(b"content1")
        file2.write_bytes(b"content2")
        file3.write_bytes(b"content3")

        digests = collect_digests(tmp_path)
        assert len(digests) == 3
        assert "file1.txt" in digests
        assert "file2.txt" in digests
        assert "file3.md" in digests

    def test_collect_ignores_subdirectories(self, tmp_path):
        """Should ignore subdirectories and only process files."""
        file1 = tmp_path / "file.txt"
        file1.write_bytes(b"content")

        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file2 = subdir / "nested.txt"
        file2.write_bytes(b"nested")

        digests = collect_digests(tmp_path)
        assert len(digests) == 1
        assert "file.txt" in digests
        assert "nested.txt" not in digests

    def test_collect_sorted_order(self, tmp_path):
        """Should collect files in sorted order."""
        # Create files in non-alphabetical order
        (tmp_path / "z_file.txt").write_bytes(b"z")
        (tmp_path / "a_file.txt").write_bytes(b"a")
        (tmp_path / "m_file.txt").write_bytes(b"m")

        digests = collect_digests(tmp_path)
        keys = list(digests.keys())
        assert keys == ["a_file.txt", "m_file.txt", "z_file.txt"]

    def test_collect_various_extensions(self, tmp_path):
        """Should handle files with various extensions."""
        (tmp_path / "file.txt").write_bytes(b"txt")
        (tmp_path / "file.md").write_bytes(b"md")
        (tmp_path / "file.json").write_bytes(b"json")
        (tmp_path / "file").write_bytes(b"no_ext")

        digests = collect_digests(tmp_path)
        assert len(digests) == 4
        assert all(
            filename in digests
            for filename in ["file.txt", "file.md", "file.json", "file"]
        )


@pytest.mark.unit
class TestMainFunction:
    """Tests for main function."""

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_source_directory_missing(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should exit with error if source directory is missing."""
        # Set up fake directories
        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", tmp_path / "nonexistent")
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", tmp_path / "template")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_with("Source context directory missing.")

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_template_directory_missing(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should exit with error if template directory is missing."""
        # Create source but not template
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr(
            "verify_context_sync.TEMPLATE_DIR", tmp_path / "nonexistent"
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_with("Template context directory missing.")

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_directories_in_sync(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should log success when directories are in sync."""
        # Create matching directories
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        # Create identical files
        (source_dir / "file1.txt").write_bytes(b"content")
        (template_dir / "file1.txt").write_bytes(b"content")

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        main()

        mock_logger.info.assert_called_with("Context directories are in sync.")

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_missing_files_in_template(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should report files missing from template."""
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        # File in source but not template
        (source_dir / "missing.txt").write_bytes(b"content")

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_with(
            "Missing context files in template: missing.txt"
        )

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_extra_files_in_template(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should report unexpected files in template."""
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        # File in template but not source
        (template_dir / "extra.txt").write_bytes(b"content")

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_with(
            "Unexpected context files in template: extra.txt"
        )

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_content_mismatch(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should report content mismatches."""
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        # Same filename, different content
        (source_dir / "file.txt").write_bytes(b"source content")
        (template_dir / "file.txt").write_bytes(b"template content")

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_with("Content mismatches detected: file.txt")

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_multiple_errors(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should report all error types when multiple issues exist."""
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        # Missing file
        (source_dir / "missing.txt").write_bytes(b"content")

        # Extra file
        (template_dir / "extra.txt").write_bytes(b"content")

        # Mismatched file
        (source_dir / "mismatch.txt").write_bytes(b"source")
        (template_dir / "mismatch.txt").write_bytes(b"template")

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        # Should have called error 3 times (missing, extra, mismatch)
        assert mock_logger.error.call_count == 3

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_multiple_missing_files_sorted(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should report multiple missing files in sorted order."""
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        # Multiple files in source but not template
        (source_dir / "z_file.txt").write_bytes(b"content")
        (source_dir / "a_file.txt").write_bytes(b"content")
        (source_dir / "m_file.txt").write_bytes(b"content")

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_with(
            "Missing context files in template: a_file.txt, m_file.txt, z_file.txt"
        )

    @patch("verify_context_sync.logger")
    @patch("verify_context_sync.configure_logging")
    def test_main_configures_logging(
        self, mock_config, mock_logger, tmp_path, monkeypatch
    ):
        """Should configure logging on startup."""
        source_dir = tmp_path / "source"
        template_dir = tmp_path / "template"
        source_dir.mkdir()
        template_dir.mkdir()

        monkeypatch.setattr("verify_context_sync.SOURCE_DIR", source_dir)
        monkeypatch.setattr("verify_context_sync.TEMPLATE_DIR", template_dir)

        main()

        mock_config.assert_called_once()
