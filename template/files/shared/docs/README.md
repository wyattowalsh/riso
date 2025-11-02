# Documentation Configuration Guide

This directory contains shared documentation configuration, utilities, and templates for the Riso template.

## Directory Structure

```
template/files/shared/docs/
├── components/          # Reusable components (version dropdowns, etc.)
├── deploy/             # Deployment configurations for various platforms
├── guidance/           # Guides and documentation
├── modules/            # Module-specific documentation
├── search/             # Search provider configurations
├── transformation/     # Content transformation utilities
├── validation/         # Documentation validation tools
└── versioning/         # Version management utilities
```

## Features

### Content Transformation
Convert documentation between formats while preserving semantic structure:
- **Markdown → RST**: For Sphinx documentation
- **Markdown → MDX**: For Fumadocs/Docusaurus

See `transformation/` for implementation.

### Validation Tools
Comprehensive validation suite:
- **Link Checking**: With exponential backoff retry (3 attempts, 1s→2s→4s)
- **Accessibility**: WCAG 2.1 Level AA compliance (non-blocking warnings)
- **Image References**: Validate all image paths
- **Cross-references**: Validate Sphinx :doc: and :ref: directives

See `validation/` for implementation.

### Search Integration
Support for multiple search providers:
- **Local**: Framework-native search (FREE, offline)
- **Algolia**: DocSearch integration (FREE tier → PAID)
- **Typesense**: Cloud or self-hosted (~$22/month)

See `search/` for configurations.

### Deployment Configurations
Ready-to-use deployment configs:
- **GitHub Pages**: Workflow with artifact storage
- **Netlify**: `netlify.toml` with build commands
- **Vercel**: `vercel.json` with framework detection
- **Cloudflare**: `wrangler.toml` for Pages

See `deploy/` for templates.

### Versioning Support
Multi-version documentation scaffolding:
- Version dropdown components
- Version detection utilities
- Configuration templates

See `versioning/` and `components/` for implementation.

## Configuration Options

All configuration is driven by Copier prompts in `template/copier.yml`:

### Framework Selection
```yaml
docs_site: fumadocs      # or sphinx-shibuya, docusaurus, none
```

### Theme & Appearance
```yaml
docs_theme_mode: auto    # or light, dark
```

### Search Provider
```yaml
docs_search_provider: local    # or algolia, typesense, none
```

### Deployment Target
```yaml
docs_deploy_target: github-pages    # or netlify, vercel, cloudflare
```

### Interactive Features
```yaml
docs_interactive_features: enabled    # or disabled
```
Enables:
- Mermaid diagram rendering
- Code tabs
- Live API examples

### Versioning
```yaml
docs_versioning: enabled    # or disabled (default)
```
⚠️ ADVANCED: Adds complexity, ~2x build time

### Quality Gates
```yaml
docs_quality_gates: enabled    # or disabled
```
Enables CI validation:
- Link checking with retry logic
- Accessibility audits
- Image validation

## Usage Examples

### Building Documentation

**Sphinx**:
```bash
uv sync --group docs
uv run make -f Makefile.docs docs
uv run make -f Makefile.docs linkcheck
```

**Fumadocs**:
```bash
pnpm install
pnpm --filter docs-fumadocs build
```

**Docusaurus**:
```bash
pnpm install
pnpm --filter docs-docusaurus build
```

### Content Transformation

```python
from shared.docs.transformation import ContentTransformer, ContentFormat

transformer = ContentTransformer()
result = transformer.transform(
    content=markdown_content,
    source_format=ContentFormat.MARKDOWN,
    target_format=ContentFormat.RST,
    file_path="docs/quickstart.md"
)

if result.success:
    print(result.content)
else:
    result.log_errors()
```

### Link Validation

```python
from shared.docs.validation import LinkChecker

checker = LinkChecker()
results = checker.check_links(
    build_dir=Path("_build/html"),
    check_external=True
)

print(results.generate_report())
```

### Accessibility Validation

```python
from shared.docs.validation import AccessibilityValidator

validator = AccessibilityValidator()
results = validator.validate(build_dir=Path("_build/html"))

for warning in results.accessibility_warnings:
    print(f"[{warning.rule_id}] {warning.help_text}")
```

## Migration Between Frameworks

See `guidance/framework-migration.md.jinja` for detailed migration guides including:
- Step-by-step procedures
- Content transformation
- Configuration updates
- Rollback procedures

## Troubleshooting

### Sphinx Import Errors
Ensure `sys.path` is configured in `docs/conf.py`:
```python
import sys
sys.path.insert(0, os.path.abspath('..'))
```

### Link Check Failures
External links may fail due to:
- Network connectivity
- Rate limiting
- Transient errors (retry logic helps)

### Build Performance
For large docs (>100 pages):
- Enable incremental builds
- Use caching in CI
- Target: <90 seconds per build

## CI/CD Integration

Documentation builds and validation run automatically via GitHub Actions:

**Workflows**:
- `riso-docs-build.yml`: Build docs, store artifacts (90-day retention)
- `riso-docs-validate.yml`: Link checking, accessibility audits

**Artifacts**:
- Built documentation (compressed, max 500MB)
- Validation reports
- Link check results

## References

- **Module Guide**: `modules/docs-site.md.jinja`
- **Migration Guide**: `guidance/framework-migration.md.jinja`
- **Specification**: `specs/018-docs-sites-overhaul/spec.md`
- **API Contracts**: `specs/018-docs-sites-overhaul/contracts/`

## Support

For issues or questions:
1. Check module documentation in `modules/docs-site.md.jinja`
2. Review framework-specific guides
3. Run validation scripts to identify issues
4. Check CI logs for build failures
