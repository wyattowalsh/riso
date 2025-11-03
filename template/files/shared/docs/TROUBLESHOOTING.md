# Documentation Troubleshooting Guide

Common issues and solutions for documentation in Riso projects.

## Build Failures

### Sphinx: Import Errors

**Symptom**:
```
ImportError: No module named 'mypackage'
WARNING: autodoc: failed to import module 'mypackage'
```

**Solution**:
1. Verify `sys.path` in `docs/conf.py`:
   ```python
   import sys
   sys.path.insert(0, os.path.abspath('..'))
   ```

2. Ensure package is installed:
   ```bash
   uv sync
   ```

3. Verify package structure:
   ```bash
   python -c "import mypackage; print(mypackage.__file__)"
   ```

### Sphinx: Missing Dependencies

**Symptom**:
```
Extension error:
Could not import extension sphinx.ext.autodoc
```

**Solution**:
```bash
# Install documentation dependencies
uv sync --group docs

# Verify Sphinx is installed
uv run sphinx-build --version
```

### Fumadocs: Build Timeout

**Symptom**:
```
Error: Build timed out after 10 minutes
```

**Solution**:
1. Clear cache:
   ```bash
   rm -rf apps/docs-fumadocs/.next
   pnpm --filter docs-fumadocs build
   ```

2. Check for circular dependencies in MDX files

3. Reduce page count or split into multiple builds

### Docusaurus: Plugin Errors

**Symptom**:
```
Error: Cannot find module '@docusaurus/theme-mermaid'
```

