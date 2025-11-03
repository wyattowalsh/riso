# Documentation Prompts Quick Reference

Quick reference for all documentation-related prompts in the Riso template.

## Primary Prompt

### `docs_site`
**Description**: Select documentation framework  
**Default**: `fumadocs`  
**Choices**:
- `none` - No documentation
- `fumadocs` - Next.js + MDX (modern, TypeScript-first)
- `sphinx-shibuya` - Python + RST (autodoc, Python-native)
- `docusaurus` - React + Markdown (feature-rich)

**Example**:
```yaml
docs_site: sphinx-shibuya
```

---

## Configuration Sub-Prompts

### `docs_theme_mode`
**Description**: Default theme appearance  
**Default**: `auto`  
**Choices**: `light`, `dark`, `auto` (system preference)  
**When**: `docs_site != 'none'`

**Example**:
```yaml
docs_theme_mode: dark
```

---

### `docs_search_provider`
**Description**: Search integration provider  
**Default**: `local`  
**Choices**:
- `none` - No search
- `local` - Framework-native (FREE, offline)
- `algolia` - Algolia DocSearch (FREE tier → PAID)
- `typesense` - Typesense Cloud (~$22/month) or self-hosted

**When**: `docs_site != 'none'`

**Example**:
```yaml
docs_search_provider: algolia
```

**Setup** (Algolia):
```bash
export ALGOLIA_APP_ID="your_app_id"
export ALGOLIA_API_KEY="your_search_key"
export ALGOLIA_INDEX_NAME="your_index"
```

---

### `docs_api_playground`
**Description**: Interactive API documentation  
**Default**: `disabled`  
**Choices**: `disabled`, `swagger`, `redoc`, `both`  
**When**: `api_tracks in ['python', 'node', 'python+node']`

**Example**:
```yaml
docs_api_playground: swagger
```

---

### `docs_deploy_target`
**Description**: Documentation deployment platform  
**Default**: `github-pages`  
**Choices**:
- `github-pages` - GitHub Pages (FREE for public repos)
- `netlify` - Netlify (FREE tier: 100GB bandwidth)
- `vercel` - Vercel (FREE tier: unlimited bandwidth)
- `cloudflare` - Cloudflare Pages (FREE tier: 500 builds/month)

**When**: `docs_site != 'none'`

**Example**:
```yaml
docs_deploy_target: vercel
```

---

### `docs_versioning`
**Description**: Multi-version documentation support  
**Default**: `disabled`  
**Choices**: `disabled`, `enabled`  
**When**: `docs_site != 'none'`

**⚠️ Warning**: ADVANCED feature, adds ~2x build time

**Example**:
```yaml
docs_versioning: enabled
```

---

### `docs_interactive_features`
**Description**: Interactive documentation features  
**Default**: `disabled`  
**Choices**: `disabled`, `enabled`  
**When**: `docs_site != 'none'`

**Enables**:
- Mermaid diagram rendering
- Code tabs
- Live API examples
- Interactive playgrounds

**Example**:
```yaml
docs_interactive_features: enabled
```

---

### `docs_quality_gates`
**Description**: Documentation quality validation in CI  
**Default**: `enabled`  
**Choices**: `disabled`, `enabled`  
**When**: `docs_site != 'none'`

**Enables**:
- Link checking with retry logic (3 attempts)
- Accessibility audits (WCAG 2.1 AA)
- Image validation
- Cross-reference validation

**Example**:
```yaml
docs_quality_gates: enabled
```

---

## Common Combinations

### Python Project with Sphinx
```yaml
docs_site: sphinx-shibuya
docs_theme_mode: auto
docs_search_provider: local
docs_api_playground: swagger
docs_deploy_target: github-pages
docs_versioning: disabled
docs_interactive_features: enabled
docs_quality_gates: enabled
```

### Node Project with Fumadocs
```yaml
docs_site: fumadocs
docs_theme_mode: dark
docs_search_provider: algolia
docs_deploy_target: vercel
docs_versioning: disabled
docs_interactive_features: enabled
docs_quality_gates: enabled
```

### Multi-language with Docusaurus
```yaml
docs_site: docusaurus
docs_theme_mode: auto
docs_search_provider: typesense
docs_deploy_target: netlify
docs_versioning: enabled
docs_interactive_features: enabled
docs_quality_gates: enabled
```

### Minimal Documentation
```yaml
docs_site: fumadocs
docs_theme_mode: light
docs_search_provider: none
docs_deploy_target: github-pages
docs_versioning: disabled
docs_interactive_features: disabled
docs_quality_gates: disabled
```

---

## Rendering with Custom Answers

### Using Answer File
```bash
copier copy . output/ --answers-file my-answers.yml
```

### Interactive Prompt
```bash
copier copy . output/
# Follow prompts...
```

### Command Line Override
```bash
copier copy . output/ \
  -d docs_site=sphinx-shibuya \
  -d docs_theme_mode=dark \
  -d docs_search_provider=local
```

---

## Validation

After rendering, validate documentation configuration:

```bash
cd output/
python scripts/ci/validate_docs_config.py .
```

---

## Build Commands

### Sphinx
```bash
uv sync --group docs
uv run make -f Makefile.docs docs
uv run make -f Makefile.docs linkcheck
```

### Fumadocs
```bash
pnpm install
pnpm --filter docs-fumadocs dev    # Development
pnpm --filter docs-fumadocs build  # Production
```

### Docusaurus
```bash
pnpm install
pnpm --filter docs-docusaurus start  # Development
pnpm --filter docs-docusaurus build  # Production
```

---

## See Also

- **Module Guide**: `template/files/shared/docs/modules/docs-site.md.jinja`
- **Migration Guide**: `template/files/shared/docs/guidance/framework-migration.md.jinja`
- **Full Specification**: `specs/018-docs-sites-overhaul/spec.md`
- **Contracts**: `specs/018-docs-sites-overhaul/contracts/prompts.yml`
