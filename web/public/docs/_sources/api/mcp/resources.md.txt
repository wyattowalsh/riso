# MCP Resources

Template metadata, sample variants, and module catalogs exposed as MCP resources.

## Catalog Resources

Module catalog and feature matrix.

```{eval-rst}
.. automodule:: riso.mcp.resources.catalog
   :members:
   :undoc-members:
   :show-inheritance:
```

## Sample Resources

Sample project variants and configurations.

```{eval-rst}
.. automodule:: riso.mcp.resources.samples
   :members:
   :undoc-members:
   :show-inheritance:
```

## Template Resources

Template metadata and prompt schemas.

```{eval-rst}
.. automodule:: riso.mcp.resources.templates
   :members:
   :undoc-members:
   :show-inheritance:
```

## Resource URIs

### Catalog Resources

- `catalog://modules` - Complete module catalog with feature matrix
- `catalog://samples` - Sample variant metadata

### Sample Resources

- `sample://variants` - List of available sample variants
- `sample://{variant_name}/answers` - Answers file for specific variant
- `sample://{variant_name}/render` - Rendered output for variant (if exists)

### Template Resources

- `template://prompts` - Template prompt schemas from copier.yml
- `template://defaults` - Default values for all prompts
- `template://metadata` - Template metadata (version, description, etc.)

## Usage

Resources are accessed via the MCP protocol:

```python
# List available sample variants
variants = await read_resource("sample://variants")

# Get template prompts
prompts = await read_resource("template://prompts")

# Get module catalog
catalog = await read_resource("catalog://modules")
```
