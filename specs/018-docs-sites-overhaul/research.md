# Phase 0 Research: Documentation Sites Overhaul

**Feature**: 018-docs-sites-overhaul  
**Date**: 2025-11-02  
**Researcher**: Speckit Plan Workflow

## Research Questions

### 1. Sphinx Makefile Patterns

**Goal**: Understand why current Sphinx Makefile targets are failing and identify correct patterns.

**Investigation**:

Examined existing Sphinx documentation and Riso template structure:

- Current issue: Sphinx sample at 0% smoke test pass rate
- Missing Makefile targets: `docs`, `linkcheck`, `doctest`, `clean-docs`
- Sphinx ≥7.4 recommends separate documentation build system from application build

**Findings**:

1. **Standard Sphinx Makefile Structure** (from Sphinx docs):

```makefile
# Makefile.docs - Separate documentation build
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = _build

.PHONY: help docs linkcheck doctest clean-docs

docs:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

doctest:
	@$(SPHINXBUILD) -M doctest "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean-docs:
	rm -rf $(BUILDDIR)/*

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
```

2. **Why Separate Makefile**:
   - Avoids target name conflicts with Python build targets
   - Clear separation of concerns (app vs docs)
   - Allows independent invocation: `uv run make -f Makefile.docs docs`

3. **Sphinx Configuration Requirements**:
   - Must set `sys.path.insert(0, os.path.abspath('.'))` for autodoc
   - Need `sphinx.ext.autodoc` and `sphinx.ext.napoleon` extensions
   - Shibuya theme ≥2024.10 requires specific HTML theme options

**Decision**: Generate `Makefile.docs` template separate from main application Makefile.

**Rationale**: Prevents target collision, follows Sphinx best practices, enables independent documentation builds.

**Alternatives Rejected**:
- Single Makefile with namespaced targets (e.g., `doc-build`) - Rejected: Still clutters main Makefile
- Sphinx-only commands without Make - Rejected: Inconsistent with Riso's make-based workflow
- tox-based documentation builds - Rejected: Adds unnecessary dependency

---

### 2. Content Transformation Strategies

**Goal**: Determine best approach for Markdown → MDX/RST conversion preserving semantic structure.

**Investigation**:

Evaluated three approaches:

1. **Pandoc** (external tool):
   - Pros: Battle-tested, handles many formats
   - Cons: External dependency (violates minimal baseline), limited custom extensions

2. **Regex-based replacement** (simple approach):
   - Pros: Fast, no dependencies
   - Cons: Fragile, breaks with nested structures, no AST awareness

3. **AST-based transformation** (Python markdown library):
   - Pros: Semantic preservation, testable, extensible, pure Python
   - Cons: More implementation work upfront

**Findings**:

AST-based approach using Python's `markdown` library + custom renderers:

```python
from markdown import Markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

class RSTRenderer(Treeprocessor):
    """Custom AST processor for RST output."""
    
    def run(self, root):
        # Process AST nodes to RST syntax
        return self._process_element(root)
    
    def _process_element(self, element):
        if element.tag == 'h1':
            return self._rst_heading(element.text, '=')
        elif element.tag == 'code':
            return self._rst_code_block(element.text)
        # ... more transformations

class ContentTransformer:
    def transform_md_to_rst(self, content: str) -> str:
        md = Markdown(extensions=['extra', 'codehilite'])
        tree = md.parser.parseDocument(content).getroot()
        renderer = RSTRenderer(md)
        return renderer.run(tree)
```

**Decision**: Implement AST-based transformation using Python's `markdown` library with custom renderers for each target format (MDX, RST).

**Rationale**:
- Preserves semantic structure through AST parsing
- Pure Python (no external dependencies)
- Extensible for framework-specific syntax (Mermaid, admonitions)
- Unit testable at transformation rule level

**Alternatives Rejected**:
- Pandoc: External dependency violates constitution principle III (Minimal Baseline)
- Regex: Too fragile for nested structures (lists within lists, inline code, etc.)

---

### 3. Mermaid Integration Patterns

**Goal**: Find consistent way to embed Mermaid diagrams across all three documentation frameworks.

**Investigation**:

Framework-specific Mermaid support:

1. **Fumadocs** (Next.js):
   - Uses `rehype-mermaid` plugin
   - Syntax: Standard markdown code blocks with `mermaid` language tag
   - Configuration in `next.config.mjs`

