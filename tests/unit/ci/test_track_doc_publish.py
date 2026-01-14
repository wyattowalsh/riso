"""Unit tests for track_doc_publish.py"""
import json
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from track_doc_publish import load_existing, main


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestLoadExisting:
    """Tests for load_existing function."""

    def test_load_existing_file_not_exists(self, tmp_path):
        """Should return empty list when file doesn't exist."""
        non_existent = tmp_path / "does_not_exist.json"
        result = load_existing(non_existent)
        assert result == []

    def test_load_existing_empty_file(self, tmp_path):
        """Should handle empty JSON array."""
        path = tmp_path / "empty.json"
        path.write_text("[]", encoding="utf-8")
        result = load_existing(path)
        assert result == []

    def test_load_existing_with_records(self, tmp_path):
        """Should load existing records correctly."""
        path = tmp_path / "records.json"
        test_data = [
            {"site": "shibuya", "status": "pass", "duration_seconds": 45.2},
            {"site": "fumadocs", "status": "fail", "duration_seconds": None}
        ]
        path.write_text(json.dumps(test_data), encoding="utf-8")

        result = load_existing(path)
        assert len(result) == 2
        assert result[0]["site"] == "shibuya"
        assert result[0]["status"] == "pass"
        assert result[1]["site"] == "fumadocs"
        assert result[1]["status"] == "fail"

    def test_load_existing_preserves_data_types(self, tmp_path):
        """Should preserve data types (str, float, None)."""
        path = tmp_path / "types.json"
        test_data = [
            {
                "site": "test",
                "status": "pass",
                "duration_seconds": 123.45,
                "notes": None
            }
        ]
        path.write_text(json.dumps(test_data), encoding="utf-8")

        result = load_existing(path)
        assert isinstance(result[0]["site"], str)
        assert isinstance(result[0]["duration_seconds"], float)
        assert result[0]["notes"] is None


