# Git Hook Interface Contract

**Feature**: 016-conventional-commit-tooling  
**Component**: Git commit-msg Hook  
**Version**: 1.0.0

## Overview

This contract defines the interface between Git's commit-msg hook and the conventional commit validation system. The hook must be executable, receive the commit message file path as an argument, and exit with appropriate status codes.

---

## Hook Invocation

### Entry Point

**Python Projects** (default when `api_tracks` excludes `node`):

```bash
#!/usr/bin/env python3
# .git/hooks/commit-msg
# Invoked automatically by Git during commit process
```

**Node.js Projects** (when `api_tracks` includes `node`):

```bash
#!/usr/bin/env node
// .git/hooks/commit-msg
// Invoked automatically by Git during commit process
```

### Execution Context

| Property | Value | Notes |
|----------|-------|-------|
| **Working Directory** | Repository root | Git sets CWD to repo root |
| **Environment Variables** | Git environment vars | `GIT_DIR`, `GIT_EDITOR`, etc. |
| **STDIN** | None | Hook does not read from stdin |
| **Arguments** | `$1` = commit message file path | Relative or absolute path |
| **Exit Code** | 0 = success, 1 = failure | Non-zero blocks commit |
| **Timeout** | <500ms target, <1000ms max | Per Technical Constraints |

### Command-Line Interface

```bash
# Invoked by Git automatically:
.git/hooks/commit-msg .git/COMMIT_EDITMSG

# Manual invocation for testing:
.git/hooks/commit-msg /path/to/test_message.txt

# With verbose logging:
COMMIT_TOOLING_VERBOSITY=verbose .git/hooks/commit-msg .git/COMMIT_EDITMSG

# With debug logging:
COMMIT_TOOLING_VERBOSITY=debug .git/hooks/commit-msg .git/COMMIT_EDITMSG
```

---

## Input Contract

### Commit Message File Format

**File Path**: First command-line argument (`sys.argv[1]` in Python, `process.argv[2]` in Node.js)

**File Content**: UTF-8 text file containing commit message

**Format**:

```text
<type>[optional scope]: <subject>

[optional body]

[optional footer]
```

**Example**:

```text
feat(api): add user authentication endpoint

Implements OAuth2 flow with JWT tokens.
Adds middleware for protected routes.

BREAKING CHANGE: Changes /login endpoint signature
```

### File Size Constraints

- **Maximum size**: 10KB (enforced by hook)
- **Empty file**: Invalid (reject with error)
- **Whitespace-only**: Invalid (reject with error)

### Edge Cases

**Merge Commits**:

```text
Merge branch 'feature-x' into main
```

- **Behavior**: Skip validation (FR-015: Ignore merge/revert commits)
- **Detection**: Message starts with "Merge"

**Revert Commits**:

```text
Revert "feat(api): add endpoint"
```

- **Behavior**: Skip validation
- **Detection**: Message starts with "Revert"

**Fixup/Squash Commits**:

```text
fixup! feat(api): add endpoint
```

- **Behavior**: Skip validation during interactive rebase
- **Detection**: Message starts with "fixup!" or "squash!"

---

## Output Contract

### Exit Codes

| Code | Meaning | Git Behavior | Hook Behavior |
|------|---------|--------------|---------------|
| **0** | Validation passed | Commit allowed | Print success message (if verbose), exit cleanly |
| **1** | Validation failed | Commit rejected | Print error messages + suggestions, exit with code 1 |
| **2** | Configuration error | Commit rejected | Print config error, exit with code 2 |
| **3** | Internal error | Commit rejected | Print stack trace (if debug), exit with code 3 |

### STDOUT Format

**Normal Mode** (default):

- No output on success (silent validation)
- Only error messages on failure

**Verbose Mode** (`COMMIT_TOOLING_VERBOSITY=verbose`):

```text
✓ Commit message validation passed
  Type: feat
  Scope: api
  Subject: add user authentication endpoint
```

**Debug Mode** (`COMMIT_TOOLING_VERBOSITY=debug`):

```text
[DEBUG] Loading configuration from .commitlintrc.yml
[DEBUG] Parsed configuration: {'extends': '@commitlint/config-conventional', ...}
[DEBUG] Validating commit message: feat(api): add user authentication
[DEBUG] Rule check: type-enum -> PASS
[DEBUG] Rule check: scope-enum -> PASS
[DEBUG] Rule check: subject-case -> PASS
✓ Commit message validation passed
```

### STDERR Format

**Validation Errors** (exit code 1):

```text
⚠️ Commit message validation failed:

[type-enum] Invalid commit type 'featrue'
  Expected one of: feat, fix, docs, style, refactor, test, chore
  Suggestion: Did you mean 'feat'?

[subject-max-length] Subject exceeds maximum length
  Length: 85 characters
  Maximum: 72 characters
  Suggestion: Shorten subject to 72 characters or less
```

**Configuration Errors** (exit code 2):