2. **Sphinx-Shibuya**:
   - Uses `sphinxcontrib-mermaid` extension
   - Syntax: `.. mermaid::` directive
   - Configuration in `conf.py`

3. **Docusaurus**:
   - Uses `@docusaurus/theme-mermaid`
   - Syntax: Standard markdown code blocks with `mermaid` language tag
   - Configuration in `docusaurus.config.js`

**Findings**:

Common pattern: All frameworks support Mermaid via plugins/extensions configured in framework config files.

Transformation approach:
- **Markdown → Markdown/MDX**: No transformation needed (preserve code blocks)
- **Markdown → RST**: Transform ````mermaid` blocks to `.. mermaid::` directives

```python
def transform_mermaid_to_rst(mermaid_block: str) -> str:
    """
    Convert:
        ```mermaid
        graph TD
            A --> B
        ```
    
    To:
        .. mermaid::
        
           graph TD
               A --> B
    """
    lines = mermaid_block.strip().split('\n')
    indented = ['   ' + line for line in lines]
    return '.. mermaid::\n\n' + '\n'.join(indented)
```

**Decision**: Framework-specific Mermaid configuration via prompt-driven template generation; content transformation for RST only.

**Rationale**:
- Leverages native framework plugins (best performance, maintainability)
- Minimal transformation needed (only Markdown → RST requires changes)
- Consistent syntax in Markdown source across projects

**Alternatives Rejected**:
- Client-side JavaScript rendering: Requires JavaScript (violates graceful degradation requirement)
- Image pre-rendering: Complex build pipeline, loses interactivity
- Single abstraction layer: Over-engineering for three well-supported frameworks

---

### 4. Search Provider Integration

**Goal**: Understand Algolia, Typesense, local search setup per framework with prompt-driven configuration.

**Investigation**:

Evaluated search providers across frameworks:

| Provider | Fumadocs | Sphinx | Docusaurus | Cost | Setup Complexity |
|----------|----------|--------|------------|------|------------------|
| **Local** | flexsearch | sphinx-search | Built-in | Free | Low |
| **Algolia** | docsearch | algoliasearch | docsearch | Free tier → Paid | Medium |
| **Typesense** | typesense-js | sphinx-typesense | plugin | Self-hosted or $0.03/hr | Medium-High |

**Findings**:

1. **Local Search** (default recommendation):
   - Fumadocs: Built-in flexsearch support via `search: { enabled: true }`
   - Sphinx: `html_theme_options = {'search_bar_position': 'sidebar'}`
   - Docusaurus: Built-in via `themeConfig.algolia = null`

2. **Algolia DocSearch**:
   - Requires application to Algolia DocSearch program
   - Free for open-source, $1/month/1K requests for commercial
   - All frameworks have first-class support

3. **Typesense**:
   - Self-hosted or cloud ($0.03/hr = ~$22/month)
   - Best for private documentation or high-volume needs
   - Requires custom integration per framework

**Configuration Pattern**:

```yaml
# copier.yml prompt
docs_search_provider:
  type: str
  help: "Search integration provider"
  choices:
    - none       # No search functionality
    - local      # Framework-native local search (FREE)
    - algolia    # Algolia DocSearch (FREE tier → PAID, requires application)
    - typesense  # Typesense Cloud or self-hosted (PAID or self-hosted infrastructure)
  default: local
