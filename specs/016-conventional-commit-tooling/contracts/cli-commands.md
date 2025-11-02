# CLI Commands Contract

**Feature**: 016-conventional-commit-tooling  
**Component**: Command-Line Interface  
**Version**: 1.0.0

## Overview

This contract defines the command-line interface for conventional commit tooling. The CLI provides commands for guided commit authoring, hook installation, configuration management, and diagnostics.

---

## Global Options

Available for all commands:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--verbosity` | `-v` | enum | `normal` | Logging level: `normal`, `verbose`, `debug` |
| `--config` | `-c` | path | `.commitlintrc.yml` | Path to config file |
| `--profile` | `-p` | enum | `standard` | Validation profile: `standard`, `strict` |
| `--help` | `-h` | flag | - | Show help message |
| `--version` | - | flag | - | Show version information |

---

## Commands

### 1. `commit` (Guided Authoring)

**Description**: Interactive commit message authoring with validation

**Usage**:

```bash
# Python projects
uv run commit

# Node.js projects
pnpm run commit
```

**Aliases**: `c`, `create`

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--type` | string | - | Pre-select commit type (skip prompt) |
| `--scope` | string | - | Pre-select scope (skip prompt) |
| `--no-verify` | flag | false | Skip validation (emergency commits) |
| `--dry-run` | flag | false | Show message without committing |

**Interactive Flow**:

1. **Type Selection**:
   ```text
   ? Select the type of change that you're committing: (Use arrow keys)
   ❯ feat:     ✨ A new feature
     fix:      🐛 A bug fix
     docs:     📝 Documentation only changes
     style:    💄 Code style changes (formatting)
     refactor: ♻️  A code change that neither fixes a bug nor adds a feature
     perf:     ⚡️ A code change that improves performance
     test:     ✅ Adding or updating tests
     chore:    🔧 Changes to build process or tooling
   ```

2. **Scope Selection** (if scopes configured):
   ```text
   ? Denote the SCOPE of this change (optional):
   > (Start typing to search...)
   ```

   **Autocomplete** (when >10 scopes):
   - Fuzzy search with Levenshtein distance
   - Live filtering as user types
   - Response time: <100ms (per SC-009)

3. **Subject Input**:
   ```text
   ? Write a SHORT, IMPERATIVE tense description of the change:
   > add user authentication endpoint
   
   [Character count: 32/72]
   ```

4. **Body Input** (optional):
   ```text
   ? Provide a LONGER description of the change (optional):
   > (Press Enter to skip)
   ```

5. **Breaking Change Prompt**:
   ```text
   ? Are there any breaking changes? (y/N)
   ```

6. **Footer Input** (optional):
   ```text
   ? List any ISSUES CLOSED by this change (optional):
   > Closes #123, #456
   ```

7. **Confirmation**:
   ```text
   ✓ Commit message preview:
   
   feat(api): add user authentication endpoint
   
   Implements OAuth2 flow with JWT tokens.
   Adds middleware for protected routes.
   
   BREAKING CHANGE: Changes /login endpoint signature
   Closes #123, #456
   
   ? Confirm commit? (Y/n)
   ```

**Exit Codes**:

- `0`: Commit successful
- `1`: Validation failed
- `2`: User cancelled
- `3`: Internal error

**Examples**:

```bash
# Standard flow
uv run commit

# Pre-select type and scope
uv run commit --type feat --scope api

# Dry run (show message without committing)
uv run commit --dry-run

# Skip validation (emergency)
uv run commit --no-verify

# Verbose logging
uv run commit --verbosity verbose
```

---

### 2. `install-hooks` (Hook Installation)

**Description**: Install Git commit-msg hook for automatic validation

**Usage**:

```bash
# Python projects
uv run commit-tooling install-hooks

# Node.js projects
pnpm run commit-tooling:install-hooks
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force` | flag | false | Overwrite existing hook |
| `--backup` | flag | true | Backup existing hook before overwrite |
| `--dry-run` | flag | false | Show installation steps without executing |

**Behavior**:

1. Check if `.git/hooks/` directory exists
2. Check if `commit-msg` hook already exists
3. If exists and not forced:
   - Error: "Hook already exists. Use --force to overwrite."
   - Exit code 1
4. If exists and forced:
   - Create backup: `.git/hooks/commit-msg.backup`
   - Overwrite hook
5. Write hook script (Python or Node.js based on project)
6. Set executable permissions: `chmod +x .git/hooks/commit-msg`
7. Validate hook works: run against test message
8. Print success message with verification steps

**Exit Codes**:

- `0`: Installation successful
- `1`: Hook already exists (without --force)
- `2`: Installation failed (permissions, missing dependencies)
- `3`: Internal error

