# Research: Conventional Commit Tooling Integration

**Date**: 2025-11-02  
**Feature**: 016-conventional-commit-tooling  
**Phase**: 0 - Outline & Research

## Research Questions

This feature builds on research completed in feature 014-changelog-release-management (section 1: "Conventional Commit Tooling Selection" and section 3: "Git Hook Installation Strategy"). The following consolidates and extends that research for standalone tooling integration.

---

## 1. Validation Tool Selection

### Decision

Use **commitlint** with **@commitlint/config-conventional** for commit message validation.

### Rationale

- **commitlint**: Industry standard (40k+ GitHub stars), extensible rule engine, supports custom types/scopes
- **config-conventional**: Standard ruleset based on Angular conventions, matches semantic-release expectations (feature 014 dependency)
- **Cross-platform**: Works on macOS, Linux, Windows via Node.js or standalone binary
- **Configurable**: YAML-based configuration (.commitlintrc.yml) for easy customization

Alternatives evaluated:

- **cocogitto** (Rust-based): Excellent performance but requires Rust toolchain, adds complexity to template baseline
- **gitlint** (Python-native): Limited ecosystem, lacks semantic-release integration, fewer configuration options
- **Custom validator**: Would require maintaining parser, regex patterns, and test suite - violates "use established tools" principle

### Implementation Notes

- Node.js projects: Install commitlint via pnpm (`pnpm add -D @commitlint/cli @commitlint/config-conventional`)
- Python-only projects: Use standalone binary via uv tool or Python wrapper calling commitlint CLI
- Configuration in `.commitlintrc.yml` (YAML for readability over JS)
- Validation runs in commit-msg hook and CI workflows

---

## 2. Guided Authoring Tool Selection

### Decision

Use **commitizen** with **cz-conventional-changelog** adapter for guided commit message authoring.

### Rationale

- **commitizen**: Widely adopted (16k+ stars), CLI prompts reduce errors, proven UX patterns
- **cz-conventional-changelog**: Standard adapter matching commitlint rules, consistent workflow
- **Cross-ecosystem**: Supports both Python and Node.js via adapters
- **Customizable**: Supports custom types, scopes, and prompts via configuration

Alternatives evaluated:

- **git-cz** (simpler wrapper): Less configuration flexibility, limited to Node.js
- **Custom prompts**: Would require maintaining UI/UX patterns, accessibility, i18n - significant overhead
- **IDE-only tools**: Doesn't work for CLI-first workflows, excludes non-IDE users

### Implementation Notes

- Node.js projects: Install commitizen via pnpm (`pnpm add -D commitizen cz-conventional-changelog`)
- Python-only projects: Use Python-based prompt library (questionary or inquirer) with custom implementation
- Configuration shares `.commitlintrc.yml` to ensure prompt options match validation rules
- Command: `pnpm run commit` (Node.js) or `uv run commit` (Python)

---

## 3. Git Hook Installation Strategy

### Decision

Implement **automatic Git hook installation via post-clone script** with manual fallback, using Python script invoked by `uv run setup-hooks` (Python projects) or `pnpm run setup-hooks` (Node projects).

### Rationale

Per clarification decision (Session 2025-11-02): "Automatic installation via post-clone script with manual fallback (uv/pnpm scripts)"

Approach:

- **Python projects**: Add `setup-hooks` script to `[tool.poe.the-poet.tasks]` or `pyproject.toml [project.scripts]`
- **Node projects**: Add `"setup-hooks": "node scripts/setup-hooks.js"` to package.json scripts
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
- Graceful degradation: If installation fails, display warning with recovery instructions, allow setup to complete

---

## 4. Logging Strategy

### Decision

Implement **structured logging with configurable verbosity levels** (normal, verbose, debug) for troubleshooting validation failures and hook malfunctions.

### Rationale

Per clarification decision (Session 2025-11-02): "Structured logging with configurable verbosity levels (normal/verbose/debug modes)"

Logging levels:

- **Normal**: Errors only (default), minimal overhead (<50ms), outputs to stderr
- **Verbose**: Errors + warnings + info messages, includes rule violations and suggestions
- **Debug**: All events including validation checks, config parsing, hook execution details

Log format:

- Structured: `[timestamp] [level] [component] message {context}`
- Context includes: commit SHA, rule violated, suggested fix, file path
- Optional log file for persistent debugging (verbose/debug modes)

Benefits:

- Developers can diagnose issues without modifying code
- CI logs provide audit trail (90-day retention per existing policy)
- Performance impact minimal in normal mode (<50ms overhead)

### Alternatives Considered

- **Minimal logging only**: Insufficient for debugging complex validation issues
- **Always verbose**: Performance overhead, log noise
- **External monitoring**: Requires SaaS dependency, violates constitution

### Implementation Notes

- Python: Use `logging` standard library with custom formatter
- Node.js: Use Winston or Bunyan for structured logging
- Environment variable: `COMMIT_TOOLING_LOG_LEVEL=normal|verbose|debug`
- CI workflows: Set `COMMIT_TOOLING_LOG_LEVEL=verbose` for detailed build logs

---

## 5. Python-Only Project Support

### Decision

Provide **Python-native validation fallback** for projects without Node.js installation.

### Rationale

Per functional requirement FR-011: "System MUST support Python-only projects without requiring Node.js installation"

Approach:

- **Option 1 (preferred)**: Python wrapper calling commitlint standalone binary (installed via uv tool)
- **Option 2 (fallback)**: Pure Python validation implementation matching commitlint rules

Implementation path:

1. Detect Node.js availability during hook setup
2. If Node.js present: Use commitlint directly
3. If Node.js absent: Use Python fallback
4. Document trade-offs in README (Python fallback has slightly different error messages)

Benefits:

- Python-only projects stay minimal (no Node.js bloat)
- Aligns with module sovereignty principle
- Fallback ensures validation always works

### Alternatives Considered

- **Require Node.js**: Violates FR-011, adds unnecessary dependency
- **Python-only everywhere**: Increased maintenance burden, ecosystem divergence
- **Skip validation for Python-only**: Defeats purpose of feature

### Implementation Notes

- Standalone commitlint binary installed via: `uv tool install @commitlint/cli` (if uv tools support npm packages) or bundle pre-compiled binary
- Python fallback parses conventional commit format using regex, validates against configured types/scopes
- Tests verify both Node.js and Python-only paths work identically

---

## 6. Monorepo Scope Management

### Decision

Support **up to 50 custom commit scopes** with autocomplete/search when count exceeds 10.

### Rationale

Per clarification decision (Session 2025-11-02): "Support up to 50 scopes with autocomplete/search for better UX"

Scale limits:

- **1-10 scopes**: Display all in simple selection list
- **11-50 scopes**: Activate autocomplete/search with fuzzy matching
- **50+ scopes**: Hard limit, enforce via configuration validation

Autocomplete requirements:

- Fuzzy matching: Partial string matching (e.g., "ap" matches "api", "app", "api-gateway")
- Performance: <100ms filter response for 50 scopes
- UI: Highlight matches, show scope descriptions

Benefits:

- Supports medium-to-large monorepos (typical 10-30 packages)
- Prevents overwhelming UX with long lists
- Hard limit encourages architectural boundaries

### Alternatives Considered

- **Unlimited scopes**: Poor UX, slow autocomplete, no architectural guidance
- **Limit to 20 scopes**: Too restrictive for real-world monorepos
- **No autocomplete**: Poor discoverability for 11+ scopes

### Implementation Notes

- Configuration validation: Error if scopes array length > 50
- Autocomplete library: inquirer (Node.js) or questionary (Python) with fuzzy search plugin
- Monorepo detection: Check for pnpm-workspace.yaml or pyproject.toml workspaces
- Documentation: Recommend grouping related packages (e.g., "services" scope for services/* packages)

---

## 7. Configuration Format

### Decision

Use **YAML format (.commitlintrc.yml)** for configuration, shared between commitlint and commitizen.

### Rationale

Configuration structure:

```yaml
extends:
  - '@commitlint/config-conventional'

rules:
  type-enum:
    - 2  # Level: error
    - always
    - [feat, fix, docs, style, refactor, test, chore, perf]
  
  scope-enum:
    - 2
    - always
    - [api, cli, docs, core]  # Custom scopes
  
  subject-case:
    - 2
    - always
    - [sentence-case, start-case, lower-case]

prompt:
  settings:
    scopeOverrides:
      feat:
        - api
        - cli
      fix:
        - api
        - core
```

Benefits:

- Human-readable, easy to edit
- Single source of truth (commitlint validates, commitizen uses for prompts)
- Supports comments for documentation
- Jinja2 templating friendly

### Alternatives Considered

- **JavaScript (.commitlintrc.js)**: Requires Node.js for Python-only projects, less template-friendly
- **JSON (.commitlintrc.json)**: No comments, harder to read
- **Separate configs**: Duplication, sync issues

### Implementation Notes

- Template renders `.commitlintrc.yml.jinja` with default types/scopes
- Monorepo: Auto-detect packages and populate scopes array
- Validation: Jinja2 template validates scope count ≤ 50
- Documentation: Examples for customizing types, scopes, rules

---

## 8. CI Integration

### Decision

Add commit validation to existing **riso-quality.yml** workflow as optional job, conditional on `commit_tooling_module=enabled`.

### Rationale

Integration approach:

```yaml
jobs:
  commit-validation:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for multi-commit PRs
      - uses: actions/setup-node@v4  # Or setup Python for fallback
      - name: Validate commits
        run: |
          # For each commit in PR, run validation
          git log origin/${{ github.base_ref }}..HEAD --format=%H | \
            xargs -I {} sh -c 'git show -s --format=%B {} | commitlint'
```

Benefits:

- Catches invalid commits from external contributors
- No local hook dependency for CI validation
- Integrates with existing workflow structure

### Alternatives Considered

- **Separate workflow**: Increases workflow count, harder to manage dependencies
- **Validate only merge commit**: Misses invalid commits in PR history
- **No CI validation**: Relies entirely on local hooks, inconsistent enforcement

### Implementation Notes

- Conditional rendering: `{% if commit_tooling_module == 'enabled' %}`
- Supports both Node.js and Python validation paths
- Artifacts: Upload validation report (90-day retention)
- Performance: Parallel validation of commits (if >10 commits)

---

## Summary of Research Findings

All technical unknowns resolved. Key decisions:

1. **Validation**: commitlint + @commitlint/config-conventional (industry standard)
2. **Guided Authoring**: commitizen + cz-conventional-changelog (proven UX)
3. **Hook Installation**: Python-based automatic installation with graceful degradation
4. **Logging**: Structured logging with 3 verbosity levels (normal/verbose/debug)
5. **Python-Only Support**: Standalone binary or pure Python fallback
6. **Monorepo**: Up to 50 scopes with autocomplete/search threshold at 10
7. **Configuration**: YAML format (.commitlintrc.yml), single source of truth
8. **CI Integration**: Optional job in riso-quality.yml, validates all PR commits

**Next Phase**: Generate data-model.md, contracts/, and quickstart.md based on these research findings.
