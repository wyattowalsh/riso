# Data Model: Changelog & Release Management

**Date**: 2025-11-02\
**Feature**: 014-changelog-release-management\
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data structures, entities, and their relationships for the changelog and release management feature. These models drive configuration file generation, commit validation, version calculation, and release orchestration.

______________________________________________________________________

## Core Entities

### 1. Commit Message

Structured text following Conventional Commits specification.

**Fields**:

- `type` (string, required): Commit type - one of: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`, `revert`
- `scope` (string, optional): Component or module affected (e.g., `api`, `cli`, `core`)
- `subject` (string, required): Short description (≤72 characters, imperative mood)
- `body` (string, optional): Detailed description (multi-line, markdown-formatted)
- `footer` (string, optional): Metadata (BREAKING CHANGE, issue references, co-authors)
- `breaking` (boolean, computed): True if footer contains "BREAKING CHANGE" or type suffixed with `!`

**Format**:

```text
<type>[optional scope][!]: <subject>

[optional body]

[optional footer]
```

**Examples**:

```text
feat(api): add user authentication endpoint

Implements OAuth2 password flow with JWT tokens.
Includes rate limiting and input validation.

Closes #123

---

fix!: correct timezone handling in date parser

BREAKING CHANGE: Date strings now require explicit timezone.
Migration: Add 'Z' suffix to UTC dates or specify offset.
```

**Validation Rules**:

- Type must be from allowed list (configurable)
- Scope must match regex pattern `[a-z0-9-]+` (if present)
- Subject required, no trailing period, lowercase first letter
- Breaking changes must include migration notes in footer

______________________________________________________________________

### 2. Version

Semantic version number following SemVer 2.0.0 specification.

**Fields**:

- `major` (integer, ≥0): Breaking changes increment
- `minor` (integer, ≥0): New features increment (resets on major bump)
- `patch` (integer, ≥0): Bug fixes increment (resets on major/minor bump)
- `pre release` (string, optional): Pre-release identifier (e.g., `alpha.1`, `beta.2`, `rc.1`)
- `build_metadata` (string, optional): Build metadata (e.g., `20130313144700`, `SHA.5114f85`)

**Format**: `MAJOR.MINOR.PATCH[-PRERELEASE][+BUILDMETADATA]`

**Examples**:

- `1.0.0` - Initial stable release
- `1.1.0` - New feature added
- `1.1.1` - Bug fix applied
- `2.0.0` - Breaking change introduced
- `2.0.0-beta.1` - Pre-release before 2.0.0
- `1.0.0+20130313144700` - With build metadata

**Calculation Rules**:

| Commit Type       | Version Bump | Example       |
| ----------------- | ------------ | ------------- |
| `fix:`            | PATCH        | 1.0.0 → 1.0.1 |
| `feat:`           | MINOR        | 1.0.0 → 1.1.0 |
| `BREAKING CHANGE` | MAJOR        | 1.0.0 → 2.0.0 |
| `chore:`, `docs:` | None         | No release    |

______________________________________________________________________

### 3. Changelog Entry

Generated markdown documenting changes for a specific version.

**Fields**:

- `version` (Version): Semantic version for this entry
- `release_date` (date, ISO 8601): Date of release (YYYY-MM-DD)
- `breaking_changes` (array of Change): Breaking changes section
- `features` (array of Change): New features section
- `bug_fixes` (array of Change): Bug fixes section
- `documentation` (array of Change): Documentation updates section
- `other` (array of Change): Other changes (chores, etc.)

**Format**:

```markdown
# [VERSION] (YYYY-MM-DD)

## 💥 BREAKING CHANGES