```text
⚠️ Configuration error:
  Could not load .commitlintrc.yml: File not found

Recovery steps:
  1. Run 'uv run commit-tooling init' to create default config
  2. Or manually create .commitlintrc.yml in project root
```

**Internal Errors** (exit code 3):

```text
⚠️ Internal error during validation:
  AttributeError: 'NoneType' object has no attribute 'get'

Stack trace:
  File "hook.py", line 42, in validate_message
    rule_config = config['rules'].get('type-enum')
                  ^^^^^^^^^^^^^^

Please report this issue at https://github.com/your-org/riso/issues
```

---

## Configuration Loading

### Discovery Order

1. `.commitlintrc.yml` in repository root
2. `.commitlintrc.yaml` in repository root
3. `commitlint.config.js` (Node.js projects only, when `api_tracks` includes `node`)
4. `package.json` → `commitlint` key (Node.js projects only)
5. Fallback to default configuration (warning logged)

### Default Configuration

If no configuration file is found:

```yaml
extends:
  - '@commitlint/config-conventional'

rules:
  type-enum:
    - 2  # error
    - always
    - [feat, fix, docs, style, refactor, test, chore]
  
  scope-enum:
    - 0  # disabled (no scope restrictions)
    - always
    - []
  
  subject-case:
    - 2
    - always
    - [sentence-case]
  
  subject-max-length:
    - 2
    - always
    - 72
```

### Configuration Caching

- **Cache duration**: 60 seconds (in-memory)
- **Invalidation**: On config file modification (check mtime)
- **No disk cache**: All caching in-memory

---

## Environment Variables

### Hook Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COMMIT_TOOLING_VERBOSITY` | enum | `normal` | Logging level: `normal`, `verbose`, `debug` |
| `COMMIT_TOOLING_CONFIG` | string | `.commitlintrc.yml` | Override config file path |
| `COMMIT_TOOLING_PROFILE` | enum | `standard` | Validation profile: `standard`, `strict` |
| `COMMIT_TOOLING_TIMEOUT` | int | `1000` | Hook timeout in milliseconds |
| `COMMIT_TOOLING_SKIP` | bool | `false` | Skip validation (for emergencies) |

### Git Integration Variables (Read-Only)

| Variable | Description | Example |
|----------|-------------|---------|
| `GIT_DIR` | Path to .git directory | `/path/to/repo/.git` |
| `GIT_EDITOR` | Configured Git editor | `vim`, `code --wait` |
| `GIT_AUTHOR_NAME` | Commit author name | `Jane Doe` |
| `GIT_AUTHOR_EMAIL` | Commit author email | `jane@example.com` |

### Examples

```bash
# Skip validation (emergency commits)
COMMIT_TOOLING_SKIP=true git commit -m "emergency fix"

# Use strict profile
COMMIT_TOOLING_PROFILE=strict git commit -m "feat(api): add endpoint"

# Increase timeout for slow CI environments
COMMIT_TOOLING_TIMEOUT=2000 git commit

# Use custom config location
COMMIT_TOOLING_CONFIG=.config/commitlint.yml git commit
```

---

## Performance Guarantees

### Latency Targets

| Scenario | Target | Maximum | Notes |
|----------|--------|---------|-------|
| **Fast Path** (valid commit) | <200ms | <500ms | No errors, minimal logging |
| **Error Path** (invalid commit) | <300ms | <1000ms | Error formatting overhead |
| **Config Parsing** | <50ms | <100ms | First time, then cached |
| **Large Message** (10KB) | <400ms | <1000ms | Includes file I/O |

### Resource Limits

- **Memory**: <10MB per hook invocation
- **CPU**: Single-core, non-blocking I/O
- **Disk I/O**: One config file read (cached), one message file read

### Timeout Behavior

If hook exceeds `COMMIT_TOOLING_TIMEOUT`:

1. Terminate validation with error
2. Print timeout message to stderr
3. Exit with code 3 (internal error)
4. Log timeout event (if verbose/debug mode)

```text
⚠️ Hook timeout exceeded (1000ms)
  Validation did not complete in time.
  Consider increasing timeout: COMMIT_TOOLING_TIMEOUT=2000 git commit
```

---

## Error Handling

### Graceful Degradation

**Missing Configuration**:

- ✅ **Action**: Use default configuration
- ✅ **Output**: Warning logged (verbose mode only)
- ✅ **Exit**: Code 0 (allow commit)

**Invalid Configuration Syntax**:

- ❌ **Action**: Reject commit
- ❌ **Output**: Configuration error message + recovery steps
- ❌ **Exit**: Code 2 (configuration error)

**Missing Dependencies** (Node.js runtime not found for Node projects):

- ❌ **Action**: Reject commit
- ❌ **Output**: Dependency error + installation instructions
- ❌ **Exit**: Code 3 (internal error)

**File I/O Errors** (cannot read commit message file):

- ❌ **Action**: Reject commit
- ❌ **Output**: File error message
- ❌ **Exit**: Code 3 (internal error)

### Recovery Instructions

**Hook Not Executable**:

```bash
chmod +x .git/hooks/commit-msg
```

**Hook Missing**:

