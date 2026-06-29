"""Unit tests for scripts.lib.validation module."""

from io import StringIO
import pytest


pytestmark = pytest.mark.usefixtures("lib_path")


@pytest.fixture
def capture_logs():
    """Fixture to capture loguru logs."""
    from loguru import logger

    # Create a string buffer to capture logs
    log_buffer = StringIO()

    # Add a sink that writes to our buffer
    handler_id = logger.add(log_buffer, format="{message}", level="DEBUG")

    yield log_buffer

    # Clean up
    logger.remove(handler_id)


@pytest.mark.unit
class TestLoadYAMLFile:
    """Tests for load_yaml_file function."""

    def test_load_valid_yaml_file(self, temp_dir):
        """Should successfully load a valid YAML file."""
        from validation import load_yaml_file

        yaml_file = temp_dir / "config.yml"
        yaml_file.write_text("""
name: test-config
version: 1.0
settings:
  enabled: true
  timeout: 30
""")

        result = load_yaml_file(yaml_file)

        assert result["success"] is True
        assert result["error"] is None
        assert result["data"] is not None
        assert result["data"]["name"] == "test-config"
        assert result["data"]["version"] == 1.0
        assert result["data"]["settings"]["enabled"] is True

    def test_load_nonexistent_file(self, temp_dir):
        """Should return error for non-existent file."""
        from validation import load_yaml_file

        result = load_yaml_file(temp_dir / "nonexistent.yml")

        assert result["success"] is False
        assert result["data"] is None
        assert "File not found" in result["error"]

    def test_load_directory_instead_of_file(self, temp_dir):
        """Should return error when path is a directory."""
        from validation import load_yaml_file

        directory = temp_dir / "subdir"
        directory.mkdir()

        result = load_yaml_file(directory)

        assert result["success"] is False
        assert result["data"] is None
        assert "not a file" in result["error"]

    def test_load_empty_yaml_file(self, temp_dir):
        """Should return error for empty YAML file."""
        from validation import load_yaml_file

        yaml_file = temp_dir / "empty.yml"
        yaml_file.write_text("")

        result = load_yaml_file(yaml_file)

        assert result["success"] is False
        assert result["data"] is None
        assert "empty" in result["error"].lower() or "null" in result["error"].lower()

    def test_load_yaml_with_null_content(self, temp_dir):
        """Should return error for YAML file containing only null."""
        from validation import load_yaml_file

        yaml_file = temp_dir / "null.yml"
        yaml_file.write_text("null")

        result = load_yaml_file(yaml_file)

        assert result["success"] is False
        assert result["data"] is None
        assert "null" in result["error"].lower() or "empty" in result["error"].lower()

    def test_load_yaml_with_invalid_syntax(self, temp_dir):
        """Should return error for YAML with syntax errors."""
        from validation import load_yaml_file

        yaml_file = temp_dir / "invalid.yml"
        yaml_file.write_text("""
name: test
  invalid indentation:
    - item
""")

        result = load_yaml_file(yaml_file)

        assert result["success"] is False
        assert result["data"] is None
        assert (
            "parsing error" in result["error"].lower()
            or "yaml" in result["error"].lower()
        )

    def test_load_yaml_with_non_dict_root(self, temp_dir):
        """Should return error when YAML root is not a dictionary."""
        from validation import load_yaml_file

        yaml_file = temp_dir / "list.yml"
        yaml_file.write_text("""
- item1
- item2
- item3
""")

        result = load_yaml_file(yaml_file)

        assert result["success"] is False
        assert result["data"] is None
        assert "Expected YAML dictionary" in result["error"]
        assert "list" in result["error"]

    @pytest.mark.parametrize(
        "encoding,should_succeed",
        [
            ("utf-8", True),
            ("latin-1", False),
        ],
    )
    def test_load_yaml_with_different_encodings(
        self, temp_dir, encoding, should_succeed
    ):
        """Should handle different file encodings."""
        from validation import load_yaml_file

        yaml_file = temp_dir / f"encoding_{encoding}.yml"
        content = "name: test\nvalue: 123"

        if encoding == "utf-8":
            yaml_file.write_text(content, encoding=encoding)
        else:
            # Write with non-UTF-8 encoding that contains invalid UTF-8 bytes
            yaml_file.write_bytes(b"name: test\nvalue: \xff\xfe")

        result = load_yaml_file(yaml_file)

        if should_succeed:
            assert result["success"] is True
            assert result["data"]["name"] == "test"
        else:
            assert result["success"] is False
            assert result["data"] is None

    def test_load_yaml_with_unexpected_exception(self, temp_dir, monkeypatch):
        """Should handle unexpected exceptions during file loading."""
        from validation import load_yaml_file

        yaml_file = temp_dir / "test.yml"
        yaml_file.write_text("name: test")

        def mock_open(*args, **kwargs):
            raise OSError("Unexpected error")

        monkeypatch.setattr("builtins.open", mock_open)

        result = load_yaml_file(yaml_file)

        assert result["success"] is False
        assert result["data"] is None
        assert "Unexpected error" in result["error"]


