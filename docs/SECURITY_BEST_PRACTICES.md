# Security Best Practices for Riso

This document outlines security best practices for developing and maintaining the Riso template system.

## Table of Contents

- [Subprocess Security](#subprocess-security)
- [Input Validation](#input-validation)
- [Authentication & Authorization](#authentication--authorization)
- [Secrets Management](#secrets-management)
- [Dependency Management](#dependency-management)
- [Security Scanning](#security-scanning)

## Subprocess Security

### ⚠️ Never Use `shell=True`

**CRITICAL**: Using `shell=True` with `subprocess` functions opens your code to **shell injection attacks**.

```python
# ❌ BAD: Vulnerable to shell injection
user_input = request.args.get('file')
subprocess.run(f"cat {user_input}", shell=True)  # DANGEROUS!

# ✅ GOOD: Safe from shell injection
from scripts.subprocess_security import run_command_safe
user_input = request.args.get('file')
safe_path = sanitize_path(user_input, allowed_parent=UPLOAD_DIR)
run_command_safe(["cat", str(safe_path)])
```

### Command Execution Best Practices

1. **Always use list-based arguments**:
   ```python
   # ✅ GOOD
   subprocess.run(["ls", "-la", directory])

   # ❌ BAD
   subprocess.run(f"ls -la {directory}", shell=True)
   ```

2. **Always set timeouts**:
   ```python
   # ✅ GOOD
   subprocess.run(["pytest"], timeout=300)

   # ❌ BAD: Can hang forever
   subprocess.run(["pytest"])
   ```

3. **Validate user inputs**:
   ```python
   from scripts.subprocess_security import sanitize_path, validate_command

   # Sanitize paths
   safe_path = sanitize_path(user_path, allowed_parent=WORK_DIR)

   # Validate commands
   validate_command(cmd_list, allowed_commands={"pytest", "ruff", "mypy"})
   ```

4. **Use restricted environments**:
   ```python
   from scripts.subprocess_security import build_restricted_env

   env = build_restricted_env(extra_vars={"MY_VAR": "value"})
   subprocess.run(["command"], env=env)
   ```

### Security Helper Functions

Riso provides security helpers in `scripts/subprocess_security.py`:

```python
from scripts.subprocess_security import (
    run_command_safe,      # Safe subprocess execution
    sanitize_path,         # Path traversal prevention
    validate_command,      # Command validation
    parse_command_safe,    # Safe shell string parsing
    build_restricted_env,  # Restricted environment
)

# Example: Safe command execution
result = run_command_safe(
    ["pytest", "tests/"],
    timeout=300,
    allowed_commands={"pytest", "python"},
)
```

### Common Vulnerabilities

#### 1. Shell Injection

```python
# ❌ VULNERABLE
filename = request.form['filename']
subprocess.run(f"cat {filename}", shell=True)

# Attack: filename = "file.txt; rm -rf /"
# Result: Executes "cat file.txt; rm -rf /"
```

```python
# ✅ SAFE
filename = request.form['filename']
safe_path = sanitize_path(filename, allowed_parent=UPLOAD_DIR)
subprocess.run(["cat", str(safe_path)], shell=False)
```

#### 2. Path Traversal

```python
# ❌ VULNERABLE
user_file = request.args.get('file')
subprocess.run(["cat", user_file])

# Attack: file = "../../etc/passwd"
# Result: Reads /etc/passwd
```

```python
# ✅ SAFE
user_file = request.args.get('file')
safe_path = sanitize_path(user_file, allowed_parent=UPLOAD_DIR)
subprocess.run(["cat", str(safe_path)])
```

#### 3. Command Injection via Arguments

```python
# ❌ VULNERABLE
flags = request.args.get('flags')
subprocess.run(["ls", flags])

# Attack: flags = "-la / && rm -rf /"
# Result: When using shell=True, this would be dangerous
```

```python
# ✅ SAFE
flags = request.args.get('flags')
allowed_flags = {"-la", "-lh", "-a"}
if flags not in allowed_flags:
    raise ValueError("Invalid flags")
subprocess.run(["ls", flags], shell=False)
```

## Input Validation

### Use Pydantic Models

Riso uses Pydantic for type-safe input validation:

```python
from pydantic import BaseModel, Field, field_validator

class ProjectConfig(BaseModel):
    project_name: str = Field(min_length=1, max_length=100)
    project_slug: str = Field(pattern=r"^[a-z][a-z0-9-]*$")

    @field_validator("project_slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug cannot start or end with hyphen")
        return v
```

See `template/hooks/validation.py` for complete examples.

### Validation Best Practices

1. **Validate at boundaries**: Validate all external inputs (user input, API requests, file uploads)
2. **Use allowlists, not denylists**: Explicitly allow known-good values instead of blocking known-bad values
3. **Fail safely**: Reject invalid input rather than trying to sanitize it
4. **Provide clear error messages**: Help users fix validation errors

## Authentication & Authorization

### JWT Authentication

The GraphQL API template uses JWT for authentication:

```python
# See: template/files/python/graphql_api/auth.py.jinja
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Required!
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Validate expiration, claims, etc.
        return payload
    except JWTError as e:
        raise AuthError(f"Invalid token: {e}")
```

### Security Requirements

1. **Always use environment variables for secrets**:
   ```python
   # ✅ GOOD
   SECRET_KEY = os.getenv("JWT_SECRET_KEY")
   if not SECRET_KEY:
       raise RuntimeError("JWT_SECRET_KEY not configured")

   # ❌ BAD
   SECRET_KEY = "hardcoded-secret-key"  # NEVER DO THIS
   ```

2. **Validate token expiration**:
   ```python
   from datetime import datetime, timezone

   exp = payload.get("exp")
   if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
       raise AuthError("Token has expired")
   ```

3. **Use strong algorithms**: HS256 minimum, RS256/ES256 preferred

## Secrets Management

### Environment Variables

1. **Never commit secrets to git**:
   ```bash
   # .env (add to .gitignore)
   JWT_SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://...
   ```

2. **Use `.env.example` for documentation**:
   ```bash
   # .env.example (commit this)
   JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

3. **Validate required secrets on startup**:
   ```python
   import os

   REQUIRED_SECRETS = ["JWT_SECRET_KEY", "DATABASE_URL"]

   for secret in REQUIRED_SECRETS:
       if not os.getenv(secret):
           raise RuntimeError(f"Required secret {secret} not configured")
   ```

### Secret Detection

Riso uses `detect-secrets` to prevent secret leakage:

```bash
# Pre-commit hook runs automatically
detect-secrets scan --baseline .secrets.baseline

# Update baseline after review
detect-secrets scan --baseline .secrets.baseline --update
```

## Dependency Management

### Automated Scanning

1. **Dependabot**: Automated dependency updates (see `.github/dependabot.yml`)
2. **Safety**: Python vulnerability scanning
   ```bash
   uv run safety check
   ```
3. **npm audit**: Node.js vulnerability scanning
   ```bash
   pnpm audit
   ```

### Best Practices

1. **Pin dependencies**: Use exact versions in production
2. **Regular updates**: Weekly Dependabot schedule
3. **Review changelogs**: Before updating, review breaking changes
4. **Test after updates**: Run full test suite after dependency updates

## Security Scanning

### Pre-commit Hooks

Riso runs security checks automatically:

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/PyCQA/bandit
  hooks:
    - id: bandit
      args: [-r, scripts/, template/hooks/]

- repo: https://github.com/Yelp/detect-secrets
  hooks:
    - id: detect-secrets
      args: [--baseline, .secrets.baseline]
```

### Bandit Security Linter

Bandit detects common security issues:

```python
# Bandit will flag these:
# B602: subprocess with shell=True
# B608: SQL injection risk
# B105: Hardcoded password
# B201: Flask debug=True in production
```

Suppress false positives with:
```python
subprocess.run(["ls"], shell=False)  # noqa: S603 (B603)
```

### Manual Security Audits

Run security scans manually:

```bash
# Bandit
uv run bandit -r scripts/ template/hooks/

# Safety
uv run safety check

# Detect secrets
detect-secrets scan

# Hadolint (Docker)
hadolint .docker/Dockerfile
```

## Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Instead, report security issues privately:

1. Email: security@example.com (update this)
2. GitHub Security Advisories: Use "Report a vulnerability" button
3. Expected response time: 48 hours

See [SECURITY.md](../SECURITY.md) for complete reporting guidelines.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## Security Checklist

Before deploying or releasing:

- [ ] No hardcoded secrets or credentials
- [ ] All `subprocess` calls use `shell=False`
- [ ] Input validation on all external inputs
- [ ] JWT secrets configured via environment variables
- [ ] Dependencies scanned for vulnerabilities
- [ ] Pre-commit hooks passing
- [ ] Security tests passing
- [ ] Secrets detection baseline updated
- [ ] Docker images scanned with hadolint
- [ ] Authentication/authorization tested
- [ ] Error messages don't leak sensitive information
- [ ] Logging doesn't include secrets or PII