**Examples**:

```bash
# Standard installation
uv run commit-tooling install-hooks

# Force overwrite existing hook
uv run commit-tooling install-hooks --force

# Dry run (show steps without executing)
uv run commit-tooling install-hooks --dry-run

# Install without backup
uv run commit-tooling install-hooks --no-backup
```

**Output**:

```text
✓ Git hooks directory found: .git/hooks/
✓ Creating backup of existing hook: .git/hooks/commit-msg.backup
✓ Installing commit-msg hook (Python backend)
✓ Setting executable permissions
✓ Validating hook installation

Hook installed successfully!

To verify, run:
  echo "test(core): validate hook" | .git/hooks/commit-msg -

To uninstall:
  rm .git/hooks/commit-msg
```

---

### 3. `init` (Configuration Initialization)

**Description**: Create default configuration file

**Usage**:

```bash
# Python projects
uv run commit-tooling init

# Node.js projects
pnpm run commit-tooling:init
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--profile` | enum | `standard` | Base profile: `standard`, `strict` |
| `--format` | enum | `yaml` | Config format: `yaml`, `json` |
| `--output` | path | `.commitlintrc.yml` | Output file path |
| `--force` | flag | false | Overwrite existing config |
| `--scopes` | string | - | Comma-separated list of scopes |

**Behavior**:

1. Check if config file already exists
2. If exists and not forced:
   - Error: "Config already exists. Use --force to overwrite."
   - Exit code 1
3. Generate default config based on profile
4. If `--scopes` provided, add to `scope-enum` rule
5. Write config to file
6. Validate config syntax
7. Print success message with next steps

**Exit Codes**:

- `0`: Config created successfully
- `1`: Config already exists (without --force)
- `2`: Invalid parameters
- `3`: Internal error

**Examples**:

```bash
# Create standard config
uv run commit-tooling init

# Create strict config with custom scopes
uv run commit-tooling init --profile strict --scopes "api,cli,docs,core"

# Create JSON config
uv run commit-tooling init --format json --output commitlint.config.json

# Force overwrite existing config
uv run commit-tooling init --force
```

**Output**:

```text
✓ Creating configuration file: .commitlintrc.yml
✓ Profile: standard
✓ Custom scopes: api, cli, docs, core
✓ Validating configuration syntax

Configuration created successfully!

Next steps:
  1. Review configuration: cat .commitlintrc.yml
  2. Install Git hook: uv run commit-tooling install-hooks
  3. Test commit: uv run commit
```

---

### 4. `validate` (Message Validation)

**Description**: Validate commit message against configuration

**Usage**:

```bash
# Validate message from file
uv run commit-tooling validate .git/COMMIT_EDITMSG

# Validate message from stdin
echo "feat(api): add endpoint" | uv run commit-tooling validate -

# Validate message from argument
uv run commit-tooling validate --message "feat(api): add endpoint"
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--message` | string | - | Commit message text (alternative to file) |
| `--json` | flag | false | Output validation result as JSON |
| `--quiet` | flag | false | Suppress output (only exit code) |

**Exit Codes**:

- `0`: Message valid
- `1`: Message invalid
- `2`: Configuration error
- `3`: Internal error

**Examples**:

```bash
# Validate current commit message
uv run commit-tooling validate .git/COMMIT_EDITMSG

# Validate custom message
uv run commit-tooling validate --message "feat(api): add endpoint"

# Validate with JSON output
uv run commit-tooling validate --message "invalid" --json

# Validate from stdin
git log --format=%B -n 1 HEAD | uv run commit-tooling validate -
```

**Output (Text)**:

```text
✓ Commit message validation passed

Type: feat
Scope: api
Subject: add user authentication endpoint
```

**Output (JSON)**:

```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "input": "feat(api): add user authentication endpoint",
  "parsed": {
    "type": "feat",
    "scope": "api",
    "subject": "add user authentication endpoint",
    "body": null,
    "footer": null
  }
}
```

**Output (Invalid Message)**:

```text
⚠️ Commit message validation failed:

[type-enum] Invalid commit type 'featrue'
  Expected one of: feat, fix, docs, style, refactor, test, chore
  Suggestion: Did you mean 'feat'?

[subject-max-length] Subject exceeds maximum length
  Length: 85 characters
  Maximum: 72 characters
```

---

### 5. `config` (Configuration Management)

**Description**: Manage and validate configuration files

**Usage**:

```bash
# Show current configuration
uv run commit-tooling config --show

# Validate configuration
uv run commit-tooling config --validate

# List available scopes
uv run commit-tooling config --list-scopes

# List available types
uv run commit-tooling config --list-types
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--show` | flag | false | Display current configuration |
| `--validate` | flag | false | Validate configuration syntax |
| `--list-scopes` | flag | false | List configured scopes |
| `--list-types` | flag | false | List configured types |
| `--json` | flag | false | Output as JSON |

**Exit Codes**:

- `0`: Success
- `1`: Configuration invalid
- `2`: Configuration not found
- `3`: Internal error

**Examples**:

```bash
# Show current config
uv run commit-tooling config --show

# Validate config syntax
uv run commit-tooling config --validate

# List scopes as JSON
uv run commit-tooling config --list-scopes --json

# List types with descriptions
uv run commit-tooling config --list-types
```

**Output (--show)**:

```yaml
extends:
  - "@commitlint/config-conventional"

rules:
  type-enum:
    - 2
    - always
    - [feat, fix, docs, style, refactor, test, chore]
  
  scope-enum:
    - 1
    - always
    - [api, cli, docs, core]

Source: /path/to/project/.commitlintrc.yml
Profile: standard
```

**Output (--list-scopes)**:

```text
Configured scopes:
  • api      Backend API endpoints
  • cli      Command-line interface
  • docs     Documentation files
  • core     Core application logic
```

**Output (--list-types)**:

```text
Configured types:
  • feat       ✨ A new feature
  • fix        🐛 A bug fix
  • docs       📝 Documentation only changes
  • style      💄 Code style changes
  • refactor   ♻️  Code refactoring
  • test       ✅ Adding or updating tests
  • chore      🔧 Build process or tooling changes
```

---

### 6. `doctor` (Diagnostics)

**Description**: Diagnose configuration and installation issues

**Usage**:

```bash
uv run commit-tooling doctor
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | false | Output as JSON |
| `--verbose` | flag | false | Show detailed checks |

**Checks**:

1. ✓ Git repository detected
2. ✓ Git hooks directory exists
3. ✓ commit-msg hook installed
4. ✓ Hook is executable
5. ✓ Configuration file exists
6. ✓ Configuration syntax valid
7. ✓ Python runtime available (for Python projects)
8. ✓ Node.js runtime available (for Node.js projects)
9. ✓ Dependencies installed (commitlint/commitizen)

**Exit Codes**:

- `0`: All checks passed
- `1`: One or more checks failed
- `3`: Internal error

**Examples**:

```bash
# Run diagnostics
uv run commit-tooling doctor

# Verbose output
uv run commit-tooling doctor --verbose

# JSON output for CI
uv run commit-tooling doctor --json
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
✓ Dependencies installed (commitlint@18.4.0)

All checks passed! 🎉

To test the hook, run:
  echo "feat(test): validate hook" | .git/hooks/commit-msg -
```

**Output (With Errors)**:

```text
Running diagnostics...

✓ Git repository detected
✓ Git hooks directory exists (.git/hooks/)
✗ commit-msg hook not installed
  Recovery: uv run commit-tooling install-hooks

✗ Configuration file not found
  Recovery: uv run commit-tooling init

⚠️ Some checks failed. Run suggested recovery commands to fix issues.
```

---

## Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COMMIT_TOOLING_VERBOSITY` | enum | `normal` | Global verbosity level |
| `COMMIT_TOOLING_CONFIG` | path | `.commitlintrc.yml` | Config file path |
| `COMMIT_TOOLING_PROFILE` | enum | `standard` | Validation profile |
| `COMMIT_TOOLING_NO_COLOR` | bool | `false` | Disable colored output |
| `COMMIT_TOOLING_TIMEOUT` | int | `1000` | Hook timeout (ms) |

---

## Integration with Git

### Git Aliases

Add to `.git/config` or `~/.gitconfig`:

```ini
[alias]
  c = !uv run commit
  cm = !uv run commit --type feat
  cf = !uv run commit --type fix
```

### Git Hooks

The CLI integrates with Git's commit-msg hook automatically. No manual configuration required after running `install-hooks`.

---

## CI Integration

### GitHub Actions Example

```yaml
- name: Validate commit messages
  run: |
    git log --format=%B origin/main..HEAD | \
      uv run commit-tooling validate -
```

### Pre-push Validation

```bash
#!/bin/bash
# .git/hooks/pre-push

# Validate all commits being pushed
git log --format=%B @{u}..HEAD | uv run commit-tooling validate -
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-02 | Initial CLI contract definition |

---

## References

- Feature Spec: `specs/016-conventional-commit-tooling/spec.md`
- Hook Interface: `specs/016-conventional-commit-tooling/contracts/hook-interface.md`
- Config Schema: `specs/016-conventional-commit-tooling/contracts/config-schema.yaml`
