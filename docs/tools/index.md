# Tool Catalog

```{raw} html
<!-- Hero Section -->
<div class="tool-catalog-hero">
  <div class="hero-content">
    <h2 class="hero-title">
      <iconify-icon icon="tabler:puzzle" width="32" height="32"></iconify-icon>
      Explore the Toolkit
    </h2>
    <p class="hero-description">
      Discover 32 carefully curated tools powering Riso templates — from blazing-fast linters to intelligent validators, AI agent skills, and production-ready frameworks.
    </p>

    <!-- Stats Grid -->
    <div class="tool-stats">
      <div class="stat-card">
        <div class="stat-number">32</div>
        <div class="stat-label">Tools</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">7</div>
        <div class="stat-label">Categories</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">12</div>
        <div class="stat-label">Types</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">6</div>
        <div class="stat-label">Validators</div>
      </div>
    </div>

    <!-- Quick Filter Pills -->
    <div class="quick-filters" role="group" aria-label="Quick category filters">
      <button class="filter-pill" data-category="" onclick="setQuickFilter('')">
        <iconify-icon icon="tabler:apps" width="16" height="16"></iconify-icon>
        All <span class="pill-count">32</span>
      </button>
      <button class="filter-pill" data-category="ai-skills" onclick="setQuickFilter('ai-skills')">
        <iconify-icon icon="tabler:brain" width="16" height="16"></iconify-icon>
        AI Skills <span class="pill-count">2</span>
      </button>
      <button class="filter-pill" data-category="riso-scripts" onclick="setQuickFilter('riso-scripts')">
        <iconify-icon icon="tabler:terminal-2" width="16" height="16"></iconify-icon>
        Scripts <span class="pill-count">6</span>
      </button>
      <button class="filter-pill" data-category="riso-validators" onclick="setQuickFilter('riso-validators')">
        <iconify-icon icon="tabler:shield-check" width="16" height="16"></iconify-icon>
        Validators <span class="pill-count">6</span>
      </button>
      <button class="filter-pill" data-category="quality" onclick="setQuickFilter('quality')">
        <iconify-icon icon="tabler:sparkles" width="16" height="16"></iconify-icon>
        Quality <span class="pill-count">6</span>
      </button>
      <button class="filter-pill" data-category="packages" onclick="setQuickFilter('packages')">
        <iconify-icon icon="tabler:package" width="16" height="16"></iconify-icon>
        Packages <span class="pill-count">3</span>
      </button>
      <button class="filter-pill" data-category="container-ci" onclick="setQuickFilter('container-ci')">
        <iconify-icon icon="tabler:brand-docker" width="16" height="16"></iconify-icon>
        CI/CD <span class="pill-count">2</span>
      </button>
      <button class="filter-pill" data-category="optional-modules" onclick="setQuickFilter('optional-modules')">
        <iconify-icon icon="tabler:plug" width="16" height="16"></iconify-icon>
        Modules <span class="pill-count">6</span>
      </button>
    </div>
  </div>
</div>

<!-- Featured Tools -->
<div class="featured-section">
  <div class="featured-header">
    <iconify-icon icon="tabler:star-filled" width="20" height="20"></iconify-icon>
    <h3 class="featured-title">Most Popular</h3>
  </div>
  <div class="featured-grid">
    <a href="ruff.html" class="featured-card">
      <div class="mini-icon"><iconify-icon icon="simple-icons:ruff" width="18" height="18"></iconify-icon></div>
      <div class="featured-card-content">
        <div class="featured-card-name">Ruff</div>
        <div class="featured-card-desc">Lightning-fast Python linter</div>
      </div>
    </a>
    <a href="uv.html" class="featured-card">
      <div class="mini-icon"><iconify-icon icon="simple-icons:astral" width="18" height="18"></iconify-icon></div>
      <div class="featured-card-content">
        <div class="featured-card-name">uv</div>
        <div class="featured-card-desc">Blazing fast package manager</div>
      </div>
    </a>
    <a href="pytest.html" class="featured-card">
      <div class="mini-icon"><iconify-icon icon="simple-icons:pytest" width="18" height="18"></iconify-icon></div>
      <div class="featured-card-content">
        <div class="featured-card-name">pytest</div>
        <div class="featured-card-desc">Python testing framework</div>
      </div>
    </a>
    <a href="fastapi.html" class="featured-card">
      <div class="mini-icon"><iconify-icon icon="simple-icons:fastapi" width="18" height="18"></iconify-icon></div>
      <div class="featured-card-content">
        <div class="featured-card-name">FastAPI</div>
        <div class="featured-card-desc">Modern async web framework</div>
      </div>
    </a>
    <a href="riso-tui.html" class="featured-card">
      <div class="mini-icon"><iconify-icon icon="tabler:terminal-2" width="18" height="18"></iconify-icon></div>
      <div class="featured-card-content">
        <div class="featured-card-name">Riso TUI</div>
        <div class="featured-card-desc">Interactive generator</div>
      </div>
    </a>
    <a href="docker.html" class="featured-card">
      <div class="mini-icon"><iconify-icon icon="logos:docker-icon" width="18" height="18"></iconify-icon></div>
      <div class="featured-card-content">
        <div class="featured-card-name">Docker</div>
        <div class="featured-card-desc">Container platform</div>
      </div>
    </a>
  </div>
</div>

<!-- Search & Filter Controls -->
<div class="tool-catalog-controls" role="search" aria-label="Filter and sort tools">
  <input type="search"
         id="tool-search"
         class="tool-search"
         placeholder="Search tools by name, tag, or description..."
         aria-label="Search tools">

  <select id="category-filter" class="filter-select" aria-label="Filter by category">
    <option value="">All Categories</option>
    <option value="ai-skills">AI Skills</option>
    <option value="riso-scripts">Riso Scripts</option>
    <option value="riso-validators">Riso Validators</option>
    <option value="quality">Quality Tools</option>
    <option value="packages">Package Managers</option>
    <option value="container-ci">Container/CI</option>
    <option value="optional-modules">Optional Modules</option>
  </select>

  <select id="type-filter" class="filter-select" aria-label="Filter by type">
    <option value="">All Types</option>
    <option value="ai-skill">AI Skill</option>
    <option value="automation">Automation</option>
    <option value="validator">Validator</option>
    <option value="linter">Linter</option>
    <option value="formatter">Formatter</option>
    <option value="type-checker">Type Checker</option>
    <option value="testing">Testing</option>
    <option value="package-manager">Package Manager</option>
    <option value="container">Container</option>
    <option value="ci">CI</option>
    <option value="mcp">MCP</option>
    <option value="framework">Framework</option>
  </select>

  <select id="sort-select" class="sort-select" aria-label="Sort tools">
    <option value="default">Default Order</option>
    <option value="name-asc">Name (A → Z)</option>
    <option value="name-desc">Name (Z → A)</option>
    <option value="category">By Category</option>
    <option value="type">By Type</option>
    <option value="popularity">Most Popular</option>
  </select>

  <div class="keyboard-hint">
    <kbd>/</kbd> to search
  </div>
</div>

<!-- Results Bar -->
<div class="tool-results-bar">
  <span id="results-count" class="tool-results-count" aria-live="polite">Showing <strong>32</strong> tools</span>
  <div class="tool-view-toggle" role="group" aria-label="View mode">
    <button id="grid-view-btn" class="view-btn active" aria-label="Grid view" title="Grid view">
      <iconify-icon icon="tabler:layout-grid" width="18" height="18"></iconify-icon>
    </button>
    <button id="list-view-btn" class="view-btn" aria-label="List view" title="List view">
      <iconify-icon icon="tabler:list" width="18" height="18"></iconify-icon>
    </button>
  </div>
</div>

<!-- Tool Cards Grid -->
<div class="tool-catalog-grid" id="tool-catalog" role="list">

  <!-- ═══════════════════════════════════════════════════════════════════════
       AI Skills
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-agents-md-manager" data-name="agents-md-manager" data-category="ai-skills" data-type="ai-skill" data-tags="agents,claude,copilot,cursor,gemini,sync,ssot" data-popularity="88" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:file-code" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-agents-md-manager"><a href="agents-md-manager.html">agents-md-manager</a></h3>
    </div>
    <p class="tool-description">AGENTS.md as SSOT with detection, quality analysis, and platform sync</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="ai-skills">AI Skills</span>
      <span class="badge badge-type" data-type="ai-skill">AI Skill</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-mcp-installer" data-name="mcp-installer" data-category="ai-skills" data-type="ai-skill" data-tags="mcp,servers,claude,cursor,copilot,sync,install" data-popularity="88" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:plug-connected" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-mcp-installer"><a href="mcp-installer.html">mcp-installer</a></h3>
    </div>
    <p class="tool-description">Universal MCP server research, installation, and cross-interface sync</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="ai-skills">AI Skills</span>
      <span class="badge badge-type" data-type="ai-skill">AI Skill</span>
    </div>
  </article>

  <!-- ═══════════════════════════════════════════════════════════════════════
       Riso Scripts
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-riso-tui" data-name="riso tui" data-category="riso-scripts" data-type="automation" data-tags="tui,textual,generator,interactive,configuration" data-popularity="90" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:terminal-2" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-riso-tui"><a href="riso-tui.html">Riso TUI</a></h3>
    </div>
    <p class="tool-description">Interactive Textual-powered terminal UI for configuring and generating projects</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-scripts">Riso Scripts</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-quality-suite" data-name="quality suite" data-category="riso-scripts" data-type="automation" data-tags="quality,lint,test,typecheck,ci" data-popularity="85" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:shield-check-filled" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-quality-suite"><a href="quality-suite.html">Quality Suite</a></h3>
    </div>
    <p class="tool-description">Unified quality pipeline running lint, typecheck, and test in sequence</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-scripts">Riso Scripts</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-render-samples" data-name="render samples" data-category="riso-scripts" data-type="automation" data-tags="samples,rendering,testing,ci,variants" data-popularity="75" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:code-dots" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-render-samples"><a href="render-samples.html">Render Samples</a></h3>
    </div>
    <p class="tool-description">Orchestrates rendering of sample project variants with smoke tests</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-scripts">Riso Scripts</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-pre-gen-hook" data-name="pre-generation hook" data-category="riso-scripts" data-type="validator" data-tags="hook,validation,pre-generation,copier" data-popularity="70" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:shield-check" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-pre-gen-hook"><a href="pre-gen-hook.html">Pre-Generation Hook</a></h3>
    </div>
    <p class="tool-description">Validates configuration before template generation begins</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-scripts">Riso Scripts</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-post-gen-hook" data-name="post-generation hook" data-category="riso-scripts" data-type="automation" data-tags="hook,post-generation,setup,copier" data-popularity="70" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:check-list" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-post-gen-hook"><a href="post-gen-hook.html">Post-Generation Hook</a></h3>
    </div>
    <p class="tool-description">Performs post-processing tasks after template generation completes</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-scripts">Riso Scripts</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-generate-compatibility-matrix" data-name="generate compatibility matrix" data-category="riso-scripts" data-type="automation" data-tags="documentation,compatibility,matrix,mermaid,prompts" data-popularity="65" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:apps" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-generate-compatibility-matrix"><a href="generate-compatibility-matrix.html">Compatibility Matrix</a></h3>
    </div>
    <p class="tool-description">Generates compatibility documentation from copier.yml prompt definitions</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-scripts">Riso Scripts</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <!-- ═══════════════════════════════════════════════════════════════════════
       Riso Validators
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-frontend-validator" data-name="frontend validator" data-category="riso-validators" data-type="validator" data-tags="validation,frontend,react,vue,svelte" data-popularity="60" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="ph:browser-bold" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-frontend-validator"><a href="frontend-validator.html">Frontend Validator</a></h3>
    </div>
    <p class="tool-description">Validates frontend framework and component library compatibility</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-validators">Validators</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-structure-validator" data-name="structure validator" data-category="riso-validators" data-type="validator" data-tags="validation,structure,layout" data-popularity="60" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="ph:tree-structure-bold" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-structure-validator"><a href="structure-validator.html">Structure Validator</a></h3>
    </div>
    <p class="tool-description">Validates project structure and layout configurations</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-validators">Validators</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-tool-validator" data-name="tool validator" data-category="riso-validators" data-type="validator" data-tags="validation,tools,compatibility" data-popularity="60" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="ph:wrench-bold" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-tool-validator"><a href="tool-validator.html">Tool Validator</a></h3>
    </div>
    <p class="tool-description">Validates development tool selections and compatibility</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-validators">Validators</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-language-validator" data-name="language validator" data-category="riso-validators" data-type="validator" data-tags="validation,python,node,versions" data-popularity="55" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="ph:translate-bold" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-language-validator"><a href="language-validator.html">Language Validator</a></h3>
    </div>
    <p class="tool-description">Validates language version and compatibility requirements</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-validators">Validators</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-build-tool-validator" data-name="build tool validator" data-category="riso-validators" data-type="validator" data-tags="validation,build,bundler" data-popularity="55" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="ph:hammer-bold" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-build-tool-validator"><a href="build-tool-validator.html">Build Tool Validator</a></h3>
    </div>
    <p class="tool-description">Validates build tool and bundler configurations</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-validators">Validators</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-monorepo-tool-validator" data-name="monorepo tool validator" data-category="riso-validators" data-type="validator" data-tags="validation,monorepo,workspaces" data-popularity="55" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="ph:folders-bold" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-monorepo-tool-validator"><a href="monorepo-tool-validator.html">Monorepo Validator</a></h3>
    </div>
    <p class="tool-description">Validates monorepo-specific tool configurations</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="riso-validators">Validators</span>
      <span class="badge badge-type" data-type="validator">Validator</span>
    </div>
  </article>

  <!-- ═══════════════════════════════════════════════════════════════════════
       Quality Tools
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-ruff" data-name="ruff" data-category="quality" data-type="linter" data-tags="python,linting,formatting,rust,fast" data-popularity="95" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:ruff" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-ruff"><a href="ruff.html">Ruff</a></h3>
    </div>
    <p class="tool-description">Extremely fast Python linter and formatter, written in Rust</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="quality">Quality</span>
      <span class="badge badge-type" data-type="linter">Linter</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-pytest" data-name="pytest" data-category="quality" data-type="testing" data-tags="python,testing,fixtures,plugins" data-popularity="95" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:pytest" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-pytest"><a href="pytest.html">pytest</a></h3>
    </div>
    <p class="tool-description">The de facto Python testing framework with powerful fixtures</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="quality">Quality</span>
      <span class="badge badge-type" data-type="testing">Testing</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-pre-commit" data-name="pre-commit" data-category="quality" data-type="automation" data-tags="git,hooks,automation,quality" data-popularity="90" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:git-commit" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-pre-commit"><a href="pre-commit.html">pre-commit</a></h3>
    </div>
    <p class="tool-description">Framework for managing and maintaining git hooks</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="quality">Quality</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-ty" data-name="ty" data-category="quality" data-type="type-checker" data-tags="python,types,astral,fast" data-popularity="85" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:brand-typescript" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-ty"><a href="ty.html">ty</a></h3>
    </div>
    <p class="tool-description">Astral's blazing-fast Python type checker</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="quality">Quality</span>
      <span class="badge badge-type" data-type="type-checker">Type Checker</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-coverage" data-name="coverage" data-category="quality" data-type="testing" data-tags="python,coverage,testing,metrics" data-popularity="80" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:chart-pie-filled" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-coverage"><a href="coverage.html">Coverage.py</a></h3>
    </div>
    <p class="tool-description">Code coverage measurement and reporting for Python</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="quality">Quality</span>
      <span class="badge badge-type" data-type="testing">Testing</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-pylint" data-name="pylint" data-category="quality" data-type="linter" data-tags="python,linting,static-analysis" data-popularity="70" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:pylint" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-pylint"><a href="pylint.html">Pylint</a></h3>
    </div>
    <p class="tool-description">Comprehensive Python code analyzer and linter</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="quality">Quality</span>
      <span class="badge badge-type" data-type="linter">Linter</span>
    </div>
  </article>

  <!-- ═══════════════════════════════════════════════════════════════════════
       Package Managers
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-uv" data-name="uv" data-category="packages" data-type="package-manager" data-tags="python,package-manager,astral,fast" data-popularity="95" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:astral" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-uv"><a href="uv.html">uv</a></h3>
    </div>
    <p class="tool-description">Extremely fast Python package installer and resolver from Astral</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="packages">Packages</span>
      <span class="badge badge-type" data-type="package-manager">Package Manager</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-pnpm" data-name="pnpm" data-category="packages" data-type="package-manager" data-tags="node,package-manager,fast,disk-efficient" data-popularity="90" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:pnpm" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-pnpm"><a href="pnpm.html">pnpm</a></h3>
    </div>
    <p class="tool-description">Fast, disk space efficient package manager for Node.js</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="packages">Packages</span>
      <span class="badge badge-type" data-type="package-manager">Package Manager</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-copier" data-name="copier" data-category="packages" data-type="automation" data-tags="template,scaffolding,jinja2,generation" data-popularity="85" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:copy" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-copier"><a href="copier.html">Copier</a></h3>
    </div>
    <p class="tool-description">Library and CLI for rendering project templates</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="packages">Packages</span>
      <span class="badge badge-type" data-type="automation">Automation</span>
    </div>
  </article>

  <!-- ═══════════════════════════════════════════════════════════════════════
       Container/CI
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-docker" data-name="docker" data-category="container-ci" data-type="container" data-tags="container,devcontainer,deployment" data-popularity="95" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="logos:docker-icon" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-docker"><a href="docker.html">Docker</a></h3>
    </div>
    <p class="tool-description">Container platform for development and deployment</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="container-ci">Container/CI</span>
      <span class="badge badge-type" data-type="container">Container</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-github-actions" data-name="github actions" data-category="container-ci" data-type="ci" data-tags="ci,cd,automation,github" data-popularity="95" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:githubactions" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-github-actions"><a href="github-actions.html">GitHub Actions</a></h3>
    </div>
    <p class="tool-description">CI/CD platform integrated with GitHub repositories</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="container-ci">Container/CI</span>
      <span class="badge badge-type" data-type="ci">CI</span>
    </div>
  </article>

  <!-- ═══════════════════════════════════════════════════════════════════════
       Optional Modules
       ═══════════════════════════════════════════════════════════════════════ -->

  <article class="tool-card" role="article" aria-labelledby="tool-fastapi" data-name="fastapi" data-category="optional-modules" data-type="framework" data-tags="python,api,async,openapi" data-popularity="95" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:fastapi" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-fastapi"><a href="fastapi.html">FastAPI</a></h3>
    </div>
    <p class="tool-description">Modern, fast Python web framework for building APIs</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="optional-modules">Modules</span>
      <span class="badge badge-type" data-type="framework">Framework</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-typer" data-name="typer" data-category="optional-modules" data-type="framework" data-tags="python,cli,typing,click" data-popularity="85" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:terminal-2" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-typer"><a href="typer.html">Typer</a></h3>
    </div>
    <p class="tool-description">Build CLI applications with Python type hints</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="optional-modules">Modules</span>
      <span class="badge badge-type" data-type="framework">Framework</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-fastify" data-name="fastify" data-category="optional-modules" data-type="framework" data-tags="node,api,typescript,fast" data-popularity="85" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" data-brand="true" aria-hidden="true"><iconify-icon icon="simple-icons:fastify" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-fastify"><a href="fastify.html">Fastify</a></h3>
    </div>
    <p class="tool-description">Fast and low overhead Node.js web framework</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="optional-modules">Modules</span>
      <span class="badge badge-type" data-type="framework">Framework</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-riso-cli" data-name="riso cli" data-category="project-tools" data-type="cli" data-tags="cli,copier,template,ai,agents,tools" data-popularity="90" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:terminal-2" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-riso-cli"><a href="riso-cli.html">Riso CLI</a></h3>
    </div>
    <p class="tool-description">Agent-native Typer CLI for template introspection, validation, and Copier operations</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="project-tools">Project Tools</span>
      <span class="badge badge-type" data-type="cli">CLI</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-strawberry-graphql" data-name="strawberry graphql" data-category="optional-modules" data-type="framework" data-tags="python,graphql,api,typing" data-popularity="75" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:strawberry" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-strawberry-graphql"><a href="strawberry-graphql.html">Strawberry GraphQL</a></h3>
    </div>
    <p class="tool-description">Python GraphQL library using dataclasses and type hints</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="optional-modules">Modules</span>
      <span class="badge badge-type" data-type="framework">Framework</span>
    </div>
  </article>

  <article class="tool-card" role="article" aria-labelledby="tool-websockets" data-name="websockets" data-category="optional-modules" data-type="framework" data-tags="python,websocket,async,realtime" data-popularity="75" tabindex="0">
    <div class="tool-card-header">
      <span class="tool-icon" aria-hidden="true"><iconify-icon icon="tabler:plug-connected" width="28" height="28"></iconify-icon></span>
      <h3 id="tool-websockets"><a href="websockets.html">websockets</a></h3>
    </div>
    <p class="tool-description">Library for building WebSocket servers and clients in Python</p>
    <div class="tool-meta">
      <span class="badge badge-category" data-category="optional-modules">Modules</span>
      <span class="badge badge-type" data-type="framework">Framework</span>
    </div>
  </article>

</div>

<!-- Empty State -->
<div id="tool-empty" class="tool-catalog-empty" aria-hidden="true">
  <iconify-icon icon="tabler:search-off" width="64" height="64"></iconify-icon>
  <p>No tools match your search</p>
  <p class="empty-hint">Try adjusting your filters or search terms</p>
  <button class="clear-filters-btn" onclick="clearAllFilters()">
    <iconify-icon icon="tabler:refresh" width="16" height="16"></iconify-icon>
    Clear all filters
  </button>
</div>
```

```{toctree}
:hidden:
:maxdepth: 1

riso-cli
riso-mcp-server
```
