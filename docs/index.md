# Riso Developer Documentation

<!-- SVG Filters for Risograph Effects -->
<svg class="riso-filters" aria-hidden="true">
  <defs>
    <filter id="riso-rough">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="5" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="1" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    <filter id="riso-grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" result="noise"/>
      <feColorMatrix type="saturate" values="0"/>
      <feBlend in="SourceGraphic" mode="multiply"/>
    </filter>
  </defs>
</svg>

<div class="hero riso-crop-marks">
  <h1 class="hero-title">Riso Template</h1>
  <p class="hero-subtitle">
    The modern, batteries-included Copier template for Python, Node.js, and full-stack projects.
    Ship faster with built-in quality tooling, CI/CD, and documentation.
  </p>
  <div class="hero-actions">
    <a href="guides/index.html" class="btn btn-primary">
      <iconify-icon icon="tabler:printer"></iconify-icon>
      Get Started
    </a>
    <a href="tools/index.html" class="btn btn-secondary">
      <iconify-icon icon="tabler:palette"></iconify-icon>
      Browse Tools
    </a>
  </div>
</div>

<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-value">32+</div>
    <div class="stat-label">Tools</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">7</div>
    <div class="stat-label">Categories</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">90%+</div>
    <div class="stat-label">Coverage Target</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">3.11+</div>
    <div class="stat-label">Python Support</div>
  </div>
</div>

:::{admonition} Quick Start
:class: tip

```bash
# Bootstrap development environment (first time)
./scripts/setup/setup.sh --install

# Render the default sample
./scripts/render-samples.sh

# Navigate to rendered project
cd samples/default/render

# Set up and run
uv sync && make quality
```
:::

:::{toctree}
:maxdepth: 2
:hidden:

Guides <guides/index>
Tools <tools/index>
API Reference <api/index>
Changelog <changelog>
:::

## Core Features

<div class="card-grid">
  <div class="feature-card">
    <div class="feature-icon">
      <iconify-icon icon="tabler:shield-check"></iconify-icon>
    </div>
    <h3 class="feature-title">Quality Gate</h3>
    <p class="feature-description">
      Run <code>make quality</code> for the canonical lane: ruff, ty, pylint, pytest with coverage.
      90%+ unit test coverage enforced.
    </p>
  </div>

  <div class="feature-card">
    <div class="feature-icon">
      <iconify-icon icon="tabler:book-2"></iconify-icon>
    </div>
    <h3 class="feature-title">Documentation First</h3>
    <p class="feature-description">
      New guides belong in <code>docs/guides/</code>. Mirror changes into the template so rendered
      projects inherit the same navigation.
    </p>
  </div>

  <div class="feature-card">
    <div class="feature-icon">
      <iconify-icon icon="tabler:robot"></iconify-icon>
    </div>
    <h3 class="feature-title">Automation Ready</h3>
    <p class="feature-description">
      Use <code>scripts/render-samples.sh</code> to refresh renders and
      <code>scripts/ci/run_quality_suite.py</code> to align quality lanes.
    </p>
  </div>

  <div class="feature-card">
    <div class="feature-icon">
      <iconify-icon icon="tabler:plug-connected"></iconify-icon>
    </div>
    <h3 class="feature-title">MCP Integration</h3>
    <p class="feature-description">
      Built-in <a href="tools/riso-mcp-server.html">MCP server</a> exposes Copier templating as AI-accessible tools.
      Generate MCP scaffolds in Python, TypeScript, or Rust.
    </p>
  </div>
</div>

<div class="section-divider"></div>

## What's Inside