@pytest.mark.unit
class TestValidatePathExists:
    """Tests for validate_path_exists function."""

    def test_validate_existing_file(self, temp_dir):
        """Should pass validation for existing file."""
        from validation import validate_path_exists

        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        result = validate_path_exists(test_file)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["file"] == str(test_file)

    def test_validate_nonexistent_path(self, temp_dir):
        """Should fail validation for non-existent path."""
        from validation import validate_path_exists

        result = validate_path_exists(temp_dir / "nonexistent.txt")

        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "does not exist" in result["errors"][0]

    def test_validate_must_be_file_with_file(self, temp_dir):
        """Should pass when path is file and must_be_file=True."""
        from validation import validate_path_exists

        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        result = validate_path_exists(test_file, must_be_file=True)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_must_be_file_with_directory(self, temp_dir):
        """Should fail when path is directory but must_be_file=True."""
        from validation import validate_path_exists

        subdir = temp_dir / "subdir"
        subdir.mkdir()

        result = validate_path_exists(subdir, must_be_file=True)

        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "not a file" in result["errors"][0]

    def test_validate_must_be_dir_with_directory(self, temp_dir):
        """Should pass when path is directory and must_be_dir=True."""
        from validation import validate_path_exists

        subdir = temp_dir / "subdir"
        subdir.mkdir()

        result = validate_path_exists(subdir, must_be_dir=True)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_must_be_dir_with_file(self, temp_dir):
        """Should fail when path is file but must_be_dir=True."""
        from validation import validate_path_exists

        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        result = validate_path_exists(test_file, must_be_dir=True)

        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "not a directory" in result["errors"][0]

    @pytest.mark.parametrize(
        "must_be_file,must_be_dir",
        [
            (False, False),
            (True, False),
            (False, True),
        ],
    )
    def test_validate_path_type_combinations(self, temp_dir, must_be_file, must_be_dir):
        """Should handle different combinations of type requirements."""
        from validation import validate_path_exists

        # Create both a file and directory
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        test_dir = temp_dir / "subdir"
        test_dir.mkdir()

        # Test with file
        file_result = validate_path_exists(
            test_file, must_be_file=must_be_file, must_be_dir=must_be_dir
        )
        if must_be_file or not must_be_dir:
            assert file_result["valid"] is True
        else:
            assert file_result["valid"] is False

        # Test with directory
        dir_result = validate_path_exists(
            test_dir, must_be_file=must_be_file, must_be_dir=must_be_dir
        )
        if must_be_dir or not must_be_file:
            assert dir_result["valid"] is True
        else:
            assert dir_result["valid"] is False


@pytest.mark.unit
class TestValidateRequiredFields:
    """Tests for validate_required_fields function."""

    def test_all_required_fields_present(self):
        """Should return no errors when all required fields present."""
        from validation import validate_required_fields

        data = {"name": "test", "version": "1.0", "enabled": True}
        required = ["name", "version", "enabled"]

        errors = validate_required_fields(data, required)

        assert errors == []

    def test_missing_single_required_field(self):
        """Should return error for single missing field."""
        from validation import validate_required_fields

        data = {"name": "test"}
        required = ["name", "version"]

        errors = validate_required_fields(data, required)

        assert len(errors) == 1
        assert "version" in errors[0]
        assert "Missing required field" in errors[0]

    def test_missing_multiple_required_fields(self):
        """Should return errors for all missing fields."""
        from validation import validate_required_fields

        data = {"name": "test"}
        required = ["name", "version", "author", "license"]

        errors = validate_required_fields(data, required)

        assert len(errors) == 3
        assert any("version" in e for e in errors)
        assert any("author" in e for e in errors)
        assert any("license" in e for e in errors)

    def test_empty_data_dict(self):
        """Should return errors for all required fields when data is empty."""
        from validation import validate_required_fields

        data = {}
        required = ["field1", "field2"]

        errors = validate_required_fields(data, required)

        assert len(errors) == 2

    def test_empty_required_list(self):
        """Should return no errors when no fields required."""
        from validation import validate_required_fields

        data = {"name": "test"}
        required = []

        errors = validate_required_fields(data, required)

        assert errors == []

    def test_context_included_in_errors(self):
        """Should include context string in error messages."""
        from validation import validate_required_fields

        data = {"name": "test"}
        required = ["name", "version"]
        context = "config.yml"

        errors = validate_required_fields(data, required, context=context)

        assert len(errors) == 1
        assert context in errors[0]
        assert errors[0].startswith(f"{context}:")

    def test_context_empty_string(self):
        """Should handle empty context string."""
        from validation import validate_required_fields

        data = {}
        required = ["field"]
        context = ""

        errors = validate_required_fields(data, required, context=context)

        assert len(errors) == 1
        assert not errors[0].startswith(":")

    @pytest.mark.parametrize("field_value", [None, "", 0, False, []])
    def test_field_with_falsy_values(self, field_value):
        """Should consider field present even with falsy values."""
        from validation import validate_required_fields

        data = {"field": field_value}
        required = ["field"]

        errors = validate_required_fields(data, required)

        assert errors == []


