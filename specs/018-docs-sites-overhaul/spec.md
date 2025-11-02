# Feature Specification: Documentation Sites Overhaul

**Feature Branch**: `018-docs-sites-overhaul`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "A full enhancement of the docs sites options and configurations, extending, enriching, and improving the docs site parts of riso"

## Clarifications

### Session 2025-11-02

- Q: When documentation content transformation fails (unsupported syntax in target framework), what should the build behavior be? → A: Fail the build immediately with actionable error message showing file/line and suggesting manual override
- Q: How should the build handle temporarily unavailable external links during CI link checking? → A: Retry external links 3 times with exponential backoff, fail only if still unreachable
- Q: What accessibility standard level should documentation builds validate against, and should violations block the build? → A: WCAG 2.1 Level AA (standard) - violations logged as warnings only

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sphinx Documentation Builds Successfully (Priority: P1)

A Python-focused team renders a project with Sphinx-Shibuya docs and can successfully build documentation locally and in CI without manual fixes, with working link checking and API documentation generation.

**Why this priority**: Sphinx is currently failing smoke tests with missing Makefile targets and import errors, blocking Python teams from using the Python-native documentation option.

**Independent Test**: Render with `docs_site=sphinx-shibuya`, run `uv run make -f Makefile.docs docs` and `uv run make -f Makefile.docs linkcheck`, verify HTML output generates without errors and link checking completes successfully.

**Acceptance Scenarios**:

1. **Given** a fresh render with `docs_site=sphinx-shibuya` (zero existing documentation), **When** the user runs `uv run make -f Makefile.docs docs`, **Then** Sphinx builds HTML documentation without missing imports or configuration errors, generating default documentation structure with index page, module navigation, and placeholder content
2. **Given** Sphinx documentation is built, **When** the user runs `uv run make -f Makefile.docs linkcheck`, **Then** the link checker validates all internal and external links without 404 errors
3. **Given** API modules are enabled with Sphinx docs, **When** Sphinx builds, **Then** API reference pages are auto-generated from docstrings using sphinx-autodoc

---

### User Story 2 - Enhanced Documentation Configuration Options (Priority: P1)

Template users can configure documentation site behavior through structured prompt options including theme customization, search provider selection, API documentation mode, and deployment target without editing template files.

**Why this priority**: Current docs implementations have hardcoded configurations, forcing users to manually edit generated files to customize themes, enable search, or adjust build outputs.

**Independent Test**: Render with extended prompts like `docs_theme_mode=dark`, `docs_search_provider=algolia`, `docs_deploy_target=vercel`, verify configuration files reflect choices without placeholder comments.

**Acceptance Scenarios**:

1. **Given** a user selects `docs_theme_mode=dark` during render (fresh project, no existing config), **When** the docs site builds, **Then** the default theme uses dark mode without requiring manual CSS edits
2. **Given** a user selects `docs_search_provider=algolia` (zero existing search configuration), **When** the docs site renders, **Then** Algolia search configuration is scaffolded with environment variable placeholders and integration instructions
3. **Given** a user selects `docs_deploy_target=netlify` (new deployment), **When** the render completes, **Then** netlify.toml configuration is generated with optimal build settings

---

### User Story 3 - Unified Documentation Content Management (Priority: P2)

Teams can manage shared documentation content (quickstart, module guides, API references) in a centralized location that renders correctly across all three documentation frameworks without duplication.

**Why this priority**: Current implementation duplicates content between template docs and rendered project docs, creating maintenance burden and sync drift.

**Independent Test**: Update `docs/modules/quality.md.jinja`, re-render all three doc variants, verify identical content appears correctly formatted in Fumadocs MDX, Sphinx RST, and Docusaurus Markdown.

**Acceptance Scenarios**:

