# Content Transformation API

**Feature**: 018-docs-sites-overhaul  
**Version**: 1.0  
**Date**: 2025-11-02

## Overview

The Content Transformation API defines interfaces for converting documentation content between formats (Markdown ↔ MDX ↔ RST) while preserving semantic meaning and handling framework-specific extensions.

## Core Interface

### ContentTransformer

Main transformation class for converting between documentation formats.

```python
from typing import Dict, Any, Optional
from enum import Enum

class ContentFormat(Enum):
    """Supported documentation content formats."""
    MARKDOWN = "markdown"
    MDX = "mdx"
    RST = "rst"

class ContentTransformer:
    """Transform documentation content between formats."""
    
    def transform(
        self,
        content: str,
        source_format: ContentFormat,
        target_format: ContentFormat,
        options: Optional[Dict[str, Any]] = None
    ) -> "TransformationResult":
        """
        Transform content from source format to target format.
        
        Args:
            content: Source content as string
            source_format: One of ContentFormat.MARKDOWN, ContentFormat.MDX, ContentFormat.RST
            target_format: One of ContentFormat.MARKDOWN, ContentFormat.MDX, ContentFormat.RST
            options: Framework-specific transformation options
        
        Returns:
            TransformationResult with converted content or errors
        
        Raises:
            TransformationError: If conversion fails (per clarification Q1 - halt build immediately)
        
        Examples:
            >>> transformer = ContentTransformer()
            >>> result = transformer.transform(
            ...     "# Heading\n\nParagraph.",
            ...     ContentFormat.MARKDOWN,
            ...     ContentFormat.RST
            ... )
            >>> print(result.content)
            Heading
            =======
            
            Paragraph.
        """
        pass
    
    def validate_content(
        self,
        content: str,
        format: ContentFormat
    ) -> "ValidationResult":
        """
        Validate content syntax for given format.
        
        Args:
            content: Content to validate
            format: Expected content format
        
        Returns:
            ValidationResult with syntax errors or warnings
        
        Examples:
            >>> transformer = ContentTransformer()
            >>> result = transformer.validate_content(
            ...     "# Heading\n\n```python\nprint('hello')\n```",
            ...     ContentFormat.MARKDOWN
            ... )
            >>> assert result.is_valid
        """
        pass
```

### TransformationResult

Result of content transformation operation.

```python
from typing import List, Optional

class TransformationError(Exception):
    """Error encountered during content transformation."""
    
    file_path: str
    line_number: int
    unsupported_syntax: str
    suggestion: str  # Manual override instructions
    
    def __str__(self) -> str:
        return (
            f"Transformation error in {self.file_path}:{self.line_number}\n"
            f"  Unsupported syntax: {self.unsupported_syntax}\n"
            f"  Suggestion: {self.suggestion}"
        )

class TransformationResult:
    """Result of content transformation."""
    
    success: bool
    content: Optional[str]
    errors: List[TransformationError]
    warnings: List[str]
    
    def raise_if_failed(self) -> None:
        """
        Raise TransformationError if transformation failed.
        
        Per clarification Q1: When transformation fails, halt build immediately
        with detailed error information.
        
        Raises:
            TransformationError: If success is False
        """
        if not self.success and self.errors:
            raise self.errors[0]  # Raise first error
    
    def log_errors(self) -> None:
        """Log all errors with details to stderr."""
        for error in self.errors:
            print(f"ERROR in {error.file_path}:{error.line_number}", file=sys.stderr)
            print(f"  Unsupported syntax: {error.unsupported_syntax}", file=sys.stderr)
            print(f"  Suggestion: {error.suggestion}", file=sys.stderr)
    
    def log_warnings(self) -> None:
        """Log all warnings to stdout."""
        for warning in self.warnings:
            print(f"WARNING: {warning}")

class ValidationResult:
    """Result of content syntax validation."""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]
```

## Transformation Rules

### Common Markdown → All Formats

Elements that transform consistently across all target formats:

| Markdown Element | Markdown Output | MDX Output | RST Output |
|-----------------|----------------|------------|-----------|
| **Headings** | `# Heading` | `# Heading` | `Heading\n========` |
| **Paragraphs** | `Paragraph text.` | `Paragraph text.` | `Paragraph text.` |
| **Bold** | `**bold**` | `**bold**` | `**bold**` |
| **Italic** | `*italic*` | `*italic*` | `*italic*` |
| **Code Inline** | `` `code` `` | `` `code` `` | ``` ``code`` ``` |
| **Lists** | `- item` | `- item` | `- item` |
| **Links** | `[text](url)` | `[text](url)` | `` `text <url>`_ `` |
| **Images** | `![alt](url)` | `![alt](url)` | `.. image:: url\n   :alt: alt` |

