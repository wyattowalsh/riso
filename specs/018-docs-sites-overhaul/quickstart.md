# Quickstart: Documentation Sites Overhaul Implementation

**Feature**: 018-docs-sites-overhaul  
**Date**: 2025-11-02  
**Status**: Developer Onboarding Guide

## Prerequisites

Before starting work on this feature, ensure you have:

- **Python 3.11+** with `uv` installed (`uv --version`)
- **Node.js 20 LTS** with `pnpm ≥8` (`node --version`, `pnpm --version`)
- **Git** repository cloned
- **Feature branch** `018-docs-sites-overhaul` checked out
- **Editor** with Python and Markdown support (VS Code, PyCharm, etc.)

## Development Environment Setup

### 1. Initial Setup

```bash
# From repository root
cd /path/to/riso

# Ensure you're on the feature branch
git checkout 018-docs-sites-overhaul

# Install Python dependencies
uv sync

# Install Node dependencies (for Fumadocs/Docusaurus work)
pnpm install

# Verify tooling versions
uv run python --version  # Should be 3.11+
pnpm --version           # Should be ≥8
```

### 2. Verify Current State

```bash
# Check Sphinx sample (currently failing - this is what we're fixing)
./scripts/render-samples.sh --variant docs-sphinx
cat samples/docs-sphinx/smoke-results.json

# Expected: All smoke tests FAIL (0% pass rate)
```

## Project Structure Tour

### Key Files for This Feature

```text
template/
├── copier.yml                       # ADD: 7 new docs configuration prompts
├── files/
│   ├── python/
│   │   └── docs/                    # MODIFY: Fix Sphinx Makefile, conf.py templates
│   │       ├── Makefile.docs.jinja  # NEW: Separate docs Makefile
│   │       └── conf.py.jinja        # MODIFY: Fix autodoc configuration
│   ├── node/
│   │   └── docs/                    # MODIFY: Enhance Fumadocs/Docusaurus configs
│   │       ├── fumadocs/
│   │       │   └── next.config.mjs.jinja  # MODIFY: Add Mermaid, search config
│   │       └── docusaurus/
│   │           └── docusaurus.config.js.jinja  # MODIFY: Add Mermaid, search config
│   └── shared/
│       ├── docs/                    # NEW: Shared content transformation system
│       │   ├── transformation/      # NEW: Markdown → MDX/RST converters
│       │   │   ├── markdown_to_mdx.py.jinja
│       │   │   ├── markdown_to_rst.py.jinja
│       │   │   └── common.py.jinja
│       │   └── validation/          # NEW: Link checking, accessibility validation
│       │       ├── link_checker.py.jinja
│       │       ├── accessibility.py.jinja
│       │       └── common.py.jinja
│       └── .github/
│           └── workflows/
│               ├── riso-docs-build.yml.jinja     # NEW: Docs build workflow
│               └── riso-docs-validate.yml.jinja  # NEW: Validation workflow

scripts/ci/
├── validate_docs_config.py          # NEW: Validate generated docs configurations
├── test_content_transformation.py   # NEW: Test Markdown → MDX/RST conversion
└── render_matrix.py                 # MODIFY: Add docs validation to smoke tests

samples/
├── docs-fumadocs/                   # MODIFY: Update with new prompts
├── docs-sphinx/                     # FIX: Currently failing (0% → 100% pass rate)
└── docs-docusaurus/                 # MODIFY: Update with new prompts

docs/
├── modules/
│   └── docs-site.md.jinja           # MODIFY: Document new configuration options
└── upgrade-guide/
    └── 018-docs-sites.md.jinja      # NEW: Migration and configuration guide

specs/018-docs-sites-overhaul/
├── spec.md                          # Feature specification (already complete)
├── plan.md                          # Implementation plan (this file's sibling)
├── research.md                      # Technology decisions (complete)
├── data-model.md                    # Entities and relationships (complete)
├── quickstart.md                    # This file
└── contracts/                       # API contracts (complete)
    ├── prompts.yml                  # Extended docs prompts
    ├── transformation-api.md        # Content transformation interface
    └── validation-api.md            # Docs validation interface
```

## Critical Path: Fix Sphinx First

**Priority**: P1 (highest)  
**Why**: Sphinx smoke tests are at 0% pass rate, blocking all documentation features.

### Step-by-Step Sphinx Fix

#### 1. Understand the Problem

```bash
# Render current Sphinx variant
./scripts/render-samples.sh --variant docs-sphinx

# Navigate to rendered project
cd samples/docs-sphinx/render

# Try to build docs (will fail)
uv run make docs
# Expected error: "make: *** No rule to make target 'docs'"

# Check what targets exist
uv run make help
# Expected: Only Python build targets, no docs targets
```