1. **Given** shared module documentation exists in `template/files/shared/docs/modules/`, **When** any docs variant renders, **Then** module pages are transformed to the target format (MDX/RST/MD) with working cross-references
2. **Given** API documentation is enabled, **When** docs build, **Then** API reference sections are auto-generated from code annotations in the appropriate format for each framework
3. **Given** documentation includes code examples, **When** docs render, **Then** syntax highlighting and copy buttons work consistently across all frameworks

---

### User Story 4 - Interactive Documentation Features (Priority: P2)

Users can enable interactive documentation features including live API playgrounds, interactive code examples, tabbed content, and embedded diagrams through prompt configuration without manual component creation.

**Why this priority**: Modern documentation sites require interactive elements for better developer experience, but current implementations provide only static content.

**Independent Test**: Render with `docs_interactive_features=enabled`, verify API playground, runnable code blocks, and Mermaid diagrams render correctly in all doc frameworks.

**Acceptance Scenarios**:

1. **Given** `docs_interactive_features=enabled` with FastAPI, **When** docs build, **Then** Swagger UI or Redoc API playground is embedded in documentation with live testing capability
2. **Given** documentation includes Python code blocks, **When** interactive features are enabled, **Then** code blocks have "Run" buttons that execute in browser using Pyodide
3. **Given** documentation includes Mermaid diagram syntax, **When** docs render, **Then** diagrams are rendered as interactive SVGs with zoom and pan capabilities

---

### User Story 5 - Documentation Versioning and Multi-Version Support (Priority: P3)

Projects can maintain documentation for multiple versions simultaneously with version selector UI, allowing users to view docs for different releases without losing historical documentation.

**Why this priority**: Mature projects need to maintain docs for multiple stable versions, but current implementation only supports single-version documentation.

**Independent Test**: Render with `docs_versioning=enabled`, simulate multiple release branches, verify version selector appears and switches between documentation versions correctly.

**Acceptance Scenarios**:

1. **Given** `docs_versioning=enabled`, **When** documentation builds for version 1.0.0, **Then** version selector UI is scaffolded with configuration for managing multiple doc versions
2. **Given** multiple doc versions exist, **When** users browse documentation, **Then** version selector allows switching between versions with URL preservation
3. **Given** new version is released, **When** docs rebuild, **Then** latest version becomes default while previous versions remain accessible

---

### Edge Cases

- When `docs_site=none` is selected, all documentation scaffolding is omitted including build scripts, dependencies, and CI jobs, with clear README guidance on re-enabling docs later
- When `api_tracks=python+node` is enabled, documentation must aggregate API references from both FastAPI and Fastify without conflicts in navigation structure
- When theme assets fail to load (CDN outage, version mismatch), documentation must gracefully degrade to readable plain text without breaking site navigation
- When search provider credentials are missing or invalid, documentation builds successfully with search disabled and clear instructions for enabling search in deployment
- When documentation source files contain invalid syntax (malformed RST, broken MDX), build process provides actionable error messages with file/line references rather than cryptic stack traces
- When documentation exceeds 1000 pages or 10GB total size, build system must apply pagination, lazy loading, and warn about potential performance degradation; extremely large docs (>5000 pages) should trigger recommendation to use subset/modular documentation strategy
- When network is unavailable during build (air-gapped environments), documentation must build successfully using only local dependencies with clear indicators for features requiring network access (external links, CDN assets, hosted search)
- When documentation contains special characters, unicode, or right-to-left (RTL) content, transformation system must preserve character encoding and directionality across all frameworks without corruption
- When search provider rate limits are exceeded or quotas exhausted, search functionality must gracefully degrade with cached results and retry logic; users must receive clear notification of temporary search unavailability
- When multiple documentation builds run concurrently (CI matrix, parallel versions), builds must not conflict on shared resources (cache directories, temporary files, port bindings) through unique workspace isolation
- When documentation hotfix is needed without full rebuild, incremental build system must support targeted page regeneration with automatic dependency invalidation for affected cross-references
- When API schemas change affecting documentation examples, build must validate all code samples against current API contracts and flag outdated examples with migration suggestions

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Template MUST expose extended `docs_site` prompt with configuration sub-prompts for theme mode (light/dark/auto), search provider (none/local/algolia/typesense), API documentation style (swagger/redoc/both), and deployment target (github-pages/netlify/vercel/cloudflare); all generated configurations MUST use environment variables for sensitive credentials (ALGOLIA_APP_ID, ALGOLIA_API_KEY, TYPESENSE_API_KEY, DEPLOY_TOKEN) with placeholder values and clear documentation on required secrets