@pytest.mark.unit
class TestMain:
    """Tests for main function."""

    def test_main_creates_output_directory(self, tmp_path):
        """Should create output directory if it doesn't exist."""
        output_file = tmp_path / "nested" / "dir" / "output.json"
        args = ["--site", "shibuya", "--output", str(output_file)]

        result = main(args)

        assert result == 0
        assert output_file.exists()
        assert output_file.parent.exists()

    def test_main_basic_record(self, tmp_path):
        """Should create basic record with required fields."""
        output_file = tmp_path / "output.json"
        args = ["--site", "fumadocs", "--output", str(output_file)]

        with patch('track_doc_publish.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
            result = main(args)

        assert result == 0
        data = json.loads(output_file.read_text())
        assert len(data) == 1
        assert data[0]["site"] == "fumadocs"
        assert data[0]["status"] == "unknown"  # default
        assert data[0]["duration_seconds"] is None
        assert data[0]["recorded_at"] == "2024-01-15T12:30:45+00:00"
        assert data[0]["notes"] is None

    def test_main_with_all_fields(self, tmp_path):
        """Should record all fields when provided."""
        output_file = tmp_path / "output.json"
        args = [
            "--site", "shibuya",
            "--status", "pass",
            "--duration", "67.89",
            "--notes", "Build completed successfully",
            "--output", str(output_file)
        ]

        result = main(args)

        assert result == 0
        data = json.loads(output_file.read_text())
        assert len(data) == 1
        assert data[0]["site"] == "shibuya"
        assert data[0]["status"] == "pass"
        assert data[0]["duration_seconds"] == 67.89
        assert data[0]["notes"] == "Build completed successfully"

    def test_main_appends_to_existing_records(self, tmp_path):
        """Should append to existing records, not overwrite."""
        output_file = tmp_path / "output.json"

        # First call
        args1 = ["--site", "shibuya", "--status", "pass", "--output", str(output_file)]
        main(args1)

        # Second call
        args2 = ["--site", "fumadocs", "--status", "fail", "--output", str(output_file)]
        main(args2)

        data = json.loads(output_file.read_text())
        assert len(data) == 2
        assert data[0]["site"] == "shibuya"
        assert data[0]["status"] == "pass"
        assert data[1]["site"] == "fumadocs"
        assert data[1]["status"] == "fail"

    def test_main_status_choices(self, tmp_path):
        """Should accept valid status choices."""
        output_file = tmp_path / "output.json"
        valid_statuses = ["pass", "fail", "pending", "unknown"]

        for status in valid_statuses:
            args = ["--site", "test", "--status", status, "--output", str(output_file)]
            result = main(args)
            assert result == 0

    def test_main_invalid_status_raises_error(self, tmp_path):
        """Should raise error for invalid status."""
        output_file = tmp_path / "output.json"
        args = ["--site", "test", "--status", "invalid_status", "--output", str(output_file)]

        with pytest.raises(SystemExit):
            main(args)

    def test_main_missing_required_site(self, tmp_path):
        """Should raise error when --site is missing."""
        output_file = tmp_path / "output.json"
        args = ["--output", str(output_file)]

        with pytest.raises(SystemExit):
            main(args)

    def test_main_duration_as_float(self, tmp_path):
        """Should handle duration as float."""
        output_file = tmp_path / "output.json"
        args = [
            "--site", "test",
            "--duration", "123.456",
            "--output", str(output_file)
        ]

        result = main(args)

        assert result == 0
        data = json.loads(output_file.read_text())
        assert data[0]["duration_seconds"] == 123.456

    def test_main_default_output_path(self, tmp_path, monkeypatch):
        """Should use default output path when not specified."""
        # Change to tmp directory to avoid creating files in real location
        monkeypatch.chdir(tmp_path)

        args = ["--site", "test"]
        result = main(args)

        assert result == 0
        # Default is samples/metadata/doc_publish.json
        default_path = tmp_path / "samples" / "metadata" / "doc_publish.json"
        assert default_path.exists()

    def test_main_preserves_json_formatting(self, tmp_path):
        """Should write JSON with proper indentation."""
        output_file = tmp_path / "output.json"
        args = ["--site", "test", "--output", str(output_file)]

        main(args)

        content = output_file.read_text()
        # Should be formatted with indent=2
        assert "  " in content  # Contains indentation
        assert "[\n  {" in content  # Array with indented object

    def test_main_records_timestamp_with_timezone(self, tmp_path):
        """Should record timestamp with UTC timezone."""
        output_file = tmp_path / "output.json"
        args = ["--site", "test", "--output", str(output_file)]

        main(args)

        data = json.loads(output_file.read_text())
        timestamp = data[0]["recorded_at"]
        # Should end with +00:00 for UTC
        assert timestamp.endswith("+00:00")
        # Should be valid ISO format
        parsed = datetime.fromisoformat(timestamp)
        assert parsed.tzinfo is not None

    def test_main_multiple_publishes_same_site(self, tmp_path):
        """Should allow multiple records for the same site."""
        output_file = tmp_path / "output.json"

        # Record multiple publishes for same site
        for i in range(3):
            args = [
                "--site", "shibuya",
                "--status", "pass",
                "--duration", str(30.0 + i),
                "--output", str(output_file)
            ]
            main(args)

        data = json.loads(output_file.read_text())
        assert len(data) == 3
        assert all(record["site"] == "shibuya" for record in data)
        assert data[0]["duration_seconds"] == 30.0
        assert data[1]["duration_seconds"] == 31.0
        assert data[2]["duration_seconds"] == 32.0

    def test_main_notes_with_special_characters(self, tmp_path):
        """Should handle notes with special characters."""
        output_file = tmp_path / "output.json"
        notes = "Build failed: Error in line 42. See logs at https://example.com/logs?id=123&format=json"
        args = [
            "--site", "test",
            "--notes", notes,
            "--output", str(output_file)
        ]

        result = main(args)

        assert result == 0
        data = json.loads(output_file.read_text())
        assert data[0]["notes"] == notes