### Metadata Frontmatter Transformation

**Consistent metadata frontmatter** (per FR-004) transforms between framework-specific formats while preserving semantic meaning:

#### Markdown/Fumadocs (MDX) Frontmatter

```yaml
---
title: "API Reference"
description: "Complete API documentation for the package"
sidebar_position: 2
tags: ["api", "reference", "advanced"]
---
```

#### Docusaurus Frontmatter

```yaml
---
title: API Reference
description: Complete API documentation for the package
sidebar_position: 2
tags:
  - api
  - reference
  - advanced
---
```

#### Sphinx (RST) Metadata

```rst
:title: API Reference
:description: Complete API documentation for the package
:sidebar_position: 2
:tags: api, reference, advanced

API Reference
=============
```

**Transformation Rules**:

| Metadata Field | Markdown/MDX | Docusaurus | RST | Notes |
|----------------|--------------|------------|-----|-------|
| `title` | YAML string | YAML string | `:title:` field | Required in all formats |
| `description` | YAML string | YAML string | `:description:` field | Optional; used for SEO |
| `sidebar_position` | YAML number | YAML number | `:sidebar_position:` field | Controls nav order |
| `tags` | YAML array | YAML array | `:tags:` comma-separated | Used for filtering/search |
| `slug` | YAML string | YAML string | N/A (use filename) | URL path override |
| `hide_title` | YAML boolean | `hide_title: true` | N/A (manual control) | Hides page title |

**Example Transformation Code**:

```python
def transform_frontmatter(
    frontmatter: Dict[str, Any],
    target_format: ContentFormat
) -> str:
    """Transform frontmatter to target format."""
    
    if target_format == ContentFormat.RST:
        # Convert YAML frontmatter to RST field list
        lines = []
        for key, value in frontmatter.items():
            if key == "tags" and isinstance(value, list):
                lines.append(f":{key}: {', '.join(value)}")
            else:
                lines.append(f":{key}: {value}")
        return "\n".join(lines) + "\n\n"
    
    elif target_format in [ContentFormat.MARKDOWN, ContentFormat.MDX]:
        # Keep as YAML frontmatter
        return "---\n" + yaml.dump(frontmatter, default_flow_style=False) + "---\n\n"
    
    return ""
```

### Mermaid Diagrams

Framework-specific transformation for Mermaid diagrams:

**Markdown/MDX → Markdown/MDX** (no transformation):
```markdown
```mermaid
graph TD
    A --> B
```
```

**Markdown → RST** (convert to Sphinx directive):
```rst
.. mermaid::

   graph TD
       A --> B
```

### Admonitions/Callouts

Framework-specific transformation for admonitions:

**Markdown → MDX** (convert to Fumadocs Callout component):
```markdown
> **Note**: This is an admonition.

→

<Callout type="info">
  This is an admonition.
</Callout>
```

**Markdown → RST** (convert to Sphinx admonition directive):
```markdown
> **Note**: This is an admonition.

→

.. note::

   This is an admonition.
```

### Code Tabs

Framework-specific transformation for tabbed code blocks:

**Markdown → MDX** (convert to Fumadocs Tabs component):
```markdown
<!-- tabs -->
## Python
```python
print("hello")
```

## JavaScript
```javascript
console.log("hello");
```
<!-- /tabs -->

→

<Tabs items={['Python', 'JavaScript']}>
  <Tab value="Python">
    ```python
    print("hello")
    ```
  </Tab>
  <Tab value="JavaScript">
    ```javascript
    console.log("hello");
    ```
  </Tab>
</Tabs>
```

**Markdown → RST** (convert to Sphinx tabs directive):
```markdown
<!-- tabs -->
## Python
```python
print("hello")
```

→

.. tabs::

   .. tab:: Python

      .. code-block:: python

         print("hello")
```

### Cross-References

Framework-specific transformation for internal links:

**Markdown → MDX**:
```markdown
[See API docs](./api.md)

→

[See API docs](/docs/api)
```

**Markdown → RST**:
```markdown
[See API docs](./api.md)

→

:doc:`See API docs <api>`
```

## Failure Modes

Per clarification Q1: When transformation fails, halt build immediately.