**Solution**:
```bash
# Reinstall dependencies
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## Link Check Failures

### External Links Timing Out

**Symptom**:
```
[broken] https://example.com/api (timeout after 10s)
```

**Causes**:
- Network connectivity issues
- Rate limiting
- Server temporarily down

**Solution**:
1. Link checker already retries 3 times with exponential backoff
2. Check if link is actually broken:
   ```bash
   curl -I https://example.com/api
   ```
3. If transient, ignore in CI temporarily
4. Update link if permanently moved

### Internal Links Broken

**Symptom**:
```
[broken] ../api/reference.html (file not found)
```

**Solution**:
1. Verify target file exists:
   ```bash
   ls docs/api/reference.rst
   ```

2. Check relative path from source file

3. For Sphinx, use `:doc:` directive:
   ```rst
   See :doc:`../api/reference` for details
   ```

## Theme Issues

### Dark Mode Not Working

**Symptom**: Theme doesn't switch to dark mode

**Solution**:
1. Check configuration in `.copier-answers.yml`:
   ```yaml
   docs_theme_mode: dark  # or auto
   ```

2. Rebuild documentation after changing theme:
   ```bash
   # Sphinx
   uv run make -f Makefile.docs clean-docs
   uv run make -f Makefile.docs docs
   
   # Fumadocs/Docusaurus
   rm -rf apps/docs-*/out apps/docs-*/build
   pnpm --filter docs-* build
   ```

3. Clear browser cache

### Custom CSS Not Applied

**Symptom**: Custom styles don't appear

**Solution**:
1. **Sphinx**: Place CSS in `docs/_static/`:
   ```bash
   mkdir -p docs/_static
   echo "body { color: red; }" > docs/_static/custom.css
   ```

2. Add to `conf.py`:
   ```python
   html_static_path = ['_static']
   html_css_files = ['custom.css']
   ```

3. Rebuild documentation

## Search Issues

### Algolia Search Not Working

**Symptom**: Search bar doesn't appear or returns no results

**Solution**:
1. Verify API keys are set:
   ```bash
   echo $ALGOLIA_APP_ID
   echo $ALGOLIA_API_KEY
   echo $ALGOLIA_INDEX_NAME
   ```

2. Check configuration in framework config file

3. Verify you've been approved for Algolia DocSearch (free tier)

4. Test API key:
   ```bash
   curl -H "X-Algolia-API-Key: $ALGOLIA_API_KEY" \
        -H "X-Algolia-Application-Id: $ALGOLIA_APP_ID" \
        "https://$ALGOLIA_APP_ID-dsn.algolia.net/1/indexes"
   ```

### Local Search Not Indexing

**Symptom**: Local search returns no results

**Solution**:
1. Rebuild documentation completely
2. Clear browser cache
3. Check search index file exists:
   - Sphinx: `_build/html/searchindex.js`
   - Fumadocs: Built-in indexing
   - Docusaurus: Built-in indexing

## Performance Issues

### Slow Build Times

**Symptom**: Build takes longer than 90 seconds

**Solution**:
1. **Enable caching** (CI):
   ```yaml
   - uses: actions/cache@v4
     with:
       path: |
         ~/.cache/uv
         node_modules
       key: ${{ runner.os }}-docs-${{ hashFiles('**/package.json') }}
   ```

2. **Incremental builds**:
   - Sphinx: Use `sphinx-autobuild` for development
   - Fumadocs: Next.js incremental builds (automatic)
   - Docusaurus: `--incremental` flag

3. **Reduce page count**: Split large docs into multiple sites

4. **Optimize images**: Compress images before committing

### Large Artifact Size

**Symptom**: Build artifact exceeds 500MB

**Solution**:
1. Check artifact size:
   ```bash
   du -sh _build/html
   ```

2. **Remove unnecessary files**:
   - Delete source `.rst`/`.md` files from output
   - Compress images
   - Remove unused assets

3. **Configure exclusions**:
   ```python
   # Sphinx conf.py
   exclude_patterns = ['_build', '**.ipynb_checkpoints']
   ```

## Accessibility Issues

### WCAG Warnings

**Symptom**: Accessibility validator reports warnings

**Note**: Warnings are non-blocking per spec

**Common Issues**:
1. **Images without alt text**:
   ```markdown
   ![Description of image](path/to/image.png)
   ```

2. **Heading hierarchy**:
   - Use only one `<h1>` per page
   - Don't skip heading levels (h1 → h3)

3. **Form labels**:
   ```html
   <label for="search">Search:</label>
   <input id="search" type="text">
   ```

## Version Management

### Version Selector Not Appearing

**Symptom**: Version dropdown doesn't show

**Solution**:
1. Verify versioning is enabled:
   ```yaml
   docs_versioning: enabled
   ```

2. Check `versions.json` exists and is valid

3. For Sphinx: Ensure `mike` is configured

4. Rebuild with versioning enabled

### Wrong Version Displayed

**Symptom**: Shows wrong version number

**Solution**:
1. Check version detection:
   ```bash
   git describe --tags --abbrev=0
   ```

2. Update `versions.json` manually if needed

3. Set `DOCS_VERSION` environment variable:
   ```bash
   export DOCS_VERSION="1.2.3"
   ```

## Deployment Issues

### GitHub Pages 404

**Symptom**: Documentation deployed but shows 404

**Solution**:
1. Check GitHub Pages settings in repository

2. Verify `gh-pages` branch exists

3. Ensure `index.html` is in root of deployment

4. Check workflow succeeded:
   ```bash
   gh run list --workflow=deploy-docs.yml
   ```

### Netlify Build Failed

**Symptom**: Netlify deploy fails

**Solution**:
1. Check build logs in Netlify dashboard

2. Verify `netlify.toml` configuration

3. Ensure build command is correct:
   ```toml
   [build]
     command = "pnpm install && pnpm run build"
   ```

4. Check Node/Python versions match requirements

## Content Transformation

### Transformation Errors

**Symptom**:
```
[ERROR] docs/api.md:42: UNSUPPORTED_SYNTAX
```

**Solution**:
1. Review error message for specific issue

2. Check transformation compatibility:
   - Use canonical Markdown subset
   - Avoid framework-specific syntax in source

3. Manual override if needed:
   - Transform problematic sections manually
   - Use framework-specific alternatives

4. Skip transformation for specific files:
   ```python
   # Add to transformation config
   skip_files = ['problematic.md']
   ```

## Debugging Tips

### Enable Verbose Logging

**Sphinx**:
```bash
uv run sphinx-build -v -W docs/ _build/html/
```

**Fumadocs**:
```bash
pnpm --filter docs-fumadocs build --debug
```

**Docusaurus**:
```bash
pnpm --filter docs-docusaurus build --verbose
```

### Check Configuration

```bash
# Validate documentation config
python scripts/ci/validate_docs_config.py .

# Check prompt values
cat .copier-answers.yml | grep docs_
```

### Test Locally

Always test builds locally before pushing:

```bash
# Use docs helper script
./scripts/docs-helper.sh setup
./scripts/docs-helper.sh build
./scripts/docs-helper.sh validate
```

## Getting Help

If issues persist:

1. **Check logs**: Review build and validation logs thoroughly
2. **Search issues**: Check GitHub issues for similar problems
3. **Validation**: Run `python scripts/ci/validate_docs_config.py`
4. **Documentation**: Review module guides in `docs/modules/`
5. **Reset**: Try clean build after removing all artifacts

## Common Error Messages

### "No module named 'sphinx'"
**Solution**: `uv sync --group docs`

### "Cannot find module '@docusaurus/core'"
**Solution**: `pnpm install`

### "Error: ENOSPC: System limit for number of file watchers reached"
**Solution**: Increase inotify watchers (Linux):
```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### "Module parse failed: Unexpected token"
**Solution**: Check Node.js version (requires 20 LTS)

### "Permission denied" when running scripts
**Solution**: `chmod +x scripts/*.sh`

## Prevention

### Pre-commit Checks

Run validation before committing:
```bash
./scripts/docs-helper.sh validate
```

### CI Integration

Ensure CI workflows are enabled:
- `riso-docs-build.yml`
- `riso-docs-validate.yml`

### Documentation

Keep documentation dependencies up to date:
```bash
# Python
uv sync --upgrade --group docs

# Node
pnpm update
```
