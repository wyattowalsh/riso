# Quickstart Guide: Conventional Commit Tooling

**Feature**: 016-conventional-commit-tooling  
**Status**: Development  
**Last Updated**: 2025-11-02

## What You'll Learn

This guide shows you how to:

1. Install the conventional commit tooling in your project
2. Set up Git hooks for automatic validation
3. Use the guided commit authoring CLI
4. Configure custom commit types and scopes
5. Integrate with CI/CD pipelines

**Time to Complete**: ~10 minutes

---

## Prerequisites

Ensure you have the Riso template rendered with `commit_tooling_module=enabled`:

```bash
# Check your project's module configuration
cat .riso/post_gen_metadata.json | grep commit_tooling_module
```

**Expected Output**:

```json
{
  "commit_tooling_module": "enabled"
}
```

**Required Tools**:

- Git ≥2.30 (check: `git --version`)
- Python ≥3.11 with uv (check: `python3 --version`, `uv version`)
- Node.js 20 LTS and pnpm ≥8 (optional, for Node.js projects with `api_tracks` including `node`)

---

## Step 1: Initialize Configuration

Create the default `.commitlintrc.yml` configuration file:

```bash
# Python projects
uv run commit-tooling init

# Node.js projects (if api_tracks includes node)
pnpm run commit-tooling:init
```

**Output**:

```text
✓ Creating configuration file: .commitlintrc.yml
✓ Profile: standard
✓ Validating configuration syntax

Configuration created successfully!
```

**What Was Created**:

```yaml
# .commitlintrc.yml
extends:
  - '@commitlint/config-conventional'

rules:
  type-enum:
    - 2  # error level
    - always
    - [feat, fix, docs, style, refactor, test, chore]
  
  subject-max-length:
    - 2
    - always
    - 72
  
  body-leading-blank:
    - 2
    - always
  
  footer-leading-blank:
    - 2
    - always
```

---

## Step 2: Install Git Hooks

Install the commit-msg hook for automatic validation:

```bash
# Python projects
uv run commit-tooling install-hooks

# Node.js projects
pnpm run commit-tooling:install-hooks
```

**Output**:

```text
✓ Git hooks directory found: .git/hooks/
✓ Installing commit-msg hook (Python backend)
✓ Setting executable permissions
✓ Validating hook installation

Hook installed successfully!
```

**What Happened**:

1. Created executable hook script: `.git/hooks/commit-msg`
2. Hook will run automatically before each commit
3. Invalid commit messages will be rejected with helpful error messages

**Verify Installation**:

```bash
# Test the hook with a valid message
echo "feat(test): validate hook installation" | .git/hooks/commit-msg -

# Test with an invalid message
echo "invalid message" | .git/hooks/commit-msg -
```

**Expected Output (Valid)**:

```text
✓ Commit message validation passed
```

**Expected Output (Invalid)**:

```text
⚠️ Commit message validation failed:

[type-enum] Invalid commit type ''
  Expected one of: feat, fix, docs, style, refactor, test, chore
```

---

## Step 3: Your First Validated Commit

Try a standard commit (will be validated automatically):

```bash
git add .
git commit -m "feat(core): add conventional commit tooling"
```

**Output**:

```text
✓ Commit message validation passed
[main a1b2c3d] feat(core): add conventional commit tooling
 1 file changed, 50 insertions(+)
```

**Try an Invalid Commit**:

```bash
git commit -m "added new feature"
```

**Output**:

```text
⚠️ Commit message validation failed:

[type-enum] Invalid commit type ''
  Expected one of: feat, fix, docs, style, refactor, test, chore
  Suggestion: Use 'feat: added new feature' for new features

Commit rejected. Fix your message and try again.
```

---

## Step 4: Use Guided Commit Authoring

For complex commits, use the interactive CLI:

```bash
# Python projects
uv run commit

# Node.js projects
pnpm run commit
```

**Interactive Flow**:

**1. Select Type**:

```text
? Select the type of change that you're committing: (Use arrow keys)
❯ feat:     ✨ A new feature
  fix:      🐛 A bug fix
  docs:     📝 Documentation only changes
  style:    💄 Code style changes (formatting)
  refactor: ♻️  A code change that neither fixes a bug nor adds a feature
  test:     ✅ Adding or updating tests
  chore:    🔧 Changes to build process or tooling
```

**2. Enter Scope** (optional):

```text
? Denote the SCOPE of this change (optional):
> api
```

**3. Enter Subject**:

```text
? Write a SHORT, IMPERATIVE tense description of the change:
> add user authentication endpoint

[Character count: 32/72]
```

**4. Enter Body** (optional):

```text
? Provide a LONGER description of the change (optional):
> Implements OAuth2 flow with JWT tokens.
Adds middleware for protected routes.
```

**5. Breaking Changes** (optional):

```text
? Are there any breaking changes? (y/N)
> y

? Describe the breaking changes:
> Changes /login endpoint signature. Old clients must update.
```

**6. Issue References** (optional):

```text
? List any ISSUES CLOSED by this change (optional):
> Closes #123, #456
```

**7. Confirm**:

```text
✓ Commit message preview:

feat(api): add user authentication endpoint

Implements OAuth2 flow with JWT tokens.
Adds middleware for protected routes.

BREAKING CHANGE: Changes /login endpoint signature. Old clients must update.
Closes #123, #456

? Confirm commit? (Y/n)
```

**8. Success**:

```text
✓ Commit created successfully!
[main b2c3d4e] feat(api): add user authentication endpoint
 5 files changed, 200 insertions(+), 10 deletions(-)
```

---

## Step 5: Configure Custom Scopes

Add project-specific scopes to improve navigation:

```bash
# Edit .commitlintrc.yml
cat >> .commitlintrc.yml << 'EOF'

# Add custom scopes
rules:
  scope-enum:
    - 1  # warning level (allows custom scopes with warning)
    - always
    - [api, cli, docs, core, web, mobile, tests, config]

# Add scope descriptions for guided authoring
prompt:
  settings:
    scopeOverrides:
      feat:
        - api
        - cli
        - core
      fix:
        - api
        - core
        - web
      docs:
        - docs
EOF
```

**Test Scope Validation**:

```bash
# Valid scope (from allowlist)
git commit -m "feat(api): add endpoint"

# Custom scope (warning logged, but allowed)
git commit -m "feat(database): add migration"
```

**With Guided Authoring** (scopes now filtered by type):

```bash
uv run commit --type feat
```

```text
? Denote the SCOPE of this change (optional):
  api
  cli
  core
> (Start typing to search...)
```

---

## Step 6: Use Strict Profile

For stricter validation (shorter subjects, mandatory lowercase):

```bash
# Regenerate config with strict profile
uv run commit-tooling init --profile strict --force
```

**Strict Profile Changes**:

| Rule | Standard | Strict |
|------|----------|--------|
| `subject-max-length` | 72 chars | 50 chars |
| `subject-case` | Off | `lower-case` only |
| `scope-enum` | Warning | Error (blocks commit) |
| `hook-timeout` | 1000ms | 500ms |

**Example**:

```bash
# Allowed in standard, rejected in strict
git commit -m "Feat(api): Add endpoint"  # ❌ Capital letters rejected

# Correct in strict profile
git commit -m "feat(api): add endpoint"  # ✅
```

---

## Step 7: Integrate with CI

Validate all commits in a pull request:

### GitHub Actions

Create `.github/workflows/validate-commits.yml`:

```yaml
name: Validate Commits

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate-commits:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Fetch full history
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv sync
      
      - name: Validate commit messages
        run: |
          BASE_SHA="${{ github.event.pull_request.base.sha }}"
          HEAD_SHA="${{ github.sha }}"
          
          # Validate each commit in the PR
          git log --format=%B "$BASE_SHA..$HEAD_SHA" | \
            uv run commit-tooling validate -
```

### Pre-push Hook (Optional)

Validate commits before pushing:

```bash
# Create .git/hooks/pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

# Validate all commits being pushed
git log --format=%B @{u}..HEAD | uv run commit-tooling validate -

if [ $? -ne 0 ]; then
  echo "⚠️ Some commits have invalid messages. Push rejected."
  exit 1
fi
EOF

chmod +x .git/hooks/pre-push
```

---

## Step 8: Troubleshooting

### Check Installation

Run diagnostics to verify everything is set up correctly:

```bash
uv run commit-tooling doctor
```

**Output**:

```text
Running diagnostics...

✓ Git repository detected
✓ Git hooks directory exists (.git/hooks/)
✓ commit-msg hook installed
✓ Hook is executable (permissions: 0755)
✓ Configuration file exists (.commitlintrc.yml)
✓ Configuration syntax valid
✓ Python runtime available (3.11.5)
✓ Dependencies installed

All checks passed! 🎉
```

### Common Issues

**Issue 1: Hook Not Executable**

```bash
# Symptom
fatal: cannot exec '.git/hooks/commit-msg': Permission denied

# Fix
chmod +x .git/hooks/commit-msg
```