- **scope**: description (#PR) ([commit](link))
  - Migration: instructions

## ✨ Features

- **scope**: description (#PR) ([commit](link))

## 🐛 Bug Fixes

- **scope**: description (#PR) ([commit](link))
```

**Categorization Rules**:

- Breaking changes always first
- Sections sorted by significance: BREAKING > Features > Fixes > Docs > Other
- Empty sections omitted
- Commits grouped by scope within sections

______________________________________________________________________

### 4. Change

Individual change entry within a changelog section.

**Fields**:

- `type` (string): Commit type
- `scope` (string, optional): Component affected
- `subject` (string): Short description
- `commit_sha` (string): Full commit SHA
- `commit_short_sha` (string): Short SHA (7 chars)
- `commit_url` (string): GitHub commit URL
- `pr_number` (integer, optional): Pull request number
- `pr_url` (string, optional): Pull request URL
- `breaking` (boolean): Is breaking change
- `migration_notes` (string, optional): Migration instructions (if breaking)

**Format**:

```markdown
- **scope**: subject (#PR) ([SHA](url))
```

______________________________________________________________________

### 5. Release Configuration

Settings defining release behavior for a project.

**Fields**:

- `branches` (array of string): Branches that trigger releases (e.g., `["main", "next"]`)
- `repository_url` (string): GitHub repository URL
- `tag_format` (string): Git tag format (e.g., `v${version}`, `${name}/v${version}` for monorepo)
- `commit_types` (map\<string, CommitTypeConfig>): Commit type configurations
- `changelog_file` (string): Changelog file path (default: `CHANGELOG.md`)
- `assets` (array of Asset): Files to attach to GitHub Release
- `plugins` (array of Plugin): semantic-release plugins configuration
- `monorepo_config` (MonorepoConfig, optional): Monorepo settings

**Example**:

```yaml
branches: ["main"]
repositoryUrl: "https://github.com/owner/repo"
tagFormat: "v${version}"
commitTypes:
  feat:
    section: "✨ Features"
    hidden: false
  fix:
    section: "🐛 Bug Fixes"
    hidden: false
  chore:
    section: null
    hidden: true
changelogFile: "CHANGELOG.md"
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
  - "@semantic-release/github"
```

______________________________________________________________________

### 6. Commit Type Config

Configuration for a specific commit type.

**Fields**:

- `section` (string, nullable): Changelog section heading (null to hide)
- `hidden` (boolean): Exclude from changelog entirely
- `emoji` (string, optional): Emoji prefix for section

**Defaults**:

| Type       | Section       | Hidden | Emoji |
| ---------- | ------------- | ------ | ----- |
| `feat`     | Features      | false  | ✨    |
| `fix`      | Bug Fixes     | false  | 🐛    |
| `docs`     | Documentation | false  | 📝    |
| `perf`     | Performance   | false  | ⚡    |
| `refactor` | Refactoring   | true   | ♻️    |
| `test`     | Tests         | true   | ✅    |
| `chore`    | Chores        | true   | 🔧    |

______________________________________________________________________

### 7. Asset

File attachment for GitHub Release.

**Fields**:

- `path` (string): File path relative to repository root
- `name` (string, optional): Display name (defaults to filename)
- `label` (string, optional): Asset label in release

**Examples**:

```yaml
assets:
  - path: "dist/*.tar.gz"
    name: "Source Distribution"
  - path: "dist/*.whl"
    name: "Python Wheel"
```

______________________________________________________________________

### 8. Plugin Configuration

semantic-release plugin with options.

**Fields**:

- `name` (string): Plugin npm package name
- `options` (object, optional): Plugin-specific configuration

**Common Plugins**:

```yaml
plugins:
  - "@semantic-release/commit-analyzer"

  - - "@semantic-release/release-notes-generator"
    - preset: "angular"
      writerOpts:
        commitGroupsSort: ["feat", "fix", "perf"]

  - - "@semantic-release/exec"
    - prepareCmd: "python scripts/update-version.py ${nextRelease.version}"
      publishCmd: "python scripts/publish-pypi.py"

  - - "@semantic-release/github"
    - assets:
        - path: "dist/*.whl"
```

______________________________________________________________________

### 9. Monorepo Configuration

Settings for monorepo projects with multiple packages.

**Fields**:

- `packages` (array of PackageConfig): Package definitions
- `versioning` (string): `independent` or `fixed` (all packages same version)
- `changelog_per_package` (boolean): Generate CHANGELOG.md per package vs. root only

**Example**:

```yaml
monorepoConfig:
  versioning: "independent"
  changelogPerPackage: true
  packages:
    - name: "api"
      path: "packages/api"
      tagFormat: "api/v${version}"
    - name: "cli"
      path: "packages/cli"
      tagFormat: "cli/v${version}"
```

______________________________________________________________________

### 10. Package Configuration

Individual package within a monorepo.

**Fields**:

- `name` (string): Package name (used in commit scopes)
- `path` (string): Package directory relative to repository root
- `tag_format` (string): Git tag format for this package
- `dependencies` (array of string, optional): Other packages this depends on (for release ordering)

______________________________________________________________________

## Relationships

```text
ReleaseConfiguration
  ├─ 1:N → CommitTypeConfig
  ├─ 1:N → Asset
  ├─ 1:N → PluginConfiguration
  └─ 0:1 → MonorepoConfig
           └─ 1:N → PackageConfig

Commit Message
  ├─ generates → Version (via calculation rules)
  └─ creates → Change (in changelog)

ChangelogEntry
  ├─ belongs to → Version
  └─ contains → 1:N Change

Change
  └─ derived from → CommitMessage
```

______________________________________________________________________

## State Transitions

### Release Lifecycle

```text
[No Release] ─┬─ Commits with feat/fix ──→ [Pending Release]
              └─ No qualifying commits ───→ [No Release]

[Pending Release] ─┬─ Trigger release ────→ [Calculating Version]
                   └─ Revert commits ─────→ [No Release]

[Calculating Version] ──────────────────→ [Generating Changelog]

[Generating Changelog] ──────────────────→ [Publishing Artifacts]

[Publishing Artifacts] ─┬─ Success ──────→ [Creating GitHub Release]
                        └─ Failure ──────→ [Release Failed]

[Creating GitHub Release] ─┬─ Success ──→ [Release Complete]
                           └─ Failure ──→ [Partial Release]

[Release Complete] ─────────────────────→ [No Release] (cycle repeats)

[Release Failed] ───── Manual intervention ──→ [Retry/Rollback]
```

### Version State

```text
[Unreleased] ─┬─ BREAKING commit ──→ [Next Major]
              ├─ feat commit ───────→ [Next Minor]
              ├─ fix commit ────────→ [Next Patch]
              └─ other commit ──────→ [Unreleased]

[Next Major/Minor/Patch] ─┬─ Release triggered ──→ [Tagged]
                          └─ More commits ────────→ [Recompute]

[Tagged] ───────────────────────────────────────→ [Released]

[Released] ──── New commits ────────────────────→ [Unreleased]
```

______________________________________________________________________

## Validation Rules

### Commit Message Validation

1. Type must be in allowed list (default: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`, `revert`)
1. Scope (if present) must match pattern: `^[a-z0-9-]+$`
1. Subject required, max 72 characters
1. Subject must not end with period
1. Breaking changes must include footer with migration notes

### Version Validation

1. Must follow SemVer 2.0.0 format
1. Major/minor/patch must be non-negative integers
1. Pre-release identifier must match `^[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*$`
1. New version must be greater than previous (no downgrades)

### Release Configuration Validation

1. At least one branch specified
1. Repository URL must be valid GitHub URL
1. Changelog file must end with `.md`
1. Plugin names must be valid npm packages
1. Monorepo package paths must exist and be unique

______________________________________________________________________

## Performance Considerations

### Commit Analysis

- Parse commits incrementally (streaming)
- Cache parsed commits between runs
- Limit analysis to commits since last tag
- Use `git log --format` for efficient parsing

### Changelog Generation

- Generate markdown in memory (no disk I/O during build)
- Batch GitHub API calls for PR/commit links
- Limit to 1000 most recent commits per release
- Use template engine for formatting (jinja2/handlebars)

### Version Calculation

- Short-circuit on first BREAKING CHANGE commit
- Use commit message cache to avoid re-parsing
- Memoize version calculation results

______________________________________________________________________

## Summary

Data model complete with 10 core entities, relationship definitions, state transitions, and validation rules. All structures support template generation via Jinja2 and JSON Schema validation.

**Next Step**: Generate contracts (JSON Schemas for configuration files).