### Failure Handling Strategy

1. **Halt Build Immediately**: Do not continue rendering subsequent files
2. **Log Detailed Error**: Show file path, line number, problematic syntax
3. **Provide Manual Override Instructions**: Suggest how to fix manually
4. **Exit with Non-Zero Status**: Signal failure to CI/CD systems

### Example Error Output

```text
ERROR: Content transformation failed in docs/advanced/custom-renderer.md:42

Unsupported syntax:
  ```custom-language
  # This language is not supported
  ```

Suggestion:
  The target framework (RST) does not support the 'custom-language' code block.
  
  Option 1: Remove the custom language and use a standard language identifier
  Option 2: Add a manual RST code block in a .rst file for this content
  Option 3: Exclude this file from transformation (add to .copier-answers.yml skip list)

Build halted. Please fix the error and re-run the build.
```

### Common Unsupported Syntax Examples

| Syntax | Why Unsupported | Suggested Fix |
|--------|----------------|---------------|
| Custom HTML tags | RST doesn't support arbitrary HTML | Use RST directives or standard Markdown |
| JSX components | RST/plain Markdown don't support JSX | Use framework-specific files or standard Markdown |
| Complex nested tables | RST table syntax is limited | Simplify table or use framework-specific syntax |
| Inline Markdown in HTML | Not portable across frameworks | Use pure Markdown or pure HTML |

## Usage Examples

### Example 1: Basic Transformation

```python
from riso.docs.transformation import ContentTransformer, ContentFormat

transformer = ContentTransformer()

markdown_content = """
# Getting Started

Welcome to the documentation!

## Installation

```bash
pip install mypackage
```

See [API Reference](./api.md) for details.
"""

result = transformer.transform(
    markdown_content,
    ContentFormat.MARKDOWN,
    ContentFormat.RST
)

if result.success:
    print(result.content)
else:
    result.log_errors()
    result.raise_if_failed()  # Halt build
```

**Expected Output**:

```rst
Getting Started
===============

Welcome to the documentation!

Installation
------------

.. code-block:: bash

   pip install mypackage

See :doc:`API Reference <api>` for details.
```

### Example 2: Transformation with Options

```python
result = transformer.transform(
    content=mermaid_diagram_markdown,
    source_format=ContentFormat.MARKDOWN,
    target_format=ContentFormat.RST,
    options={
        "mermaid_to_directive": True,
        "preserve_whitespace": True,
        "target_framework": "sphinx-shibuya"
    }
)
```

### Example 3: Batch Transformation with Error Handling

```python
from pathlib import Path

docs_dir = Path("docs")
output_dir = Path("docs_rst")
transformer = ContentTransformer()

failed_files = []

for md_file in docs_dir.rglob("*.md"):
    content = md_file.read_text()
    result = transformer.transform(
        content,
        ContentFormat.MARKDOWN,
        ContentFormat.RST
    )
    
    if result.success:
        output_file = output_dir / md_file.relative_to(docs_dir).with_suffix('.rst')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result.content)
    else:
        failed_files.append(md_file)
        result.log_errors()

if failed_files:
    print(f"\nTransformation failed for {len(failed_files)} files:")
    for file in failed_files:
        print(f"  - {file}")
    sys.exit(1)  # Halt build per clarification Q1
```

## Implementation Notes

### AST-Based Transformation Approach

The implementation uses Abstract Syntax Tree (AST) parsing for robust transformation:

1. **Parse Markdown**: Use Python's `markdown` library to parse into AST
2. **Transform AST**: Apply transformation rules to each node
3. **Render Target Format**: Generate target format syntax from transformed AST

**Benefits**:
- Preserves semantic structure (not just text replacement)
- Handles nested elements correctly (lists within lists, inline code, etc.)
- Extensible for new transformation rules
- Unit testable at the rule level

### Extension Points

Custom transformations can be registered via plugin system:

```python
from riso.docs.transformation import ContentTransformer, TransformationRule

def custom_mermaid_transformer(ast_node):
    """Custom Mermaid transformation for specific framework."""
    # Implementation
    pass

transformer = ContentTransformer()
transformer.register_rule(TransformationRule(
    source_format=ContentFormat.MARKDOWN,
    target_format=ContentFormat.RST,
    element_type="mermaid",
    transformer_fn=custom_mermaid_transformer
))
```

---

**API Version**: 1.0  
**Status**: Ready for Implementation  
**Related**: See `validation-api.md` for documentation validation interfaces
