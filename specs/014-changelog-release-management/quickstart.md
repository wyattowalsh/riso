# Quickstart: Changelog & Release Management

**Feature**: 014-changelog-release-management  
**Date**: 2025-11-02  
**For**: Developers implementing or using the changelog module

## Overview

This guide walks through setting up automated changelog generation and release management for a Riso-generated project. Follow these steps to enable conventional commits, automatic versioning, and registry publishing.

---

## Prerequisites

- Riso template rendered with `changelog_module=enabled`
- GitHub repository with Actions enabled
- Node.js 20 LTS installed (for semantic-release)
- Python 3.11+ with uv (for Python projects)
- Registry accounts (PyPI, npm, Docker Hub) with credentials

---

## Quick Setup (5 minutes)

### 1. Install Git Hooks

**For Python projects**:
```bash
uv run setup-hooks
```

**For Node projects**:
```bash
pnpm run setup-hooks
```

**Verify installation**:
```bash
# Should show commit-msg hook installed
ls -la .git/hooks/commit-msg
```

### 2. Configure GitHub Secrets

Navigate to repository **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `PYPI_TOKEN` | PyPI API token | [pypi.org/manage/account/token](https://pypi.org/manage/account/token/) |
| `NPM_TOKEN` | npm authentication token | `npm login && npm token create` |
| `DOCKER_HUB_USERNAME` | Docker Hub username | Your Docker Hub account |
| `DOCKER_HUB_TOKEN` | Docker Hub access token | [hub.docker.com/settings/security](https://hub.docker.com/settings/security) |

**Note**: `GITHUB_TOKEN` is automatically provided by Actions - no manual setup needed.

### 3. Make Your First Conventional Commit

```bash
git add .
git commit -m "feat: add user authentication module

Implements OAuth2 password flow with JWT tokens.
Includes rate limiting and input validation."
```

The commit hook will validate the format. If invalid, you'll see:

```text
❌ Commit message does not follow conventional format

Expected format:
  <type>(<scope>): <subject>

Examples:
  feat(api): add user authentication
  fix(cli): correct argument parsing
  docs: update README with examples
```

### 4. Push and Trigger Release

```bash
git push origin main
```

The `riso-release.yml` workflow will:
1. Analyze commits since last release
2. Calculate next version (e.g., 1.0.0 → 1.1.0 for `feat:`)
3. Generate changelog entry
4. Update version in package files
5. Create GitHub Release
6. Publish to configured registries

**Release completes in <10 minutes**.

---

## Commit Message Format

### Structure

```text
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description | Version Bump | Example |
|------|-------------|--------------|---------|
| `feat` | New feature | MINOR (1.0.0 → 1.1.0) | `feat(api): add user search` |
| `fix` | Bug fix | PATCH (1.0.0 → 1.0.1) | `fix(cli): handle empty input` |
| `docs` | Documentation | None | `docs: update API guide` |
| `chore` | Maintenance | None | `chore(deps): update dependencies` |
| `refactor` | Code restructure | None | `refactor(core): simplify auth logic` |
| `test` | Add tests | None | `test(api): add integration tests` |
| `perf` | Performance | PATCH | `perf(db): optimize query` |

### Breaking Changes

Trigger MAJOR version bump (1.0.0 → 2.0.0):

```text
feat!: redesign authentication API

BREAKING CHANGE: Auth endpoints now require OAuth2 tokens.
Migration: Update client code to use new OAuth2 flow.
See docs/migration-v2.md for details.
```

**Note**: Include migration instructions in footer.

---

## Manual Release

Trigger release without pushing to main:

```bash
# Via GitHub UI:
# Actions → Release → Run workflow → Select branch → Run workflow

# Via GitHub CLI:
gh workflow run release.yml
```

---

## Dry Run (Testing)

Test release process without publishing:

```bash
# Set DRY_RUN environment variable
DRY_RUN=true npx semantic-release --dry-run

# Shows:
# - Calculated next version
# - Generated changelog
# - Would-be published artifacts
```

---

## Monorepo Projects

For monorepos with independent package versioning:

### Commit Format

Include package scope:

```bash
git commit -m "feat(api): add user endpoint"  # Releases api package
git commit -m "fix(cli): correct flag parsing"  # Releases cli package
```

### Release Tags

Each package gets independent tags:
- `api/v1.2.0`
- `cli/v2.0.1`

### Workflow

Matrix strategy releases packages in dependency order:

```yaml
# Defined in .releaserc.yml per package
packages:
  - name: api
    path: packages/api
  - name: cli
    path: packages/cli
    dependencies: [api]  # Released after api
```

---

## Troubleshooting

### Commit Hook Not Running

**Symptom**: Commits with invalid format accepted

**Fix**:
```bash
# Reinstall hooks
uv run setup-hooks  # or pnpm run setup-hooks

# Verify hook exists
cat .git/hooks/commit-msg
```

### Release Workflow Fails

**Symptom**: GitHub Actions workflow fails with credential error

**Fix**:
1. Verify secrets configured: Settings → Secrets → Actions
2. Check secret names match exactly (case-sensitive)
3. Test credentials locally:
   ```bash
   # PyPI
   python -m twine check dist/*
   
   # npm
   npm login && npm whoami
   
   # Docker Hub
   echo $DOCKER_HUB_TOKEN | docker login -u $DOCKER_HUB_USERNAME --password-stdin
   ```

### Version Not Bumping

**Symptom**: Push to main doesn't trigger release

**Cause**: No qualifying commits since last release

**Fix**:
- Ensure commits have `feat:` or `fix:` type
- Check commit history: `git log --oneline`
- Verify last release tag: `git describe --tags --abbrev=0`

### Changelog Not Updated

**Symptom**: CHANGELOG.md not generated

**Fix**:
```bash
# Check .releaserc.yml includes changelog plugin
cat .releaserc.yml | grep changelog

# Should see:
# plugins:
#   - "@semantic-release/changelog"
```

---

## Advanced Configuration

### Custom Commit Types

Edit `.commitlintrc.yml`:

```yaml
rules:
  type-enum:
    - 2
    - always
    - [feat, fix, docs, chore, refactor, test, perf, security, breaking]
```

### Custom Changelog Sections

Edit `.releaserc.yml`:

```yaml
plugins:
  - - "@semantic-release/release-notes-generator"
    - preset: "angular"
      writerOpts:
        commitGroupsSort: ["feat", "fix", "perf", "security"]
        transform:
          feat: "✨ New Features"
          fix: "🐛 Bug Fixes"
          security: "🔒 Security Updates"
```

### Registry-Specific Configuration

**PyPI only (skip npm)**:
```yaml
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
  - - "@semantic-release/exec"
    - publishCmd: "python scripts/publish-pypi.py"
  - "@semantic-release/github"
  # npm plugin omitted
```

---

## Credential Rotation

**Schedule**: Annual rotation recommended

**Process**:

1. **Generate new tokens**:
   - PyPI: [pypi.org/manage/account/token](https://pypi.org/manage/account/token/)
   - npm: `npm token create`
   - Docker Hub: [hub.docker.com/settings/security](https://hub.docker.com/settings/security)

2. **Update GitHub Secrets**:
   - Settings → Secrets → Actions → Edit secret

3. **Test new credentials**:
   ```bash
   # Trigger test release
   gh workflow run release.yml
   ```

4. **Revoke old tokens**:
   - Only after confirming new tokens work

---

## Next Steps

- [Full Module Documentation](../docs/modules/changelog-release.md)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning Guide](https://semver.org/)
- [semantic-release Documentation](https://semantic-release.gitbook.io/)

---

## Summary

You now have:
- ✅ Git hooks validating commit messages
- ✅ GitHub Actions automating releases
- ✅ Registry credentials configured
- ✅ Conventional commit workflow established

**Next commit triggers your first automated release!**