```bash
# Python projects
uv run commit-tooling install-hooks

# Node.js projects
pnpm run commit-tooling:install-hooks
```

**Configuration Errors**:

```bash
# Regenerate default configuration
uv run commit-tooling init --force

# Validate configuration
uv run commit-tooling config --validate
```

---

## Testing Interface

### Test Invocation

```bash
# Validate test message file
.git/hooks/commit-msg tests/fixtures/valid_commit.txt

# Validate message from stdin (for CI)
echo "feat(api): add endpoint" | .git/hooks/commit-msg -

# Validate and show debug output
COMMIT_TOOLING_VERBOSITY=debug .git/hooks/commit-msg tests/fixtures/valid_commit.txt
```

### Test Fixtures

**Valid Message** (`tests/fixtures/valid_commit.txt`):

```text
feat(api): add user authentication endpoint

Implements OAuth2 flow with JWT tokens.
```

**Invalid Type** (`tests/fixtures/invalid_type.txt`):

```text
featrue(api): add endpoint
```

**Missing Subject** (`tests/fixtures/missing_subject.txt`):

```text
feat(api):
```

**Too Long** (`tests/fixtures/too_long.txt`):

```text
feat(api): this is an extremely long subject line that exceeds the maximum allowed length of 72 characters
```

### Expected Outputs

| Fixture | Exit Code | STDERR Contains |
|---------|-----------|-----------------|
| `valid_commit.txt` | 0 | (empty in normal mode) |
| `invalid_type.txt` | 1 | `[type-enum] Invalid commit type` |
| `missing_subject.txt` | 1 | `[subject-empty] Subject cannot be empty` |
| `too_long.txt` | 1 | `[subject-max-length] Subject exceeds maximum length` |

---

## Security Considerations

### Input Validation

- **Sanitize commit message**: Escape special characters before regex matching
- **Validate file paths**: Reject paths outside repository root
- **Limit file size**: Reject files >10KB (prevent DoS)

### Code Injection Prevention

- **No eval/exec**: Hook must not execute commit message content as code
- **No shell expansion**: Use subprocess APIs with array arguments (no shell=True)
- **Config validation**: Validate config schema before loading (prevent arbitrary code execution)

### File Permissions

- **Hook file**: `0755` (executable by owner, read-only for others)
- **Config file**: `0644` (read-only for all)
- **Log files**: `0600` (read/write by owner only)

---

## Integration Points

### With Git

- **Pre-commit hook**: No direct integration (commit-msg runs after pre-commit)
- **Commit template**: Hook validates messages from `.gitmessage` template
- **Interactive rebase**: Hook validates fixup/squash commits (skips validation)

### With CI/CD

- **GitHub Actions**: Workflow reads commit messages via `git log`, validates batch
- **Pre-push validation**: Optional validation before push (future enhancement)
- **MR/PR comments**: Validation results posted as comments (future enhancement)

### With CLI Tools

- **Commitizen**: CLI uses same configuration for prompts
- **Husky**: Husky manages hook installation (alternative to built-in script)
- **Conventional Changelog**: Shares commit type conventions

---

## Examples

### Minimal Hook Implementation (Python)

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
from commit_tooling.validator import validate_message

def main():
    if len(sys.argv) < 2:
        print("Usage: commit-msg <message-file>", file=sys.stderr)
        sys.exit(3)
    
    message_file = Path(sys.argv[1])
    if not message_file.exists():
        print(f"Error: Message file not found: {message_file}", file=sys.stderr)
        sys.exit(3)
    
    message = message_file.read_text(encoding='utf-8')
    result = validate_message(message)
    
    if result.is_valid:
        sys.exit(0)
    else:
        print("⚠️ Commit message validation failed:", file=sys.stderr)
        for error in result.errors:
            print(f"  [{error.rule}] {error.message}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Minimal Hook Implementation (Node.js)

```javascript
#!/usr/bin/env node
const fs = require('fs');
const { validateMessage } = require('@commitlint/validate');

async function main() {
  if (process.argv.length < 3) {
    console.error('Usage: commit-msg <message-file>');
    process.exit(3);
  }
  
  const messageFile = process.argv[2];
  if (!fs.existsSync(messageFile)) {
    console.error(`Error: Message file not found: ${messageFile}`);
    process.exit(3);
  }
  
  const message = fs.readFileSync(messageFile, 'utf-8');
  const result = await validateMessage(message);
  
  if (result.valid) {
    process.exit(0);
  } else {
    console.error('⚠️ Commit message validation failed:');
    result.errors.forEach(error => {
      console.error(`  [${error.name}] ${error.message}`);
    });
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Internal error:', err.message);
  process.exit(3);
});
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-02 | Initial contract definition |

---

## References

- Git Hooks Documentation: https://git-scm.com/docs/githooks#_commit_msg
- Conventional Commits Specification: https://www.conventionalcommits.org/
- Feature Spec: `specs/016-conventional-commit-tooling/spec.md`
- Data Model: `specs/016-conventional-commit-tooling/data-model.md`
