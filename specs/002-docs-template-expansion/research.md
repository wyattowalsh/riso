# Research Log: Expanded Documentation Template Options

## Documentation Frameworks

### Decision: Keep Fumadocs as the default docs variant leveraging Next.js 15 and Tailwind CSS 4
- **Rationale**: The official manual installation guide now requires Next.js 15 and Tailwind CSS 4, aligning with the template’s existing Node.js toolchain and enabling the revamped MDX pipeline.citeturn1search0
- **Supporting Evidence**: The v15 release announcement confirms the migration to Tailwind CSS 4 and associated configuration updates.citeturn1search1
- **Alternatives Considered**:
  - Make Shibuya the default to reduce Node dependencies, but this would sacrifice parity with TypeScript-first teams and the built-in MDX workflow.
  - Default to Docusaurus, which adds heavier React tooling and DocSearch setup overhead best reserved for opt-in variants.

### Decision: Offer Sphinx Shibuya as the Python-focused documentation variant
- **Rationale**: Shibuya provides a modern responsive layout, built-in dark/light mode, and curated support for Jupyter-centric extensions valued by Python teams.citeturn3search0turn3search7turn3search8
- **Alternatives Considered**:
  - PyData theme: stable but less opinionated on branding and Jupyter UX.
  - Material for Sphinx: comprehensive yet heavier and slower to build for notebook-powered docs.

### Decision: Support Docusaurus 3.9 with Algolia DocSearch v4 (AskAI) as the front-end heavy option
- **Rationale**: Docusaurus 3.9 adds DocSearch v4 (including AskAI) and drops legacy Node 18, providing an AI-assisted search experience for large React/TypeScript organizations.citeturn4search2turn4search1
- **Alternatives Considered**:
  - Keep Docusaurus 2.x: misses DocSearch v4 and recent build optimizations.
  - Adopt other React static generators (e.g., Nextra) that lack the governance tooling and plugin ecosystem.

## Toolchain Provisioning & Automation

### Decision: Manage Node.js 20 LTS and pnpm ≥8 via mise auto-install
- **Rationale**: mise’s configuration supports automatic installation of declared tools and keeps auto-install enabled by default, allowing hooks to hydrate Node and pnpm non-interactively.citeturn1search3turn1search6
- **Alternatives Considered**:
  - Volta: Node-only, no built-in pnpm integration.
  - asdf: versatile but slower and less script-friendly for cross-platform hooks.

### Decision: Use uv-managed Python environments (`uv sync`) for deterministic Sphinx builds
- **Rationale**: uv provides fast virtual environment creation, reproducible lockfiles, and automatic interpreter downloads when missing, keeping docs builds consistent across platforms.citeturn5search3turn5search2turn5search6
- **Alternatives Considered**:
  - pip-tools + virtualenv: slower and duplicates functionality already standardized in Riso.
  - Poetry: redundant with uv and slower for CI.

### Decision: Hooks attempt a single auto-install pass before failing fast with remediation
- **Rationale**: Combining mise’s auto-install and uv’s managed interpreter downloads allows hooks to fix the majority of local/environment gaps while still aborting to protect deterministic renders when tooling cannot be provisioned.citeturn1search3turn5search2
- **Alternatives Considered**:
  - Silent skips of docs steps (risks undiscovered CI failures).
  - Immediate failures (higher friction for onboarding).

## Governance Evidence & Artifacts

### Decision: Publish documentation build outputs as GitHub Actions artifacts (v4)
- **Rationale**: GitHub Actions artifacts default to 90-day retention, can be tuned per artifact, and v4 of `actions/upload-artifact` improves performance while deprecating v3 before January 30, 2025—aligning with governance evidence needs.citeturn0search2turn2view0turn0search4
- **Alternatives Considered**:
  - Committing build assets to the repo (bloats history, risks drift).
  - Discarding artifacts (loses reproducibility evidence).