```

Generate framework-specific config based on selection:

```python
# template/files/shared/docs/search_config.py.jinja
{% if docs_search_provider == 'algolia' %}
# Algolia configuration
ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')
ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY')
ALGOLIA_INDEX_NAME = os.getenv('ALGOLIA_INDEX_NAME')
{% elif docs_search_provider == 'typesense' %}
# Typesense configuration
TYPESENSE_API_KEY = os.getenv('TYPESENSE_API_KEY')
TYPESENSE_HOST = os.getenv('TYPESENSE_HOST', 'localhost:8108')
{% endif %}
```

**Decision**: Default to local search; prompt-driven configuration for external providers with environment variable templates.

**Rationale**:
- Local search is free, zero-configuration, works offline
- External providers opt-in via prompts (follows Module Sovereignty)
- Environment variables keep API keys out of generated code

**Alternatives Rejected**:
- Runtime provider detection: Violates Deterministic Generation principle
- Single search abstraction: Over-engineering, each framework has different APIs
- Forced Algolia: Cost barrier for users, vendor lock-in

---

### 5. Accessibility Validation Tools

**Goal**: Select WCAG 2.1 Level AA validation tooling for CI integration.

**Investigation**:

Evaluated three tools:

1. **axe-core**:
   - Industry standard (Deque Systems)
   - Python: `pytest-axe` integration
   - Node: `@axe-core/cli`
   - 90+ WCAG rules
   - Active maintenance

2. **pa11y**:
   - Node.js only
   - Uses HTML CodeSniffer
   - Good for headless Chrome testing
   - Less actively maintained

3. **Lighthouse**:
   - Google's tool
   - Requires full browser (heavy)
   - Good for performance + accessibility
   - Overkill for docs-only validation

**Findings**:

axe-core best fit:

```bash
# Python stack (Sphinx)
uv add pytest-axe
uv run pytest tests/test_accessibility.py

# Node stack (Fumadocs/Docusaurus)
pnpm add -D @axe-core/cli
pnpm exec axe http://localhost:3000 --rules wcag21aa
```

**Sample Test**:

```python
# tests/test_accessibility.py
import pytest
from pytest_axe import Axe

def test_docs_homepage_accessibility(selenium):
    """Test documentation homepage meets WCAG 2.1 AA."""
    selenium.get('http://localhost:8000')
    axe = Axe(selenium)
    axe.inject()
    results = axe.run()
    
    # Non-blocking per clarification Q3
    if results['violations']:
        print(f"Accessibility warnings: {len(results['violations'])}")
        for violation in results['violations']:
            print(f"  - {violation['id']}: {violation['help']}")
    
    # Only fail on critical errors (incomplete, not violations)
    assert len(results['incomplete']) == 0, "Critical accessibility errors found"
```

**Decision**: Use axe-core via `pytest-axe` (Python) and `@axe-core/cli` (Node) for WCAG 2.1 Level AA validation.

**Rationale**:
- Industry standard with excellent documentation
- Dual Python/Node support matches Riso stack
- Integrates with existing pytest quality suite
- Non-blocking warnings per clarification Q3

**Alternatives Rejected**:
- pa11y: Node-only (doesn't support Sphinx without extra tooling)
- Lighthouse: Too heavy, targets full web apps not documentation
- Manual audits: Not scalable, not automatable

---

### 6. Documentation Versioning Patterns

**Goal**: Understand version management for Sphinx (mike), Docusaurus (native), Fumadocs (custom).

**Investigation**:

Framework versioning approaches:

1. **Sphinx + mike**:
   - `mike` CLI tool manages multiple versions
   - Generates version selector in sidebar
   - Deployable to GitHub Pages
   - Config: `mike.yml` + git tags

2. **Docusaurus**:
   - Native versioning via `npm run docusaurus docs:version 1.0.0`
   - Versions stored in `versioned_docs/` and `versioned_sidebars/`
   - Version dropdown built-in
   - Config: `docusaurus.config.js` versions array

3. **Fumadocs**:
   - No native versioning (Next.js app)
   - Manual approach: separate routes per version (`app/v1/`, `app/v2/`)
   - Requires custom version switcher component
   - Alternative: separate deployments per version

**Findings**:

Versioning adds significant complexity:

- Sphinx: Requires `mike` dependency + git tag workflow
- Docusaurus: Well-supported but doubles build time (all versions)
- Fumadocs: Manual implementation required (20-30 lines of component code)

**Configuration Pattern**:

```yaml
# copier.yml
docs_versioning:
  type: str
  help: "Enable multi-version documentation support (adds build complexity)"
  choices:
    - disabled
    - enabled
  default: disabled
  when: "{{ docs_site != 'none' }}"
