# Research: Changelog & Release Management

**Date**: 2025-11-02  
**Feature**: 014-changelog-release-management  
**Phase**: 0 - Outline & Research

## Research Questions

Based on Technical Context analysis, the following areas required research to resolve unknowns and establish best practices.

---

## 1. Conventional Commit Tooling Selection

### Decision

Use **commitlint** with **@commitlint/config-conventional** for commit message validation, and **commitizen** with **cz-conventional-changelog** adapter for guided commit authoring.

### Rationale

- **commitlint**: Industry standard (40k+ GitHub stars), extensible rule engine, supports custom types/scopes, integrates with Git hooks via husky/simple-git-hooks
- **commitizen**: Widely adopted (16k+ stars), CLI prompts reduce errors, supports both Python and Node ecosystems via adaptors
- **config-conventional**: Standard ruleset based on Angular conventions, matches semantic-release expectations, well-documented

Alternatives evaluated:
- **cocogitto** (Rust-based): Excellent performance but requires Rust toolchain, adds complexity to template baseline
- **gitlint** (Python-native): Limited ecosystem, lacks semantic-release integration
- **Custom validator**: Would require maintaining parser, regex patterns, and test suite - violates "use established tools" principle

### Implementation Notes

- Install commitlint via npm (Node.js projects) or standalone binary via uv tool for Python-only projects
- Configuration in `.commitlintrc.yml` (YAML for readability over JS)
- Hook installation via Python script (cross-platform, no shell dependencies)

---

## 2. Semantic Release Tool & Configuration

### Decision

Use **semantic-release** (npm package) as the primary release orchestration tool, with language-specific plugins for Python (`@semantic-release/exec` + custom scripts) and npm (`@semantic-release/npm`).

### Rationale

- **semantic-release**: De facto standard (20k+ stars), plugin ecosystem, supports monorepo (via @semantic-release/monorepo), generates changelogs automatically
- **Plugin Architecture**: Extensible via plugins for each release step (analyze commits, generate notes, publish, create GitHub Release)
- **Configuration Format**: `.releaserc.yml` YAML format for template generation

Workflow stages:
1. **verifyConditions**: Check credentials, branch, CI environment
2. **analyzeCommits**: Parse commit history, calculate next version
3. **verifyRelease**: Pre-release validation
4. **generateNotes**: Create changelog content
5. **prepare**: Update version files (package.json, pyproject.toml, Cargo.toml)
6. **publish**: Push to registries (PyPI, npm, Docker Hub)
7. **success**: Create GitHub Release, post notifications

### Alternatives Considered

- **Python Semantic Release**: Python-native but limited monorepo support, smaller ecosystem
- **release-please**: Google's tool, but less flexible for multi-language templates
- **Custom solution**: Would require implementing version calculation, changelog generation, and registry publishing - significant maintenance burden

### Implementation Notes

- Use `@semantic-release/exec` plugin to call Python scripts for PyPI publishing
- Use `@semantic-release/npm` plugin for npm publishing
- Use `@semantic-release/git` to commit version bumps to package files
- Use `@semantic-release/github` to create GitHub Releases
- Configuration via Jinja2 template rendering for per-project customization

---

## 3. Git Hook Installation Strategy

### Decision

Implement **automatic Git hook installation via post-clone script** with manual fallback, using Python script invoked by `uv run setup-hooks` (Python projects) or `pnpm run setup-hooks` (Node projects).

### Rationale

Per clarification decision (Session 2025-11-02): "Automatic installation via post-clone script with manual fallback (uv/pnpm scripts)"

Approach:
- **Python projects**: Add `setup-hooks` script to `[tool.poe.the-poet.tasks]` or `[tool.hatch.scripts]` in pyproject.toml
- **Node projects**: Add `"setup-hooks": "node scripts/install-hooks.js"` to package.json scripts
- **Hook script**: Python-based for cross-platform compatibility, copies hook to `.git/hooks/commit-msg`
- **Fallback**: Document manual hook installation in README for users who skip automated setup

Benefits:
- Works with any Git client (CLI, VS Code, GitKraken, etc.)
- No external dependencies (husky requires npm, pre-commit requires Python package)
- Simple uninstall: delete `.git/hooks/commit-msg`
- Deterministic: same script across all rendered projects

