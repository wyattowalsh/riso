# Shared Validation Utilities - Usage Guide

This document provides examples of how to use the shared validation utilities in `/scripts/lib/validation.py` for CI validation scripts.

## Quick Start

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.validation import (
    ValidationResult,
    load_yaml_file,
    validate_path_exists,
    validate_required_fields,
    print_validation_summary,
)
```

## Common Use Cases

### 1. Loading YAML Files with Error Handling

**Before:**
```python
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
except yaml.YAMLError as e:
    errors.append(f"YAML parsing error: {e}")
    return False, errors
except Exception as e:
    errors.append(f"Validation error: {e}")
    return False, errors
```

**After:**
```python
result = load_yaml_file(config_path)
if not result["success"]:
    errors.append(f"config.yml: {result['error']}")
    return False, errors

config = result["data"]
```

### 2. Validating Required Fields

**Before:**
```python
if 'name' not in config:
    errors.append("config.yml: Missing 'name' field")
if 'version' not in config:
    errors.append("config.yml: Missing 'version' field")
```

**After:**
```python
field_errors = validate_required_fields(
    config,
    ['name', 'version'],
    context="config.yml"
)
errors.extend(field_errors)
```

### 3. Validating Paths

**Before:**
```python
if not directory.exists():
    print(f"Error: Directory not found: {directory}", file=sys.stderr)
    return 1

if not directory.is_dir():
    print(f"Error: Not a directory: {directory}", file=sys.stderr)
    return 1
```

**After:**
```python
path_result = validate_path_exists(directory, must_be_dir=True)
if not path_result["valid"]:
    print(f"Directory validation failed:", file=sys.stderr)
    for error in path_result["errors"]:
        print(f"  - {error}", file=sys.stderr)
    return 1
```

### 4. Creating Validation Results

**Before:**
```python
return {
    "file": str(filepath),
    "passed": len(errors) == 0,
    "errors": errors,
    "warnings": warnings,
}
```

**After:**
```python
return create_validation_result(
    filepath,
    errors=errors,
    warnings=warnings
)
```

### 5. Printing Validation Summaries

**Before:**
```python
print(f"\n{'=' * 70}")
print("Validation Summary")
print(f"{'=' * 70}")
print(f"Total files: {len(results)}")
print(f"Passed: {sum(1 for r in results if r['valid'])}")
# ... more manual formatting
```

**After:**
```python
print_validation_summary(
    results,
    title="Validation Summary",
    show_warnings=True
)
```

## Migration Checklist

When migrating a validation script to use shared utilities:

- [ ] Add import statements for shared utilities
- [ ] Replace manual YAML loading with `load_yaml_file()`
- [ ] Replace field validation loops with `validate_required_fields()`
- [ ] Replace path existence checks with `validate_path_exists()`
- [ ] Use `create_validation_result()` for consistent result structures
- [ ] Replace custom summary printing with `print_validation_summary()` or `print_error_list()`
- [ ] Test the script to ensure it works correctly

## Scripts to Migrate

The following scripts can benefit from using the shared utilities:

1. ✅ **validate_release_configs.py** - Already migrated (reference implementation)
2. ⏳ **validate_dockerfiles.py** - Can use `validate_path_exists()`, `print_validation_summary()`
3. ⏳ **validate_workflows.py** - Can use validation result types and summary printing
4. ⏳ **validate_saas_combinations.py** - Can use result reporting utilities

## Examples

See `/scripts/ci/validate_release_configs.py` for a complete example of a script using the shared validation utilities.
