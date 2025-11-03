# Documentation Sites Upgrade Guide

Guide for upgrading documentation configuration in existing Riso projects.

## Upgrading to Enhanced Documentation (Feature 018)

If your project was rendered before the documentation sites overhaul, follow this guide to upgrade.

## What's New

**7 New Configuration Options**:
1. `docs_theme_mode` - Theme appearance control
2. `docs_search_provider` - Search integration options
3. `docs_api_playground` - Interactive API documentation
4. `docs_deploy_target` - Deployment platform selection
5. `docs_versioning` - Multi-version support
6. `docs_interactive_features` - Enhanced features (Mermaid, etc.)
7. `docs_quality_gates` - CI validation

**Enhanced Features**:
- Complete Sphinx scaffolding (fixes build issues)
- Content transformation system (Markdown ↔ RST ↔ MDX)
- Link checking with retry logic
- Accessibility validation (WCAG 2.1 AA)
- Deployment configurations for 4 platforms
- Version management utilities

## Upgrade Steps

### 1. Backup Current Configuration

```bash
# Backup your current documentation
cp -r docs/ docs.backup/
cp -r apps/docs-* apps.backup/ 2>/dev/null || true

# Backup answers file
cp .copier-answers.yml .copier-answers.yml.backup
```

### 2. Update Copier Answers

Add new prompts to `.copier-answers.yml`:

```yaml
# Existing docs_site prompt (keep your current value)
docs_site: sphinx-shibuya  # or fumadocs, docusaurus

# New prompts (add these)
docs_theme_mode: auto
docs_search_provider: local
docs_api_playground: disabled
docs_deploy_target: github-pages
docs_versioning: disabled
docs_interactive_features: disabled
docs_quality_gates: enabled
```

### 3. Run Copier Update

```bash
copier update
```

This will:
- Add new configuration files
- Update documentation templates
- Add validation utilities
- Configure deployment

### 4. Review Generated Files

**Sphinx Projects** - Check:
- `Makefile.docs` - New separate makefile
- `docs/conf.py` - Enhanced configuration
- `docs/api/` - New API reference structure
- `docs/modules/` - Module documentation

**Fumadocs Projects** - Check:
- `apps/docs-fumadocs/next.config.mjs` - Enhanced config
- Search and theme configuration

**Docusaurus Projects** - Check:
- `apps/docs-docusaurus/docusaurus.config.js` - Enhanced config
- Theme and search configuration

### 5. Migrate Content (If Needed)

If switching frameworks, use the transformation system:

```bash
# Example: Sphinx to Fumadocs
python -c "
from shared.docs.transformation import ContentTransformer, ContentFormat
from pathlib import Path

transformer = ContentTransformer()
for rst_file in Path('docs').rglob('*.rst'):
    content = rst_file.read_text()
    result = transformer.transform(
        content,
        ContentFormat.RST,
        ContentFormat.MDX,
        str(rst_file)
    )
    if result.success:
        # Save to new location
        mdx_file = Path('apps/docs-fumadocs/content') / rst_file.relative_to('docs').with_suffix('.mdx')
        mdx_file.parent.mkdir(parents=True, exist_ok=True)
        mdx_file.write_text(result.content)
"
```

### 6. Test Build

**Sphinx**:
```bash
uv sync --group docs
uv run make -f Makefile.docs docs
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

### 7. Validate Configuration

```bash
python scripts/ci/validate_docs_config.py .
```

### 8. Update CI/CD (If Applicable)

New workflows are added:
- `.github/workflows/riso-docs-build.yml`
- `.github/workflows/riso-docs-validate.yml`

Review and commit these workflows.

## Breaking Changes

### Sphinx Projects

**Before**:
```bash
make docs  # May have failed
```

**After**:
```bash
uv run make -f Makefile.docs docs  # Separate makefile
```

### Configuration Location

**Before**:
```yaml
# Only docs_site in .copier-answers.yml
docs_site: fumadocs
```

**After**:
```yaml
# Multiple documentation options
docs_site: fumadocs
docs_theme_mode: auto
docs_search_provider: local
# ... more options
```

## Migration Scenarios

### Scenario 1: Sphinx Not Building

**Problem**: Sphinx documentation fails to build with import errors

**Solution**:
1. Run copier update
2. New `Makefile.docs` fixes target issues
3. Enhanced `conf.py` fixes autodoc configuration
4. Build with: `uv run make -f Makefile.docs docs`

### Scenario 2: Want to Add Search

**Problem**: Need search functionality in documentation

**Solution**:
1. Update `.copier-answers.yml`:
   ```yaml
   docs_search_provider: algolia  # or local, typesense
   ```
2. Run `copier update`
3. For Algolia, set environment variables:
   ```bash
   export ALGOLIA_APP_ID="..."
   export ALGOLIA_API_KEY="..."
   export ALGOLIA_INDEX_NAME="..."
   ```

### Scenario 3: Want Dark Theme

**Problem**: Documentation only has light theme

**Solution**:
1. Update `.copier-answers.yml`:
   ```yaml
   docs_theme_mode: dark  # or auto
   ```
2. Run `copier update`
3. Rebuild documentation

### Scenario 4: Add Mermaid Diagrams

**Problem**: Want to include Mermaid diagrams

**Solution**:
1. Update `.copier-answers.yml`:
   ```yaml
   docs_interactive_features: enabled
   ```
2. Run `copier update`
3. Use Mermaid in your docs:
   ````markdown
   ```mermaid
   graph TD
       A[Start] --> B[Process]
       B --> C[End]
   ```
   ````

## Rollback Procedure

If upgrade causes issues:

### 1. Restore Backups

```bash
# Restore documentation
rm -rf docs/
mv docs.backup/ docs/

# Restore apps (if applicable)
rm -rf apps/docs-*
mv apps.backup/docs-* apps/

# Restore answers
mv .copier-answers.yml.backup .copier-answers.yml
```

### 2. Revert Copier Update

```bash
# Check git history
git log --oneline

# Revert to before update
git revert <commit-hash>
```

### 3. Report Issues

If you encounter problems:
1. Check validation output: `python scripts/ci/validate_docs_config.py .`
2. Review build logs
3. Consult troubleshooting guide in `docs/modules/docs-site.md.jinja`

## Compatibility

**Minimum Requirements**:
- Copier ≥9.1.0
- Python ≥3.11 (for Sphinx)
- Node.js 20 LTS (for Fumadocs/Docusaurus)
- uv ≥0.4 (for Python projects)
- pnpm ≥8 (for Node projects)

**Framework Versions**:
- Sphinx ≥7.4
- Shibuya theme ≥2024.10
- Fumadocs ≥13.0
- Docusaurus ≥3.5

## FAQs

**Q: Do I need to upgrade?**  
A: Optional, but recommended for:
- Sphinx projects with build failures
- Projects wanting search functionality
- Projects needing theme customization
- Projects requiring CI validation

**Q: Will my existing documentation work?**  
A: Yes, existing content remains compatible. Enhanced features are additive.

**Q: Can I mix old and new configuration?**  
A: No, use copier update to ensure consistency.

**Q: What if I don't want quality gates?**  
A: Set `docs_quality_gates: disabled` in answers file.

**Q: How do I switch frameworks?**  
A: See `guidance/framework-migration.md.jinja` for detailed migration guides.

## Support

For issues or questions:
- Review module guide: `template/files/shared/docs/modules/docs-site.md.jinja`
- Check migration guide: `template/files/shared/docs/guidance/framework-migration.md.jinja`
- Validate config: `python scripts/ci/validate_docs_config.py .`
- Review specification: `specs/018-docs-sites-overhaul/spec.md`