@pytest.mark.unit
class TestCreateValidationResult:
    """Tests for create_validation_result function."""

    def test_create_result_with_no_errors(self, temp_dir):
        """Should create valid result when no errors."""
        from validation import create_validation_result

        result = create_validation_result(temp_dir / "test.yml", errors=[])

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_create_result_with_errors(self, temp_dir):
        """Should create invalid result when errors present."""
        from validation import create_validation_result

        errors = ["Error 1", "Error 2"]
        result = create_validation_result(temp_dir / "test.yml", errors=errors)

        assert result["valid"] is False
        assert result["errors"] == errors
        assert result["warnings"] == []

    def test_create_result_with_warnings(self, temp_dir):
        """Should include warnings in result."""
        from validation import create_validation_result

        warnings = ["Warning 1", "Warning 2"]
        result = create_validation_result(
            temp_dir / "test.yml", errors=[], warnings=warnings
        )

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == warnings

    def test_create_result_with_errors_and_warnings(self, temp_dir):
        """Should handle both errors and warnings."""
        from validation import create_validation_result

        errors = ["Error"]
        warnings = ["Warning"]
        result = create_validation_result(
            temp_dir / "test.yml", errors=errors, warnings=warnings
        )

        assert result["valid"] is False
        assert result["errors"] == errors
        assert result["warnings"] == warnings

    def test_create_result_with_string_path(self):
        """Should accept string path instead of Path object."""
        from validation import create_validation_result

        result = create_validation_result("/path/to/file.yml", errors=[])

        assert result["file"] == "/path/to/file.yml"
        assert result["valid"] is True


@pytest.mark.unit
class TestPrintValidationSummary:
    """Tests for print_validation_summary function."""

    def test_print_summary_all_passed(self, capture_logs):
        """Should print summary for all passing validations."""
        from validation import print_validation_summary, ValidationResult

        results = [
            ValidationResult(file="test1.yml", valid=True, errors=[], warnings=[]),
            ValidationResult(file="test2.yml", valid=True, errors=[], warnings=[]),
        ]

        print_validation_summary(results)

        log_output = capture_logs.getvalue()
        assert "Total files: 2" in log_output
        assert "Passed: 2" in log_output
        assert "Failed: 0" in log_output
        assert "PASS" in log_output

    def test_print_summary_with_failures(self, capture_logs):
        """Should print summary with failure details."""
        from validation import print_validation_summary, ValidationResult

        results = [
            ValidationResult(file="pass.yml", valid=True, errors=[], warnings=[]),
            ValidationResult(
                file="fail.yml", valid=False, errors=["Error 1", "Error 2"], warnings=[]
            ),
        ]

        print_validation_summary(results)

        log_output = capture_logs.getvalue()
        assert "Total files: 2" in log_output
        assert "Passed: 1" in log_output
        assert "Failed: 1" in log_output
        assert "FAIL" in log_output
        assert "Error 1" in log_output
        assert "Error 2" in log_output

    def test_print_summary_with_warnings(self, capture_logs):
        """Should print warnings when show_warnings=True."""
        from validation import print_validation_summary, ValidationResult

        results = [
            ValidationResult(
                file="test.yml", valid=True, errors=[], warnings=["Warning 1"]
            ),
        ]

        print_validation_summary(results, show_warnings=True)

        log_output = capture_logs.getvalue()
        assert "Warning 1" in log_output

    def test_print_summary_hide_warnings(self, capture_logs):
        """Should not print warnings when show_warnings=False."""
        from validation import print_validation_summary, ValidationResult

        results = [
            ValidationResult(
                file="test.yml", valid=True, errors=[], warnings=["Warning 1"]
            ),
        ]

        print_validation_summary(results, show_warnings=False)

        log_output = capture_logs.getvalue()
        assert "Warning 1" not in log_output

    def test_print_summary_custom_title(self, capture_logs):
        """Should use custom title when provided."""
        from validation import print_validation_summary, ValidationResult

        results = [
            ValidationResult(file="test.yml", valid=True, errors=[], warnings=[])
        ]
        custom_title = "Custom Validation Report"

        print_validation_summary(results, title=custom_title)

        log_output = capture_logs.getvalue()
        assert custom_title in log_output

    def test_print_summary_empty_results(self, capture_logs):
        """Should handle empty results list."""
        from validation import print_validation_summary

        print_validation_summary([])

        log_output = capture_logs.getvalue()
        assert "Total files: 0" in log_output
        assert "Passed: 0" in log_output
        assert "Failed: 0" in log_output