- **FR-002**: Sphinx-Shibuya implementation MUST generate complete Makefile.docs with targets for `docs`, `linkcheck`, `doctest`, and `clean-docs`, all executable via `uv run make -f Makefile.docs <target>`

- **FR-003**: Sphinx configuration MUST include sphinx-autodoc extension properly configured to generate API reference pages from Python docstrings with type hint rendering

- **FR-004**: All three documentation frameworks MUST support consistent metadata frontmatter with the following fields: `title` (string, required, max 100 chars), `description` (string, optional, max 300 chars), `sidebar_position` (integer, optional, 1-9999), `tags` (array of strings, optional, max 10 tags), `slug` (string, optional, URL-safe), `hide_table_of_contents` (boolean, optional), `custom_edit_url` (string, optional, valid URL); frontmatter MUST transform correctly to each framework's format (reStructuredText (RST) field lists for Sphinx with `:fieldname: value` syntax, YAML frontmatter for MDX/Fumadocs, Docusaurus-compatible YAML) per transformation rules in contracts/transformation-api.md; validation MUST reject: unsupported fields, type mismatches, invalid URLs, non-URL-safe slugs

- **FR-005**: Documentation builds MUST validate successfully before project render completes, failing fast with actionable error messages formatted as `[ERROR] {component}:{check}: {description}\nRequired: {missing_items}\nDocumentation: {docs_url}` if critical docs dependencies or configurations are missing

- **FR-006**: Fumadocs implementation MUST scaffold Next.js 15 app with App Router, TypeScript strict mode enabled (`"strict": true` in tsconfig.json), zero `any` types in generated code, proper TypeScript types with 100% type coverage validation, and MDX content layer using Fumadocs' native content API

- **FR-007**: Docusaurus implementation MUST configure v3 with TypeScript, proper docusaurus.config.ts, and plugin ecosystem for versioning and search when requested

- **FR-008**: All documentation frameworks MUST support Mermaid diagram rendering out-of-box with consistent syntax and interactive pan/zoom capabilities

