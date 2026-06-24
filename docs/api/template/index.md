# Template Utilities

Template discovery and metadata utilities.

```{eval-rst}
.. automodule:: riso.template
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Overview

The template module provides utilities for working with the Riso template:

- Template location and discovery
- Version information
- Metadata extraction
- Path resolution

## Template Discovery

```python
from riso.template import get_template_path, get_template_metadata

# Get template directory
template_dir = get_template_path()

# Get template metadata
metadata = get_template_metadata()
print(f"Template version: {metadata['version']}")
print(f"Template description: {metadata['description']}")
```

## Path Utilities

```python
from riso.template import resolve_template_path

# Resolve paths relative to template root
copier_yml = resolve_template_path("copier.yml")
files_dir = resolve_template_path("files")
```

## Version Information

```python
from riso.template import get_template_version, is_development_version

# Get template version
version = get_template_version()

# Check if development version
if is_development_version():
    print("Running development version")
```

## Integration

The template module integrates with:

- {py:mod}`riso.mcp.tools.copier_api` - Template rendering
- {py:mod}`riso.mcp.resources.templates` - Template metadata resources
- {py:mod}`riso.mcp.resources.samples` - Sample variant discovery