@pytest.mark.unit
class TestCheckYAMLDependency:
    """Tests for check_yaml_dependency function."""

    def test_yaml_installed(self):
        """Should return True when PyYAML is installed."""
        from validation import check_yaml_dependency

        result = check_yaml_dependency()

        # Since we're running tests, PyYAML should be installed
        assert result is True

    def test_yaml_not_installed(self, monkeypatch):
        """Should return False when PyYAML is not available."""
        from validation import check_yaml_dependency

        # Mock the import to raise ImportError
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        result = check_yaml_dependency()

        assert result is False


@pytest.mark.unit
class TestPrintErrorList:
    """Tests for print_error_list function."""

    def test_print_errors(self, capture_logs):
        """Should print formatted error list."""
        from validation import print_error_list

        errors = ["Error 1", "Error 2", "Error 3"]

        print_error_list(errors)

        log_output = capture_logs.getvalue()
        assert "Error 1" in log_output
        assert "Error 2" in log_output
        assert "Error 3" in log_output

    def test_print_errors_custom_title(self, capture_logs):
        """Should use custom title when provided."""
        from validation import print_error_list

        errors = ["Error"]
        custom_title = "Custom Error Report"

        print_error_list(errors, title=custom_title)

        log_output = capture_logs.getvalue()
        assert custom_title in log_output

    def test_print_errors_empty_list(self, capture_logs):
        """Should not print anything for empty error list."""
        from validation import print_error_list

        print_error_list([])

        # No logs should be produced for empty list
        assert capture_logs.getvalue() == ""

    def test_print_errors_single_error(self, capture_logs):
        """Should handle single error correctly."""
        from validation import print_error_list

        errors = ["Single error message"]

        print_error_list(errors)

        log_output = capture_logs.getvalue()
        assert "Single error message" in log_output
        assert "Validation Errors" in log_output


@pytest.mark.unit
class TestValidationResultType:
    """Tests for ValidationResult TypedDict structure."""

    def test_validation_result_structure(self):
        """Should create ValidationResult with all required fields."""
        from validation import ValidationResult

        result = ValidationResult(file="test.yml", valid=True, errors=[], warnings=[])

        assert result["file"] == "test.yml"
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validation_result_with_data(self):
        """Should store error and warning data correctly."""
        from validation import ValidationResult

        result = ValidationResult(
            file="config.yml",
            valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
        )

        assert result["file"] == "config.yml"
        assert result["valid"] is False
        assert len(result["errors"]) == 2
        assert len(result["warnings"]) == 1


@pytest.mark.unit
class TestYAMLLoadResultType:
    """Tests for YAMLLoadResult TypedDict structure."""

    def test_yaml_load_result_success(self):
        """Should create successful YAMLLoadResult."""
        from validation import YAMLLoadResult

        result = YAMLLoadResult(success=True, data={"key": "value"}, error=None)

        assert result["success"] is True
        assert result["data"]["key"] == "value"
        assert result["error"] is None

    def test_yaml_load_result_failure(self):
        """Should create failed YAMLLoadResult."""
        from validation import YAMLLoadResult

        result = YAMLLoadResult(success=False, data=None, error="Parse error")

        assert result["success"] is False
        assert result["data"] is None
        assert result["error"] == "Parse error"