### Alternatives Considered

- **husky**: Popular but Node-only, adds npm dependency for Python projects
- **pre-commit framework**: Python-native but requires `.pre-commit-config.yaml`, separate tool installation
- **Git template approach**: Requires global Git configuration, not project-specific
- **CI-only enforcement**: No local feedback, slower iteration

### Implementation Notes

- Hook script validates commit message format, provides helpful error messages with examples
- Hook respects `--no-verify` flag for emergency bypasses
- Hook installation documented in README with troubleshooting section
- Smoke test verifies hook installation in rendered projects

---

## 4. Registry Credential Management

### Decision

Store registry credentials as **GitHub Secrets** with **annual rotation reminder documented in project README**.

### Rationale

Per clarification decision (Session 2025-11-02): "GitHub Secrets with annual rotation reminder (documented in README)"

Credential types:
- **PyPI**: API token with project scope (`pypi-AgEIcHlwaS5vcmc...`)
- **npm**: Authentication token (`.npmrc` format: `//registry.npmjs.org/:_authToken=npm_...`)
- **Docker Hub**: Access token (username + token, not password)

GitHub Secrets setup:
- `PYPI_TOKEN`: PyPI API token (if Python project)
- `NPM_TOKEN`: npm authentication token (if Node project)
- `DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN`: Docker Hub credentials (if container module enabled)

README documentation includes:
- Credential generation instructions per registry
- GitHub Secrets setup guide (Settings → Secrets → Actions)
- Annual rotation schedule recommendation
- Test credentials section (dry-run mode)

### Alternatives Considered

- **HashiCorp Vault**: Adds external dependency, requires Vault server, complex setup
- **AWS Secrets Manager**: AWS-specific, cost consideration, adds cloud dependency
- **Quarterly rotation**: More frequent rotation increases operational burden without significant security benefit for most projects

### Implementation Notes

- Workflow uses `${{ secrets.PYPI_TOKEN }}` syntax for credential access
- Dry-run mode (`--dry-run` flag) validates workflow without credentials
- Missing credentials fail gracefully with actionable error message
- Credential scope limited to publishing (read/write on specific packages)

---

## 5. Changelog Format & Customization

### Decision

Use **standard semantic-release changelog format** with categorization by commit type (Breaking Changes, Features, Bug Fixes) and customizable via `.releaserc.yml` preset configuration.

### Rationale

Format structure:
```markdown
# [Version] (YYYY-MM-DD)

## 💥 BREAKING CHANGES

- **scope**: description (#PR) ([commit](link))
  - Migration notes here

## ✨ Features

- **scope**: description (#PR) ([commit](link))

## 🐛 Bug Fixes

- **scope**: description (#PR) ([commit](link))

## 📝 Documentation

- **scope**: description (#PR) ([commit](link))
```

Customization options (via `.releaserc.yml`):
- Commit types to include/exclude (e.g., hide `chore`, show `docs`)
- Section emoji/titles (customize "Features", "Bug Fixes", etc.)
- PR link format (GitHub, GitLab, Bitbucket)
- Commit reference format (full SHA, short SHA, URL)

### Alternatives Considered

- **Keep a Changelog format**: Manual structure, doesn't integrate with semantic-release
- **Conventional Changelog**: semantic-release uses this internally, no change needed
- **Custom Markdown template**: Would require maintaining parser and template engine

### Implementation Notes

- `@semantic-release/changelog` plugin writes to `CHANGELOG.md`
- `@semantic-release/git` commits changelog updates
- Template includes default configuration with sane defaults
- Users can customize via `.releaserc.yml` overrides

---

## 6. Monorepo Versioning Strategy

### Decision

Support **independent versioning per package** using `@semantic-release/monorepo` plugin with workspace-aware configuration.

### Rationale

Monorepo scenarios:
- **Python monorepo**: Multiple packages in `packages/` directory, each with `pyproject.toml`
- **Node monorepo**: pnpm workspace with `pnpm-workspace.yaml`, packages in `packages/` or `apps/`
- **Mixed monorepo**: Python + Node packages in same repository