**Issue 2: Configuration Not Found**

```bash
# Symptom
⚠️ Configuration error: Could not load .commitlintrc.yml

# Fix
uv run commit-tooling init
```

**Issue 3: Hook Timeout**

```bash
# Symptom
⚠️ Hook timeout exceeded (1000ms)

# Fix: Increase timeout
COMMIT_TOOLING_TIMEOUT=2000 git commit
```

**Issue 4: Node.js Runtime Missing** (Node.js projects)

```bash
# Symptom
Hook requires Node.js runtime (not found)

# Fix
mise install node@20
# or
nvm install 20
```

---

## Advanced Usage

### Emergency Commits

Skip validation for emergency fixes:

```bash
# Option 1: Environment variable
COMMIT_TOOLING_SKIP=true git commit -m "emergency fix"

# Option 2: --no-verify flag (skips all hooks)
git commit --no-verify -m "emergency fix"

# Option 3: Guided authoring with skip
uv run commit --no-verify
```

### Custom Configuration Location

Use a different config file:

```bash
# Set environment variable
export COMMIT_TOOLING_CONFIG=.config/commitlint.yml

# Or pass to each command
uv run commit-tooling validate --config .config/commitlint.yml
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
# Normal mode (errors only)
git commit -m "feat: add feature"

# Verbose mode (errors + warnings + info)
COMMIT_TOOLING_VERBOSITY=verbose git commit -m "feat: add feature"

# Debug mode (all logs)
COMMIT_TOOLING_VERBOSITY=debug git commit -m "feat: add feature"
```

**Debug Output Example**:

```text
[DEBUG] Loading configuration from .commitlintrc.yml
[DEBUG] Parsed configuration: {'extends': '@commitlint/config-conventional', ...}
[DEBUG] Validating commit message: feat(api): add endpoint
[DEBUG] Rule check: type-enum -> PASS (type='feat', allowed=['feat', 'fix', ...])
[DEBUG] Rule check: scope-enum -> PASS (scope='api', allowed=['api', 'cli', ...])
[DEBUG] Rule check: subject-case -> PASS (case='lower', expected=['lower', 'sentence'])
[DEBUG] Rule check: subject-max-length -> PASS (length=12, max=72)
✓ Commit message validation passed (45ms)
```

### Autocomplete for Large Projects

When you have many scopes (>10), fuzzy search autocomplete activates automatically:

```bash
# With 50 scopes configured
uv run commit --type feat
```

```text
? Denote the SCOPE of this change (optional):
> (Start typing to search...)

# User types "auth"
? Denote the SCOPE of this change (optional):
> auth
  authentication
  authorization
  auth-api
  auth-cli
```

**Performance**: <100ms response time for 50 scopes (per SC-009, Scalability Constraints)

---

## Next Steps

**✅ You've completed the quickstart!**

You now know how to:

- ✓ Initialize configuration
- ✓ Install Git hooks
- ✓ Make validated commits
- ✓ Use guided authoring
- ✓ Configure custom scopes
- ✓ Integrate with CI/CD
- ✓ Troubleshoot issues

**Explore Further**:

1. **Configuration**: Read `contracts/config-schema.yaml` for all available rules
2. **CLI**: See `contracts/cli-commands.md` for full command reference
3. **Hooks**: Review `contracts/hook-interface.md` for hook behavior details
4. **Advanced**: Configure custom types, emoji prefixes, and more

**Community & Support**:

- Report issues: https://github.com/your-org/riso/issues
- Documentation: See `docs/modules/commit-tooling.md` in rendered projects
- Examples: Check `samples/` directory in the Riso template repository

---

## Summary

**Time Spent**: ~10 minutes  
**What You Installed**:

- Configuration file: `.commitlintrc.yml`
- Git hook: `.git/hooks/commit-msg`
- CLI tools: `commit`, `commit-tooling`

**Key Commands**:

```bash
# Initialize
uv run commit-tooling init

# Install hooks
uv run commit-tooling install-hooks

# Guided commit
uv run commit

# Manual commit (validated)
git commit -m "feat(scope): subject"

# Validate message
uv run commit-tooling validate --message "feat: example"

# Diagnostics
uv run commit-tooling doctor
```

**Resources**:

- Conventional Commits: https://www.conventionalcommits.org/
- Commitlint: https://commitlint.js.org/
- Commitizen: https://commitizen-tools.github.io/commitizen/

---

**Congratulations!** Your project now enforces conventional commit format automatically. 🎉