<div class="card-grid-2">
  <div class="callout">
    <div class="callout-icon">
      <iconify-icon icon="tabler:template"></iconify-icon>
    </div>
    <div class="callout-content">
      <div class="callout-title">Template Renderer</div>
      <div class="callout-text">
        <code>scripts/render-samples.sh</code> orchestrates Copier runs and keeps smoke results
        aligned with <code>samples/metadata/module_success.json</code>.
      </div>
    </div>
  </div>

  <div class="callout">
    <div class="callout-icon">
      <iconify-icon icon="tabler:test-pipe"></iconify-icon>
    </div>
    <div class="callout-content">
      <div class="callout-title">Quality Tooling</div>
      <div class="callout-text">
        The Python quality lane lives in <code>template/files/shared/quality/</code> with
        Makefile + uv tasks and CI orchestration scripts.
      </div>
    </div>
  </div>

  <div class="callout">
    <div class="callout-icon">
      <iconify-icon icon="tabler:git-merge"></iconify-icon>
    </div>
    <div class="callout-content">
      <div class="callout-title">Context Sync</div>
      <div class="callout-text">
        Canonical GitHub context files in <code>.github/context/</code> are validated by
        <code>scripts/ci/verify_context_sync.py</code>.
      </div>
    </div>
  </div>

  <div class="callout">
    <div class="callout-icon">
      <iconify-icon icon="tabler:file-text"></iconify-icon>
    </div>
    <div class="callout-content">
      <div class="callout-title">Docs Payload</div>
      <div class="callout-text">
        This Sphinx site is mirrored to the template under <code>template/files/python/docs/</code>
        so new projects inherit the same authoring experience.
      </div>
    </div>
  </div>
</div>

<div class="section-divider"></div>

## Quality & Coverage

<div class="card-grid-3">
  <div class="stat-card">
    <div class="stat-value" style="font-size: 1.5rem;">
      <iconify-icon icon="tabler:chart-pie"></iconify-icon>
    </div>
    <div class="stat-label" style="font-size: 0.875rem; line-height: 1.4;">
      <strong>Coverage Floor</strong><br>
      90% unit test coverage across Python packages
    </div>
  </div>

  <div class="stat-card">
    <div class="stat-value" style="font-size: 1.5rem;">
      <iconify-icon icon="tabler:package"></iconify-icon>
    </div>
    <div class="stat-label" style="font-size: 0.875rem; line-height: 1.4;">
      <strong>Artifacts</strong><br>
      JUnit XML, Cobertura, and log bundles uploaded
    </div>
  </div>

  <div class="stat-card">
    <div class="stat-value" style="font-size: 1.5rem;">
      <iconify-icon icon="tabler:versions"></iconify-icon>
    </div>
    <div class="stat-label" style="font-size: 0.875rem; line-height: 1.4;">
      <strong>Matrix</strong><br>
      Python 3.11-3.13 required across all versions
    </div>
  </div>
</div>

:::{admonition} Coverage Policy
:class: note

Aim for **90% unit test coverage** across rendered Python packages. Integration and e2e suites must
exercise critical paths (auth, CLI, API, background tasks). Enforce `--cov-fail-under=90` locally
and in CI to prevent regressions.
:::

<div class="section-divider"></div>

## Quick Links

<div class="quick-links">
  <a href="guides/index.html" class="quick-link">
    <iconify-icon icon="tabler:compass"></iconify-icon>
    Guides
  </a>
  <a href="tools/index.html" class="quick-link">
    <iconify-icon icon="tabler:tools"></iconify-icon>
    Tool Catalog
  </a>
  <a href="api/index.html" class="quick-link">
    <iconify-icon icon="tabler:code"></iconify-icon>
    API Reference
  </a>
  <a href="changelog.html" class="quick-link">
    <iconify-icon icon="tabler:history"></iconify-icon>
    Changelog
  </a>
  <a href="guides/testing-strategy.html" class="quick-link">
    <iconify-icon icon="tabler:test-pipe"></iconify-icon>
    Testing Strategy
  </a>
  <a href="tools/riso-mcp-server.html" class="quick-link">
    <iconify-icon icon="tabler:plug-connected"></iconify-icon>
    MCP Server
  </a>
  <a href="https://github.com/openai/riso" class="quick-link" target="_blank">
    <iconify-icon icon="tabler:brand-github"></iconify-icon>
    GitHub
  </a>
</div>

---

<p class="text-center text-muted" style="margin-top: 2rem;">
  Built with <iconify-icon icon="tabler:heart" style="color: var(--riso-primary);"></iconify-icon> using
  <a href="https://shibuya.lepture.com/">Shibuya</a> and
  <a href="https://www.sphinx-doc.org/">Sphinx</a>
</p>