**Root Cause**: Missing Makefile targets for documentation builds.

#### 2. Create Makefile.docs Template

```bash
# Create new Makefile specifically for docs
# Location: template/files/python/docs/Makefile.docs.jinja

cat > template/files/python/docs/Makefile.docs.jinja << 'EOF'
# Makefile.docs - Documentation build targets
# Generated by Riso template (feature: 018-docs-sites-overhaul)

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = _build

.PHONY: help docs linkcheck doctest clean-docs

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

docs:
	@echo "Building Sphinx documentation..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
	@echo "Documentation built successfully!"
	@echo "Open _build/html/index.html to view."

linkcheck:
	@echo "Checking external links..."
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

doctest:
	@echo "Running doctests..."
	@$(SPHINXBUILD) -M doctest "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean-docs:
	@echo "Cleaning documentation build artifacts..."
	@rm -rf $(BUILDDIR)/*
EOF
```

#### 3. Fix Sphinx conf.py Template

```bash
# Location: template/files/python/docs/conf.py.jinja
# Key fixes:
# 1. Add sys.path modification for autodoc
# 2. Enable autodoc and napoleon extensions
# 3. Configure Shibuya theme options
```

**Example fixes**:

```python
# template/files/python/docs/conf.py.jinja

import os
import sys

# Add project root to path for autodoc
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = '{{ project_name }}'
copyright = '2025, {{ author_name }}'
author = '{{ author_name }}'

# Extensions
extensions = [
    'sphinx.ext.autodoc',       # Auto-generate API docs from docstrings
    'sphinx.ext.napoleon',      # Support Google/NumPy docstring styles
    'sphinx.ext.viewcode',      # Add links to source code
    'sphinxcontrib.mermaid',    # Mermaid diagram support
]

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# HTML theme
html_theme = 'shibuya'
html_theme_options = {
    'dark_mode': {% if docs_theme_mode == 'dark' %}True{% elif docs_theme_mode == 'light' %}False{% else %}'auto'{% endif %},
}

# Linkcheck configuration (per research.md decision 7)
linkcheck_retries = 3
linkcheck_timeout = 10
linkcheck_ignore = [
    r'http://localhost:\d+',
    r'https://example\.com',
]
```

#### 4. Test the Fix

```bash
# Re-render with fixes
./scripts/render-samples.sh --variant docs-sphinx

# Test docs build
cd samples/docs-sphinx/render
uv run make -f Makefile.docs docs

# Should succeed and generate _build/html/

# Test link checking
uv run make -f Makefile.docs linkcheck

# Should succeed (or show external link failures only)
```

#### 5. Verify Smoke Tests Pass

```bash
# Run smoke tests
cd /path/to/riso
uv run python scripts/ci/render_matrix.py

# Check results
cat samples/docs-sphinx/smoke-results.json

# Expected: "passed": true (100% pass rate)
```

## Adding New Configuration Prompts

### 1. Edit copier.yml

```bash
# Location: template/copier.yml

# Add at end of file (after existing docs_site prompt):
cat >> template/copier.yml << 'EOF'

docs_theme_mode:
  type: str
  help: "Default theme appearance (light/dark/auto for system preference)"
  choices:
    - light
    - dark
    - auto
  default: auto
  when: "{{ docs_site != 'none' }}"

docs_search_provider:
  type: str
  help: "Search integration provider"
  choices:
    - none
    - local
    - algolia
    - typesense
  default: local
  when: "{{ docs_site != 'none' }}"

# ... (see contracts/prompts.yml for full list)
EOF
```

### 2. Use Prompts in Templates

```jinja
{# template/files/shared/docs/config.py.jinja #}

# Documentation configuration generated by Riso template

DOCS_FRAMEWORK = "{{ docs_site }}"
DOCS_THEME_MODE = "{{ docs_theme_mode }}"
DOCS_SEARCH_PROVIDER = "{{ docs_search_provider }}"

{% if docs_search_provider == 'algolia' %}
# Algolia configuration (requires environment variables)
ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')
ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY')
ALGOLIA_INDEX_NAME = os.getenv('ALGOLIA_INDEX_NAME')
{% endif %}
```

### 3. Test Prompt Rendering

```bash
# Render with custom answers
cat > /tmp/test-answers.yml << 'EOF'
project_name: test-docs
docs_site: sphinx-shibuya
docs_theme_mode: dark
docs_search_provider: algolia
EOF

copier copy . /tmp/test-render --answers-file /tmp/test-answers.yml

# Verify generated config
cat /tmp/test-render/docs/conf.py | grep -A5 "theme_mode"
```

## Implementing Content Transformation

### 1. Create Transformation Module

```bash
# Location: template/files/shared/docs/transformation/common.py.jinja
```