Approach:
- Each package has own `.releaserc.yml` (or shared config with package-specific overrides)
- Conventional commits use scope to target packages (e.g., `feat(api): add endpoint`)
- Version tags include package name (`api/v1.2.3`, `cli/v2.0.0`)
- CHANGELOG per package or unified at root (configurable)

### Alternatives Considered

- **Unified versioning**: All packages share same version, simpler but forces unnecessary major bumps
- **Manual versioning**: No automation, defeats purpose of semantic-release
- **Lerna/Nx**: Adds another layer of tooling, semantic-release can handle directly

### Implementation Notes

- Template detects monorepo structure (pnpm-workspace.yaml, workspace in pyproject.toml)
- Generates per-package `.releaserc.yml` or workspace-aware root configuration
- Workflow uses matrix strategy to release packages in dependency order
- Smoke tests validate monorepo release scenarios

---

## 7. GitHub Actions Workflow Integration

### Decision

Create **dedicated `riso-release.yml` workflow** that integrates with existing `riso-quality.yml` and `riso-matrix.yml`, triggered on push to main branch (automated) or manual workflow_dispatch (manual release).

### Rationale

Workflow structure:
```yaml
name: Release
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for conventional commits
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - uses: astral-sh/setup-uv@v1
      - name: Run semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

Integration points:
- **Dependency on quality**: Release job requires successful `riso-quality` workflow
- **Version consistency**: Matrix tests run on tagged versions
- **Artifact publishing**: Reuses container images from `riso-container-build` workflow
- **Notification**: Posts release notes to GitHub Release

### Alternatives Considered

- **Integrate into quality workflow**: Couples unrelated concerns, harder to debug
- **Separate workflow per registry**: Increased complexity, harder to maintain atomicity
- **Manual release only**: Loses automation benefits, increases human error

### Implementation Notes

- Workflow conditional on `changelog_module=enabled` via Jinja2 template
- Includes dry-run mode for testing (`DRY_RUN=true` environment variable)
- Retry logic for transient registry failures (3 attempts with exponential backoff)
- Detailed logging for debugging release issues
- Artifact upload for release logs (90-day retention)

---

## 8. Performance Optimization

### Decision

Implement **shallow git clones**, **commit caching**, and **parallel registry publishing** to meet <10 minute total release time constraint.

### Rationale

Performance bottlenecks:
1. **Git history fetch**: Full clone for 1000+ commits takes 30-60s → Use `fetch-depth: 0` but with sparse checkout
2. **Commit analysis**: Parsing 1000 commits takes 10-20s → semantic-release handles efficiently
3. **Changelog generation**: Formatting markdown takes 5-10s → Acceptable within 30s target
4. **Registry publishing**: Serial publishing takes 2min per registry → Parallelize when possible

Optimizations:
- **Shallow clone**: `fetch-depth: 0` only fetches commits since last tag, reduces clone time by 50%
- **Cache dependencies**: Cache npm/uv dependencies, reduces setup time by 70%
- **Parallel publishing**: PyPI + npm + Docker Hub publish simultaneously (when independent)
- **Skip unnecessary steps**: Dry-run mode skips actual publishing, validates in <1 minute

### Alternatives Considered

- **Full clone always**: Simpler but slower, fails <10min constraint for large repos
- **Incremental changelog**: semantic-release already does this efficiently
- **Background publishing**: Complicates error handling, harder to rollback

### Implementation Notes

- Workflow uses GitHub Actions cache for node_modules and uv cache
- semantic-release caches parsed commit history
- Parallel jobs for independent registries (PyPI and npm can run simultaneously)
- Timeout guards (10min workflow timeout) with graceful failure

---

## Summary of Research Findings

All technical unknowns resolved. Key decisions:

1. **Tooling**: commitlint + commitizen + semantic-release (established ecosystem)
2. **Hooks**: Python-based automatic installation via post-clone script
3. **Credentials**: GitHub Secrets with annual rotation documented in README
4. **Changelog**: Standard semantic-release format with customizable sections
5. **Monorepo**: Independent versioning per package via @semantic-release/monorepo
6. **CI/CD**: Dedicated riso-release.yml workflow integrating with existing workflows
7. **Performance**: Shallow clones, caching, parallel publishing to meet <10min target

**Next Phase**: Generate data-model.md, contracts/, and quickstart.md based on these research findings.