- **FR-009**: Template MUST provide shared documentation content transformation system that converts canonical Markdown to framework-specific formats (reStructuredText (RST) for Sphinx, MDX for Fumadocs, enhanced Markdown for Docusaurus); transformation failures MUST halt the build with actionable error messages formatted as `[ERROR] {file_path}:{line_number}: {error_type} - {description}\nSuggestion: {fix_guidance}` indicating file path, line number, error type (UNSUPPORTED_SYNTAX, MALFORMED_INPUT, ENCODING_ERROR, INVALID_REFERENCE), description, and manual override instructions; transformation system MUST handle encoding issues (UTF-8 validation), malformed input (incomplete code blocks, invalid frontmatter), and unsupported syntax (framework-specific directives in shared content); canonical Markdown subset MUST support: headings (#-######), paragraphs, code blocks with language tags, inline code, bold/italic/strikethrough, links (inline and reference), images, ordered/unordered lists, blockquotes, tables (GFM), horizontal rules, HTML comments; MUST reject: raw HTML tags (except in MDX output), framework-specific directives in shared content (e.g., Sphinx :doc:, Docusaurus imports), JavaScript/script tags

- **FR-010**: When `docs_search_provider` is set to local/algolia/typesense, documentation MUST scaffold appropriate search integration with example configuration and environment variable templates

- **FR-011**: When `docs_api_playground=enabled` with FastAPI/Fastify APIs, documentation MUST embed interactive API exploration UI (Swagger UI or Redoc) with working "Try it out" functionality including: (1) CORS configuration allowing documentation domain origins, (2) authentication support via environment variables (API_KEY, BEARER_TOKEN) with secure credential injection, (3) request/response examples with editable payloads, (4) rate limiting indicators and error handling for 429/503 responses, (5) graceful degradation when API backend is unavailable (showing static schema with "API offline" notice)

- **FR-012**: Documentation CI jobs MUST build docs as artifacts with 90-day retention (maximum 500MB per artifact with automatic compression), perform link checking with retry logic (3 attempts with exponential backoff delays of 1s, 2s, 4s for external links), validate internal references, and fail builds on broken links or missing pages after retries exhausted; CI MUST implement rollback procedures on deployment failure including: (1) preserve previous successful build artifacts, (2) revert deployment to last known good version, (3) emit deployment failure notification with rollback status, (4) retain failed build logs for debugging

- **FR-013**: Quality suite MUST extend to validate documentation builds, checking for broken links, missing images, invalid cross-references, and WCAG 2.1 Level AA accessibility violations (logged as warnings without blocking builds); validation MUST produce structured reports including: (1) link check results with retry history, (2) image reference validation with size/format checks, (3) cross-reference completeness for internal navigation, (4) accessibility violations with WCAG criterion references and remediation guidance

- **FR-014**: Upgrade guide MUST document migration paths between documentation frameworks with automated comparison showing content drift and configuration differences

- **FR-015**: When `docs_versioning=enabled`, template MUST scaffold version management system compatible with selected framework's versioning approach (mike for Sphinx, native versioning for Docusaurus, custom for Fumadocs)

- **FR-016**: Documentation build system MUST implement caching for unchanged content including: (1) dependency caching for framework packages (Node modules, Python packages), (2) incremental builds detecting file changes via content hashing, (3) cached transformation results invalidated on source file modification, (4) cache hit/miss metrics logged for optimization; builds MUST complete in <20 seconds for unchanged documentation (cache hit), <90 seconds for full rebuild (cache miss) per SC-004

- **FR-017**: Template MUST provide migration support including: (1) detection of legacy documentation configurations in existing renders, (2) automated upgrade scripts transforming old config formats to new prompt-based system, (3) migration validation comparing old and new outputs for content parity, (4) rollback capability preserving original configuration files; upgrade guide MUST document: breaking changes, migration steps with examples, framework-specific migration patterns, validation procedures, troubleshooting common issues

- **FR-018**: Documentation build system MUST support preview environments separate from production including: (1) preview-specific build configurations with draft content visibility, (2) authentication-protected preview deployments with temporary access tokens, (3) preview-to-production promotion workflows with validation gates, (4) automatic preview cleanup after 30 days or merge, (5) preview URL generation with unique identifiers (PR number, branch name, commit SHA); preview builds MUST complete in <60 seconds for incremental changes

### Non-Functional Requirements

- **NFR-001**: Documentation build system MUST maintain <10% performance degradation for projects growing from 10 to 1000 pages; builds MUST scale linearly with content size using incremental build optimization

- **NFR-002**: All documentation deployment credentials and API keys MUST be stored as environment variables, never committed to version control; generated configuration files MUST use placeholder values with validation warnings if production secrets are detected

- **NFR-003**: Documentation sites MUST maintain WCAG 2.1 Level AA compliance including: keyboard navigation for all interactive elements, screen reader compatibility, minimum 4.5:1 color contrast ratio for normal text, proper heading hierarchy, descriptive link text, form labels and error messages

- **NFR-004**: Template code for documentation generation MUST maintain ≥80% test coverage with unit tests for transformation logic, integration tests for full build workflows, and smoke tests for all supported framework variants

- **NFR-005**: Documentation build metrics MUST be collected including: build duration, cache hit rate, link check results, artifact size, transformation error count; metrics MUST be exportable for monitoring dashboards and trend analysis

- **NFR-006**: Documentation sites MUST maintain 99.5% build reliability (successful builds without manual intervention) measured across 200+ test renders per month; build failures MUST be categorized by root cause (dependency, configuration, content, infrastructure)

### Template Prompts & Variants

- **Prompt**: `docs_site` — **Type**: Baseline — **Default**: `fumadocs` — **Choices**: `none`, `fumadocs`, `sphinx-shibuya`, `docusaurus` — **Implication**: Selects documentation framework and triggers sub-prompts for framework-specific configuration

- **Prompt**: `docs_theme_mode` — **Type**: Optional — **Default**: `auto` — **Choices**: `light`, `dark`, `auto` — **When**: `docs_site != none` — **Implication**: Configures default theme appearance with system preference detection for auto mode

- **Prompt**: `docs_search_provider` — **Type**: Optional — **Default**: `local` — **Choices**: `none`, `local`, `algolia`, `typesense` — **When**: `docs_site != none` — **Implication**: Scaffolds search integration with provider-specific configuration and API key placeholders

- **Prompt**: `docs_api_playground` — **Type**: Optional — **Default**: `disabled` — **Choices**: `disabled`, `swagger`, `redoc`, `both` — **When**: `api_tracks in ['python', 'node', 'python+node']` — **Implication**: Embeds interactive API documentation with live request testing

- **Prompt**: `docs_deploy_target` — **Type**: Optional — **Default**: `github-pages` — **Choices**: `github-pages`, `netlify`, `vercel`, `cloudflare` — **When**: `docs_site != none` — **Implication**: Generates deployment configuration files and CI workflow for selected platform

- **Prompt**: `docs_versioning` — **Type**: Optional — **Default**: `disabled` — **Choices**: `disabled`, `enabled` — **When**: `docs_site != none` — **Implication**: Scaffolds multi-version documentation support with version selector UI

- **Prompt**: `docs_interactive_features` — **Type**: Optional — **Default**: `disabled` — **Choices**: `disabled`, `enabled` — **When**: `docs_site != none` — **Implication**: Enables runnable code blocks, embedded playgrounds, and enhanced interactive components

### Key Entities

- **DocumentationFramework**: Defines selected framework, build commands, configuration files, content format, and plugin ecosystem
- **DocumentationConfiguration**: Captures theme mode, search provider, API playground style, deployment target, versioning preference, and interactive features toggle
- **SharedDocumentationContent**: Represents canonical documentation source that transforms to framework-specific formats via content pipeline
- **DocumentationBuildArtifact**: Built documentation output stored in CI with metadata (framework, version, build timestamp, size, validation results)
- **DocumentationValidationReport**: Results of link checking, reference validation, accessibility scan, and spell checking across all documentation pages
- **DocumentationSearchIndex**: Search provider configuration, indexed content, update timestamp, and query performance metrics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of documentation variants (Fumadocs, Sphinx, Docusaurus) build successfully on first render without manual configuration fixes; validated by automated smoke tests checking: (1) zero build errors in stdout/stderr, (2) presence of expected output files (HTML/assets), (3) navigation structure completeness, (4) absence of placeholder/TODO comments in generated configs

- **SC-002**: Documentation link checking completes with 0 broken internal links and <2% broken external links (after 3 retry attempts with exponential backoff, excluding intentionally offline references) across all sample renders; measured per-variant with detailed reporting of link status (200, 404, timeout, retry count)

- **SC-003**: Sphinx-Shibuya smoke tests achieve 100% pass rate (currently 0% - all tests failing) within 2 weeks of implementation completion

- **SC-004**: Documentation build time stays under 90 seconds for projects with <100 Markdown source files across all frameworks on standard GitHub Actions runners

- **SC-005**: 95% of users complete documentation customization (theme, search, deployment) through prompts alone without editing template-generated files; measured through user surveys (n≥20) and telemetry tracking manual file edits in rendered projects within 30 days of creation

- **SC-006**: Documentation search returns relevant results within 200ms for local search and 500ms for hosted search providers (Algolia, Typesense); measured at p95 latency with >90% query relevance score on standardized test corpus

- **SC-007**: Interactive API playgrounds successfully execute 98% of valid API requests without CORS or authentication errors in docs preview environment; measured using test corpus of 50+ request scenarios across GET/POST/PUT/DELETE with authentication variations

- **SC-008**: Documentation versioning UI allows switching between versions in <1 second with correct content loading and URL state management; measured as time from version selection to content render completion with no JavaScript errors

## Assumptions

- Node.js 20 LTS with pnpm ≥8 and Python 3.11+ with uv remain required for documentation builds across all frameworks
- Documentation content is primarily authored in Markdown-compatible formats with framework-specific extensions as needed
- Teams deploying documentation have access to environment variables for configuring API keys, search credentials, and deployment secrets
- Fumadocs, Sphinx Shibuya, and Docusaurus remain actively maintained with stable APIs for configuration and theming
- Documentation versioning is managed through Git tags/branches aligned with software release process
- Search providers (Algolia, Typesense) offer free tiers sufficient for small-to-medium documentation sites

## Dependencies & External Inputs

- Fumadocs ≥13.0.0 with Next.js 15 and React 18+ for React-based documentation framework
- Sphinx ≥7.4 with Shibuya theme ≥2024.10, sphinx-autodoc, sphinx-linkcheck extensions for Python documentation
- Docusaurus ≥3.5 with TypeScript support and plugin ecosystem for feature-rich documentation
- Search provider SDKs: @algolia/client-search ≥4.0, typesense ≥1.7, or framework-native search implementations
- Mermaid ≥10.0 for diagram rendering across all frameworks
- Existing quality automation (`scripts/ci/render_matrix.py`, `scripts/ci/record_module_success.py`) for smoke testing
- Documentation deployment platforms (GitHub Pages, Netlify, Vercel, Cloudflare Pages) with CI/CD integration

## Risks & Mitigations

- **Risk**: Framework-specific syntax divergence makes content transformation complex
  **Mitigation**: Establish canonical Markdown subset with clear transformation rules; automate conversion with tested pipelines; maintain framework-specific override capability

- **Risk**: Sphinx Makefile targets vary between Python projects and documentation projects
  **Mitigation**: Generate dedicated docs Makefile separate from Python build Makefile; use uv run prefix for all targets; test all targets in smoke suite

- **Risk**: Search provider costs escalate for projects with large documentation sets
  **Mitigation**: Default to local search; clearly document search provider limits; provide cost estimation in prompts

- **Risk**: Interactive features increase page weight and load time
  **Mitigation**: Lazy-load interactive components; make features opt-in; measure and enforce performance budgets

- **Risk**: Version management complexity overwhelms small projects
  **Mitigation**: Make versioning opt-in; provide simple "latest only" default; document version cleanup strategies

- **Risk**: Multiple documentation frameworks increase maintenance burden
  **Mitigation**: Extract shared logic into template macros; automate cross-framework testing; deprecate poorly-adopted frameworks after 6-month evaluation

## Out of Scope

- Custom documentation theme development beyond configuring official framework themes
- Documentation content authoring tools or CMS integrations (users edit Markdown files directly)
- Automated documentation generation from code comments beyond standard Sphinx autodoc and TypeDoc
- Real-time collaborative editing of documentation content
- Documentation analytics beyond basic page view metrics from deployment platforms
- Multi-language documentation and internationalization (i18n) support
- Documentation payment walls or access control systems
- Integration with external documentation hosting services (ReadTheDocs, GitBook)