**Template Structure**:

```python
# template/files/shared/docs/transformation/common.py.jinja

"""
Content transformation utilities for documentation.
Feature: 018-docs-sites-overhaul
"""

from typing import Callable, List
from dataclasses import dataclass
from enum import Enum

class ContentFormat(Enum):
    MARKDOWN = "markdown"
    MDX = "mdx"
    RST = "rst"

@dataclass
class TransformationRule:
    source_format: ContentFormat
    target_format: ContentFormat
    transformation_fn: Callable[[str], str]
    
    def apply(self, content: str) -> str:
        """Apply transformation to content."""
        return self.transformation_fn(content)

# ... (see contracts/transformation-api.md for full implementation)
```

### 2. Create Test Suite

```bash
# Location: tests/test_content_transformation.py

cat > tests/test_content_transformation.py << 'EOF'
"""
Tests for content transformation (Markdown → MDX/RST).
Feature: 018-docs-sites-overhaul
"""

import pytest
from riso.docs.transformation import ContentTransformer, ContentFormat

def test_markdown_to_rst_headings():
    """Test Markdown heading conversion to RST."""
    transformer = ContentTransformer()
    
    markdown = "# Heading Level 1\n\n## Heading Level 2"
    result = transformer.transform(markdown, ContentFormat.MARKDOWN, ContentFormat.RST)
    
    assert result.success
    assert "Heading Level 1" in result.content
    assert "===============" in result.content  # RST underline

def test_markdown_to_rst_code_blocks():
    """Test code block conversion."""
    transformer = ContentTransformer()
    
    markdown = "```python\nprint('hello')\n```"
    result = transformer.transform(markdown, ContentFormat.MARKDOWN, ContentFormat.RST)
    
    assert result.success
    assert ".. code-block:: python" in result.content
    assert "print('hello')" in result.content

def test_transformation_failure_halts_build():
    """Test that transformation failures halt the build (per clarification Q1)."""
    transformer = ContentTransformer()
    
    # Invalid syntax that cannot be transformed
    markdown = "```unsupported-language\ncode\n```"
    result = transformer.transform(markdown, ContentFormat.MARKDOWN, ContentFormat.RST)
    
    assert not result.success
    assert len(result.errors) > 0
    assert "unsupported" in result.errors[0].unsupported_syntax.lower()
    
    # Should raise on raise_if_failed()
    with pytest.raises(Exception):
        result.raise_if_failed()
EOF
```

### 3. Run TDD Workflow

```bash
# RED: Tests fail initially
uv run pytest tests/test_content_transformation.py -v
# Expected: FAILED (not yet implemented)

# GREEN: Implement transformation
# Edit template/files/shared/docs/transformation/markdown_to_rst.py.jinja
# ... (implementation based on research.md decision 2: AST-based approach)

# Re-test
uv run pytest tests/test_content_transformation.py -v
# Expected: PASSED

# REFACTOR: Clean up implementation
# Run full quality suite
make quality
```

## Testing Content Transformation

### Unit Tests

```bash
# Run transformation tests
uv run pytest tests/test_content_transformation.py -v

# Test specific transformation
uv run python -c "
from riso.docs.transformation import ContentTransformer, ContentFormat
transformer = ContentTransformer()
result = transformer.transform('# Heading', ContentFormat.MARKDOWN, ContentFormat.RST)
print(result.content)
"
```

### Integration Tests

```bash
# Test transformation in rendered project
./scripts/render-samples.sh --variant docs-sphinx

cd samples/docs-sphinx/render

# Create test Markdown file
cat > docs/test.md << 'EOF'
# Test Document

This is a test document with **bold** and *italic* text.

```python
def hello():
    print("world")
```

See [other docs](./index.md) for more.
EOF

# Transform to RST
uv run python -c "
from pathlib import Path
from shared.docs.transformation import ContentTransformer, ContentFormat

transformer = ContentTransformer()
content = Path('docs/test.md').read_text()
result = transformer.transform(content, ContentFormat.MARKDOWN, ContentFormat.RST)

if result.success:
    Path('docs/test.rst').write_text(result.content)
    print('✅ Transformation succeeded')
else:
    result.log_errors()
    exit(1)
"

# Verify RST output
cat docs/test.rst
```

## Validation & Quality Checks

### Local Validation

```bash
# Validate all docs configurations
uv run python scripts/ci/validate_docs_config.py

# Expected output:
# ✅ Fumadocs configuration valid
# ✅ Sphinx configuration valid
# ✅ Docusaurus configuration valid
```

### Full Render Matrix

```bash
# Render all variants
uv run python scripts/ci/render_matrix.py

# Check smoke test results
cat samples/metadata/module_success.json

# Expected: docs_site module at 100% success for all frameworks
```

