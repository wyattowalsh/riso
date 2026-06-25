# Template Utilities

Copier template helpers for loading configuration, validating answers, and running operations.

```{eval-rst}
.. automodule:: riso.template
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Overview

The `riso.template` module provides Python APIs used by the `riso` CLI and maintainer automation:

- Load `copier.yml` and prompt definitions
- Merge defaults and validate answers
- List sample variants and module catalog
- Run Copier copy, update, and recopy operations

For path resolution from arbitrary environments, prefer `riso.core.paths` or the CLI (`riso template path`).

## Template paths (checkout)

When running from a repository checkout, helpers default to the local `template/` and `samples/` directories:

```python
from riso.template import get_template_path, get_samples_path

template_dir = get_template_path()
samples_dir = get_samples_path()
```

## Configuration and prompts

```python
from riso.template import load_copier_config, get_prompts, get_defaults

config = load_copier_config(template_dir)
prompts = get_prompts(template_dir)
defaults = get_defaults(template_dir, project_name="My App")
```

## Validation

```python
from riso.template import validate_answers

result = validate_answers({"project_name": "My App"}, template_dir)
if not result.valid:
    print(result.errors)
print(result.warnings)
```

## Sample variants and catalog

```python
from riso.template import list_sample_variants, get_module_catalog

variants = list_sample_variants(samples_dir)
catalog = get_module_catalog(template_dir)
```

## Integration

The template module integrates with:

- {py:mod}`riso.cli` — Agent-native CLI for Copier operations
- {py:mod}`riso.core` — Shared errors, validation, paths, and diff utilities