```

**Scaffold when enabled**:

- **Sphinx**: Generate `mike.yml`, document `mike deploy` workflow
- **Docusaurus**: Add versioning config to `docusaurus.config.js`, create `versions.json`
- **Fumadocs**: Generate version switcher component in `components/VersionSwitcher.tsx`, document multi-version routing

**Decision**: Make versioning opt-in via prompt (default disabled); scaffold framework-specific patterns when enabled.

**Rationale**:
- Versioning is advanced feature (not needed for most projects initially)
- Significant build complexity (2x build time for Docusaurus)
- Well-documented per framework when needed

**Alternatives Rejected**:
- Always enable versioning: Over-engineering, slows builds
- Single versioning abstraction: Frameworks too different (native vs manual)
- External tool (git branches): Doesn't integrate with framework UX

---

### 7. Link Checking Retry Logic

**Goal**: Implement exponential backoff for external link validation to handle transient network errors.

**Investigation**:

Sphinx `linkcheck` builder configuration:

```python
# conf.py
linkcheck_retries = 3
linkcheck_timeout = 10
linkcheck_workers = 5
linkcheck_anchors = True
linkcheck_ignore = [
    r'http://localhost:\d+',  # Ignore local servers
    r'https://example\.com',  # Ignore placeholders
]
```

**Exponential Backoff Algorithm**:

```python
import time
from typing import List

def check_link_with_retry(url: str, max_attempts: int = 3, initial_delay: float = 1.0) -> bool:
    """
    Check link with exponential backoff retry logic.
    
    Args:
        url: URL to check
        max_attempts: Maximum retry attempts (default: 3 per clarification Q2)
        initial_delay: Initial delay in seconds (default: 1.0)
    
    Returns:
        True if link is valid, False after all retries exhausted
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code < 400:
                return True
        except requests.RequestException as e:
            attempt += 1
            if attempt < max_attempts:
                delay = initial_delay * (2 ** attempt)  # Exponential backoff
                print(f"Retry {attempt}/{max_attempts} for {url} after {delay}s: {e}")
                time.sleep(delay)
            else:
                print(f"Link check failed after {max_attempts} attempts: {url}")
                return False
    return False
```

**Configuration per Framework**:

- **Sphinx**: Use built-in `linkcheck_retries` + custom `linkcheck_timeout`
- **Fumadocs/Docusaurus**: Generate `scripts/check-links.js` with retry logic using `axios-retry` library

**Decision**: Use Sphinx built-in retry for Sphinx projects; generate custom link checker script with exponential backoff for Node-based frameworks.

**Rationale**:
- Sphinx has built-in support (no extra code needed)
- Node frameworks need custom script (10-15 lines)
- 3 retries with exponential backoff handles most transient failures

**Alternatives Rejected**:
- No retry logic: Fails on transient network errors
- Fixed delay retry: Doesn't adapt to network conditions
- External service (e.g., linkchecker.io): Adds external dependency

---

## Research Summary

### Key Decisions

1. **Sphinx Makefile**: Generate separate `Makefile.docs` to avoid target collisions
2. **Content Transformation**: AST-based using Python `markdown` library with custom renderers
3. **Mermaid**: Framework-native plugins with RST-only transformation
4. **Search**: Default to local search; prompt-driven external provider config
5. **Accessibility**: axe-core (pytest-axe for Python, @axe-core/cli for Node)
6. **Versioning**: Opt-in via prompt, scaffold framework-specific patterns
7. **Link Checking**: Sphinx built-in retry + custom script for Node frameworks

### Technologies Selected

- **Python**: markdown library (AST parsing), pytest-axe (accessibility)
- **Node**: @axe-core/cli (accessibility), axios-retry (link checking)
- **Sphinx**: sphinxcontrib-mermaid, sphinx.ext.autodoc, sphinx.ext.napoleon
- **Fumadocs**: rehype-mermaid, flexsearch
- **Docusaurus**: @docusaurus/theme-mermaid, built-in search

### Implementation Risks

1. **Content Transformation Complexity**: AST-based approach requires careful testing
   - Mitigation: Comprehensive unit tests for each transformation rule
   
2. **Framework Version Compatibility**: Plugins may break across framework updates
   - Mitigation: Pin exact versions in generated `pyproject.toml` and `package.json`
   
3. **Accessibility False Positives**: axe-core may flag intentional design choices
   - Mitigation: Non-blocking warnings per clarification Q3; document override patterns

### Next Steps

Proceed to Phase 1 design:

1. Create `data-model.md` with entities and relationships
2. Generate `contracts/` with prompt schemas and transformation/validation APIs
3. Write `quickstart.md` for developer onboarding
4. Update agent context with new dependencies and commands

---

**Research Complete**: 2025-11-02  
**Approved for Phase 1**: Yes