### Quality Suite

```bash
# Run full quality checks
make quality

# or, when make is unavailable
QUALITY_PROFILE=standard uv run task quality

# Expected: All checks pass (ruff, mypy, pylint, pytest)
```

## Debugging Tips

### Sphinx Build Failures

```bash
# Check Sphinx configuration
cd samples/docs-sphinx/render
uv run python -c "import sys; sys.path.insert(0, '.'); import docs.conf as conf; print(conf.__dict__)"

# Run Sphinx with verbose output
uv run sphinx-build -v docs _build/html

# Check Sphinx version
uv run python -m sphinx --version
```

### Link Checking Failures

```bash
# Run link check with verbose output
cd samples/docs-sphinx/render
uv run sphinx-build -b linkcheck docs _build/linkcheck -v

# Check link check report
cat _build/linkcheck/output.txt
```

### Content Transformation Failures

```bash
# Test transformation in isolation
uv run python scripts/ci/test_content_transformation.py --file docs/api.md --target rst

# Debug with Python REPL
uv run python
>>> from riso.docs.transformation import ContentTransformer, ContentFormat
>>> transformer = ContentTransformer()
>>> result = transformer.transform("# Test", ContentFormat.MARKDOWN, ContentFormat.RST)
>>> print(result.content)
```

### Accessibility Validation Issues

```bash
# Run accessibility check on local server
cd samples/docs-fumadocs/render
pnpm run dev &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Run axe-core validation
pnpm exec axe http://localhost:3000 --rules wcag21aa

# Cleanup
kill $SERVER_PID
```

## Common Commands Reference

```bash
# === Rendering ===
./scripts/render-samples.sh                                    # Render default variant
./scripts/render-samples.sh --variant docs-sphinx              # Render specific variant

# === Quality ===
make quality                                                   # Run full quality suite
QUALITY_PROFILE=strict make quality                            # Run with strict checks

# === Testing ===
uv run pytest tests/test_content_transformation.py -v          # Test transformations
uv run pytest tests/test_docs_validation.py -v                 # Test validation

# === CI Scripts ===
uv run python scripts/ci/render_matrix.py                      # Render all variants
uv run python scripts/ci/record_module_success.py              # Update success rates
uv run python scripts/ci/validate_docs_config.py               # Validate configs

# === Documentation ===
cd samples/docs-sphinx/render && uv run make -f Makefile.docs docs       # Build Sphinx docs
cd samples/docs-fumadocs/render && pnpm run build                         # Build Fumadocs
cd samples/docs-docusaurus/render && pnpm run build                       # Build Docusaurus
```

## Next Steps

Follow the implementation priority from spec.md:

1. **P1: Fix Sphinx** (User Story 1) ← START HERE
   - Fix Makefile.docs template
   - Fix conf.py template
   - Verify smoke tests pass (0% → 100%)

2. **P1: Add Configuration Prompts** (User Story 2)
   - Add 7 new prompts to copier.yml
   - Test prompt rendering
   - Update sample answers

3. **P2: Implement Content Transformation** (User Story 3)
   - Create transformation module
   - Implement AST-based converters
   - Add comprehensive tests

4. **P2: Add Interactive Features** (User Story 4)
   - Mermaid diagram support
   - Code tabs implementation
   - API playground integration

5. **P3: Documentation Versioning** (User Story 5)
   - Optional versioning scaffold
   - Framework-specific patterns
   - Version switcher components

## Getting Help

- **Feature Specification**: `specs/018-docs-sites-overhaul/spec.md`
- **Implementation Plan**: `specs/018-docs-sites-overhaul/plan.md`
- **Research Decisions**: `specs/018-docs-sites-overhaul/research.md`
- **Data Model**: `specs/018-docs-sites-overhaul/data-model.md`
- **API Contracts**: `specs/018-docs-sites-overhaul/contracts/`

## Success Criteria Checklist

Track progress against spec.md success criteria:

- [ ] **SC-001**: Sphinx template renders without errors
- [ ] **SC-002**: Fumadocs and Docusaurus render without errors
- [ ] **SC-003**: Sphinx smoke test pass rate 0% → 100%
- [ ] **SC-004**: 7 new prompts functional in copier.yml
- [ ] **SC-005**: Documentation build completes in <90 seconds
- [ ] **SC-006**: Link checking completes in <5 minutes
- [ ] **SC-007**: Content transformation supports Markdown, MDX, RST
- [ ] **SC-008**: Accessibility validation reports WCAG 2.1 AA warnings

When all criteria pass, the feature is complete! 🎉

---

**Quickstart Version**: 1.0  
**Created**: 2025-11-02  
**Status**: Ready for Development
